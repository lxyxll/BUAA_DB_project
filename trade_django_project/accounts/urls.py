# accounts/urls.py

from django.urls import path
from .views import (
    register,
    login_view,
    logout_view,
    profile,
    update_profile_view,
    change_password_view,
    admin_user_list_view,
    admin_ban_user_view,
    admin_unban_user_view,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("profile/", profile, name="profile"),
    path("profile/edit/", update_profile_view, name="update_profile"),
    path("password/change/", change_password_view, name="change_password"),

    # 管理员
    path("admin/users/", admin_user_list_view, name="admin_user_list"),
    path("admin/users/<int:user_id>/ban/", admin_ban_user_view),
    path("admin/users/<int:user_id>/unban/", admin_unban_user_view),
]