# 以下を追加
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CodeHeaderView,CodeView

router = DefaultRouter()
router.register('codeheader', CodeHeaderView)
router.register('code',CodeView)

urlpatterns = [
    path('', include(router.urls)),
]
