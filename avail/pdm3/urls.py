from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NodeViewSet, TreeViewSet, ParentChildViewSet, TreeInstanceViewSet

router = DefaultRouter()
router.register(r'nodes', NodeViewSet)
router.register(r'trees', TreeViewSet)
router.register(r'parent-child', ParentChildViewSet)
router.register(r'tree-instances', TreeInstanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
