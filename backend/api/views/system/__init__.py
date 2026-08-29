"""views.system 子模块聚合。"""

from .config import ConfigViewSet, SystemNameView
from .dept import DepartmentViewSet
from .dict import DictDataViewSet, DictTypeViewSet
from .log import OperationLogViewSet
from .menu import MenuViewSet
from .post import PostViewSet
from .role import RoleViewSet
from .user import UserViewSet

__all__ = [
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
]
