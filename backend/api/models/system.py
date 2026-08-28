"""系统管理模型。

包含:
- 字典类型 DictType / 字典明细 DictData
- 参数设置 Config
- 操作日志 OperationLog
"""

from __future__ import annotations

from datetime import datetime

from django.db import models

from .auth import User
from .base import BaseModel


class DictType(BaseModel):
    """字典类型。"""

    name = models.CharField(max_length=64, verbose_name="字典名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="字典编码")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )

    class Meta:
        verbose_name = "字典类型"
        verbose_name_plural = verbose_name
        db_table = "sys_dict_type"

    def __str__(self):
        return self.name


class DictData(BaseModel):
    """字典明细。"""

    dict_type = models.ForeignKey(
        DictType, on_delete=models.CASCADE, related_name="items", verbose_name="字典类型"
    )
    label = models.CharField(max_length=64, verbose_name="字典标签")
    value = models.CharField(max_length=128, verbose_name="字典键值")
    css_class = models.CharField(max_length=64, blank=True, default="", verbose_name="样式属性")
    list_class = models.CharField(
        max_length=64, blank=True, default="", verbose_name="表格回显样式"
    )
    is_default = models.BooleanField(default=False, verbose_name="是否默认")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )

    class Meta:
        verbose_name = "字典明细"
        verbose_name_plural = verbose_name
        db_table = "sys_dict_data"
        unique_together = [("dict_type", "value")]

    def __str__(self):
        return f"{self.dict_type.code} - {self.label}"


class Config(BaseModel):
    """参数设置。"""

    name = models.CharField(max_length=64, verbose_name="参数名称")
    code = models.CharField(max_length=128, unique=True, verbose_name="参数键名")
    value = models.CharField(max_length=500, blank=True, default="", verbose_name="参数键值")
    value_type = models.CharField(
        max_length=16,
        default="S",
        choices=(("S", "字符串"), ("N", "数字"), ("B", "布尔"), ("J", "JSON")),
        verbose_name="类型",
    )
    is_system = models.BooleanField(default=False, verbose_name="是否系统内置")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )

    class Meta:
        verbose_name = "参数设置"
        verbose_name_plural = verbose_name
        db_table = "sys_config"

    def __str__(self):
        return self.name


class OperationLog(BaseModel):
    """操作日志。"""

    TYPE_CHOICES = (
        ("1", "其它"),
        ("2", "新增"),
        ("3", "修改"),
        ("4", "删除"),
        ("5", "授权"),
        ("6", "导出"),
        ("7", "导入"),
        ("8", "登录"),
        ("9", "登出"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operation_logs",
        verbose_name="操作用户",
    )
    username = models.CharField(max_length=64, blank=True, default="", verbose_name="账号")
    module = models.CharField(max_length=64, blank=True, default="", verbose_name="模块")
    description = models.CharField(max_length=255, blank=True, default="", verbose_name="描述")
    operation_type = models.CharField(
        max_length=16, default="1", choices=TYPE_CHOICES, verbose_name="操作类型"
    )
    method = models.CharField(max_length=16, blank=True, default="", verbose_name="HTTP方法")
    request_url = models.CharField(max_length=500, blank=True, default="", verbose_name="请求URL")
    request_params = models.TextField(blank=True, default="", verbose_name="请求参数")
    ip = models.CharField(max_length=64, blank=True, default="", verbose_name="IP")
    location = models.CharField(max_length=128, blank=True, default="", verbose_name="地点")
    response_result = models.TextField(blank=True, default="", verbose_name="返回结果")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "成功"), ("0", "失败")), verbose_name="状态"
    )
    cost_time = models.IntegerField(default=0, verbose_name="耗时(ms)")
    error_msg = models.TextField(blank=True, default="", verbose_name="错误消息")
    operated_at = models.DateTimeField(default=datetime.now, verbose_name="操作时间")

    class Meta:
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        db_table = "sys_operation_log"
        ordering = ["-operated_at"]

    def __str__(self):
        return f"{self.username} - {self.module}"
