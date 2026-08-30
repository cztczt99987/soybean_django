"""系统管理域 Serializers：字典类型 / 字典明细。"""

from __future__ import annotations

from rest_framework import serializers

from ...models import DictData, DictType


class DictTypeSerializer(serializers.ModelSerializer):
    dictId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    items = serializers.SerializerMethodField(required=False)

    class Meta:
        model = DictType
        exclude = ("is_deleted",)

    def get_items(self, obj: DictType):
        return DictDataSerializer(obj.items.filter(is_deleted=False), many=True).data


class DictDataSerializer(serializers.ModelSerializer):
    dictCode = serializers.CharField(source="dict_type.code", read_only=True)  # noqa: N815
    dictCodeInput = serializers.CharField(write_only=True, required=False, allow_blank=True)  # noqa: N815

    class Meta:
        model = DictData
        exclude = ("is_deleted", "dict_type")
        extra_kwargs = {"dict_type": {"required": False}}

    def validate(self, attrs):
        code = attrs.pop("dictCodeInput", None)
        if self.instance:
            return attrs
        if not code and "dict_type" not in attrs:
            raise serializers.ValidationError("必须指定字典类型编码 dictCodeInput")
        if code:
            try:
                attrs["dict_type"] = DictType.objects.get(code=code, is_deleted=False)
            except DictType.DoesNotExist as exc:
                raise serializers.ValidationError(f"字典类型 {code} 不存在") from exc
        # unique_together 含未序列化的 dict_type 字段时 DRF 会跳过校验, 这里手动查重
        dict_type = attrs.get("dict_type")
        value = attrs.get("value")
        if dict_type and value and DictData.objects.filter(
            dict_type=dict_type, value=value, is_deleted=False
        ).exists():
            raise serializers.ValidationError(f"该字典类型下键值 {value} 已存在")
        return attrs
