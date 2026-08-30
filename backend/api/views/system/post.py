"""岗位管理 ViewSet。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Post
from ...serializers import PostSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, crud_schema_view, ok


@extend_schema_view(**crud_schema_view("岗位", "系统管理"))
class PostViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = Post
    serializer_class = PostSerializer
    module_name = "岗位管理"
    filter_map = {"name": "name__icontains", "code": "code__icontains", "status": "status"}

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 [{id, name, code}]，仅含启用状态的岗位")},
        summary="获取岗位下拉选项",
        description="返回全部启用状态岗位的精简列表，供用户管理表单选择岗位使用。",
        tags=["系统管理"],
    )
    @action(detail=False, methods=["get"], url_path="options")
    def options(self, request):
        rows = list(self._base_qs().filter(status="1").values("id", "name", "code"))
        return Response(ok(rows))
