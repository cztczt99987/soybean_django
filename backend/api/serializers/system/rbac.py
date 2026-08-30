"""系统管理域 Serializers：RBAC（部门 / 岗位 / 角色 / 菜单 / 用户）。"""

from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from ...models import Department, Menu, Post, Role, User


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
    """列表场景：不嵌套 children，返回 departmentId / parentId 字段。"""

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
