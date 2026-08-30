"""定时任务视图：CRUD + 暂停/恢复/立即执行/执行历史。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import TaskExecutionLog, TaskJob
from ...scheduler import scheduler_engine
from ...serializers import TaskJobSerializer
from ..common import AuthenticatedViewSet, _CRUDMixin, _log_operation, crud_schema_view, ok, paginate


@extend_schema_view(**crud_schema_view("定时任务", "任务管理"))
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

    def destroy(self, request, pk=None):
        scheduler_engine.unschedule_job(int(pk))
        return super().destroy(request, pk=pk)

    @extend_schema(
        responses={200: OpenApiResponse(description="data 固定为 true")},
        summary="暂停任务",
        description="将任务置为停用状态并从调度器移除，停止触发；任务配置保留，可随时恢复。",
        tags=["任务管理"],
    )
    @action(detail=True, methods=["post"], url_path="pause")
    def pause(self, request, pk=None):
        """暂停任务: 停用并从调度器移除。"""
        job = self._base_qs().get(pk=pk)
        job.status = "0"
        job.save(update_fields=["status"])
        scheduler_engine.unschedule_job(job.id)
        _log_operation(request, "定时任务", f"暂停任务: {job.name}", op_type="3")
        return Response(ok(True))

    @extend_schema(
        responses={200: OpenApiResponse(description="data 固定为 true")},
        summary="恢复任务",
        description="将任务置为启用状态并重新注册到调度器，恢复按 cron/间隔规则触发。",
        tags=["任务管理"],
    )
    @action(detail=True, methods=["post"], url_path="resume")
    def resume(self, request, pk=None):
        """恢复任务: 启用并重新注册到调度器。"""
        job = self._base_qs().get(pk=pk)
        job.status = "1"
        job.save(update_fields=["status"])
        scheduler_engine.schedule_job(job.id)
        _log_operation(request, "定时任务", f"恢复任务: {job.name}", op_type="3")
        return Response(ok(True))

    @extend_schema(
        responses={200: OpenApiResponse(description="data 固定为 true；执行为异步，结果见执行日志")},
        summary="立即执行任务",
        description="手动触发任务立即异步执行一次，不影响原有调度计划；执行结果可在执行历史中查看。",
        tags=["任务管理"],
    )
    @action(detail=True, methods=["post"], url_path="run-once")
    def run_once(self, request, pk=None):
        """立即执行一次 (异步)。"""
        job = self._base_qs().get(pk=pk)
        scheduler_engine.run_once(job.id)
        _log_operation(request, "定时任务", f"手动执行任务: {job.name}", op_type="3")
        return Response(ok(True))

    @extend_schema(
        responses={200: OpenApiResponse(description="统一响应：data = {current, size, total, records} 分页结构")},
        summary="任务执行历史",
        description="分页查询该任务的执行日志（按开始时间倒序），含执行状态、耗时、结果与异常信息。",
        tags=["任务管理"],
    )
    @action(detail=True, methods=["get"], url_path="logs")
    def logs(self, request, pk=None):
        """任务执行历史。"""
        qs = TaskExecutionLog.objects.filter(job_id=pk, is_deleted=False).order_by("-started_at", "-id")
        return Response(ok(paginate(qs, request, TaskExecutionLogSerializer)))

    @extend_schema(
        responses={200: OpenApiResponse(description="返回 [{key: 处理器标识, label: 中文名称]}")},
        summary="获取内置处理器清单",
        description="返回系统内置的任务处理器列表（key 与说明），供新建/编辑定时任务时选择处理器使用。",
        tags=["任务管理"],
    )
    @action(detail=False, methods=["get"], url_path="handlers")
    def handlers(self, request):
        """内置处理器清单 (供表单下拉)。"""
        from ...scheduler import JOB_HANDLERS  # noqa: PLC0415

        rows = [{"key": k, "label": v.__doc__.splitlines()[0] if v.__doc__ else k} for k, v in JOB_HANDLERS.items()]
        return Response(ok(rows))
