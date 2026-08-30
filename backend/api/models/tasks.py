"""任务管理模块模型。

包含:
- TaskJob          定时任务定义 (CRON / 固定间隔 / 指定时间)
- TaskExecutionLog 任务执行历史
- SchedulerNode    执行节点 (注册 / 心跳 / 负载)
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from .base import BaseModel

# 任务状态
TASK_STATUS_CHOICES = (("1", "启用"), ("0", "停用"))
# 优先级
PRIORITY_CHOICES = (("1", "高"), ("2", "中"), ("3", "低"))
# 触发方式
TRIGGER_CHOICES = (("cron", "CRON表达式"), ("interval", "固定间隔"), ("date", "指定时间"))
# 任务类型
JOB_TYPE_CHOICES = (("function", "内置函数"), ("http", "HTTP请求"))
# 执行状态
EXEC_STATUS_CHOICES = (
    ("running", "执行中"),
    ("success", "成功"),
    ("failed", "失败"),
    ("timeout", "超时"),
)


class TaskJob(BaseModel):
    """定时任务定义。"""

    name = models.CharField(max_length=64, unique=True, verbose_name="任务名称")
    description = models.CharField(max_length=255, blank=True, default="", verbose_name="任务描述")
    job_type = models.CharField(
        max_length=16, default="function", choices=JOB_TYPE_CHOICES, verbose_name="任务类型"
    )
    # function 类型: 内置处理器 key, 见 api/scheduler.py JOB_HANDLERS
    handler = models.CharField(max_length=64, blank=True, default="", verbose_name="内置处理器")
    # http 类型: 请求配置
    http_method = models.CharField(max_length=8, blank=True, default="GET", verbose_name="HTTP方法")
    http_url = models.CharField(max_length=500, blank=True, default="", verbose_name="HTTP地址")
    http_body = models.TextField(blank=True, default="", verbose_name="HTTP请求体")
    # 触发配置
    trigger_type = models.CharField(
        max_length=16, default="cron", choices=TRIGGER_CHOICES, verbose_name="触发方式"
    )
    cron_expr = models.CharField(
        max_length=64, blank=True, default="", verbose_name="CRON表达式",
        help_text="5段式: 分 时 日 月 周, 如 '0 3 * * *' 每天3点",
    )
    interval_seconds = models.PositiveIntegerField(default=60, verbose_name="间隔秒数")
    run_date = models.DateTimeField(null=True, blank=True, verbose_name="指定执行时间")
    priority = models.CharField(max_length=4, default="2", choices=PRIORITY_CHOICES, verbose_name="优先级")
    timeout_seconds = models.PositiveIntegerField(default=300, verbose_name="超时秒数")
    status = models.CharField(max_length=4, default="1", choices=TASK_STATUS_CHOICES, verbose_name="状态")
    # 运行时信息 (调度器回写)
    next_run_at = models.DateTimeField(null=True, blank=True, verbose_name="下次执行时间")
    last_run_at = models.DateTimeField(null=True, blank=True, verbose_name="上次执行时间")
    last_status = models.CharField(max_length=16, blank=True, default="", verbose_name="上次执行状态")

    class Meta:
        ordering = ["sort_order", "-id"]
        verbose_name = "定时任务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def trigger_desc(self) -> str:
        """触发规则的人性化描述, 供卡片展示。"""
        if self.trigger_type == "cron":
            return self.cron_expr
        if self.trigger_type == "interval":
            return f"每 {self.interval_seconds}s"
        if self.run_date:
            return timezone.localtime(self.run_date).strftime("%Y-%m-%d %H:%M:%S")
        return "-"


class TaskExecutionLog(BaseModel):
    """任务执行历史。"""

    job = models.ForeignKey(
        TaskJob, on_delete=models.CASCADE, related_name="executions", verbose_name="任务"
    )
    job_name = models.CharField(max_length=64, verbose_name="任务名称快照")
    node = models.ForeignKey(
        "SchedulerNode", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="executions", verbose_name="执行节点",
    )
    node_name = models.CharField(max_length=64, blank=True, default="", verbose_name="节点名称快照")
    status = models.CharField(
        max_length=16, default="running", choices=EXEC_STATUS_CHOICES, verbose_name="执行状态"
    )
    trigger = models.CharField(max_length=16, blank=True, default="", verbose_name="触发方式快照")
    started_at = models.DateTimeField(default=timezone.now, verbose_name="开始时间")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    duration_ms = models.PositiveIntegerField(default=0, verbose_name="耗时(ms)")
    output = models.TextField(blank=True, default="", verbose_name="执行输出")
    error_msg = models.TextField(blank=True, default="", verbose_name="错误信息")

    class Meta:
        ordering = ["-started_at", "-id"]
        verbose_name = "任务执行日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.job_name}@{self.started_at:%Y-%m-%d %H:%M:%S}"


class SchedulerNode(BaseModel):
    """任务执行节点。

    本机调度器启动时自动注册 is_local=True 的节点并维持心跳;
    远程节点需部署执行代理, 通过心跳接口上报存活与负载。
    """

    name = models.CharField(max_length=64, unique=True, verbose_name="节点名称")
    node_id = models.CharField(max_length=64, unique=True, verbose_name="节点唯一标识")
    host = models.CharField(max_length=64, verbose_name="主机地址")
    port = models.PositiveIntegerField(default=8000, verbose_name="端口")
    is_local = models.BooleanField(default=False, verbose_name="是否本机节点")
    status = models.CharField(max_length=4, default="1", choices=TASK_STATUS_CHOICES, verbose_name="启用状态")
    max_concurrency = models.PositiveIntegerField(default=4, verbose_name="最大并发数")
    current_load = models.PositiveIntegerField(default=0, verbose_name="当前负载")
    version = models.CharField(max_length=32, blank=True, default="", verbose_name="执行器版本")
    heartbeat_at = models.DateTimeField(null=True, blank=True, verbose_name="最后心跳时间")

    # 心跳超过该秒数视为离线
    OFFLINE_AFTER_SECONDS = 30

    class Meta:
        ordering = ["sort_order", "-id"]
        verbose_name = "执行节点"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def is_online(self) -> bool:
        if self.status != "1":
            return False
        if not self.heartbeat_at:
            return False
        return (timezone.now() - self.heartbeat_at).total_seconds() <= self.OFFLINE_AFTER_SECONDS
