"""调度器监控视图：运行状态 / 控制 / 控制台日志。"""

from __future__ import annotations

from rest_framework.response import Response

from ...scheduler import scheduler_engine
from ..common import APIView, _log_operation, fail, ok, require_auth


class SchedulerStatusView(APIView):
    """调度器运行状态与监控指标。"""

    @require_auth
    def get(self, request):
        return Response(ok(scheduler_engine.status()))


class SchedulerControlView(APIView):
    """调度器控制: body { action } = start|pause|resume|shutdown|clear|reload。"""

    ACTIONS = ("start", "pause", "resume", "shutdown", "clear", "reload")

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

    @require_auth
    def get(self, request):
        keyword = (request.query_params.get("keyword") or "").strip()
        return Response(ok(scheduler_engine.console_logs(keyword)))
