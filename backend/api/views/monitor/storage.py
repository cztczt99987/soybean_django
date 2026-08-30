"""存储配置视图（本地 / 阿里云 OSS / 腾讯云 COS / 七牛云 Kodo）。"""

from __future__ import annotations

from pathlib import Path

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.response import Response

from ...models import Config
from ...serializers.schemas import STORAGE_TYPES, StorageSaveRequestSerializer, StorageTypeQuerySerializer
from ..common import APIView, _log_operation, fail, ok, require_auth

# 存储配置在 sys_config 表中的键名（类型清单以 serializers.schemas.STORAGE_TYPES 为唯一来源）
STORAGE_CONFIG_KEYS = {t: f"storage.{t}" for t in STORAGE_TYPES}
STORAGE_ACTIVE_KEY = "storage.active"


class StorageConfigView(APIView):
    """存储配置读取 / 保存 / 切换 / 验证。

    GET  ?type=local|aliyun|tencent|qiniu  返回该类型配置 + 当前激活类型
    POST body { type, config }             保存配置
    POST body { type, validate: true }     验证配置（不落库）
    POST body { active: type }             切换激活存储方式
    """

    @extend_schema(
        parameters=[StorageTypeQuerySerializer],
        responses={200: OpenApiResponse(description="返回 {type, config, active}")},
        summary="读取存储配置",
    )
    @require_auth
    def get(self, request):
        import json  # noqa: PLC0415

        stype = (request.query_params.get("type") or "local").strip()
        if stype not in STORAGE_CONFIG_KEYS:
            return Response(fail("不支持的存储类型"))

        cfg = Config.objects.filter(code=STORAGE_CONFIG_KEYS[stype], is_deleted=False).first()
        config_data = {}
        if cfg and cfg.value:
            try:
                config_data = json.loads(cfg.value)
            except ValueError:
                config_data = {}

        active = Config.objects.filter(code=STORAGE_ACTIVE_KEY, is_deleted=False).first()
        return Response(ok({"type": stype, "config": config_data, "active": active.value if active else "local"}))

    @extend_schema(
        request=StorageSaveRequestSerializer,
        responses={200: OpenApiResponse(description="保存/切换返回 true；验证返回 {valid: true}")},
        summary="保存 / 验证 / 切换存储配置",
    )
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
