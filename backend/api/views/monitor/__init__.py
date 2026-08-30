"""views.monitor 子模块聚合。

- server.py   服务器信息（只读）
- cache.py    Redis 缓存管理
- file.py     文件目录浏览 / 下载
- storage.py  存储配置
"""

from .cache import CacheDeleteView, CacheDetailView, CacheListView
from .file import FileDownloadView, FileListView
from .server import ServerInfoView
from .storage import StorageConfigView

__all__ = [
    "ServerInfoView",
    "CacheListView",
    "CacheDeleteView",
    "CacheDetailView",
    "FileListView",
    "FileDownloadView",
    "StorageConfigView",
]
