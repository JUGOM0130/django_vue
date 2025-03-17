from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    # Code関連のViewSet
    PrefixViewSet,
    CodeViewSet,
    CodeVersionViewSet,
    CodeChangeLogViewSet,
    CodeMetadataViewSet,
    # Tree関連のViewSet
    TreeViewSet,
    TreeStructureViewSet,
    TreeVersionViewSet,
    TreeCodeQuantityViewSet,
    TreeChangeLogViewSet
)

class APIRouter:
    def __init__(self, version='v1'):
        self.router = DefaultRouter()
        self.version = version
        self.register_endpoints()

    def register_endpoints(self):
        # Code関連のエンドポイント
        code_endpoints = {
            'prefix': PrefixViewSet,
            'code': CodeViewSet,
            'code-version': CodeVersionViewSet,
            'code-change-log': CodeChangeLogViewSet,
            'code-metadata': CodeMetadataViewSet,
        }

        # Tree関連のエンドポイント
        tree_endpoints = {
            'tree': TreeViewSet,
            'tree-structure': TreeStructureViewSet,
            'tree-version': TreeVersionViewSet,
            'tree-code-quantity': TreeCodeQuantityViewSet,
            'tree-change-log': TreeChangeLogViewSet,
        }

        # エンドポイントの登録
        for path, viewset in {**code_endpoints, **tree_endpoints}.items():
            self.router.register(f'{path}', viewset)

    @property
    def urls(self):
        return self.router.urls

# APIルーターのインスタンス作成
api_router = APIRouter(version='v1')

# URLパターンの定義
urlpatterns = [
    path('', include(api_router.urls)),
]