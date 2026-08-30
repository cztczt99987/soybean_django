"""api.views 对外聚合导出。

保持 ``from . import views`` / ``from api.views import UserViewSet`` 两种引用不变，
从而 urls.py、外部脚本、tests 都无需修改。

模块划分:
- common.py  跨模块公共设施（响应封装 / 分页 / 认证 / _CRUDMixin）
- auth/      鉴权域（验证码 / 登录 / 登出 / 用户信息 / 健康检查 / 动态路由）
- system/    系统管理域（用户 / 角色 / 菜单 / 部门 / 岗位 / 字典 / 参数 / 日志）
- monitor/   监控域（服务器 / 缓存 / 文件 / 存储）
- task/      任务域（定时任务 / 执行日志 / 执行节点 / 调度器）
"""

from .auth import (
    CaptchaView,
    ConstantRoutesView,
    HealthCheckView,
    IsRouteExistView,
    LoginView,
    LogoutView,
    UserRoutesView,
    UserInfoView,
)
from .common import (
    AUTH_CODE,
    AuthenticatedViewSet,
    ERROR_CODE,
    SUCCESS_CODE,
    _CRUDMixin,
    _get_current_user,
    _issue_token,
    _log_operation,
    _TOKENS,
    fail,
    get_client_ip,
    ok,
    paginate,
    require_auth,
)
from .monitor import (
    CacheDeleteView,
    CacheDetailView,
    CacheListView,
    FileDownloadView,
    FileListView,
    ServerInfoView,
    StorageConfigView,
)
from .system import (
    ConfigViewSet,
    DepartmentViewSet,
    DictDataViewSet,
    DictTypeViewSet,
    MenuViewSet,
    OperationLogViewSet,
    PostViewSet,
    RoleViewSet,
    SystemNameView,
    UserViewSet,
)
from .task import (
    SchedulerConsoleView,
    SchedulerControlView,
    SchedulerNodeViewSet,
    SchedulerStatusView,
    TaskExecutionLogViewSet,
    TaskJobViewSet,
)

__all__ = [
    # 常量与通用工具
    "SUCCESS_CODE",
    "ERROR_CODE",
    "AUTH_CODE",
    "ok",
    "fail",
    "paginate",
    "get_client_ip",
    "_TOKENS",
    "_issue_token",
    "_get_current_user",
    "_log_operation",
    "require_auth",
    "AuthenticatedViewSet",
    "_CRUDMixin",
    # 顶层 APIView
    "CaptchaView",
    "HealthCheckView",
    "LoginView",
    "LogoutView",
    "UserInfoView",
    "ConstantRoutesView",
    "UserRoutesView",
    "IsRouteExistView",
    # 业务 ViewSet
    "UserViewSet",
    "RoleViewSet",
    "MenuViewSet",
    "DepartmentViewSet",
    "PostViewSet",
    "DictTypeViewSet",
    "DictDataViewSet",
    "ConfigViewSet",
    "SystemNameView",
    "OperationLogViewSet",
    # 任务管理
    "TaskJobViewSet",
    "TaskExecutionLogViewSet",
    "SchedulerNodeViewSet",
    "SchedulerStatusView",
    "SchedulerControlView",
    "SchedulerConsoleView",
    # 监控管理
    "ServerInfoView",
    "CacheListView",
    "CacheDeleteView",
    "CacheDetailView",
    "FileListView",
    "FileDownloadView",
    "StorageConfigView",
]
