from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from tasks.views import index, register

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/tasks/", include("tasks.urls")),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("register/", register, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", index, name="index"),
]