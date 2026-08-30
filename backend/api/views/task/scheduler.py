"""调度器监控视图：运行状态 / 控制 / 控制台日志。"""

from __future__ import annotations

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response

from ...scheduler import scheduler_engine
from ..common import APIView, _log_operation, fail, ok, require_auth


class SchedulerStatusView(APIView):
    """调度器运行状态与监控指标。"""

    @extend_schema(
        responses={200: OpenApiResponse(description="返回调度器运行状态、任务数、线程等运行指标")},
        summary="获取调度器运行状态",
        description="查询内置调度器的运行状态与监控指标（是否运行、注册任务数、线程信息等）。需登录。",
        tags=["任务管理"],
    )
    @require_auth
    def get(self, request):
        return Response(ok(scheduler_engine.status()))


class SchedulerControlView(APIView):
    """调度器控制: body { action } = start|pause|resume|shutdown|clear|reload。"""

    ACTIONS = ("start", "pause", "resume", "shutdown", "clear", "reload")

    @extend_schema(
        responses={200: OpenApiResponse(description="返回操作后的调度器状态；reload 额外返回 {reloaded: 任务数}")},
        summary="调度器控制",
        description=(
            "对调度器执行控制操作，请求体 { action }，可选值："
            "start 启动 / pause 暂停 / resume 恢复 / shutdown 关闭 / clear 清空任务 / reload 重载全部任务。需登录。"
        ),
        tags=["任务管理"],
    )
    @require_auth
    def post(self, request):
        action = str((request.data or {}).get("action") or "")
        if action not in self.ACTIONS:
            return Response(fail(f"不支持的操作: {action}"))

        if action == "start":
            scheduler_engine.start()
        elif action == "pause":
            if not scheduler_engine.is_running:
                return Response(fail("调度器未运行"))
            scheduler_engine.pause()
        elif action == "resume":
            scheduler_engine.resume()
        elif action == "shutdown":
            scheduler_engine.shutdown()
        elif action == "clear":
            scheduler_engine.clear_jobs()
        elif action == "reload":
            if not scheduler_engine.is_running:
                scheduler_engine.start()
            count = scheduler_engine.reload_jobs()
            return Response(ok({"reloaded": count}))

        _log_operation(request, "调度器监控", f"调度器操作: {action}", op_type="3")
        return Response(ok(scheduler_engine.status()))


class SchedulerConsoleView(APIView):
    """调度器控制台日志: GET ?keyword=xxx。"""

    @extend_schema(
        responses={200: OpenApiResponse(description="返回调度器控制台日志数组（支持 keyword 过滤）")},
        summary="获取调度器控制台日志",
        description="查询调度器运行过程的控制台输出日志，支持 keyword 关键字过滤。需登录。",
        tags=["任务管理"],
    )
    @require_auth
    def get(self, request):
        keyword = (request.query_params.get("keyword") or "").strip()
        return Response(ok(scheduler_engine.console_logs(keyword)))
