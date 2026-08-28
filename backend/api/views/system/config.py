"""参数设置 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Config
from ...serializers import ConfigSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, fail, ok


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
