"""views.auth 子模块聚合。

- account.py  验证码 / 登录 / 登出 / 用户信息 / 健康检查
- route.py    动态路由
"""

from .account import CaptchaView, HealthCheckView, LoginView, LogoutView, UserInfoView
from .route import ConstantRoutesView, IsRouteExistView, UserRoutesView

__all__ = [
    "CaptchaView",
    "HealthCheckView",
    "LoginView",
    "LogoutView",
    "UserInfoView",
    "ConstantRoutesView",
    "UserRoutesView",
    "IsRouteExistView",
]
