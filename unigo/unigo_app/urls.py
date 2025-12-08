from django.urls import path
from . import views

app_name = "unigo_app"

urlpatterns = [
    # Pages
    path("", views.home, name="home"),
    path("auth/", views.auth, name="auth"),
    path("chat/", views.chat, name="chat"),
    path("setting/", views.setting, name="setting"),

    # Auth API
    path("api/auth/signup", views.auth_signup, name="auth_signup"),
    path("api/auth/login", views.auth_login, name="auth_login"),
    path("api/auth/logout", views.auth_logout, name="auth_logout"),
    path("api/auth/me", views.auth_me, name="auth_me"),

    # Feature API
    path("api/chat", views.chat_api, name="chat_api"),
    path("api/onboarding", views.onboarding_api, name="onboarding_api"),
]
