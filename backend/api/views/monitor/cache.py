"""Redis 缓存管理视图（列表 / 单删 / 批删 / 清空 / 详情）。"""

from __future__ import annotations

import json
import os
import time

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response

from ...serializers.schemas import (
    CacheDeleteRequestSerializer,
    CacheDetailQuerySerializer,
    CacheListQuerySerializer,
)
from ..common import APIView, _log_operation, fail, ok, require_auth


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


# 缓存 key 业务分类的中文标签（未收录的分类直接显示分类名本身）
_CACHE_CATEGORY_LABELS = {
    "menu_routes": "动态路由缓存",
    "refresh_token": "刷新令牌",
    "system_config": "系统参数缓存",
    "system_dict": "字典缓存",
    "session": "会话缓存",
}


def _strip_cache_prefix(key: str) -> str | None:
    """剥离 Django 缓存 key 的前缀/版本号，返回业务 key；不是 Django 缓存 key 时返回 None。"""
    prefix = getattr(settings, "CACHES", {}).get("default", {}).get("KEY_PREFIX", "")
    if not prefix or not key.startswith(prefix):
        return None
    k = key[len(prefix):].lstrip(":")
    parts = k.split(":", 1)
    if len(parts) == 2 and parts[0].isdigit():
        k = parts[1]
    return k or None


def _cache_key_category(key: str) -> str:
    """识别缓存 key 的业务分类：剥离前缀/版本号后取第一段。"""
    k = _strip_cache_prefix(key)
    if k is None:
        k = key.lstrip(":")
    cat = k.split(":", 1)[0].strip()
    return cat or "other"


def _cache_key_category_label(category: str) -> str:
    return _CACHE_CATEGORY_LABELS.get(category, category)


def _fmt_bytes(n: float) -> str:
    """字节人性化显示。"""
    if not n or n <= 0:
        return "0B"
    units = ["B", "K", "M", "G", "T"]
    idx = 0
    val = float(n)
    while val >= 1024 and idx < len(units) - 1:
        val /= 1024
        idx += 1
    return f"{val:.2f}{units[idx]}"


def _collect_server_info(client) -> dict:
    """采集 Redis 监控信息：版本/运行模式/内存/CPU/网络IO/AOF/RDB/命令统计等。"""
    info_server = client.info("server")
    info_memory = client.info("memory")
    info_persist = client.info("persistence")

    # CPU 与网络 IO 采用两次采样求差，得到瞬时值
    cpu1 = client.info("cpu")
    stats1 = client.info("stats")
    time.sleep(0.2)
    cpu2 = client.info("cpu")
    stats2 = client.info("stats")
    sample = 0.2
    used_cpu = (
        (cpu2.get("used_cpu_sys", 0) - cpu1.get("used_cpu_sys", 0))
        + (cpu2.get("used_cpu_user", 0) - cpu1.get("used_cpu_user", 0))
    ) / sample * 100
    net_in = (stats2.get("total_net_input_bytes", 0) - stats1.get("total_net_input_bytes", 0)) / sample / 1024
    net_out = (stats2.get("total_net_output_bytes", 0) - stats1.get("total_net_output_bytes", 0)) / sample / 1024

    # 命令统计：{"cmdstat_get": {"calls": 12, ...}} → {"get": 12}
    command_stats: dict = {}
    for name, stat in (client.info("commandstats") or {}).items():
        command_stats[name.replace("cmdstat_", "")] = int(stat.get("calls", 0))

    max_memory = info_memory.get("maxmemory", 0)
    return {
        "redisVersion": info_server.get("redis_version", ""),
        "runMode": "单机" if info_server.get("redis_mode", "standalone") == "standalone" else "集群",
        "port": info_server.get("tcp_port", 0),
        "connectedClients": info_memory.get("connected_clients", 0),
        "uptimeDays": info_server.get("uptime_in_days", 0),
        "usedMemory": info_memory.get("used_memory", 0),
        "usedMemoryHuman": info_memory.get("used_memory_human", ""),
        "maxMemory": max_memory,
        "maxMemoryHuman": _fmt_bytes(max_memory),
        "usedCpuPercent": round(max(used_cpu, 0), 2),
        "aofEnabled": bool(info_persist.get("aof_enabled", 0)),
        "rdbStatus": info_persist.get("rdb_last_bgsave_status", "ok"),
        "dbSize": client.dbsize(),
        "netInKps": round(max(net_in, 0), 2),
        "netOutKps": round(max(net_out, 0), 2),
        "commandStats": command_stats,
    }


class CacheListView(APIView):
    """缓存对象列表（key / 分类 / 类型 / 大小 / TTL），并按分类汇总。"""

    @extend_schema(
        parameters=[CacheListQuerySerializer],
        responses={200: OpenApiResponse(description="返回 {mode, total, records, categories, serverInfo}")},
        summary="缓存列表",
    )
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
            except Exception:  # noqa: BLE001
                continue
            # MEMORY USAGE 为 Redis 4.0+ 命令（Windows 旧版 3.x 不支持），失败时回退 0
            try:
                size = client.memory_usage(key) or 0
            except Exception:  # noqa: BLE001
                size = 0
            category = _cache_key_category(key)
            records.append(
                {
                    "key": key,
                    "type": key_type,
                    "size": size,
                    "ttl": ttl if ttl and ttl > 0 else -1,
                    "category": category,
                    "categoryLabel": _cache_key_category_label(category),
                }
            )
            if len(records) >= 1000:
                break

        records.sort(key=lambda r: r["key"])

        # 按分类汇总（数量 / 占用大小），供前端分类筛选与分类删除使用
        category_map: dict = {}
        for r in records:
            item = category_map.setdefault(
                r["category"], {"name": r["category"], "label": r["categoryLabel"], "count": 0, "size": 0}
            )
            item["count"] += 1
            item["size"] += r["size"]
        categories = sorted(category_map.values(), key=lambda c: c["name"])

        server_info = _collect_server_info(client)
        return Response(
            ok({"mode": "redis", "total": len(records), "records": records, "categories": categories, "serverInfo": server_info})
        )


class CacheDeleteView(APIView):
    """删除缓存：body { key } 单删 / { keys: [] } 批删 / { category } 按分类删 / { all: true } 清空。"""

    @extend_schema(
        request=CacheDeleteRequestSerializer,
        responses={200: OpenApiResponse(description="返回 {deleted}，清空全部时为 -1")},
        summary="删除缓存",
    )
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

        # 按业务分类删除：扫描全库，删除属于该分类的所有 key
        category = data.get("category")
        if category:
            keys = [k for k in client.scan_iter(match="*", count=500) if _cache_key_category(k) == category]
            if not keys:
                return Response(ok({"deleted": 0}))
            pipe = client.pipeline()
            for k in keys:
                pipe.delete(k)
            deleted = sum(pipe.execute())
            _log_operation(request, "缓存管理", f"按分类删除缓存 [{category}], 数量={len(keys)}", op_type="4")
            return Response(ok({"deleted": deleted}))

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


def _read_key_value(client, key: str, key_type: str):
    """按 Redis 数据类型读取 key 的完整内容。"""
    try:
        if key_type == "string":
            return client.get(key)
        if key_type == "hash":
            return client.hgetall(key)
        if key_type == "list":
            return client.lrange(key, 0, -1)
        if key_type == "set":
            return list(client.smembers(key))
        if key_type == "zset":
            return client.zrange(key, 0, -1, withscores=True)
        return None
    except Exception:  # noqa: BLE001
        return None


class CacheDetailView(APIView):
    """查看单个缓存键的内容：GET /monitor/cache/detail?key=xxx。"""

    @extend_schema(
        parameters=[CacheDetailQuerySerializer],
        responses={200: OpenApiResponse(description="返回 {key, type, ttl, value}")},
        summary="缓存详情",
    )
    @require_auth
    def get(self, request):
        client = _get_redis_client()
        if client is None:
            return Response(fail("当前未启用 Redis 缓存（LocMem 模式不支持管理）"))

        key = (request.query_params.get("key") or "").strip()
        if not key:
            return Response(fail("请指定要查看的缓存键名"))
        if not client.exists(key):
            return Response(fail("缓存键不存在或已过期"))

        key_type = client.type(key)
        ttl = client.ttl(key)

        # 优先通过 Django 缓存框架反查（值是 pickle 序列化存储的，直接读 Redis 会得到乱码）
        value = None
        biz_key = _strip_cache_prefix(key)
        if biz_key:
            try:
                from django.core.cache import cache

                obj = cache.get(biz_key)
                if isinstance(obj, str):
                    value = obj
                elif obj is not None:
                    value = json.dumps(obj, ensure_ascii=False, default=str, indent=2)
            except Exception:  # noqa: BLE001
                value = None

        # 非 Django 缓存 key 或反查失败时，按 Redis 原生类型读取
        if value is None:
            raw = _read_key_value(client, key, key_type)
            if isinstance(raw, str):
                value = raw
            else:
                value = json.dumps(raw, ensure_ascii=False, default=str, indent=2)

        return Response(
            ok({"key": key, "type": key_type, "ttl": ttl if ttl and ttl > 0 else -1, "value": value})
        )
