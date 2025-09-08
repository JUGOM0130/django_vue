# urls.py
"""
コード管理システムのURL設定
REST APIエンドポイントのルーティングを定義
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PrefixViewSet,
    CodeViewSet,
    CodeVersionViewSet,
    CodeChangeLogViewSet,
    CodeMetadataViewSet
)


class CodeAPIRouter:
    """
    コード管理システム用のAPIルーター
    
    機能説明:
    - ViewSetをAPIエンドポイントとして自動登録
    - REST APIの標準的なURL構造を提供
    """
    
    def __init__(self, version='v1'):
        self.router = DefaultRouter()
        self.version = version
        self.register_endpoints()

    def register_endpoints(self):
        """
        ViewSetをAPIエンドポイントとして登録
        
        機能説明:
        各ViewSetを適切なURLパターンで登録する
        
        登録されるエンドポイント:
        - prefixes/ → PrefixViewSet
        - codes/ → CodeViewSet  
        - code-versions/ → CodeVersionViewSet
        - code-change-logs/ → CodeChangeLogViewSet
        - code-metadata/ → CodeMetadataViewSet
        """
        
        # Code関連のエンドポイント登録
        code_endpoints = {
            # プレフィックス管理
            # GET    /api/prefixes/                    - プレフィックス一覧取得
            # POST   /api/prefixes/                    - プレフィックス作成
            # GET    /api/prefixes/{id}/               - プレフィックス詳細取得
            # PUT    /api/prefixes/{id}/               - プレフィックス更新
            # DELETE /api/prefixes/{id}/               - プレフィックス削除
            # POST   /api/prefixes/{id}/generate_code/ - コード生成
            # GET    /api/prefixes/{id}/preview_code/  - 次のコードプレビュー
            'prefixes': PrefixViewSet,
            
            # コード管理
            # GET    /api/codes/                       - コード一覧取得
            # POST   /api/codes/                       - コード作成
            # GET    /api/codes/{id}/                  - コード詳細取得
            # PUT    /api/codes/{id}/                  - コード更新
            # DELETE /api/codes/{id}/                  - コード削除
            # GET    /api/codes/{id}/versions/         - コードのバージョン一覧取得
            # GET    /api/codes/{id}/change_history/   - コードの変更履歴取得
            'codes': CodeViewSet,
            
            # コードバージョン管理
            # GET    /api/code-versions/               - バージョン一覧取得
            # POST   /api/code-versions/               - バージョン作成
            # GET    /api/code-versions/{id}/          - バージョン詳細取得
            # PUT    /api/code-versions/{id}/          - バージョン更新
            # DELETE /api/code-versions/{id}/          - バージョン削除
            # POST   /api/code-versions/{id}/activate/ - バージョンアクティブ化
            # POST   /api/code-versions/{id}/archive/  - バージョンアーカイブ
            'code-versions': CodeVersionViewSet,
            
            # コード変更ログ（読み取り専用）
            # GET    /api/code-change-logs/            - 変更ログ一覧取得
            # GET    /api/code-change-logs/{id}/       - 変更ログ詳細取得
            'code-change-logs': CodeChangeLogViewSet,
            
            # コードメタデータ管理
            # GET    /api/code-metadata/               - メタデータ一覧取得
            # POST   /api/code-metadata/               - メタデータ作成
            # GET    /api/code-metadata/{id}/          - メタデータ詳細取得
            # PUT    /api/code-metadata/{id}/          - メタデータ更新
            # DELETE /api/code-metadata/{id}/          - メタデータ削除
            # POST   /api/code-metadata/{id}/add_tag/  - タグ追加
            'code-metadata': CodeMetadataViewSet,
        }

        # エンドポイントの登録
        for path, viewset in code_endpoints.items():
            self.router.register(path, viewset)

    @property
    def urls(self):
        """
        ルーターのURLパターンを返す
        
        Returns:
            list: URLパターンのリスト
        """
        return self.router.urls

    def get_api_endpoints(self):
        """
        APIエンドポイントの一覧を取得
        
        機能説明:
        ドキュメント生成やデバッグ用にエンドポイント一覧を取得
        
        Returns:
            dict: エンドポイントの辞書
        """
        endpoints = {}
        for url_pattern in self.router.urls:
            if hasattr(url_pattern, 'pattern'):
                endpoints[str(url_pattern.pattern)] = url_pattern.callback
        return endpoints


# APIルーターのインスタンス作成
api_router = CodeAPIRouter(version='v1')

# URLパターンの定義
urlpatterns = [
    # ==========================================
    # API エンドポイント
    # ==========================================
    
    # メインAPI（全てのエンドポイント）
    path('api/', include(api_router.urls)),
]