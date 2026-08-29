"""系统管理模块单元测试。

覆盖范围:
1. 404 链路: 常量路由(404/403/500 页面定义) / isRouteExist / API 404 状态码
2. 管理模块 CRUD: 用户/角色/菜单/部门/岗位/字典/参数/日志
   - 新增: 数据校验 + 权限控制 + 数据持久化 + 操作日志
   - 删除: 软删除 + 批量删除 + 权限验证 + 数据完整性
   - 修改: 数据更新 + 业务规则(唯一性/缓存失效)
   - 查询: 条件筛选 + 分页 + 数据准确性

约定: 所有接口返回 {code, msg, data}, 成功 code="0000"; 业务失败 code="5000"; 未登录 code="1000"。

注: 前端 404 页面的样式与交互渲染属于浏览器端行为, 不在 Django 单测范围内。
"""

from __future__ import annotations

from django.core.cache import cache
from django.test import TestCase

from .models import Config, Department, DictData, DictType, Menu, OperationLog, Post, Role, User
from .views.common import _issue_token, bump_routes_version, user_routes_cache_key

API = "/api"


def auth_header(token: str) -> dict:
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class BaseAuthTestCase(TestCase):
    """提供已登录的超管账号与请求封装。"""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create(username="tester", nickname="测试员")
        cls.admin.set_password("tester@123")
        cls.admin.save(update_fields=["password"])

    def setUp(self):
        token, _refresh = _issue_token(self.admin)
        self.token = token
        self.client.defaults.update(auth_header(token))

    def get(self, path, params=None, **kwargs):
        return self.client.get(f"{API}{path}", params, **kwargs)

    def post(self, path, data=None, **kwargs):
        return self.client.post(f"{API}{path}", data=data, content_type="application/json", **kwargs)

    def put(self, path, data=None, **kwargs):
        return self.client.put(f"{API}{path}", data=data, content_type="application/json", **kwargs)

    def delete(self, path, **kwargs):
        return self.client.delete(f"{API}{path}", **kwargs)

    @staticmethod
    def body(resp) -> dict:
        return resp.json()

    @staticmethod
    def data_of(resp):
        return resp.json()["data"]


# ===================== 1. 404 链路 =====================


class Route404Tests(BaseAuthTestCase):
    """404 相关: 常量路由定义 / isRouteExist / API 404 状态码。"""

    def test_constant_routes_define_404_page(self):
        """输入: GET /route/getConstantRoutes
        预期: 返回 code=0000, 包含 404/403/500/login 四个常量路由, 且 meta.constant=True
        验证: 前端 404 页面所依赖的路由定义完整"""
        resp = self.get("/route/getConstantRoutes")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.body(resp)["code"], "0000")
        routes = {r["name"]: r for r in self.data_of(resp)}
        for name in ("404", "403", "500", "login"):
            self.assertIn(name, routes)
            self.assertTrue(routes[name]["meta"]["constant"])
        self.assertEqual(routes["404"]["component"], "layout.blank$view.404")

    def test_is_route_exist_false_for_unknown_route(self):
        """输入: routeName=NoSuchRoute (库中不存在)
        预期: data=False, 前端据此渲染 404 页面"""
        resp = self.get("/route/isRouteExist", {"routeName": "NoSuchRoute"})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.data_of(resp))

    def test_is_route_exist_false_for_blank_route(self):
        """输入: routeName 为空
        预期: data=False (边界条件)"""
        resp = self.get("/route/isRouteExist", {"routeName": ""})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertFalse(self.data_of(resp))

    def test_is_route_exist_true_for_existing_menu(self):
        """输入: 先创建启用菜单 name=known_page, 再查询 routeName=known_page
        预期: data=True"""
        Menu.objects.create(name="known_page", title="已知页面", status="1")
        resp = self.get("/route/isRouteExist", {"routeName": "known_page"})
        self.assertTrue(self.data_of(resp))

    def test_is_route_exist_false_for_disabled_menu(self):
        """输入: 创建停用(status=0)菜单后查询
        预期: data=False (停用菜单视为不存在)"""
        Menu.objects.create(name="disabled_page", title="停用页面", status="0")
        resp = self.get("/route/isRouteExist", {"routeName": "disabled_page"})
        self.assertFalse(self.data_of(resp))

    def test_unknown_api_path_returns_404(self):
        """输入: 请求不存在的接口路径 /api/no/such/api/
        预期: HTTP 404"""
        resp = self.client.get(f"{API}/no/such/api/")
        self.assertEqual(resp.status_code, 404)


# ===================== 2. 权限控制 =====================


class AuthRequiredTests(TestCase):
    """未登录访问保护: 所有管理接口必须携带有效 token。"""

    def test_list_without_token_returns_401(self):
        """输入: 无 Authorization 头请求用户列表
        预期: HTTP 401, code=1000"""
        resp = self.client.get(f"{API}/system/user/")
        self.assertEqual(resp.status_code, 401)
        body = resp.json()
        self.assertEqual(body["code"], "1000")

    def test_create_without_token_returns_401(self):
        """输入: 无 token POST 新增配置
        预期: HTTP 401, 数据不落库"""
        resp = self.client.post(
            f"{API}/system/config/",
            data={"name": "x", "code": "x.1", "value": "1"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(Config.objects.filter(code="x.1").count(), 0)

    def test_invalid_token_returns_401(self):
        """输入: 伪造 token
        预期: HTTP 401"""
        resp = self.client.get(f"{API}/system/user/", **auth_header("invalid-token"))
        self.assertEqual(resp.status_code, 401)


# ===================== 3. 各模块 CRUD =====================


class UserCRUDTests(BaseAuthTestCase):
    """用户管理: 新增/修改/删除/查询。"""

    def test_create_user_persists_with_default_password(self):
        """输入: {username, nickname} 合法数据
        预期: code=0000; 用户落库; 默认密码 123456 可校验通过; 记录操作日志"""
        payload = {"username": "u_new", "nickname": "新用户"}
        resp = self.post("/system/user/", payload)
        self.assertEqual(self.body(resp)["code"], "0000")
        user = User.objects.filter(username="u_new").first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password("123456"))
        self.assertTrue(
            OperationLog.objects.filter(module="用户管理", operation_type="2", username="tester").exists()
        )

    def test_create_user_with_roles(self):
        """输入: 携带 roleIds=[R_SUPER 角色id]
        预期: 用户角色关联正确持久化"""
        role = Role.objects.create(name="管理员", code="R_SUPER")
        resp = self.post("/system/user/", {"username": "u_role", "nickname": "有角色", "roleIds": [role.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        user = User.objects.get(username="u_role")
        self.assertEqual(list(user.roles.values_list("code", flat=True)), ["R_SUPER"])

    def test_create_user_missing_nickname_rejected(self):
        """输入: 缺少必填字段 nickname
        预期: HTTP 400, code=5000, 数据不落库"""
        count = User.objects.count()
        resp = self.post("/system/user/", {"username": "u_bad"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.body(resp)["code"], "5000")
        self.assertEqual(User.objects.count(), count)

    def test_create_user_duplicate_username_rejected(self):
        """输入: 已存在的 username (唯一约束)
        预期: HTTP 400, code=5000, 不产生重复数据"""
        User.objects.create(username="dup", nickname="原有")
        count = User.objects.count()
        resp = self.post("/system/user/", {"username": "dup", "nickname": "重复"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.body(resp)["code"], "5000")
        self.assertEqual(User.objects.count(), count)

    def test_update_user_changes_data(self):
        """输入: PUT 修改 nickname 与 roleIds
        预期: code=0000; 字段更新; 角色替换生效"""
        role_a = Role.objects.create(name="A", code="R_A")
        role_b = Role.objects.create(name="B", code="R_B")
        user = User.objects.create(username="u_edit", nickname="旧名")
        user.roles.set([role_a])
        resp = self.put(f"/system/user/{user.id}/", {"nickname": "新名", "roleIds": [role_b.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        user.refresh_from_db()
        self.assertEqual(user.nickname, "新名")
        self.assertEqual(list(user.roles.values_list("code", flat=True)), ["R_B"])

    def test_delete_user_is_soft_delete(self):
        """输入: DELETE 已有用户
        预期: code=0000; 行仍在库中且 is_deleted=True (数据完整性: 物理不删)"""
        user = User.objects.create(username="u_del", nickname="待删")
        resp = self.delete(f"/system/user/{user.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(User.objects.filter(pk=user.pk, is_deleted=True).exists())

    def test_batch_delete_users(self):
        """输入: POST batch-delete 携带 2 个 id
        预期: code=0000; 两个用户均软删除"""
        u1 = User.objects.create(username="b1", nickname="批1")
        u2 = User.objects.create(username="b2", nickname="批2")
        resp = self.post("/system/user/batch-delete/", {"ids": [u1.id, u2.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(User.objects.filter(pk=u1.pk, is_deleted=True).exists())
        self.assertTrue(User.objects.filter(pk=u2.pk, is_deleted=True).exists())

    def test_list_pagination_and_filter(self):
        """输入: 先造 12 个 u_page* 用户, 请求 current=1&size=10 与 keyword=u_page
        预期: total=12; 第一页 10 条; keyword 命中且数据准确"""
        for i in range(12):
            User.objects.create(username=f"u_page{i:02d}", nickname=f"分页{i}")
        resp = self.get("/system/user/", {"current": "1", "size": "10", "keyword": "u_page"})
        data = self.data_of(resp)
        self.assertEqual(data["total"], 12)
        self.assertEqual(data["current"], 1)
        self.assertEqual(data["size"], 10)
        self.assertEqual(len(data["records"]), 10)
        self.assertTrue(all(r["username"].startswith("u_page") for r in data["records"]))
        # 第二页
        resp = self.get("/system/user/", {"current": "2", "size": "10", "keyword": "u_page"})
        self.assertEqual(len(self.data_of(resp)["records"]), 2)

    def test_list_status_filter(self):
        """输入: 一启用一停用用户, status=0 筛选
        预期: 仅返回停用用户"""
        User.objects.create(username="f_on", nickname="启用")
        User.objects.create(username="f_off", nickname="停用", status="0")
        resp = self.get("/system/user/", {"status": "0"})
        records = self.data_of(resp)["records"]
        self.assertEqual([r["username"] for r in records], ["f_off"])

    def test_retrieve_nonexistent_user_returns_error(self):
        """输入: 查询不存在的 id=999999
        预期: 返回统一错误信封 code=5000 (异常被自定义 handler 捕获, 不裸奔 traceback)"""
        resp = self.get("/system/user/999999/")
        body = self.body(resp)
        self.assertNotEqual(body["code"], "0000")
        self.assertIn("msg", body)


class RoleCRUDTests(BaseAuthTestCase):
    """角色管理: 新增(含菜单授权)/修改/删除/查询。"""

    def test_create_role_with_menus(self):
        """输入: name/code + menuIds=[m1,m2]
        预期: 角色落库且菜单授权持久化; 查询接口回显 menuIds"""
        m1 = Menu.objects.create(name="rm1", title="R菜单1", status="1")
        m2 = Menu.objects.create(name="rm2", title="R菜单2", status="1")
        resp = self.post("/system/role/", {"name": "角色X", "code": "R_X", "menuIds": [m1.id, m2.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        role = Role.objects.get(code="R_X")
        self.assertEqual(set(role.menus.values_list("id", flat=True)), {m1.id, m2.id})

    def test_create_role_duplicate_code_rejected(self):
        """输入: 重复角色编码
        预期: HTTP 400, code=5000, 不落库"""
        Role.objects.create(name="原有", code="R_DUP")
        count = Role.objects.count()
        resp = self.post("/system/role/", {"name": "重复", "code": "R_DUP"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Role.objects.count(), count)

    def test_update_role_replaces_menus(self):
        """输入: PUT 将 menuIds 由 [m1] 改为 [m2]
        预期: 授权整体替换为 [m2] (业务规则: 全量覆盖)"""
        m1 = Menu.objects.create(name="rm1", title="菜单1", status="1")
        m2 = Menu.objects.create(name="rm2", title="菜单2", status="1")
        role = Role.objects.create(name="角色Y", code="R_Y")
        role.menus.set([m1])
        resp = self.put(f"/system/role/{role.id}/", {"menuIds": [m2.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        role.refresh_from_db()
        self.assertEqual(list(role.menus.values_list("id", flat=True)), [m2.id])

    def test_assign_menus_bumps_route_cache_version(self):
        """输入: assign-menus 授权动作
        预期: code=0000; 菜单授权变更后全局路由缓存版本号 +1 (缓存失效联动)"""
        role = Role.objects.create(name="角色Z", code="R_Z")
        menu = Menu.objects.create(name="rzm", title="Z菜单", status="1")
        key = user_routes_cache_key(self.admin.id)
        cache.set(key, {"cached": True}, 300)
        version_before = cache.get("menu_routes:ver", 1)
        resp = self.post(f"/system/role/{role.id}/assign-menus/", {"menuIds": [menu.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertEqual(role.menus.count(), 1)
        self.assertGreater(cache.get("menu_routes:ver", 1), version_before)

    def test_delete_role_soft(self):
        """输入: DELETE 角色
        预期: 软删除; 用户多对多关联随之解除查询可见性"""
        role = Role.objects.create(name="待删角色", code="R_DEL")
        resp = self.delete(f"/system/role/{role.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(Role.objects.filter(pk=role.pk, is_deleted=True).exists())

    def test_list_code_filter(self):
        """输入: code=R_F1/R_F2 两个角色, code=R_F1 精确过滤
        预期: 仅命中 R_F1 (icontains 模糊)"""
        Role.objects.create(name="F1", code="R_F1")
        Role.objects.create(name="F2", code="R_F2")
        resp = self.get("/system/role/", {"code": "R_F1"})
        records = self.data_of(resp)["records"]
        self.assertEqual([r["code"] for r in records], ["R_F1"])


class MenuCRUDTests(BaseAuthTestCase):
    """菜单管理: 新增/修改/删除/树查询/缓存联动。"""

    def setUp(self):
        super().setUp()
        bump_routes_version()  # 隔离其他用例对缓存版本的影响

    def test_create_menu_persists_and_bumps_cache_version(self):
        """输入: 新增目录菜单
        预期: code=0000; 落库; 全局路由缓存版本 +1 (菜单变更使所有用户缓存失效)"""
        version_before = cache.get("menu_routes:ver", 1)
        resp = self.post("/system/menu/", {"name": "m_root", "title": "根目录", "menu_type": "1", "order": 1})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(Menu.objects.filter(name="m_root", menu_type="1").exists())
        self.assertEqual(cache.get("menu_routes:ver", 1), version_before + 1)

    def test_tree_reflects_parent_child_hierarchy(self):
        """输入: 建 父目录 + 子菜单, GET tree
        预期: 树中父节点 children 包含子节点, 顶层只含父节点"""
        parent = Menu.objects.create(name="t_parent", title="父", menu_type="1")
        child = Menu.objects.create(name="t_child", title="子", menu_type="2", parent=parent)
        resp = self.get("/system/menu/tree/")
        roots = self.data_of(resp)
        parent_node = next(r for r in roots if r["name"] == "t_parent")
        self.assertEqual([c["id"] for c in parent_node["children"]], [child.id])
        self.assertNotIn("t_child", [r["name"] for r in roots])

    def test_tree_orders_by_order_field(self):
        """输入: 两个子菜单 order 分别为 2、1
        预期: children 按 order 升序 (查询数据准确性)"""
        parent = Menu.objects.create(name="o_parent", title="父", menu_type="1")
        Menu.objects.create(name="o_second", title="第二", menu_type="2", parent=parent, order=2)
        Menu.objects.create(name="o_first", title="第一", menu_type="2", parent=parent, order=1)
        resp = self.get("/system/menu/tree/")
        node = next(r for r in self.data_of(resp) if r["name"] == "o_parent")
        self.assertEqual([c["name"] for c in node["children"]], ["o_first", "o_second"])

    def test_soft_deleted_parent_hides_subtree_from_tree(self):
        """输入: 软删除父目录
        预期: tree 中父节点与其子树均不返回 (子节点 parentId 指向已删父, 不作为根返回)"""
        parent = Menu.objects.create(name="d_parent", title="父", menu_type="1")
        Menu.objects.create(name="d_child", title="子", menu_type="2", parent=parent)
        resp = self.delete(f"/system/menu/{parent.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        # 子菜单未被物理删除 (数据完整性)
        self.assertTrue(Menu.objects.filter(name="d_child", is_deleted=False).exists())
        resp = self.get("/system/menu/tree/")
        names = [r["name"] for r in self.data_of(resp)]
        self.assertNotIn("d_parent", names)
        self.assertNotIn("d_child", names)

    def test_update_menu_partial_fields(self):
        """输入: PUT 仅改 title 与 hide_in_menu
        预期: 其余字段不变, 目标字段更新"""
        menu = Menu.objects.create(name="u_menu", title="旧名", menu_type="2")
        resp = self.put(f"/system/menu/{menu.id}/", {"title": "新名", "hide_in_menu": True})
        self.assertEqual(self.body(resp)["code"], "0000")
        menu.refresh_from_db()
        self.assertEqual(menu.title, "新名")
        self.assertTrue(menu.hide_in_menu)
        self.assertEqual(menu.name, "u_menu")

    def test_batch_delete_menus(self):
        """输入: batch-delete 2 个按钮菜单
        预期: 均软删除"""
        b1 = Menu.objects.create(name="bt1", title="按钮1", menu_type="3")
        b2 = Menu.objects.create(name="bt2", title="按钮2", menu_type="3")
        resp = self.post("/system/menu/batch-delete/", {"ids": [b1.id, b2.id]})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertEqual(Menu.objects.filter(pk__in=[b1.pk, b2.pk], is_deleted=False).count(), 0)


class DepartmentCRUDTests(BaseAuthTestCase):
    """部门管理。"""

    def test_create_department_and_tree(self):
        """输入: 建总公司 + 技术中心(子部门), GET tree
        预期: 树中子部门嵌套于总公司 children"""
        resp = self.post("/system/dept/", {"name": "总公司", "code": "D_HQ"})
        self.assertEqual(self.body(resp)["code"], "0000")
        hq = Department.objects.get(code="D_HQ")
        self.post("/system/dept/", {"name": "技术中心", "code": "D_TECH", "parent": hq.id})
        resp = self.get("/system/dept/tree/")
        hq_node = next(r for r in self.data_of(resp) if r["code"] == "D_HQ")
        self.assertIn("D_TECH", [c["code"] for c in hq_node["children"]])

    def test_create_department_duplicate_code_rejected(self):
        """输入: 重复部门编码
        预期: HTTP 400, code=5000"""
        Department.objects.create(name="A部", code="D_DUP")
        resp = self.post("/system/dept/", {"name": "B部", "code": "D_DUP"})
        self.assertEqual(resp.status_code, 400)

    def test_delete_department_keeps_users_intact(self):
        """输入: 部门下有用户, DELETE 部门 (软删)
        预期: 部门软删; 用户记录完整保留 (SET_NULL 语义在软删下不触发置空, 记录现状)"""
        dept = Department.objects.create(name="待删部", code="D_DEL")
        user = User.objects.create(username="d_u", nickname="部员", department=dept)
        resp = self.delete(f"/system/dept/{dept.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        user.refresh_from_db()
        self.assertIsNotNone(user.department_id)  # 软删不触发外键置空
        self.assertTrue(Department.objects.filter(pk=dept.pk, is_deleted=True).exists())


class PostCRUDTests(BaseAuthTestCase):
    """岗位管理。"""

    def test_create_update_delete(self):
        """输入: 新增岗位 → PUT 改名 → DELETE
        预期: 三步均 code=0000, 状态逐步变化"""
        resp = self.post("/system/post/", {"name": "工程师", "code": "P_DEV"})
        self.assertEqual(self.body(resp)["code"], "0000")
        post = Post.objects.get(code="P_DEV")
        resp = self.put(f"/system/post/{post.id}/", {"name": "高级工程师"})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(Post.objects.filter(code="P_DEV", name="高级工程师").exists())
        resp = self.delete(f"/system/post/{post.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(Post.objects.filter(pk=post.pk, is_deleted=True).exists())

    def test_create_post_duplicate_code_rejected(self):
        """输入: 重复岗位编码
        预期: HTTP 400"""
        Post.objects.create(name="原有", code="P_DUP")
        resp = self.post("/system/post/", {"name": "重复", "code": "P_DUP"})
        self.assertEqual(resp.status_code, 400)


class DictCRUDTests(BaseAuthTestCase):
    """字典类型与字典数据。"""

    def test_create_dict_type(self):
        """输入: 新增字典类型
        预期: code=0000, 落库"""
        resp = self.post("/system/dict/type/", {"name": "性别", "code": "gender"})
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(DictType.objects.filter(code="gender").exists())

    def test_create_dict_data_with_type_code(self):
        """输入: dictCodeInput=gender + label/value
        预期: 明细关联到指定类型"""
        DictType.objects.create(name="性别", code="gender")
        resp = self.post(
            "/system/dict/data/",
            {"dictCodeInput": "gender", "label": "男", "value": "1"},
        )
        self.assertEqual(self.body(resp)["code"], "0000")
        data = DictData.objects.get(value="1")
        self.assertEqual(data.dict_type.code, "gender")

    def test_create_dict_data_without_type_rejected(self):
        """输入: 缺少 dictCodeInput 且无 dict_type
        预期: HTTP 400, code=5000 (业务规则校验)"""
        resp = self.post("/system/dict/data/", {"label": "未知", "value": "x"})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.body(resp)["code"], "5000")

    def test_create_dict_data_with_unknown_type_rejected(self):
        """输入: dictCodeInput=not_exist (不存在的类型)
        预期: HTTP 400, msg 提示类型不存在"""
        resp = self.post("/system/dict/data/", {"dictCodeInput": "not_exist", "label": "x", "value": "x"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("不存在", self.body(resp)["msg"])

    def test_duplicate_value_in_same_type_rejected(self):
        """输入: 同一类型下重复 value (unique_together)
        预期: HTTP 400"""
        dtype = DictType.objects.create(name="性别", code="gender")
        DictData.objects.create(dict_type=dtype, label="男", value="1")
        resp = self.post("/system/dict/data/", {"dictCodeInput": "gender", "label": "男2", "value": "1"})
        self.assertEqual(resp.status_code, 400)

    def test_db_level_cascade_delete_dict_type(self):
        """输入: 物理删除字典类型 (ORM 级联行为验证)
        预期: on_delete=CASCADE 使明细一并删除"""
        dtype = DictType.objects.create(name="级联", code="cascade_t")
        DictData.objects.create(dict_type=dtype, label="a", value="a")
        DictData.objects.create(dict_type=dtype, label="b", value="b")
        dtype.delete()
        self.assertEqual(DictData.objects.filter(dict_type_id=dtype.pk).count(), 0)


class ConfigCRUDTests(BaseAuthTestCase):
    """参数设置: CRUD + storage.* 隐藏规则 + by-key + 系统名称。"""

    def test_create_update_delete_config(self):
        """输入: 新增参数 → PUT 改值 → DELETE
        预期: 全链路 code=0000, 值更新并软删"""
        resp = self.post("/system/config/", {"name": "测试参数", "code": "test.param", "value": "v1"})
        self.assertEqual(self.body(resp)["code"], "0000")
        cfg = Config.objects.get(code="test.param")
        resp = self.put(f"/system/config/{cfg.id}/", {"value": "v2"})
        self.assertEqual(self.body(resp)["code"], "0000")
        cfg.refresh_from_db()
        self.assertEqual(cfg.value, "v2")
        resp = self.delete(f"/system/config/{cfg.id}/")
        self.assertEqual(self.body(resp)["code"], "0000")
        self.assertTrue(Config.objects.filter(pk=cfg.pk, is_deleted=True).exists())

    def test_list_excludes_storage_codes(self):
        """输入: 库中存在 sys.* 与 storage.* 参数
        预期: 参数设置列表不含 storage.* (由存储管理维护), 含 sys.*"""
        Config.objects.create(name="系统名称", code="sys.system.name", value="X")
        Config.objects.create(name="本地存储", code="storage.local", value="{}")
        resp = self.get("/system/config/")
        codes = [r["code"] for r in self.data_of(resp)["records"]]
        self.assertIn("sys.system.name", codes)
        self.assertNotIn("storage.local", codes)

    def test_by_key_returns_enabled_config(self):
        """输入: GET by-key?code=sys.system.name (启用状态)
        预期: 返回该参数完整数据; 不存在的 code 返回 data=None"""
        Config.objects.create(name="系统名称", code="sys.system.name", value="Soybean")
        resp = self.get("/system/config/by-key/", {"code": "sys.system.name"})
        self.assertEqual(self.data_of(resp)["value"], "Soybean")
        resp = self.get("/system/config/by-key/", {"code": "no.such.code"})
        self.assertIsNone(self.data_of(resp))

    def test_by_key_requires_code_param(self):
        """输入: 不带 code 参数
        预期: code=5000, msg 提示"""
        resp = self.get("/system/config/by-key/")
        self.assertEqual(self.body(resp)["code"], "5000")


class OperationLogTests(BaseAuthTestCase):
    """操作日志: 查询与自动记录。"""

    def test_mutation_creates_operation_log(self):
        """输入: 执行一次新增 + 一次删除
        预期: 产生 op_type=2(新增) 与 op_type=4(删除) 两条日志, username 记录操作人"""
        resp = self.post("/system/post/", {"name": "日志岗位", "code": "P_LOG"})
        post_id = self.data_of(resp)["postId"]
        self.delete(f"/system/post/{post_id}/")
        self.assertTrue(OperationLog.objects.filter(module="岗位管理", operation_type="2").exists())
        self.assertTrue(OperationLog.objects.filter(module="岗位管理", operation_type="4").exists())
        log = OperationLog.objects.filter(module="岗位管理", operation_type="2").first()
        self.assertEqual(log.username, "tester")

    def test_log_list_pagination(self):
        """输入: 造 3 条日志, size=2
        预期: total=3, 第一页 2 条 (分页处理)"""
        for i in range(3):
            OperationLog.objects.create(module="测试", description=f"日志{i}", username="tester")
        resp = self.get("/system/log/", {"current": "1", "size": "2"})
        data = self.data_of(resp)
        self.assertEqual(data["total"], 3)
        self.assertEqual(len(data["records"]), 2)
