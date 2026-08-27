"""系统管理 Serializers。"""

from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from .models import (
    Config,
    Department,
    DictData,
    DictType,
    Menu,
    OperationLog,
    Post,
    Role,
    User,
)


class IdNameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class PaginationMixin:
    """分页入参（query params）。"""

    current = serializers.IntegerField(min_value=1, default=1)
    size = serializers.IntegerField(min_value=1, default=10)


# ============ 部门 ============


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = ("is_deleted",)
        extra_kwargs = {"parent": {"required": False}}

    children = serializers.SerializerMethodField()

    def get_children(self, obj: Department):
        children = obj.children.filter(is_deleted=False)
        return DepartmentSerializer(children, many=True).data


class DepartmentFlatSerializer(serializers.ModelSerializer):
    """列表场景：不嵌套 children，返回 departmentId 等字段给前端选择器用。"""

    departmentId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    parentId = serializers.IntegerField(source="parent_id", allow_null=True, required=False)  # noqa: N815

    class Meta:
        model = Department
        fields = [
            "departmentId",
            "id",
            "name",
            "code",
            "parentId",
            "parent",
            "leader",
            "phone",
            "email",
            "status",
            "sort_order",
            "remark",
            "created_at",
            "updated_at",
        ]


# ============ 岗位 ============


class PostSerializer(serializers.ModelSerializer):
    postId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815

    class Meta:
        model = Post
        exclude = ("is_deleted",)


# ============ 角色 ============


class RoleSerializer(serializers.ModelSerializer):
    roleId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    menuIds = serializers.ListField(  # noqa: N815
        child=serializers.IntegerField(), write_only=True, required=False
    )
    departmentIds = serializers.ListField(  # noqa: N815
        child=serializers.IntegerField(), write_only=True, required=False
    )
    menus = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()

    class Meta:
        model = Role
        exclude = ("is_deleted",)

    def get_menus(self, obj: Role):
        return sorted(obj.menus.values_list("id", flat=True))

    def get_departments(self, obj: Role):
        return sorted(obj.departments.values_list("id", flat=True))

    @transaction.atomic
    def create(self, validated_data):
        menu_ids = validated_data.pop("menuIds", []) or []
        dept_ids = validated_data.pop("departmentIds", []) or []
        role = super().create(validated_data)
        if menu_ids:
            role.menus.set(menu_ids)
        if dept_ids:
            role.departments.set(dept_ids)
        return role

    @transaction.atomic
    def update(self, instance: Role, validated_data):
        menu_ids = validated_data.pop("menuIds", None)
        dept_ids = validated_data.pop("departmentIds", None)
        role = super().update(instance, validated_data)
        if menu_ids is not None:
            role.menus.set(menu_ids)
        if dept_ids is not None:
            role.departments.set(dept_ids)
        return role


class RoleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "code", "status")


# ============ 菜单 ============


class MenuSerializer(serializers.ModelSerializer):
    menuId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    parentId = serializers.IntegerField(source="parent_id", allow_null=True, required=False)  # noqa: N815
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        exclude = ("is_deleted",)

    def get_children(self, obj: Menu):
        children = obj.children.filter(is_deleted=False).order_by("order", "id")
        return MenuSerializer(children, many=True).data


class MenuFlatSerializer(serializers.ModelSerializer):
    menuId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    parentId = serializers.IntegerField(source="parent_id", allow_null=True, required=False)  # noqa: N815

    class Meta:
        model = Menu
        exclude = ("is_deleted",)


# ============ 用户 ============


class UserSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815
    dept = serializers.SerializerMethodField()
    roleIds = serializers.ListField(  # noqa: N815
        child=serializers.IntegerField(), write_only=True, required=False
    )
    postIds = serializers.ListField(  # noqa: N815
        child=serializers.IntegerField(), write_only=True, required=False
    )
    roles = RoleSimpleSerializer(many=True, read_only=True)
    posts = PostSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        exclude = ("is_deleted",)

    def get_dept(self, obj: User):
        if not obj.department:
            return None
        return {
            "id": obj.department.id,
            "name": obj.department.name,
            "code": obj.department.code,
        }

    @transaction.atomic
    def create(self, validated_data):
        role_ids = validated_data.pop("roleIds", []) or []
        post_ids = validated_data.pop("postIds", []) or []
        raw_pwd = validated_data.pop("password", None) or "123456"
        user = super().create(validated_data)
        user.set_password(raw_pwd)
        user.save(update_fields=["password"])
        if role_ids:
            user.roles.set(role_ids)
        if post_ids:
            user.posts.set(post_ids)
        return user

    @transaction.atomic
    def update(self, instance: User, validated_data):
        role_ids = validated_data.pop("roleIds", None)
        post_ids = validated_data.pop("postIds", None)
        raw_pwd = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if raw_pwd:
            user.set_password(raw_pwd)
            user.save(update_fields=["password"])
        if role_ids is not None:
            user.roles.set(role_ids)
        if post_ids is not None:
            user.posts.set(post_ids)
        return user


# ============ 字典类型 + 明细 ============


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
        return attrs


# ============ 参数设置 ============


class ConfigSerializer(serializers.ModelSerializer):
    configId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815

    class Meta:
        model = Config
        exclude = ("is_deleted",)


# ============ 操作日志 ============


class OperationLogSerializer(serializers.ModelSerializer):
    logId = serializers.IntegerField(source="id", read_only=True)  # noqa: N815

    class Meta:
        model = OperationLog
        fields = "__all__"
