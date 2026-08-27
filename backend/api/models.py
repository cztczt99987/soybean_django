"""系统管理模块。

包含:
- 基础模型（带创建者、更新时间、软删除、排序）
- 8 个业务模型（用户 / 角色 / 菜单 / 部门 / 岗位 / 字典 / 参数 / 日志）
- 响应包装、分页、通用过滤工具
"""

from __future__ import annotations

from datetime import datetime

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


class Department(BaseModel):
    """部门。"""

    name = models.CharField(max_length=64, verbose_name="部门名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="部门编码")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="上级部门",
    )
    leader = models.CharField(max_length=32, blank=True, default="", verbose_name="负责人")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="联系电话")
    email = models.EmailField(max_length=128, blank=True, default="", verbose_name="邮箱")
    status = models.CharField(
        max_length=16,
        default="1",
        choices=(("1", "启用"), ("0", "停用")),
        verbose_name="状态",
    )

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = verbose_name
        db_table = "sys_department"

    def __str__(self):
        return self.name


class Post(BaseModel):
    """岗位。"""

    name = models.CharField(max_length=64, verbose_name="岗位名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="岗位编码")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )

    class Meta:
        verbose_name = "岗位"
        verbose_name_plural = verbose_name
        db_table = "sys_post"

    def __str__(self):
        return self.name


class Role(BaseModel):
    """角色。"""

    name = models.CharField(max_length=64, verbose_name="角色名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="角色编码")
    data_scope = models.CharField(
        max_length=16,
        default="1",
        choices=(
            ("1", "全部数据权限"),
            ("2", "自定义数据权限"),
            ("3", "本部门数据权限"),
            ("4", "本部门及以下数据权限"),
            ("5", "仅本人数据权限"),
        ),
        verbose_name="数据权限范围",
    )
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )
    menus = models.ManyToManyField(
        "Menu", blank=True, related_name="roles", verbose_name="关联菜单"
    )
    departments = models.ManyToManyField(
        "Department", blank=True, related_name="roles", verbose_name="自定义数据权限部门"
    )

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        db_table = "sys_role"

    def __str__(self):
        return self.name


class Menu(BaseModel):
    """菜单 & 权限按钮。

    type: 1=目录, 2=菜单, 3=按钮
    """

    MENU_TYPE_CHOICES = (("1", "目录"), ("2", "菜单"), ("3", "按钮"))

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="上级菜单",
    )
    name = models.CharField(max_length=64, verbose_name="菜单名称")
    title = models.CharField(max_length=64, blank=True, default="", verbose_name="显示名称(meta)")
    path = models.CharField(max_length=255, blank=True, default="", verbose_name="路由路径")
    component = models.CharField(
        max_length=255, blank=True, default="", verbose_name="组件路径(layout.base$view.xxx)"
    )
    permission = models.CharField(
        max_length=128, blank=True, default="", verbose_name="权限标识(按钮级)"
    )
    icon = models.CharField(max_length=64, blank=True, default="", verbose_name="图标")
    menu_type = models.CharField(
        max_length=16, default="2", choices=MENU_TYPE_CHOICES, verbose_name="菜单类型"
    )
    order = models.IntegerField(default=0, verbose_name="显示顺序")
    i18n_key = models.CharField(
        max_length=128, blank=True, default="", verbose_name="i18n Key"
    )
    keep_alive = models.BooleanField(default=True, verbose_name="是否缓存")
    hide_in_menu = models.BooleanField(default=False, verbose_name="是否隐藏菜单")
    external_link = models.CharField(
        max_length=255, blank=True, default="", verbose_name="外链地址"
    )
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )

    class Meta:
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        db_table = "sys_menu"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class User(BaseModel):
    """系统用户。"""

    username = models.CharField(max_length=64, unique=True, verbose_name="登录账号")
    password = models.CharField(max_length=128, default="pbkdf2_sha256$notset", verbose_name="密码")
    nickname = models.CharField(max_length=64, verbose_name="用户昵称")
    avatar = models.CharField(
        max_length=255,
        blank=True,
        default="https://unpkg.com/@vbenjs/static-source@0.1.7/source/avatar-v1.webp",
        verbose_name="头像",
    )
    email = models.EmailField(max_length=128, blank=True, default="", verbose_name="邮箱")
    phone = models.CharField(max_length=20, blank=True, default="", verbose_name="手机")
    gender = models.CharField(
        max_length=8,
        default="0",
        choices=(("0", "未知"), ("1", "男"), ("2", "女")),
        verbose_name="性别",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="归属部门",
    )
    posts = models.ManyToManyField(Post, blank=True, related_name="users", verbose_name="岗位")
    roles = models.ManyToManyField(Role, blank=True, related_name="users", verbose_name="角色")
    status = models.CharField(
        max_length=16, default="1", choices=(("1", "启用"), ("0", "停用")), verbose_name="状态"
    )
    login_ip = models.CharField(max_length=64, blank=True, default="", verbose_name="最后登录IP")
    login_at = models.DateTimeField(null=True, blank=True, verbose_name="最后登录时间")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["nickname"]

    @property
    def is_authenticated(self):
        return True

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        db_table = "sys_user"

    def __str__(self):
        return f"{self.username}({self.nickname})"

    def set_password(self, raw: str):
        """快速生成一个简单口令 hash，保证登录可用。
        开发模式下为了不额外引入 django.contrib.auth 的强依赖，使用基础 SHA256+SALT。
        """
        import hashlib
        import os

        salt = os.urandom(8).hex()
        digest = hashlib.sha256((salt + raw).encode("utf-8")).hexdigest()
        self.password = f"sha256${salt}${digest}"

    def check_password(self, raw: str) -> bool:
        import hashlib

        if not raw or not self.password or "$" not in self.password:
            return False
        algo, salt, digest = self.password.split("$", 2)
        if algo == "sha256":
            return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest() == digest
        return False


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
