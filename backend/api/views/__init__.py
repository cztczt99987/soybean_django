"""api.views 对外聚合导出。

保持 ``from . import views`` / ``from api.views import UserViewSet`` 两种引用不变，
从而 urls.py、外部脚本、tests 都无需修改。
"""

from .auth import HealthCheckView, LoginView, LogoutView, UserInfoView
from ..serializers.common import PaginationMixin
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
from .route import ConstantRoutesView, IsRouteExistView, UserRoutesView
from .monitor import (
    CacheDeleteView,
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
    UserViewSet,
)

__all__ = [
    # 常量与通用工具
    "SUCCESS_CODE",
    "ERROR_CODE",
    "AUTH_CODE",
    "PaginationMixin",
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
    "OperationLogViewSet",
]
