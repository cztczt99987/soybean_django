"""系统管理域 Serializers：操作日志。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    logId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815

    class Meta:
        model = OperationLog
        fields = "__all__"
