"""岗位管理 ViewSet。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Post
from ...serializers import PostSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, ok


class PostViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Post
    serializer_class = PostSerializer
    module_name = "岗位管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))
