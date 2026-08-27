from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, UserInfoSerializer, RouteSerializer


class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "message": "Django backend is running"})


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        if username == "admin" and password == "admin123":
            return Response(
                {
                    "data": {
                        "accessToken": "mock-access-token-" + username,
                        "refreshToken": "mock-refresh-token-" + username,
                    }
                }
            )
        return Response(
            {"message": "用户名或密码错误", "code": 401},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class UserInfoView(APIView):
    permission_classes = []

    def get(self, request):
        user_data = {
            "id": 1,
            "username": "admin",
            "nickname": "超级管理员",
            "avatar": "/src/assets/imgs/soybean.jpg",
            "roles": ["super"],
        }
        serializer = UserInfoSerializer(user_data)
        return Response({"data": serializer.data})


class LogoutView(APIView):
    permission_classes = []

    def post(self, request):
        return Response({"message": "登出成功"})


class RoutesView(APIView):
    permission_classes = []

    def get(self, request):
        routes = [
            {
                "name": "home",
                "path": "/home",
                "component": "view.home.index",
                "meta": {
                    "title": "首页",
                    "i18nKey": "route.home",
                    "icon": "mdi:monitor-dashboard",
                    "order": 1,
                },
            },
            {
                "name": "403",
                "path": "/error/403",
                "component": "view._builtin.403.index",
                "meta": {"title": "403", "requiresAuth": False, "constant": True},
            },
            {
                "name": "404",
                "path": "/error/404",
                "component": "view._builtin.404.index",
                "meta": {"title": "404", "requiresAuth": False, "constant": True},
            },
            {
                "name": "500",
                "path": "/error/500",
                "component": "view._builtin.500.index",
                "meta": {"title": "500", "requiresAuth": False, "constant": True},
            },
        ]
        return Response({"data": routes})
