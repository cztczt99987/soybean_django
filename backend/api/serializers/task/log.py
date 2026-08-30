"""任务域 Serializers：任务执行日志。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import TaskExecutionLog


class TaskExecutionLogSerializer(serializers.ModelSerializer):
    jobName = serializers.CharField(source="job_name", read_only=True)  # noqa: N815
    nodeName = serializers.CharField(source="node_name", read_only=True)  # noqa: N815

    class Meta:
        model = TaskExecutionLog
        exclude = ("is_deleted",)
