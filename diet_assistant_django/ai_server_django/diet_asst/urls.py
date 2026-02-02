"""diet_asst 应用的 URL配置（二级路由）"""
from django.urls import path
from . import views

# 二级路由
urlpatterns = [
    # 助手聊天接口
    path("ai/", views.assistant, name="assistant"),
    # 上传文件接口
    path("upload/", views.uploadfile, name="uploadfile"),
    # 对话历史记录接口
    path("history/", views.history, name="history"),
    # 获取历史对话接口
    path("continue/", views.continue_history, name="continue"),
    # 删除某条对话记录接口
    path("delTheme/", views.del_theme, name="delTheme"),
]
