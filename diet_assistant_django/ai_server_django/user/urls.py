"""user应用的URL配置：二级路由"""

from django.urls import path
from . import views

# 二级路由
urlpatterns = [
    # 用户注册接口
    path("reg/", views.register, name="register"),
    # 用户登录接口
    path("login/", views.login, name="login"),
]

