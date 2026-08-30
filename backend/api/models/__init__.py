"""api.models 对外聚合导出。

Django 在扫描模型时会加载 models 包下 __init__ 中的所有导入，
因此保持 ``from api.models import User`` / ``from .models import User``
两种形式都能工作，makemigrations 检测不到任何变更。
"""

from .base import BaseModel
from .rbac import Department, Menu, Post, Role, User
from .system import Config, DictData, DictType, OperationLog
from .tasks import SchedulerNode, TaskExecutionLog, TaskJob

__all__ = [
    "BaseModel",
    "Department",
    "Post",
    "Role",
    "Menu",
    "User",
    "DictType",
    "DictData",
    "Config",
    "OperationLog",
    "TaskJob",
    "TaskExecutionLog",
    "SchedulerNode",
]
