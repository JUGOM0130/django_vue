from django.urls import path, include
from rest_framework.routers import DefaultRouter

# シンプルなViewSet
from .views import NodeViewSet, TreeViewSet, ParentChildViewSet, TreeInstanceViewSet,PrefixViewSet
# シンプルではないViewset
from .views import CodeGenerationView,CodeUpdateView,CodeVersionHistoryView,AllCodeVersionHistoryView

router = DefaultRouter()
router.register(r'nodes', NodeViewSet)
router.register(r'trees', TreeViewSet)
router.register(r'parent-child', ParentChildViewSet)
router.register(r'tree-instances', TreeInstanceViewSet)
router.register(r'prefix', PrefixViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-code/', CodeGenerationView.as_view(), name='generate-code'),
    path('update-code/', CodeUpdateView.as_view(), name='update-code'),
    path('code-history/<str:code>/', CodeVersionHistoryView.as_view(), name='code-history'),
    path('all-code-history/', AllCodeVersionHistoryView.as_view(), name='all-code-history'),
]

