from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserInfoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    nickname = serializers.CharField()
    avatar = serializers.CharField()
    roles = serializers.ListField(child=serializers.CharField())


class RouteMetaSerializer(serializers.Serializer):
    title = serializers.CharField()
    i18nKey = serializers.CharField(required=False, allow_blank=True)
    requiresAuth = serializers.BooleanField(default=True)
    icon = serializers.CharField(required=False, allow_blank=True)
    order = serializers.IntegerField(required=False)
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    keepAlive = serializers.BooleanField(required=False)
    constant = serializers.BooleanField(required=False)


class RouteSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    component = serializers.CharField(required=False, allow_blank=True)
    meta = RouteMetaSerializer()
    children = serializers.ListField(child=serializers.DictField(), required=False)
