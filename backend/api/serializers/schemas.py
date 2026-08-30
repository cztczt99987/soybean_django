"""APIView 接口文档 Schema 序列化器。

供 @extend_schema / parameters 使用，仅用于生成 Swagger 文档（请求参数与请求体定义），
不参与实际的数据校验流程。覆盖鉴权 / 路由 / 监控等无法被自动识别的普通视图。
"""

from __future__ import annotations

from rest_framework import serializers

# 存储方式类型清单（唯一来源，views/monitor/storage.py 由此派生配置键）
STORAGE_TYPES = ["local", "aliyun", "tencent", "qiniu"]


# ============ 通用列表查询（ViewSet list） ============


class ListQuerySerializer(serializers.Serializer):
    """通用列表查询参数：分页 + 关键字 + 时间范围（beginTime/endTime 仅对含 created_at 的模型生效）。"""

    current = serializers.IntegerField(required=False, default=1, help_text="页码（从 1 开始）")
    size = serializers.IntegerField(required=False, default=10, help_text="每页条数")
    keyword = serializers.CharField(required=False, help_text="关键字（对文本字段模糊匹配）")
    beginTime = serializers.DateTimeField(required=False, help_text="创建时间起（如 2026-01-01 或 2026-01-01 00:00:00）")  # noqa: N815
    endTime = serializers.DateTimeField(required=False, help_text="创建时间止")  # noqa: N815


# ============ 鉴权 ============


class LoginRequestSerializer(serializers.Serializer):
    """登录请求体（需先调用 GET /api/auth/captcha 获取图形验证码）。"""

    username = serializers.CharField(help_text="账号")
    password = serializers.CharField(help_text="密码", style={"input_type": "password"})
    captchaKey = serializers.CharField(help_text="验证码 key（来自 GET /api/auth/captcha）")  # noqa: N815
    captchaCode = serializers.CharField(help_text="加减法计算结果，如表达式 12+7=? 则输入 19")  # noqa: N815


# ============ 路由 ============


class RouteExistQuerySerializer(serializers.Serializer):
    """路由存在性检查查询参数。"""

    routeName = serializers.CharField(required=False, help_text="路由名称（可选，缺省返回 False）")  # noqa: N815


# ============ 缓存监控 ============


class CacheListQuerySerializer(serializers.Serializer):
    """缓存列表查询参数。"""

    keyword = serializers.CharField(required=False, help_text="缓存键名关键字（模糊匹配）")


class CacheDeleteRequestSerializer(serializers.Serializer):
    """缓存删除请求体：key 单删 / keys 批删 / category 按分类删 / all 清空。"""

    key = serializers.CharField(required=False, help_text="单个缓存键名")
    keys = serializers.ListField(child=serializers.CharField(), required=False, help_text="多个缓存键名")
    category = serializers.CharField(required=False, help_text="业务分类（如 menu_routes）")
    all = serializers.BooleanField(required=False, help_text="是否清空全部缓存")


class CacheDetailQuerySerializer(serializers.Serializer):
    """缓存详情查询参数。"""

    key = serializers.CharField(required=True, help_text="缓存键名")


# ============ 文件管理 ============


class FileListQuerySerializer(serializers.Serializer):
    """目录浏览查询参数。"""

    path = serializers.CharField(required=False, help_text="相对路径（缺省为根目录）")


class FileDownloadQuerySerializer(serializers.Serializer):
    """文件下载查询参数。"""

    path = serializers.CharField(required=True, help_text="文件相对路径")


# ============ 存储配置 ============


class StorageTypeQuerySerializer(serializers.Serializer):
    """存储配置读取查询参数。"""

    type = serializers.ChoiceField(choices=STORAGE_TYPES, required=False, default="local", help_text="存储类型")


class StorageSaveRequestSerializer(serializers.Serializer):
    """存储配置保存 / 验证 / 切换请求体。"""

    type = serializers.ChoiceField(choices=STORAGE_TYPES, required=False, help_text="存储类型")
    config = serializers.DictField(required=False, help_text="配置项（type 对应的键值对）")
    validate = serializers.BooleanField(required=False, help_text="仅验证不落库")
    active = serializers.ChoiceField(choices=STORAGE_TYPES, required=False, help_text="切换激活存储方式")
