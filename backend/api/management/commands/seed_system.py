"""种子数据：首次 migrate 后可通过 `python manage.py seed_system` 初始化。"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from api.models import (
    Config,
    Department,
    DictData,
    DictType,
    Menu,
    Post,
    Role,
    User,
)


class Command(BaseCommand):
    help = "初始化系统管理模块的种子数据（角色、菜单、用户、字典、参数、部门、岗位）"

    def handle(self, *args, **options):
        try:
            self._seed_department()
            self._seed_post()
            self._seed_roles()
            self._seed_menus()
            self._seed_users()
            self._seed_dict()
            self._seed_config()
            self._bind_roles_menus()
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f"初始化失败: {exc}") from exc
        self.stdout.write(self.style.SUCCESS("系统管理种子数据初始化完成 ✅"))

    # -------------------- 辅助 --------------------
    @staticmethod
    def _dept(name, code, *, parent=None, **extra):
        d, created = Department.objects.get_or_create(
            code=code,
            defaults={"name": name, "parent": parent, **extra},
        )
        if not created:
            d.name = name
            d.parent = parent
            for k, v in extra.items():
                setattr(d, k, v)
            d.save()
        return d

    @staticmethod
    def _post(name, code, **extra):
        p, created = Post.objects.get_or_create(
            code=code,
            defaults={"name": name, **extra},
        )
        if not created:
            p.name = name
            for k, v in extra.items():
                setattr(p, k, v)
            p.save()
        return p

    @staticmethod
    def _role(name, code, **extra):
        r, created = Role.objects.get_or_create(
            code=code,
            defaults={"name": name, **extra},
        )
        if not created:
            r.name = name
            for k, v in extra.items():
                setattr(r, k, v)
            r.save()
        return r

    @staticmethod
    def _cfg(name, code, value, **extra):
        c, created = Config.objects.get_or_create(
            code=code,
            defaults={"name": name, "value": value, **extra},
        )
        if not created:
            c.name = name
            c.value = value
            for k, v in extra.items():
                setattr(c, k, v)
            c.save()
        return c

    # -------------------- 部门 --------------------
    def _seed_department(self):
        top = self._dept("总公司", "HQ", leader="张三", phone="13800000000", email="hq@example.com")
        self._dept("技术中心", "TECH", parent=top, leader="李四")
        self._dept("市场部", "MKT", parent=top, leader="王五")
        self._dept("财务部", "FIN", parent=top, leader="赵六")
        self._dept("人力资源部", "HR", parent=top, leader="孙七")

    # -------------------- 岗位 --------------------
    def _seed_post(self):
        self._post("董事长", "CEO")
        self._post("技术总监", "CTO")
        self._post("高级开发工程师", "SR_DEV")
        self._post("前端工程师", "FE_DEV")
        self._post("后端工程师", "BE_DEV")
        self._post("市场专员", "MKT_STAFF")
        self._post("会计", "ACCOUNTANT")
        self._post("HR 专员", "HR_STAFF")

    # -------------------- 角色 --------------------
    def _seed_roles(self):
        self._role("超级管理员", "R_SUPER", data_scope="1")
        self._role("部门管理员", "R_DEPT", data_scope="4")
        self._role("普通用户", "R_USER", data_scope="5")
        self._role("访客", "R_GUEST", data_scope="5", status="1")

    # -------------------- 菜单 --------------------
    def _menu(self, name, title, *, menu_type="2", parent=None, order=0, **extra):
        safe_name = name
        m, created = Menu.objects.get_or_create(
            name=safe_name,
            defaults={
                "title": title,
                "menu_type": menu_type,
                "parent": parent,
                "order": order,
                **extra,
            },
        )
        if not created:
            m.title = title
            m.menu_type = menu_type
            m.parent = parent
            m.order = order
            for k, v in extra.items():
                setattr(m, k, v)
            m.save()
        return m

    def _seed_menus(self):
        # 一级目录：系统管理
        system = self._menu(
            "system",
            "系统管理",
            menu_type="1",
            order=10,
            path="/system",
            component="layout.base$view.system",
            icon="mdi:cog-outline",
            i18n_key="route.system",
        )
        children = [
            ("system_user", "用户管理", "/system/user", "layout.base$view.system_user", "mdi:account-group-outline", 1, "system:user:view"),
            ("system_role", "角色管理", "/system/role", "layout.base$view.system_role", "mdi:shield-account-outline", 2, "system:role:view"),
            ("system_menu", "菜单管理", "/system/menu", "layout.base$view.system_menu", "mdi:menu-open", 3, "system:menu:view"),
            ("system_dept", "部门管理", "/system/dept", "layout.base$view.system_dept", "mdi:office-building-outline", 4, "system:dept:view"),
            ("system_post", "岗位管理", "/system/post", "layout.base$view.system_post", "mdi:badge-account-outline", 5, "system:post:view"),
            ("system_dict", "字典管理", "/system/dict", "layout.base$view.system_dict", "mdi:book-open-page-variant-outline", 6, "system:dict:view"),
            ("system_config", "参数设置", "/system/config", "layout.base$view.system_config", "mdi:tune-variant", 7, "system:config:view"),
            ("system_log", "日志管理", "/system/log", "layout.base$view.system_log", "mdi:file-document-multiple-outline", 8, "system:log:view"),
        ]
        for n, title, path, comp, icon, order, perm in children:
            menu = self._menu(
                n,
                title,
                parent=system,
                path=path,
                component=comp,
                icon=icon,
                order=order,
                menu_type="2",
                i18n_key=f"route.{n}",
            )
            # 5 个按钮权限
            button_kwargs = {"parent": menu, "menu_type": "3"}
            btn_perms = [
                (f"{n}:add", "新增", perm.replace(":view", ":add"), 1),
                (f"{n}:edit", "修改", perm.replace(":view", ":edit"), 2),
                (f"{n}:delete", "删除", perm.replace(":view", ":delete"), 3),
                (f"{n}:export", "导出", perm.replace(":view", ":export"), 4),
                (f"{n}:batch-delete", "批量删除", perm.replace(":view", ":batch-delete"), 5),
            ]
            for m_name, m_title, p, o in btn_perms:
                Menu.objects.update_or_create(
                    name=m_name,
                    defaults={
                        "title": m_title,
                        "permission": p,
                        "order": o,
                        "parent": menu,
                        "menu_type": "3",
                        "hide_in_menu": True,
                    },
                )

    # -------------------- 用户 --------------------
    def _seed_users(self):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "nickname": "超级管理员",
                "phone": "13800000000",
                "email": "admin@example.com",
                "gender": "1",
                "department": Department.objects.filter(code="TECH").first(),
            },
        )
        if created or admin.password.startswith("pbkdf2_sha256$notset"):
            admin.set_password("admin123")
        admin.nickname = "超级管理员"
        admin.save()
        admin.roles.set(list(Role.objects.filter(code="R_SUPER")))
        admin.posts.set(list(Post.objects.filter(code__in=["CEO", "CTO"])))

        demo, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "nickname": "演示用户",
                "phone": "13800000001",
                "email": "demo@example.com",
                "gender": "1",
                "department": Department.objects.filter(code="MKT").first(),
            },
        )
        if created or demo.password.startswith("pbkdf2_sha256$notset"):
            demo.set_password("demo123")
        demo.nickname = "演示用户"
        demo.save()
        demo.roles.set(list(Role.objects.filter(code__in=["R_USER", "R_DEPT"])))
        demo.posts.set(list(Post.objects.filter(code="MKT_STAFF")))

    # -------------------- 字典 --------------------
    def _dict_type(self, name, code, items):
        dt, _ = DictType.objects.get_or_create(code=code, defaults={"name": name})
        dt.name = name
        dt.save()
        DictData.objects.filter(dict_type=dt).delete()
        for idx, (label, value, list_class, is_default) in enumerate(items, start=1):
            DictData.objects.create(
                dict_type=dt,
                label=label,
                value=value,
                list_class=list_class,
                is_default=is_default,
                sort_order=idx,
            )

    def _seed_dict(self):
        self._dict_type(
            "用户性别",
            "sys_user_sex",
            [
                ("男", "1", "success", True),
                ("女", "2", "warning", False),
                ("未知", "0", "info", False),
            ],
        )
        self._dict_type(
            "菜单状态",
            "sys_show_hide",
            [
                ("显示", "0", "", True),
                ("隐藏", "1", "", False),
            ],
        )
        self._dict_type(
            "状态（开关）",
            "sys_normal_disable",
            [
                ("正常", "1", "success", True),
                ("停用", "0", "error", False),
            ],
        )
        self._dict_type(
            "操作类型",
            "sys_oper_type",
            [
                ("其它", "1", "info", True),
                ("新增", "2", "success", False),
                ("修改", "3", "warning", False),
                ("删除", "4", "error", False),
                ("授权", "5", "primary", False),
                ("导出", "6", "", False),
                ("导入", "7", "", False),
                ("登录", "8", "", False),
                ("登出", "9", "", False),
            ],
        )
        self._dict_type(
            "系统是否",
            "sys_yes_no",
            [
                ("是", "Y", "success", False),
                ("否", "N", "info", True),
            ],
        )

    # -------------------- 参数 --------------------
    def _seed_config(self):
        self._cfg("主框架页-默认皮肤样式名称", "sys.index.skinName", "skin-blue", value_type="S", is_system=True)
        self._cfg("用户管理-账号初始密码", "sys.user.initPassword", "123456", value_type="S", is_system=True)
        self._cfg("主框架页-侧边栏主题", "sys.index.sideTheme", "theme-dark", value_type="S", is_system=True)
        self._cfg("账号自助-是否开启用户注册", "sys.account.registerUser", "false", value_type="B", is_system=True)
        self._cfg("账号自助-是否开启验证码", "sys.account.captchaEnabled", "true", value_type="B", is_system=True)
        self._cfg("系统名称", "sys.system.name", "Soybean Django 管理系统", value_type="S", is_system=True)

    # -------------------- 角色-菜单 --------------------
    def _bind_roles_menus(self):
        super_role = Role.objects.get(code="R_SUPER")
        all_menu_ids = list(Menu.objects.values_list("id", flat=True))
        super_role.menus.set(all_menu_ids)

        user_role = Role.objects.get(code="R_USER")
        # 普通用户只给用户/角色/字典/日志(只读在 dynamic 模式由后端过滤按钮)
        limited_names = ["system", "system_user", "system_dept", "system_dict", "system_log"]
        limited = list(Menu.objects.filter(name__in=limited_names).values_list("id", flat=True))
        user_role.menus.set(limited)
