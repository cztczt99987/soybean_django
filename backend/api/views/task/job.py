"""定时任务视图：CRUD + 暂停/恢复/立即执行/执行历史。"""

from __future__ import annotations

from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import TaskExecutionLog, TaskJob
from ...scheduler import scheduler_engine
from ...serializers import TaskJobSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, _log_operation, ok, paginate


class TaskJobViewSet(_CRUDMixin, AuthenticatedViewSet):
    model = TaskJob
    serializer_class = TaskJobSerializer
    module_name = "定时任务"
    filter_map = {"name": "name__icontains", "status": "status", "trigger_type": "trigger_type"}

    def _after_mutation(self, instance=None):
        """任务数据变更后同步调度器。"""
        if instance is None:
            return
        if getattr(instance, "is_deleted", False) or instance.status != "1":
            scheduler_engine.unschedule_job(instance.id)
        else:
            scheduler_engine.schedule_job(instance.id)

    def create(self, request):
        resp = super().create(request)
        return resp

    def destroy(self, request, pk=None):
        scheduler_engine.unschedule_job(int(pk))
        return super().destroy(request, pk=pk)

    @action(detail=True, methods=["post"], url_path="pause")
    def pause(self, request, pk=None):
        """暂停任务: 停用并从调度器移除。"""
        job = self._base_qs().get(pk=pk)
        job.status = "0"
        job.save(update_fields=["status"])
        scheduler_engine.unschedule_job(job.id)
        _log_operation(request, "定时任务", f"暂停任务: {job.name}", op_type="3")
        return Response(ok(True))

    @action(detail=True, methods=["post"], url_path="resume")
    def resume(self, request, pk=None):
        """恢复任务: 启用并重新注册到调度器。"""
        job = self._base_qs().get(pk=pk)
        job.status = "1"
        job.save(update_fields=["status"])
        scheduler_engine.schedule_job(job.id)
        _log_operation(request, "定时任务", f"恢复任务: {job.name}", op_type="3")
        return Response(ok(True))

    @action(detail=True, methods=["post"], url_path="run-once")
    def run_once(self, request, pk=None):
        """立即执行一次 (异步)。"""
        job = self._base_qs().get(pk=pk)
        scheduler_engine.run_once(job.id)
        _log_operation(request, "定时任务", f"手动执行任务: {job.name}", op_type="3")
        return Response(ok(True))

    @action(detail=True, methods=["get"], url_path="logs")
    def logs(self, request, pk=None):
        """任务执行历史。"""
        qs = TaskExecutionLog.objects.filter(job_id=pk, is_deleted=False).order_by("-started_at", "-id")
        return Response(ok(paginate(qs, request, TaskExecutionLogSerializer)))

    @action(detail=False, methods=["get"], url_path="handlers")
    def handlers(self, request):
        """内置处理器清单 (供表单下拉)。"""
        from ...scheduler import JOB_HANDLERS  # noqa: PLC0415

        rows = [{"key": k, "label": v.__doc__.splitlines()[0] if v.__doc__ else k} for k, v in JOB_HANDLERS.items()]
        return Response(ok(rows))
