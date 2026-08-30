from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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
# 任务管理
router.register("task/job", views.TaskJobViewSet, basename="task-job")
router.register("task/log", views.TaskExecutionLogViewSet, basename="task-log")
router.register("task/node", views.SchedulerNodeViewSet, basename="task-node")

urlpatterns = [
    # 公开接口：须注册在 router 之前，避免被 /system/config/{pk}/ 详情路由捕获
    path("system/config/system-name/", views.SystemNameView.as_view(), name="system-config-name"),
    path("", include(router.urls)),
    path("health", views.HealthCheckView.as_view(), name="health"),
    path("auth/captcha", views.CaptchaView.as_view(), name="captcha"),
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/logout", views.LogoutView.as_view(), name="logout"),
    path("auth/getUserInfo", views.UserInfoView.as_view(), name="user-info"),
    path("route/getConstantRoutes", views.ConstantRoutesView.as_view(), name="constant-routes"),
    path("route/getUserRoutes", views.UserRoutesView.as_view(), name="user-routes"),
    path("route/isRouteExist", views.IsRouteExistView.as_view(), name="route-exist"),
    # 监控管理
    path("monitor/server", views.ServerInfoView.as_view(), name="monitor-server"),
    path("monitor/cache", views.CacheListView.as_view(), name="monitor-cache"),
    path("monitor/cache/detail", views.CacheDetailView.as_view(), name="monitor-cache-detail"),
    path("monitor/cache/delete", views.CacheDeleteView.as_view(), name="monitor-cache-delete"),
    path("monitor/files", views.FileListView.as_view(), name="monitor-files"),
    path("monitor/file/download", views.FileDownloadView.as_view(), name="monitor-file-download"),
    path("monitor/storage", views.StorageConfigView.as_view(), name="monitor-storage"),
    # 任务管理 - 调度器
    path("task/scheduler/status", views.SchedulerStatusView.as_view(), name="task-scheduler-status"),
    path("task/scheduler/control", views.SchedulerControlView.as_view(), name="task-scheduler-control"),
    path("task/scheduler/console", views.SchedulerConsoleView.as_view(), name="task-scheduler-console"),
    # Swagger / OpenAPI 文档
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-docs"),
    # 兼容旧 URL (前端老代码仍有可能引用)
    path("auth/user-info", views.UserInfoView.as_view(), name="user-info-compat"),
    path("route/routes", views.UserRoutesView.as_view(), name="routes-compat"),
]
