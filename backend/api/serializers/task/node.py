"""任务域 Serializers：执行节点。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import SchedulerNode


class SchedulerNodeSerializer(serializers.ModelSerializer):
    isOnline = serializers.BooleanField(source="is_online", read_only=True)  # noqa: N815
    isLocal = serializers.BooleanField(source="is_local", read_only=True)  # noqa: N815

    class Meta:
        model = SchedulerNode
        exclude = ("is_deleted",)
        read_only_fields = ["is_local", "heartbeat_at"]
