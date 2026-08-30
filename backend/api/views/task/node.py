"""执行节点视图：CRUD + 启用/禁用 + 心跳上报。"""

from __future__ import annotations

from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import SchedulerNode
from ...serializers import SchedulerNodeSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, _log_operation, fail, ok


class SchedulerNodeViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = SchedulerNode
    serializer_class = SchedulerNodeSerializer
    module_name = "执行节点"
    filter_map = {"name": "name__icontains", "status": "status"}

    def _after_mutation(self, instance=None):
        pass

    def destroy(self, request, pk=None):
        node = self._base_qs().get(pk=pk)
        if node.is_local:
            return Response(fail("本机节点不允许删除"))
        return super().destroy(request, pk=pk)

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle(self, request, pk=None):
        """启用/禁用节点。"""
        node = self._base_qs().get(pk=pk)
        node.status = "0" if node.status == "1" else "1"
        node.save(update_fields=["status"])
        _log_operation(request, "执行节点", f"{'启用' if node.status == '1' else '禁用'}节点: {node.name}", op_type="3")
        return Response(ok(SchedulerNodeSerializer(node).data))

    @action(detail=False, methods=["post"], url_path="heartbeat")
    def heartbeat(self, request):
        """远程执行代理心跳上报: body { nodeId, load, version }。"""
        data = request.data or {}
        node_id = str(data.get("nodeId") or "")
        if not node_id:
            return Response(fail("缺少 nodeId"))
        node = SchedulerNode.objects.filter(node_id=node_id, is_deleted=False).first()
        if node is None:
            return Response(fail("节点未注册"))
        node.heartbeat_at = timezone.now()
        node.current_load = int(data.get("load") or 0)
        if data.get("version"):
            node.version = str(data["version"])[:32]
        node.save(update_fields=["heartbeat_at", "current_load", "version"])
        return Response(ok(True))
