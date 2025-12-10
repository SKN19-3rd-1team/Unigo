from django.urls import path
from . import views

app_name = "unigo_app"

urlpatterns = [
    # Pages
    path("", views.home, name="home"),
    path("auth/", views.auth, name="auth"),
    path("logout/", views.logout_view, name="logout"),
    path("chat/", views.chat, name="chat"),
    path("setting/", views.setting, name="setting"),
    # Auth API
    path("api/auth/signup", views.auth_signup, name="auth_signup"),
    path("api/auth/login", views.auth_login, name="auth_login"),
    path("api/auth/logout", views.auth_logout, name="auth_logout"),
    path("api/auth/me", views.auth_me, name="auth_me"),
    path("api/auth/check-email", views.auth_check_email, name="auth_check_email"),
    path(
        "api/auth/check-username", views.auth_check_username, name="auth_check_username"
    ),
    # Setting API
    path("api/setting/check-username", views.check_username, name="check_username"),
    path("api/setting/change-nickname", views.change_nickname, name="change_nickname"),
    path("api/setting/change-password", views.change_password, name="change_password"),
    # Feature API
    path("api/chat", views.chat_api, name="chat_api"),
    path("api/chat/history", views.chat_history, name="chat_history"),
    path("api/chat/reset", views.reset_chat_history, name="reset_chat_history"),
    path("api/onboarding", views.onboarding_api, name="onboarding_api"),
]
