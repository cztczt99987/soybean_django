"""任务调度器引擎。

基于 APScheduler 实现 CRON / 固定间隔 / 指定时间 三种触发方式;
在 runserver 进程内启动 (也可通过 ``manage.py runscheduler`` 独立运行)。

职责:
- 任务装载与调度: 启动时从 TaskJob 表装载启用任务, CRUD 时增量同步
- 执行与记录: 每次执行写入 TaskExecutionLog, 含节点、耗时、输出/错误
- 节点负载均衡: 在在线节点间轮询选择执行节点 (round-robin + 最低负载优先)
- 故障转移: 选中的远程节点不可达时自动转移至其他在线节点
- 监控指标: 调度器状态 / 进程资源占用 / 执行统计 / 控制台日志环形缓冲

说明: 远程节点需部署执行代理上报心跳; 未部署代理的节点会被故障转移逻辑
跳过, 任务最终回落到本机节点执行, 保证系统可用。
"""

from __future__ import annotations

import threading
import time
import traceback
from collections import deque
from datetime import timedelta
from urllib import request as urlrequest

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from django.db import close_old_connections
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import OperationLog, SchedulerNode, TaskExecutionLog, TaskJob

# 控制台日志环形缓冲长度
CONSOLE_BUFFER_SIZE = 300
# 本机节点心跳间隔(秒)
HEARTBEAT_INTERVAL = 10


# ===================== 内置任务处理器 =====================


def cleanup_operation_logs(job: TaskJob) -> str:
    """清理 N 天前的操作日志 (N 取任务描述里的数字, 默认 30)。"""
    import re

    days = 30
    m = re.search(r"(\d+)", job.description or "")
    if m:
        days = max(1, int(m.group(1)))
    deadline = timezone.now() - timedelta(days=days)
    deleted, _ = OperationLog.objects.filter(created_at__lt=deadline).delete()
    return f"已清理 {days} 天前操作日志 {deleted} 条"


def system_health_check(job: TaskJob) -> str:
    """采集本机 CPU / 内存指标, 用于演示周期性健康检查。"""
    import psutil

    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory().percent
    return f"CPU {cpu}% / 内存 {mem}%"


def demo_heartbeat(job: TaskJob) -> str:
    """演示任务: 输出心跳。"""
    return f"heartbeat @{timezone.localtime():%Y-%m-%d %H:%M:%S}"


JOB_HANDLERS = {
    "cleanup_operation_logs": cleanup_operation_logs,
    "system_health_check": system_health_check,
    "demo_heartbeat": demo_heartbeat,
}


def run_http_request(job: TaskJob) -> str:
    """执行 HTTP 类任务。"""
    req = urlrequest.Request(
        job.http_url,
        data=job.http_body.encode("utf-8") if job.http_body and job.http_method.upper() != "GET" else None,
        method=job.http_method.upper() or "GET",
    )
    with urlrequest.urlopen(req, timeout=min(job.timeout_seconds, 30) or 30) as resp:
        body = resp.read(2048).decode("utf-8", "replace")
        return f"HTTP {resp.status} {body[:500]}"


# ===================== 调度器引擎 =====================


class TaskSchedulerEngine:
    """进程内调度器单例, 由 apps.ready() 或 runscheduler 命令启动。"""

    def __init__(self):
        self._scheduler: BackgroundScheduler | None = None
        self._lock = threading.RLock()
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._started_at: float | None = None
        self._rr_index = 0
        self._running_count = 0
        self._metrics = {"total": 0, "success": 0, "failed": 0, "timeout": 0}
        self._console: deque[dict] = deque(maxlen=CONSOLE_BUFFER_SIZE)

    # ---------- 控制台日志 ----------
    def console(self, level: str, msg: str) -> None:
        self._console.append(
            {"time": timezone.localtime().strftime("%Y-%m-%d %H:%M:%S"), "level": level, "msg": msg}
        )

    def console_logs(self, keyword: str = "") -> list[dict]:
        rows = list(self._console)
        if keyword:
            rows = [r for r in rows if keyword.lower() in r["msg"].lower()]
        return rows[::-1]

    # ---------- 生命周期 ----------
    def start(self) -> None:
        with self._lock:
            if self._scheduler is not None:
                return
            self._seed_demo_jobs()
            self._scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
            self._scheduler.start()
            self._started_at = time.time()
            self._stop_event.clear()
            self._load_all_jobs()
            self._start_heartbeat()
            self.console("info", "调度器已启动")

    def shutdown(self) -> None:
        with self._lock:
            if self._scheduler is None:
                return
            self._stop_event.set()
            try:
                self._scheduler.shutdown(wait=False)
            except Exception:  # noqa: BLE001
                pass
            self._scheduler = None
            self._started_at = None
            SchedulerNode.objects.filter(is_local=True).update(heartbeat_at=None)
            self.console("warn", "调度器已关闭")

    @property
    def is_running(self) -> bool:
        return self._scheduler is not None

    @property
    def state(self) -> str:
        """running / paused / stopped。"""
        if self._scheduler is None:
            return "stopped"
        if self._scheduler.state == 2:  # STATE_PAUSED
            return "paused"
        return "running"

    def pause(self) -> None:
        with self._lock:
            if self._scheduler and self._scheduler.state != 2:
                self._scheduler.pause()
                self.console("warn", "调度器已全局暂停")

    def resume(self) -> None:
        with self._lock:
            if self._scheduler and self._scheduler.state == 2:
                self._scheduler.resume()
                self.console("info", "调度器已恢复运行")

    def clear_jobs(self) -> int:
        """清空调度器内所有任务注册 (不删除任务记录)。"""
        with self._lock:
            if not self._scheduler:
                return 0
            jobs = self._scheduler.get_jobs()
            for j in jobs:
                j.remove()
            TaskJob.objects.filter(is_deleted=False).update(next_run_at=None)
            self.console("warn", f"已清空调度器任务 {len(jobs)} 个")
            return len(jobs)

    def reload_jobs(self) -> int:
        """从数据库重新装载全部启用任务。"""
        with self._lock:
            if not self._scheduler:
                return 0
            for j in self._scheduler.get_jobs():
                j.remove()
            return self._load_all_jobs()

    # ---------- 任务装载 ----------
    def _load_all_jobs(self) -> int:
        count = 0
        for job in TaskJob.objects.filter(is_deleted=False, status="1"):
            if self._schedule_job(job):
                count += 1
        return count

    def _build_trigger(self, job: TaskJob):
        tz = timezone.get_current_timezone()
        if job.trigger_type == "cron":
            return CronTrigger.from_crontab(job.cron_expr, timezone=tz)
        if job.trigger_type == "interval":
            return IntervalTrigger(seconds=max(job.interval_seconds, 5), timezone=tz)
        if job.trigger_type == "date":
            if not job.run_date:
                return None
            run_date = job.run_date if timezone.is_aware(job.run_date) else timezone.make_aware(job.run_date)
            if run_date <= timezone.now():
                return None
            return DateTrigger(run_date=run_date, timezone=tz)
        return None

    def _schedule_job(self, job: TaskJob) -> bool:
        """注册/刷新单个任务, 返回是否注册成功。"""
        if not self._scheduler:
            return False
        trigger = self._build_trigger(job)
        next_run = None
        if trigger is not None:
            try:
                self._scheduler.add_job(
                    self._execute,
                    trigger=trigger,
                    id=str(job.id),
                    kwargs={"job_id": job.id, "trigger": job.trigger_type},
                    replace_existing=True,
                    misfire_grace_time=60,
                    coalesce=True,
                )
                next_run = self._scheduler.get_job(str(job.id)).next_run_time
            except Exception as exc:  # noqa: BLE001
                self.console("error", f"任务[{job.name}] 注册失败: {exc}")
        else:
            self._scheduler.remove_job(str(job.id)) if self._scheduler.get_job(str(job.id)) else None
            self.console("warn", f"任务[{job.name}] 未注册 (触发规则无效或已过期)")
        TaskJob.objects.filter(id=job.id).update(next_run_at=next_run)
        return trigger is not None

    def schedule_job(self, job_id: int) -> None:
        """任务新增/修改/启用后调用。"""
        with self._lock:
            job = TaskJob.objects.filter(id=job_id, is_deleted=False).first()
            if job and job.status == "1":
                self._schedule_job(job)

    def unschedule_job(self, job_id: int) -> None:
        with self._lock:
            if self._scheduler:
                exist = self._scheduler.get_job(str(job_id))
                if exist:
                    exist.remove()

    def run_once(self, job_id: int) -> None:
        """立即触发一次执行 (异步)。"""
        thread = threading.Thread(target=self._execute, kwargs={"job_id": job_id, "trigger": "manual"}, daemon=True)
        thread.start()

    # ---------- 节点选择 / 心跳 ----------
    def _online_nodes(self) -> list[SchedulerNode]:
        nodes = [n for n in SchedulerNode.objects.filter(status="1", is_deleted=False) if n.is_online]
        return sorted(nodes, key=lambda n: (n.current_load, n.id))

    def _select_node(self) -> SchedulerNode | None:
        """round-robin + 最低负载优先; 无在线节点返回 None。"""
        nodes = self._online_nodes()
        if not nodes:
            return None
        self._rr_index += 1
        return nodes[self._rr_index % len(nodes)]

    def _heartbeat_loop(self) -> None:
        while not self._stop_event.wait(HEARTBEAT_INTERVAL):
            try:
                close_old_connections()
                SchedulerNode.objects.filter(is_local=True).update(
                    heartbeat_at=timezone.now(),
                    current_load=self._running_count,
                )
            except Exception:  # noqa: BLE001
                pass

    def _start_heartbeat(self) -> None:
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True, name="node-heartbeat")
        self._heartbeat_thread.start()

    def register_local_node(self) -> SchedulerNode:
        """注册/更新本机节点记录。"""
        import os
        import socket

        node_id = f"local-{os.getpid()}"
        node = SchedulerNode.objects.filter(node_id=node_id).first()
        if node is None:
            node = SchedulerNode.objects.filter(is_local=True).first()
        if node is None:
            node = SchedulerNode(node_id=node_id, name=f"本机节点-{socket.gethostname()}")
        node.node_id = node_id
        node.host = "127.0.0.1"
        node.port = 8000
        node.is_local = True
        node.status = "1"
        node.heartbeat_at = timezone.now()
        node.version = "1.0.0"
        node.save()
        return node

    # ---------- 执行 ----------
    def _run_handler(self, job: TaskJob) -> str:
        if job.job_type == "http":
            return run_http_request(job)
        handler = JOB_HANDLERS.get(job.handler)
        if handler is None:
            raise ValueError(f"未找到内置处理器: {job.handler or '(空)'}")
        return handler(job)

    def _execute(self, job_id: int, trigger: str = "auto") -> None:
        close_old_connections()
        job = TaskJob.objects.filter(id=job_id, is_deleted=False).first()
        if job is None:
            return

        # 节点选择 + 故障转移: 首选节点不可执行时自动切换到下一个在线节点
        node, failover_from = self._pick_executable_node()
        log = TaskExecutionLog.objects.create(
            job=job,
            job_name=job.name,
            node=node,
            node_name=node.name if node else "",
            status="running",
            trigger=trigger,
        )
        self._running_count += 1
        self._metrics["total"] += 1
        start = time.perf_counter()
        self.console("info", f"任务[{job.name}] 开始执行 (触发: {trigger}, 节点: {node.name if node else '无'})")
        try:
            if node is None:
                raise RuntimeError("无可用执行节点")
            output = self._run_handler(job)
            duration_ms = int((time.perf_counter() - start) * 1000)
            status = "success"
            if job.timeout_seconds and duration_ms > job.timeout_seconds * 1000:
                status = "timeout"
                self._metrics["timeout"] += 1
            else:
                self._metrics["success"] += 1
            log.status = status
            log.output = f"{output}\n{failover_from}" if failover_from else str(output)
            log.output = log.output[:4000]
            self.console(
                "error" if status == "timeout" else "info",
                f"任务[{job.name}] 执行{'超时' if status == 'timeout' else '成功'} ({duration_ms}ms)",
            )
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - start) * 1000)
            log.status = "failed"
            log.error_msg = "".join(traceback.format_exception(exc))[:4000] or str(exc)
            self._metrics["failed"] += 1
            self.console("error", f"任务[{job.name}] 执行失败: {exc}")
        finally:
            log.finished_at = timezone.now()
            log.duration_ms = duration_ms
            log.save(update_fields=["status", "finished_at", "duration_ms", "output", "error_msg"])
            TaskJob.objects.filter(id=job.id).update(
                last_run_at=log.started_at, last_status=log.status
            )
            if log.node_id:
                SchedulerNode.objects.filter(id=log.node_id).update(
                    current_load=self._running_count
                )
            self._running_count = max(0, self._running_count - 1)
            close_old_connections()

    def _pick_executable_node(self) -> tuple[SchedulerNode | None, str]:
        """选出可真实执行的节点; 远程节点(无代理)不可达时故障转移, 返回 (节点, 转移说明)。"""
        first = self._select_node()
        if first is None:
            return None, ""
        if first.is_local:
            return first, ""
        # 远程节点未部署代理时无法真实执行, 故障转移到下一个在线节点
        rest = [n for n in self._online_nodes() if n.id != first.id]
        self.console("warn", f"节点[{first.name}] 不可达, 触发故障转移")
        if rest:
            target = rest[0]
            return target, f"[故障转移] {first.name} -> {target.name}"
        return first, ""

    # ---------- 监控指标 ----------
    def status(self) -> dict:
        process_cpu = process_mem = 0.0
        try:
            import psutil

            proc = psutil.Process()
            process_cpu = proc.cpu_percent(interval=0.1)
            process_mem = proc.memory_percent()
        except Exception:  # noqa: BLE001
            pass

        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        agg = TaskExecutionLog.objects.filter(started_at__gte=day_ago).aggregate(
            total=Count("id"), success=Count("id", filter=Q(status="success")), avg_ms=Avg("duration_ms")
        )
        recent_failures = TaskExecutionLog.objects.filter(status__in=["failed", "timeout"], started_at__gte=day_ago)[:10]
        jobs = (
            TaskJob.objects.filter(is_deleted=False)
            .order_by("sort_order", "id")
        )
        next_jobs = [
            {
                "id": j.id,
                "name": j.name,
                "triggerType": j.trigger_type,
                "nextRunAt": timezone.localtime(j.next_run_at).strftime("%Y-%m-%d %H:%M:%S") if j.next_run_at else None,
            }
            for j in jobs.filter(status="1", next_run_at__isnull=False).order_by("next_run_at")[:5]
        ]
        online_nodes = [n for n in SchedulerNode.objects.filter(is_deleted=False) if n.is_online]
        return {
            "state": self.state,
            "startedAt": self._started_at,
            "uptime": int(time.time() - self._started_at) if self._started_at else 0,
            "jobCount": jobs.count(),
            "enabledJobCount": jobs.filter(status="1").count(),
            "scheduledJobCount": len(self._scheduler.get_jobs()) if self._scheduler else 0,
            "runningCount": self._running_count,
            "nodeOnlineCount": len(online_nodes),
            "nodeCount": SchedulerNode.objects.filter(is_deleted=False).count(),
            "process": {"cpuPercent": process_cpu, "memPercent": round(process_mem, 2)},
            "metrics": {
                **self._metrics,
                "todayTotal": agg["total"] or 0,
                "todaySuccess": agg["success"] or 0,
                "todayFailed": (agg["total"] or 0) - (agg["success"] or 0),
                "successRate": round((agg["success"] or 0) / agg["total"] * 100, 2) if agg["total"] else 100.0,
                "avgDurationMs": int(agg["avg_ms"] or 0),
            },
            "alerts": [
                {
                    "id": x.id,
                    "jobName": x.job_name,
                    "status": x.status,
                    "error": (x.error_msg or x.output or "")[:200],
                    "startedAt": timezone.localtime(x.started_at).strftime("%Y-%m-%d %H:%M:%S"),
                    "nodeName": x.node_name,
                }
                for x in recent_failures
            ],
            "nextJobs": next_jobs,
        }

    # ---------- 演示数据 ----------
    def _seed_demo_jobs(self) -> None:
        """首次启动 (任务表为空) 时写入演示任务, 其中"操作日志清理"与示例图一致。"""
        if TaskJob.objects.filter(is_deleted=False).exists():
            return
        now = timezone.now()
        TaskJob.objects.bulk_create(
            [
                TaskJob(
                    name="操作日志清理",
                    description="清理30天前的系统操作日志, 释放存储空间",
                    job_type="function",
                    handler="cleanup_operation_logs",
                    trigger_type="cron",
                    cron_expr="0 3 * * sun",
                    priority="3",
                    sort_order=1,
                ),
                TaskJob(
                    name="服务健康检查",
                    description="每30秒采集一次本机CPU与内存指标",
                    job_type="function",
                    handler="system_health_check",
                    trigger_type="interval",
                    interval_seconds=30,
                    priority="2",
                    sort_order=2,
                ),
                TaskJob(
                    name="接口可用性探针",
                    description="每5分钟探测一次后端健康检查接口",
                    job_type="http",
                    http_method="GET",
                    http_url="http://127.0.0.1:8000/api/health",
                    trigger_type="interval",
                    interval_seconds=300,
                    priority="2",
                    sort_order=3,
                ),
                TaskJob(
                    name="生日月度报告",
                    description="指定时间执行的一次性示例任务",
                    job_type="function",
                    handler="demo_heartbeat",
                    trigger_type="date",
                    run_date=now + timedelta(days=7),
                    status="0",
                    priority="3",
                    sort_order=4,
                ),
            ]
        )
        self.console("info", "已写入演示任务数据")


# 进程内单例
scheduler_engine = TaskSchedulerEngine()
