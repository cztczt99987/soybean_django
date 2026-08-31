"""参数设置视图。"""

from __future__ import annotations

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Config
from ...serializers import ConfigSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, crud_schema_view, fail, ok


class SystemNameView(APIView):
    """系统名称（公开接口，供登录页/文档标题使用）。"""

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 {name: 系统名称}；未配置时 name 为空字符串")},
        summary="获取系统名称",
        description="公开接口。读取参数 sys.system.name 的值，用于登录页标题、浏览器标签等展示。",
        tags=["系统管理"],
    )
    def get(self, request):
        cfg = Config.objects.filter(code="sys.system.name", is_deleted=False, status="1").first()
        return Response(ok({"name": cfg.value if cfg else ""}))


@extend_schema_view(**crud_schema_view("系统参数", "系统管理"))
class ConfigViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Config
    serializer_class = ConfigSerializer
    module_name = "参数设置"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    def _base_qs(self):
        # storage.* 参数由监控-存储管理维护，不在参数设置中展示/编辑
        return super()._base_qs().exclude(code__startswith="storage.")

    @extend_schema(
        parameters=[OpenApiParameter("code", str, OpenApiParameter.QUERY, description="参数键名，如 sys.system.name")],
        responses={200: OpenApiResponse(description="返回参数对象；code 未传或不存在时 data 为 null")},
        summary="按键名查询参数",
        description="按参数键名（code）精确查询单个系统参数，供业务模块读取配置使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="by-key")
    def by_key(self, request):
        code = (request.query_params.get("code") or "").strip()
        if not code:
            return Response(fail("请传入参数键名 code"))
        cfg = Config.objects.filter(code=code, is_deleted=False, status="1").first()
        return Response(ok(ConfigSerializer(cfg).data if cfg else None))
