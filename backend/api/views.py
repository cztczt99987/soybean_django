"""后端视图。

统一返回结构: {"code": "0000", "msg": "", "data": ...}
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
from rest_framework.views import APIView

from .models import (
    Config,
    Department,
    DictData,
    DictType,
    Menu,
    OperationLog,
    Post,
    Role,
    User,
)
from .serializers import (
    ConfigSerializer,
    DepartmentFlatSerializer,
    DepartmentSerializer,
    DictDataSerializer,
    DictTypeSerializer,
    MenuFlatSerializer,
    MenuSerializer,
    OperationLogSerializer,
    PostSerializer,
    RoleSerializer,
    UserSerializer,
)

# ===================== 通用工具 =====================

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


def _log_operation(request, module: str, description: str, *, op_type: str = "1", status: str = "1", cost: int = 0, error_msg: str = "", response: str = ""):
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
            request_params=json.dumps(request.query_params) if request.query_params else (json.dumps(request.data) if hasattr(request, "data") and request.data else ""),
            ip=get_client_ip(request),
            response_result=response[:4000] if response else "",
            status=status,
            cost_time=cost,
            error_msg=error_msg,
        )
    except Exception:
        pass


# ===================== 健康检查 / 鉴权 / 路由 =====================


class HealthCheckView(APIView):
    def get(self, request):
        return Response(ok({"status": "ok", "time": timezone.now().isoformat()}))


class LoginView(APIView):
    def post(self, request):
        start = time.perf_counter()
        username = (request.data or {}).get("username") or (request.data or {}).get("userName")
        password = (request.data or {}).get("password")
        if not username or not password:
            resp = fail("账号和密码不能为空")
            return Response(resp)
        user = User.objects.filter(username=username, is_deleted=False).first()
        if not user:
            resp = fail("账号或密码错误")
            return Response(resp, status=status.HTTP_200_OK)
        if user.status != "1":
            resp = fail("账号已被停用")
            return Response(resp)
        if not user.check_password(password):
            resp = fail("账号或密码错误")
            _log_operation(
                request, "auth", f"{username} 登录失败", op_type="8", status="0",
                cost=int((time.perf_counter() - start) * 1000),
                error_msg="密码错误",
            )
            return Response(resp)
        token, refresh = _issue_token(user)
        user.login_ip = get_client_ip(request)
        user.login_at = timezone.now()
        user.save(update_fields=["login_ip", "login_at"])
        _log_operation(
            request, "auth", f"{username} 登录成功", op_type="8",
            cost=int((time.perf_counter() - start) * 1000),
        )
        return Response(ok({"token": token, "refreshToken": refresh}))


class LogoutView(APIView):
    def post(self, request):
        token = _get_token_from_request(request)
        if token:
            entry = _TOKENS.pop(token, None)
            if entry and entry.get("refresh"):
                _TOKENS.pop(entry["refresh"], None)
        return Response(ok(True, msg="登出成功"))


class UserInfoView(APIView):
    @require_auth
    def get(self, request):
        u: User = request.sys_user
        role_codes = list(u.roles.values_list("code", flat=True))
        menu_perms = list(
            Menu.objects.filter(
                roles__in=u.roles.all(),
                is_deleted=False,
                status="1",
                permission__gt="",
            ).values_list("permission", flat=True)
        )
        # 超管自动持有所有权限
        if "R_SUPER" in role_codes:
            menu_perms = list(
                Menu.objects.filter(is_deleted=False, status="1", permission__gt="").values_list(
                    "permission", flat=True
                )
            )
        data = {
            "userId": str(u.id),
            "userName": u.username,
            "nickname": u.nickname,
            "avatar": u.avatar,
            "email": u.email,
            "phone": u.phone,
            "dept": {
                "id": u.department_id,
                "name": u.department.name if u.department else "",
                "code": u.department.code if u.department else "",
            },
            "roles": role_codes,
            "buttons": list(dict.fromkeys(menu_perms)),
        }
        return Response(ok(data))


def _menu_to_route(menu: Menu) -> dict:
    component = menu.component or ("layout.base$view.system" if menu.menu_type == "1" else "")
    meta = {
        "title": menu.title or menu.name,
        "icon": menu.icon or "",
        "order": menu.order or 0,
        "keepAlive": menu.keep_alive,
        "hideInMenu": menu.hide_in_menu,
    }
    if menu.i18n_key:
        meta["i18nKey"] = menu.i18n_key
    if menu.external_link:
        meta["href"] = menu.external_link
    # roles 留空，避免 static 模式二次过滤时与 dynamic 模式冲突
    return {
        "id": str(menu.id),
        "name": menu.name,
        "path": menu.path or f"/{menu.name}",
        "component": component,
        "meta": meta,
        "children": [],
    }


def _menu_to_tree_nodes(menus, parent_id=None):
    nodes = []
    for m in sorted(menus, key=lambda x: (x.order or 0, x.id)):
        if m.parent_id != parent_id:
            continue
        # 按钮级不入路由树
        if m.menu_type == "3":
            continue
        node = _menu_to_route(m)
        children = _menu_to_tree_nodes(menus, m.id)
        if children:
            node["children"] = children
        nodes.append(node)
    return nodes


class ConstantRoutesView(APIView):
    def get(self, request):
        constants = [
            {
                "name": "login",
                "path": "/login/:module?",
                "component": "view._builtin.login.index",
                "meta": {"title": "login", "i18nKey": "route.login", "constant": True},
            },
            {
                "name": "403",
                "path": "/error/403",
                "component": "view._builtin.403.index",
                "meta": {"title": "403", "constant": True},
            },
            {
                "name": "404",
                "path": "/error/404",
                "component": "view._builtin.404.index",
                "meta": {"title": "404", "constant": True},
            },
            {
                "name": "500",
                "path": "/error/500",
                "component": "view._builtin.500.index",
                "meta": {"title": "500", "constant": True},
            },
        ]
        return Response(ok(constants))


class UserRoutesView(APIView):
    @require_auth
    def get(self, request):
        u: User = request.sys_user
        role_ids = list(u.roles.values_list("id", flat=True))
        is_super = any(code == "R_SUPER" for code in u.roles.values_list("code", flat=True))

        menu_qs = Menu.objects.filter(is_deleted=False, status="1", menu_type__in=["1", "2"]).order_by("order", "id")
        if not is_super:
            # 角色关联的菜单 + 其祖先链（保证父目录存在）
            role_menus = Menu.objects.filter(roles__id__in=role_ids, is_deleted=False)
            menu_ids = set(role_menus.values_list("id", flat=True))
            ancestors_ids = set(menu_ids)
            changed = True
            while changed:
                changed = False
                parents = (
                    Menu.objects.filter(children__id__in=list(ancestors_ids))
                    .values_list("id", "parent_id", "is_deleted")
                )
                for pid, ppid, deleted in parents:
                    if deleted:
                        continue
                    if pid not in ancestors_ids:
                        ancestors_ids.add(pid)
                        changed = True
                    if ppid and ppid not in ancestors_ids:
                        ancestors_ids.add(ppid)
                        changed = True
            menu_qs = menu_qs.filter(id__in=list(ancestors_ids))
        menus = list(menu_qs)
        # 始终加上首页
        routes = [
            {
                "id": "home",
                "name": "home",
                "path": "/home",
                "component": "layout.base$view.home",
                "meta": {
                    "title": "首页",
                    "i18nKey": "route.home",
                    "icon": "mdi:monitor-dashboard",
                    "order": 1,
                },
                "children": [],
            },
            *_menu_to_tree_nodes(menus),
        ]
        return Response(ok({"routes": routes, "home": "home"}))


class IsRouteExistView(APIView):
    def get(self, request):
        route_name = (request.query_params.get("routeName") or "").strip()
        if not route_name:
            return Response(ok(False))
        in_const = route_name in {"login", "403", "404", "500", "home"}
        in_menu = Menu.objects.filter(name=route_name, is_deleted=False, status="1").exists()
        return Response(ok(in_const or in_menu))


# ===================== 通用 CRUD 基类 =====================


class _CRUDMixin:
    """把 5 个常用操作 (list/tree/create/update/delete/batch_delete) 统一起来。

    子类赋值:
      model / serializer_class / list_serializer_class(可选) / module_name / log_desc(可选)
    """

    model: type[db_models.Model] = None
    serializer_class: type[serializers.Serializer] = None
    list_serializer_class: type[serializers.Serializer] | None = None
    module_name: str = ""
    list_display_name = ""

    # 子类可覆盖: dict[str, str] key=query_param, value=orm_lookup
    # 如: {"name": "name__icontains", "status": "status"}
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
        # 通用 keyword: keyword 模糊搜索 (charfields)
        kw = params.get("keyword")
        if kw:
            q = Q()
            char_fields = [
                f.name for f in self.model._meta.get_fields()
                if isinstance(f, (db_models.CharField, db_models.TextField, db_models.EmailField))
            ]
            for name in char_fields:
                q |= Q(**{f"{name}__icontains": kw})
            qs = qs.filter(q)
        # 通用时间范围: beginTime / endTime 作用于 created_at 字段
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
        _log_operation(request, self.module_name or self.model.__name__, f"批量删除, 数量={len(ids)}", op_type="4")
        return Response(ok(True))


# ===================== 8 个业务视图 =====================


class DepartmentViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Department
    serializer_class = DepartmentFlatSerializer
    list_serializer_class = DepartmentFlatSerializer
    module_name = "部门管理"
    filter_map = {"name": "name__icontains", "status": "status", "code": "code"}

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        qs = self._apply_query_filters(Department.objects.filter(is_deleted=False), request)
        root = DepartmentFlatSerializer(qs.filter(parent=None), many=True).data
        by_parent = {d["id"]: d for d in root}
        all_items = DepartmentFlatSerializer(qs, many=True).data
        # 构建 children
        node_by_id = {d["id"]: d for d in all_items}
        for d in all_items:
            d["children"] = []
        for d in all_items:
            if d["parentId"] and d["parentId"] in node_by_id:
                node_by_id[d["parentId"]]["children"].append(d)
        trees = [d for d in all_items if not d["parentId"]]
        return Response(ok(trees))

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().order_by("sort_order", "id").values("id", "name", "code", "parent_id"))
        return Response(ok(rows))


class PostViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Post
    serializer_class = PostSerializer
    module_name = "岗位管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))


class RoleViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Role
    serializer_class = RoleSerializer
    module_name = "角色管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))

    @action(detail=True, methods=["post"], url_path="assign-menus")
    def assign_menus(self, request, pk=None):
        role = self._base_qs().get(pk=pk)
        menu_ids = (request.data or {}).get("menuIds") or []
        role.menus.set(menu_ids)
        _log_operation(request, self.module_name, f"分配菜单权限: {role.name}", op_type="5")
        return Response(ok(True))


class MenuViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Menu
    serializer_class = MenuFlatSerializer
    list_serializer_class = MenuFlatSerializer
    module_name = "菜单管理"
    filter_map = {"name": "name__icontains", "status": "status", "menuType": "menu_type"}

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        qs = self._apply_query_filters(Menu.objects.filter(is_deleted=False), request)
        all_items = MenuFlatSerializer(qs, many=True).data
        for d in all_items:
            d["children"] = []
        by_id = {d["id"]: d for d in all_items}
        for d in all_items:
            if d["parentId"] and d["parentId"] in by_id:
                by_id[d["parentId"]]["children"].append(d)
        return Response(ok([d for d in all_items if not d["parentId"]]))

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "title", "parent_id", "menu_type"))
        return Response(ok(rows))


class UserViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = User
    serializer_class = UserSerializer
    module_name = "用户管理"
    filter_map = {
        "username": "username__icontains",
        "nickname": "nickname__icontains",
        "phone": "phone__icontains",
        "status": "status",
        "deptId": "department_id",
        "department": "department_id",
    }

    @action(detail=True, methods=["post"], url_path="reset-pwd")
    def reset_pwd(self, request, pk=None):
        u = self._base_qs().get(pk=pk)
        raw = (request.data or {}).get("password") or "123456"
        u.set_password(raw)
        u.save(update_fields=["password"])
        _log_operation(request, self.module_name, f"重置密码: {u.username}", op_type="3")
        return Response(ok(True))

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        u = self._base_qs().get(pk=pk)
        s = (request.data or {}).get("status")
        if s not in ("0", "1"):
            return Response(fail("状态值非法"))
        u.status = s
        u.save(update_fields=["status"])
        _log_operation(request, self.module_name, f"修改状态: {u.username} -> {s}", op_type="3")
        return Response(ok(True))


class DictTypeViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictType
    serializer_class = DictTypeSerializer
    module_name = "字典管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))

    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        dtype = self._base_qs().get(pk=pk)
        rows = DictData.objects.filter(dict_type=dtype, is_deleted=False)
        return Response(ok(DictDataSerializer(rows, many=True).data))


class DictDataViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = DictData
    serializer_class = DictDataSerializer
    module_name = "字典明细"
    filter_map = {"label": "label__icontains", "status": "status", "dictCode": "dict_type__code"}

    @action(detail=False, methods=["get"], url_path="by-code")
    def by_code(self, request):
        code = (request.query_params.get("code") or "").strip()
        if not code:
            return Response(fail("请传入字典编码 code"))
        try:
            dtype = DictType.objects.get(code=code, is_deleted=False)
        except DictType.DoesNotExist:
            return Response(ok([]))
        rows = DictData.objects.filter(dict_type=dtype, is_deleted=False, status="1").order_by(
            "sort_order", "id"
        )
        return Response(ok(DictDataSerializer(rows, many=True).data))


class ConfigViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Config
    serializer_class = ConfigSerializer
    module_name = "参数设置"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="by-key")
    def by_key(self, request):
        code = (request.query_params.get("code") or "").strip()
        if not code:
            return Response(fail("请传入参数键名 code"))
        cfg = Config.objects.filter(code=code, is_deleted=False, status="1").first()
        return Response(ok(ConfigSerializer(cfg).data if cfg else None))


class OperationLogViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = OperationLog
    serializer_class = OperationLogSerializer
    module_name = "操作日志"
    http_method_names = ["get", "delete", "head", "options"]
    filter_map = {
        "username": "username__icontains",
        "module": "module__icontains",
        "description": "description__icontains",
        "operationType": "operation_type",
        "status": "status",
    }

    @action(detail=False, methods=["post"], url_path="clean")
    def clean(self, request):
        days = int((request.data or {}).get("days") or 30)
        from datetime import timedelta

        threshold = timezone.now() - timedelta(days=days)
        n, _ = OperationLog.objects.filter(operated_at__lt=threshold).delete()
        return Response(ok({"deleted": n}))
