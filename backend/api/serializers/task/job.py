"""任务域 Serializers：定时任务。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import TaskJob


class TaskJobSerializer(serializers.ModelSerializer):
    triggerDesc = serializers.CharField(source="trigger_desc", read_only=True)  # noqa: N815
    isRunning = serializers.SerializerMethodField()  # noqa: N815

    class Meta:
        model = TaskJob
        exclude = ("is_deleted",)
        read_only_fields = ["next_run_at", "last_run_at", "last_status"]

    def get_isRunning(self, obj) -> bool:
        from ...scheduler import scheduler_engine  # noqa: PLC0415

        return scheduler_engine.is_running and obj.next_run_at is not None

    def validate(self, attrs):
        trigger_type = attrs.get("trigger_type", getattr(self.instance, "trigger_type", "cron"))
        if trigger_type == "cron" and not attrs.get("cron_expr", getattr(self.instance, "cron_expr", "")):
            raise serializers.ValidationError("CRON 触发方式必须填写 CRON 表达式")
        if trigger_type == "http":
            url = attrs.get("http_url", getattr(self.instance, "http_url", ""))
            if not url:
                raise serializers.ValidationError("HTTP 类型任务必须填写请求地址")
        return attrs
