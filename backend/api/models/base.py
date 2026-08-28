"""基础模型。

所有业务表共用：审计字段 + 软删除 + 排序 + 备注。
"""

from __future__ import annotations

from django.db import models


class BaseModel(models.Model):
    """带审计字段和软删除的基础模型。"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    remark = models.CharField(max_length=255, blank=True, default="", verbose_name="备注")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")

    class Meta:
        abstract = True
        ordering = ["sort_order", "-id"]
