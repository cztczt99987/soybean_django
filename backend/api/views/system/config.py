"""参数设置 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Config
from ...serializers import ConfigSerializer
from ..common import APIView, AuthenticatedViewSet, _CRUDMixin, fail, ok


class SystemNameView(APIView):
    """系统名称（公开接口，供登录页/文档标题使用）。"""

    def get(self, request):
        cfg = Config.objects.filter(code="sys.system.name", is_deleted=False, status="1").first()
        return Response(ok({"name": cfg.value if cfg else ""}))


class ConfigViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Config
    serializer_class = ConfigSerializer
    module_name = "参数设置"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    def _base_qs(self):
        # storage.* 参数由监控-存储管理维护，不在参数设置中展示/编辑
        return super()._base_qs().exclude(code__startswith="storage.")

    @action(detail=False, methods=["get"], url_path="by-key")
    def by_key(self, request):
        code = (request.query_params.get("code") or "").strip()
        if not code:
            return Response(fail("请传入参数键名 code"))
        cfg = Config.objects.filter(code=code, is_deleted=False, status="1").first()
        return Response(ok(ConfigSerializer(cfg).data if cfg else None))
