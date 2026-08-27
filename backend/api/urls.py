from django.urls import path
from . import views

urlpatterns = [
    path("health", views.HealthCheckView.as_view(), name="health"),
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/user-info", views.UserInfoView.as_view(), name="user-info"),
    path("auth/logout", views.LogoutView.as_view(), name="logout"),
    path("route/routes", views.RoutesView.as_view(), name="routes"),
]
