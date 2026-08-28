"""路由相关视图。

constantRoutes（内置路由）/ userRoutes（按当前角色动态菜单）/ isRouteExist
"""

from __future__ import annotations

from django.core.cache import cache
from rest_framework.response import Response

from ..models import Menu, User
from .common import (
    APIView,
    _ROUTES_TTL,
    ok,
    require_auth,
    user_routes_cache_key,
)


def _menu_to_route(menu: Menu) -> dict:
    # 一级目录默认布局容器; 二级目录透明分组(无 component); 叶子菜单按视图目录名映射
    if menu.component:
        component = menu.component
    elif menu.menu_type == "1":
        component = "layout.base" if menu.parent_id is None else ""
    else:
        component = f"view.{menu.name}"
    meta = {
        "title": menu.title or menu.name,
        "icon": menu.icon or "",
        "order": menu.order or 0,
        "keepAlive": menu.keep_alive,
        "hideInMenu": menu.hide_in_menu,
    }
    if menu.i18n_key:
        meta["i18nKey"] = menu.i18n_key
    if menu.external_link:
        meta["href"] = menu.external_link
    return {
        "id": str(menu.id),
        "name": menu.name,
        "path": menu.path or f"/{menu.name}",
        "component": component,
        "meta": meta,
        "children": [],
    }


def _menu_to_tree_nodes(menus, parent_id=None):
    nodes = []
    for m in sorted(menus, key=lambda x: (x.order or 0, x.id)):
        if m.parent_id != parent_id:
            continue
        if m.menu_type == "3":
            continue
        node = _menu_to_route(m)
        children = _menu_to_tree_nodes(menus, m.id)
        if children:
            node["children"] = children
        nodes.append(node)
    return nodes


class ConstantRoutesView(APIView):
    def get(self, request):
        # 与前端 elegant-router 生成的静态常量路由保持一致：
        # 单级路由 component 必须是 "layout.blank$view.<name>" 格式
        constants = [
            {
                "name": "403",
                "path": "/403",
                "component": "layout.blank$view.403",
                "meta": {"title": "403", "i18nKey": "route.403", "constant": True, "hideInMenu": True},
            },
            {
                "name": "404",
                "path": "/404",
                "component": "layout.blank$view.404",
                "meta": {"title": "404", "i18nKey": "route.404", "constant": True, "hideInMenu": True},
            },
            {
                "name": "500",
                "path": "/500",
                "component": "layout.blank$view.500",
                "meta": {"title": "500", "i18nKey": "route.500", "constant": True, "hideInMenu": True},
            },
            {
                "name": "login",
                "path": "/login/:module(pwd-login|code-login|register|reset-pwd|bind-wechat)?",
                "component": "layout.blank$view.login",
                "props": True,
                "meta": {"title": "login", "i18nKey": "route.login", "constant": True, "hideInMenu": True},
            },
        ]
        return Response(ok(constants))


class UserRoutesView(APIView):
    @require_auth
    def get(self, request):
        u: User = request.sys_user
        key = user_routes_cache_key(u.id)
        payload = cache.get(key)
        if payload is None:
            payload = self._build_routes(u)
            cache.set(key, payload, _ROUTES_TTL)
        return Response(ok(payload))

    def _build_routes(self, u: User) -> dict:
        role_ids = list(u.roles.values_list("id", flat=True))
        is_super = any(code == "R_SUPER" for code in u.roles.values_list("code", flat=True))

        menu_qs = Menu.objects.filter(
            is_deleted=False, status="1", menu_type__in=["1", "2"]
        ).order_by("order", "id")
        if not is_super:
            # 角色关联菜单 + 所有祖先（保证父目录存在）
            role_menus = Menu.objects.filter(roles__id__in=role_ids, is_deleted=False)
            menu_ids = set(role_menus.values_list("id", flat=True))
            ancestors_ids = set(menu_ids)
            changed = True
            while changed:
                changed = False
                parents = Menu.objects.filter(children__id__in=list(ancestors_ids)).values_list(
                    "id", "parent_id", "is_deleted"
                )
                for pid, ppid, deleted in parents:
                    if deleted:
                        continue
                    if pid not in ancestors_ids:
                        ancestors_ids.add(pid)
                        changed = True
                    if ppid and ppid not in ancestors_ids:
                        ancestors_ids.add(ppid)
                        changed = True
            menu_qs = menu_qs.filter(id__in=list(ancestors_ids))
        menus = list(menu_qs)
        routes = [
            {
                "id": "home",
                "name": "home",
                "path": "/home",
                "component": "layout.base$view.home",
                "meta": {
                    "title": "首页",
                    "i18nKey": "route.home",
                    "icon": "mdi:monitor-dashboard",
                    "order": 1,
                },
                "children": [],
            },
            *_menu_to_tree_nodes(menus),
        ]
        return {"routes": routes, "home": "home"}


class IsRouteExistView(APIView):
    def get(self, request):
        route_name = (request.query_params.get("routeName") or "").strip()
        if not route_name:
            return Response(ok(False))
        in_const = route_name in {"login", "403", "404", "500", "home"}
        in_menu = Menu.objects.filter(name=route_name, is_deleted=False, status="1").exists()
        return Response(ok(in_const or in_menu))
