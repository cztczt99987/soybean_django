"""系统管理域 Serializers：参数设置。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import Config


class ConfigSerializer(serializers.ModelSerializer):
    configId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815

    class Meta:
        model = Config
        exclude = ("is_deleted",)
