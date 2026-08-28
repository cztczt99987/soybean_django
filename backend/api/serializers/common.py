"""Serializers 通用组件。"""

from __future__ import annotations

from rest_framework import serializers


class IdNameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class PaginationMixin:
    """分页入参（query params）。"""

    current = serializers.IntegerField(min_value=1, default=1)
    size = serializers.IntegerField(min_value=1, default=10)
