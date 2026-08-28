"""监控管理视图。

包含:
- 服务器信息（只读）
- Redis 缓存管理（列表 / 单删 / 批删 / 清空）
- 服务器文件目录浏览 + 文件下载
- 存储配置（本地 / 阿里云 OSS / 腾讯云 COS / 七牛云 Kodo）
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import time
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
from rest_framework.response import Response

from ..models import Config
from .common import APIView, _log_operation, fail, ok, require_auth

BOOT_TIME = time.time()

# 存储配置在 sys_config 表中的键名与可选类型
STORAGE_CONFIG_KEYS = {
    "local": "storage.local",
    "aliyun": "storage.aliyun",
    "tencent": "storage.tencent",
    "qiniu": "storage.qiniu",
}
STORAGE_ACTIVE_KEY = "storage.active"

# 文件浏览允许访问的根目录（项目根）
FILE_BROWSE_ROOT = Path(settings.BASE_DIR).parent.resolve()


def _get_redis_client():
    """尝试获取原生 redis 客户端；未配置 Redis 返回 None。"""
    try:
        import redis  # noqa: PLC0415

        url = getattr(settings, "_REDIS_URL", None) or os.environ.get("REDIS_URL")
        if not url:
            caches = getattr(settings, "CACHES", {})
            location = caches.get("default", {}).get("LOCATION", "")
            if isinstance(location, str) and location.startswith("redis://"):
                url = location
        if not url:
            return None
        return redis.Redis.from_url(url, decode_responses=True)
    except Exception:  # noqa: BLE001
        return None


# ===================== 服务器信息 =====================


class ServerInfoView(APIView):
    """服务器基础信息（只读）。"""

    @require_auth
    def get(self, request):
        import psutil  # noqa: PLC0415

        cpu_percent = psutil.cpu_percent(interval=0.3)
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        boot = psutil.boot_time()
        disk_root = psutil.disk_usage(str(Path(settings.BASE_DIR).drive or "/"))

        disks = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except OSError:
                continue
            disks.append(
                {
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                }
            )

        net_io = psutil.net_io_counters()

        data = {
            "os": {
                "name": platform.system(),
                "version": platform.version(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor() or "N/A",
                "pythonVersion": platform.python_version(),
                "djangoVersion": __import__("django").get_version(),
                "hostname": socket.gethostname(),
                "bootTime": int(boot),
                "uptime": int(time.time() - boot),
            },
            "cpu": {
                "physicalCores": psutil.cpu_count(logical=False) or 0,
                "logicalCores": psutil.cpu_count(logical=True) or 0,
                "percent": cpu_percent,
                "freqCurrent": round(cpu_freq.current, 0) if cpu_freq else 0,
                "freqMin": round(cpu_freq.min, 0) if cpu_freq and cpu_freq.min else 0,
                "freqMax": round(cpu_freq.max, 0) if cpu_freq and cpu_freq.max else 0,
            },
            "memory": {
                "total": mem.total,
                "used": mem.used,
                "available": mem.available,
                "percent": mem.percent,
                "swapTotal": swap.total,
                "swapUsed": swap.used,
                "swapPercent": swap.percent,
            },
            "disks": disks,
            "diskRoot": {
                "total": disk_root.total,
                "used": disk_root.used,
                "free": disk_root.free,
                "percent": disk_root.percent,
            },
            "network": {
                "ip": _local_ip(),
                "bytesSent": net_io.bytes_sent,
                "bytesRecv": net_io.bytes_recv,
                "packetsSent": net_io.packets_sent,
                "packetsRecv": net_io.packets_recv,
            },
            "process": {
                "pid": os.getpid(),
                "startedAt": BOOT_TIME,
            },
        }
        return Response(ok(data))


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


# ===================== Redis 缓存管理 =====================


class CacheListView(APIView):
    """缓存对象列表（key / 类型 / 大小 / TTL）。"""

    @require_auth
    def get(self, request):
        client = _get_redis_client()
        if client is None:
            return Response(
                ok(
                    {
                        "mode": "locmem",
                        "total": 0,
                        "records": [],
                        "serverInfo": {},
                    }
                )
            )

        pattern = (request.query_params.get("keyword") or "*").strip()
        if not pattern.startswith("*"):
            pattern = f"*{pattern}"
        if not pattern.endswith("*"):
            pattern = f"{pattern}*"

        records = []
        for key in client.scan_iter(match=pattern, count=500):
            try:
                key_type = client.type(key)
                ttl = client.ttl(key)
                size = client.memory_usage(key) or 0
            except Exception:  # noqa: BLE001
                continue
            records.append(
                {
                    "key": key,
                    "type": key_type,
                    "size": size,
                    "ttl": ttl if ttl and ttl > 0 else -1,
                }
            )
            if len(records) >= 1000:
                break

        records.sort(key=lambda r: r["key"])

        info = client.info("memory")
        server_info = {
            "redisVersion": info.get("redis_version", ""),
            "usedMemory": info.get("used_memory", 0),
            "usedMemoryHuman": info.get("used_memory_human", ""),
            "maxMemoryHuman": info.get("maxmemory_human", "0"),
            "connectedClients": info.get("connected_clients", 0),
            "dbSize": client.dbsize(),
        }
        return Response(ok({"mode": "redis", "total": len(records), "records": records, "serverInfo": server_info}))


class CacheDeleteView(APIView):
    """删除缓存：body { key } 单删 / { keys: [] } 批删 / { all: true } 清空。"""

    @require_auth
    def post(self, request):
        client = _get_redis_client()
        if client is None:
            return Response(fail("当前未启用 Redis 缓存（LocMem 模式不支持管理）"))

        data = request.data or {}
        deleted = 0

        if data.get("all"):
            deleted = client.flushdb() and 1 or 0
            _log_operation(request, "缓存管理", "清空全部缓存", op_type="4")
            return Response(ok({"deleted": -1}))

        keys = data.get("keys") or []
        single = data.get("key")
        if single:
            keys = [single, *keys]

        if not keys:
            return Response(fail("请指定要删除的缓存 key"))

        pipe = client.pipeline()
        for k in keys:
            pipe.delete(k)
        deleted = sum(pipe.execute())

        _log_operation(request, "缓存管理", f"删除缓存 {len(keys)} 个", op_type="4")
        return Response(ok({"deleted": deleted}))


# ===================== 文件目录浏览 =====================


def _safe_resolve(rel_path: str) -> Path:
    """把相对路径解析到 FILE_BROWSE_ROOT 内，防目录穿越。"""
    base = FILE_BROWSE_ROOT
    target = (base / (rel_path or ".")).resolve()
    if target != base and base not in target.parents:
        raise ValueError("非法路径")
    return target


class FileListView(APIView):
    """服务器目录列表。"""

    @require_auth
    def get(self, request):
        rel = (request.query_params.get("path") or "").strip()
        try:
            target = _safe_resolve(rel)
        except ValueError:
            return Response(fail("非法路径"))

        if not target.exists() or not target.is_dir():
            return Response(fail("目录不存在"))

        entries = []
        for child in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            try:
                st = child.stat()
                hidden = child.name.startswith(".")
                if child.is_dir():
                    # 目录不做递归统计（node_modules 等级联目录会极慢），size 固定 0，前端显示 '-'
                    entries.append(
                        {
                            "name": child.name,
                            "path": str(child.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/"),
                            "isDir": True,
                            "size": 0,
                            "modified": int(st.st_mtime),
                            "hidden": hidden,
                        }
                    )
                else:
                    entries.append(
                        {
                            "name": child.name,
                            "path": str(child.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/"),
                            "isDir": False,
                            "size": st.st_size,
                            "modified": int(st.st_mtime),
                            "hidden": hidden,
                        }
                    )
            except (PermissionError, OSError):
                continue

        usage = shutil.disk_usage(str(target))
        return Response(
            ok(
                {
                    "currentPath": str(target.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/") or ".",
                    "parentPath": (
                        str(target.parent.relative_to(FILE_BROWSE_ROOT)).replace("\\", "/")
                        if target != FILE_BROWSE_ROOT
                        else None
                    ),
                    "entries": entries,
                    "disk": {"total": usage.total, "used": usage.used, "free": usage.free},
                }
            )
        )


class FileDownloadView(APIView):
    """下载单个文件。"""

    @require_auth
    def get(self, request):
        rel = (request.query_params.get("path") or "").strip()
        try:
            target = _safe_resolve(rel)
        except ValueError:
            return Response(fail("非法路径"))

        if not target.is_file():
            return Response(fail("文件不存在"))

        _log_operation(request, "文件管理", f"下载文件 {rel}", op_type="6")
        return FileResponse(target.open("rb"), as_attachment=True, filename=target.name)


# ===================== 存储配置管理 =====================


class StorageConfigView(APIView):
    """存储配置读取 / 保存 / 切换 / 验证。

    GET  ?type=local|aliyun|tencent|qiniu  返回该类型配置 + 当前激活类型
    POST body { type, config }             保存配置
    POST body { type, validate: true }     验证配置（不落库）
    POST body { active: type }             切换激活存储方式
    """

    @require_auth
    def get(self, request):
        stype = (request.query_params.get("type") or "local").strip()
        if stype not in STORAGE_CONFIG_KEYS:
            return Response(fail("不支持的存储类型"))

        import json  # noqa: PLC0415

        cfg = Config.objects.filter(code=STORAGE_CONFIG_KEYS[stype], is_deleted=False).first()
        config_data = {}
        if cfg and cfg.value:
            try:
                config_data = json.loads(cfg.value)
            except ValueError:
                config_data = {}

        active = Config.objects.filter(code=STORAGE_ACTIVE_KEY, is_deleted=False).first()
        return Response(ok({"type": stype, "config": config_data, "active": active.value if active else "local"}))

    @require_auth
    def post(self, request):
        import json  # noqa: PLC0415

        data = request.data or {}

        # 切换激活存储方式
        if data.get("active"):
            stype = str(data["active"])
            if stype not in STORAGE_CONFIG_KEYS:
                return Response(fail("不支持的存储类型"))
            cfg, _ = Config.objects.get_or_create(
                code=STORAGE_ACTIVE_KEY,
                defaults={"name": "激活存储方式", "value": stype, "is_system": True},
            )
            cfg.value = stype
            cfg.save()
            _log_operation(request, "存储管理", f"切换存储方式为 {stype}", op_type="5")
            return Response(ok(True))

        stype = (data.get("type") or "").strip()
        if stype not in STORAGE_CONFIG_KEYS:
            return Response(fail("不支持的存储类型"))

        config = data.get("config") or {}
        error = _validate_storage_config(stype, config)
        if error:
            return Response(fail(error))

        # 仅验证不落库
        if data.get("validate"):
            return Response(ok({"valid": True}))

        cfg, created = Config.objects.get_or_create(
            code=STORAGE_CONFIG_KEYS[stype],
            defaults={
                "name": f"存储配置-{stype}",
                "value": json.dumps(config, ensure_ascii=False),
                "value_type": "J",
                "is_system": True,
            },
        )
        if not created:
            cfg.value = json.dumps(config, ensure_ascii=False)
            cfg.save()

        _log_operation(request, "存储管理", f"保存 {stype} 存储配置", op_type="3")
        return Response(ok(True))


def _validate_storage_config(stype: str, config: dict) -> str | None:
    """校验各存储必填字段；返回错误消息或 None。"""

    def required_fields(fields: list[str]) -> str | None:
        missing = [f for f in fields if not str(config.get(f) or "").strip()]
        if missing:
            return f"缺少必填配置: {', '.join(missing)}"
        return None

    if stype == "local":
        base_path = str(config.get("basePath") or "").strip()
        if not base_path:
            return "缺少必填配置: basePath"
        if not Path(base_path).exists():
            return f"本地目录不存在: {base_path}"
        return None
    if stype == "aliyun":
        return required_fields(["endpoint", "bucket", "accessKeyId", "accessKeySecret"])
    if stype == "tencent":
        return required_fields(["region", "bucket", "secretId", "secretKey"])
    if stype == "qiniu":
        return required_fields(["zone", "bucket", "accessKey", "secretKey"])
    return "不支持的存储类型"
