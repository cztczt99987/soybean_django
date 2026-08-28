"""views 通用组件。

包含：
- 统一响应码 ok/fail
- 分页 paginate
- 客户端 IP / 操作日志
- 极简 Bearer Token（内存存储）+ require_auth 装饰器 + AuthenticatedViewSet
- 通用 CRUD Mixin：_CRUDMixin
"""

from __future__ import annotations

import json
import secrets
import time
from functools import wraps

from django.db import models as db_models
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView  # noqa: F401  由子模块直接使用

from ..models import OperationLog, User

# ===================== 响应常量 =====================

SUCCESS_CODE = "0000"
ERROR_CODE = "5000"
AUTH_CODE = "1000"


def ok(data=None, msg: str = "") -> dict:
    return {"code": SUCCESS_CODE, "msg": msg, "data": data}


def fail(msg: str, code: str = ERROR_CODE, data=None) -> dict:
    return {"code": code, "msg": msg, "data": data}


def paginate(queryset, request, mapper=None):
    """简单分页：current / size / total / records。"""

    current = int(request.query_params.get("current") or 1)
    size = min(int(request.query_params.get("size") or 10), 500)
    total = queryset.count()
    start = (current - 1) * size
    rows = queryset[start : start + size]
    if mapper is None:
        serializer_cls = None
    elif isinstance(mapper, type):
        serializer_cls = mapper
        mapper = None
    else:
        serializer_cls = None

    if mapper:
        records = [mapper(x) for x in rows]
    else:
        if serializer_cls is None:
            records = list(rows.values())
        else:
            records = serializer_cls(rows, many=True).data
    return {
        "current": current,
        "size": size,
        "total": total,
        "records": records,
    }


def get_client_ip(request: HttpRequest) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


# ===================== 极简 Token 认证 =====================
# 开发阶段使用内存 token 存储；生产可替换为 Redis 或 JWT。

_TOKENS: dict[str, dict] = {}


def _issue_token(user: User) -> tuple[str, str]:
    token = secrets.token_hex(32)
    refresh = secrets.token_hex(32)
    _TOKENS[token] = {
        "user_id": user.id,
        "refresh": refresh,
        "expires_at": time.time() + 3600 * 8,
    }
    _TOKENS[refresh] = {
        "user_id": user.id,
        "is_refresh": True,
        "expires_at": time.time() + 3600 * 24 * 7,
    }
    return token, refresh


def _get_token_from_request(request) -> str | None:
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if header.lower().startswith("bearer "):
        return header.split(" ", 1)[1].strip()
    return None


def _get_current_user(request) -> User | None:
    token = _get_token_from_request(request)
    if not token:
        return None
    entry = _TOKENS.get(token)
    if not entry or entry.get("is_refresh"):
        return None
    if entry.get("expires_at", 0) < time.time():
        _TOKENS.pop(token, None)
        return None
    return User.objects.filter(id=entry["user_id"], is_deleted=False, status="1").first()


def require_auth(view_func):
    """装饰器：要求登录。"""

    @wraps(view_func)
    def _wrapped(self, request, *args, **kwargs):
        user = _get_current_user(request)
        if not user:
            return Response(
                fail("未登录或会话已过期", code=AUTH_CODE),
                status=status.HTTP_401_UNAUTHORIZED,
            )
        request.sys_user = user
        return view_func(self, request, *args, **kwargs)

    return _wrapped


class AuthenticatedViewSet(viewsets.GenericViewSet):
    """所有业务 CRUD 都要求登录；会把当前用户挂到 request.sys_user。"""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = _get_current_user(request)
        if not user:
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("未登录或会话已过期")
        request.sys_user = user


def _log_operation(
    request,
    module: str,
    description: str,
    *,
    op_type: str = "1",
    status: str = "1",
    cost: int = 0,
    error_msg: str = "",
    response: str = "",
):
    try:
        user = getattr(request, "sys_user", None) or _get_current_user(request)
        OperationLog.objects.create(
            user=user,
            username=user.username if user else "",
            module=module,
            description=description,
            operation_type=op_type,
            method=request.method,
            request_url=request.path,
            request_params=(
                json.dumps(request.query_params)
                if request.query_params
                else (json.dumps(request.data) if hasattr(request, "data") and request.data else "")
            ),
            ip=get_client_ip(request),
            response_result=response[:4000] if response else "",
            status=status,
            cost_time=cost,
            error_msg=error_msg,
        )
    except Exception:
        pass


# ===================== 通用 CRUD 基类 =====================


class _CRUDMixin:
    """把 5 个常用操作 (list/tree/create/update/delete/batch_delete) 统一起来。

    子类赋值:
      model / serializer_class / list_serializer_class(可选) / module_name
      filter_map(可选): dict[str, str] key=query_param, value=orm_lookup
    """

    model: type[db_models.Model] = None
    serializer_class: type[serializers.Serializer] = None
    list_serializer_class: type[serializers.Serializer] | None = None
    module_name: str = ""
    list_display_name = ""

    filter_map: dict[str, str] = {}

    def _base_qs(self):
        if hasattr(self.model, "_meta") and "is_deleted" in {f.name for f in self.model._meta.get_fields()}:
            return self.model.objects.filter(is_deleted=False)
        return self.model.objects.all()

    def _apply_query_filters(self, qs, request):
        params = request.query_params
        for key, lookup in self.filter_map.items():
            v = params.get(key)
            if v not in (None, ""):
                qs = qs.filter(**{lookup: v})
        # 通用 keyword：charfield 模糊搜索
        kw = params.get("keyword")
        if kw:
            q = Q()
            char_fields = [
                f.name
                for f in self.model._meta.get_fields()
                if isinstance(f, (db_models.CharField, db_models.TextField, db_models.EmailField))
            ]
            for name in char_fields:
                q |= Q(**{f"{name}__icontains": kw})
            qs = qs.filter(q)
        # 通用 beginTime / endTime（作用于 created_at）
        bt = params.get("beginTime")
        et = params.get("endTime")
        if hasattr(self.model, "created_at"):
            if bt:
                qs = qs.filter(created_at__gte=bt)
            if et:
                qs = qs.filter(created_at__lte=et + " 23:59:59" if len(et) <= 10 else et)
        return qs

    def list(self, request):
        qs = self._apply_query_filters(self._base_qs(), request)
        data = paginate(qs, request, self.list_serializer_class or self.serializer_class)
        return Response(ok(data))

    def retrieve(self, request, pk=None):
        obj = self._base_qs().get(pk=pk)
        return Response(ok(self.serializer_class(obj).data))

    def create(self, request):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        instance = ser.save()
        _log_operation(request, self.module_name or self.model.__name__, f"新增: {instance}", op_type="2")
        return Response(ok(ser.data))

    def update(self, request, pk=None):
        obj = self._base_qs().get(pk=pk)
        ser = self.serializer_class(obj, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        instance = ser.save()
        _log_operation(request, self.module_name or self.model.__name__, f"修改: {instance}", op_type="3")
        return Response(ok(ser.data))

    def destroy(self, request, pk=None):
        obj = self._base_qs().get(pk=pk)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
            obj.save(update_fields=["is_deleted"])
        else:
            obj.delete()
        _log_operation(request, self.module_name or self.model.__name__, f"删除: {obj}", op_type="4")
        return Response(ok(True))

    @action(detail=False, methods=["post"], url_path="batch-delete")
    def batch_delete(self, request):
        ids = (request.data or {}).get("ids") or (request.data or {}).get("idList") or []
        if not ids:
            return Response(fail("请指定要删除的记录 ID 列表"))
        qs = self._base_qs().filter(id__in=list(ids))
        if hasattr(self.model, "is_deleted"):
            qs.update(is_deleted=True)
        else:
            qs.delete()
        _log_operation(
            request, self.module_name or self.model.__name__, f"批量删除, 数量={len(ids)}", op_type="4"
        )
        return Response(ok(True))
