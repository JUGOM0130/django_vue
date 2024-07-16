
# 以下を追加
from django.urls import path
from . import views

urlpatterns = [
    path('',views.tree_view, name="tree")
]
