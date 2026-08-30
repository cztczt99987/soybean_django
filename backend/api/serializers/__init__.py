"""api.serializers 对外聚合导出。

模块划分:
- common.py   跨模块通用（分页 Mixin / IdName）
- schemas.py  APIView 文档 Schema 序列化器（横切关注点，仅供 @extend_schema 使用）
- system/     系统管理域（RBAC / 字典 / 参数 / 日志）
- task/       任务域（定时任务 / 执行日志 / 执行节点）
"""

from .common import IdNameSerializer, PaginationMixin
from .system import (
    ConfigSerializer,
    DictDataSerializer,
    DictTypeSerializer,
    DepartmentFlatSerializer,
    DepartmentSerializer,
    MenuFlatSerializer,
    MenuSerializer,
    OperationLogSerializer,
    PostSerializer,
    RoleSerializer,
    RoleSimpleSerializer,
    UserSerializer,
)
from .task import SchedulerNodeSerializer, TaskExecutionLogSerializer, TaskJobSerializer

__all__ = [
    "IdNameSerializer",
    "PaginationMixin",
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
    "TaskJobSerializer",
    "TaskExecutionLogSerializer",
    "SchedulerNodeSerializer",
]
