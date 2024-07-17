
# 以下を追加
from django.urls import path
from . import views

urlpatterns = [
    path('',views.LoginViewClass.as_view(), name="login"),
    path('tree/',views.TreeViewClass.as_view(), name="tree")
]
