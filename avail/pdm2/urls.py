# 以下を追加
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodeHeaderView,CodeView,NodeView,TreeView,ParentChildView
from . import views

router = DefaultRouter()
router.register('codeheader', CodeHeaderView)
router.register('code',CodeView)
router.register('node',NodeView)
router.register('tree',TreeView)
router.register('parent_child',ParentChildView)

urlpatterns = [
    path('', include(router.urls)),
]
