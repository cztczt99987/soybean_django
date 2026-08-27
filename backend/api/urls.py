from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("system/user", views.UserViewSet, basename="system-user")
router.register("system/role", views.RoleViewSet, basename="system-role")
router.register("system/menu", views.MenuViewSet, basename="system-menu")
router.register("system/dept", views.DepartmentViewSet, basename="system-dept")
router.register("system/post", views.PostViewSet, basename="system-post")
router.register("system/dict/type", views.DictTypeViewSet, basename="system-dict-type")
router.register("system/dict/data", views.DictDataViewSet, basename="system-dict-data")
router.register("system/config", views.ConfigViewSet, basename="system-config")
router.register("system/log", views.OperationLogViewSet, basename="system-log")

urlpatterns = [
    path("", include(router.urls)),
    path("health", views.HealthCheckView.as_view(), name="health"),
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/logout", views.LogoutView.as_view(), name="logout"),
    path("auth/getUserInfo", views.UserInfoView.as_view(), name="user-info"),
    path("route/getConstantRoutes", views.ConstantRoutesView.as_view(), name="constant-routes"),
    path("route/getUserRoutes", views.UserRoutesView.as_view(), name="user-routes"),
    path("route/isRouteExist", views.IsRouteExistView.as_view(), name="route-exist"),
    # 兼容旧 URL (前端老代码仍有可能引用)
    path("auth/user-info", views.UserInfoView.as_view(), name="user-info-compat"),
    path("route/routes", views.UserRoutesView.as_view(), name="routes-compat"),
]
