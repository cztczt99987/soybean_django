"""serializers.system 子模块聚合。

- rbac.py   部门 / 岗位 / 角色 / 菜单 / 用户
- dict.py   字典类型 / 字典明细
- config.py 参数设置
- log.py    操作日志
"""

from .config import ConfigSerializer
from .dict import DictDataSerializer, DictTypeSerializer
from .log import OperationLogSerializer
from .rbac import (
    DepartmentFlatSerializer,
    DepartmentSerializer,
    MenuFlatSerializer,
    MenuSerializer,
    PostSerializer,
    RoleSerializer,
    RoleSimpleSerializer,
    UserSerializer,
)

__all__ = [
    "DepartmentSerializer",
    "DepartmentFlatSerializer",
    "PostSerializer",
    "RoleSerializer",
    "RoleSimpleSerializer",
    "MenuSerializer",
    "MenuFlatSerializer",
    "UserSerializer",
    "DictTypeSerializer",
    "DictDataSerializer",
    "ConfigSerializer",
    "OperationLogSerializer",
]
