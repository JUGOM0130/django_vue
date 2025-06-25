# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

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
    TreeChangeLogViewSet,
    TreeNodeViewSet,
    SharedStructureGroupViewSet
)

# ==========================================
# システム情報・ヘルスチェック用のView
# ==========================================

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import datetime


class SystemInfoView(APIView):
    """
    システム情報取得API
    APIエンドポイント: GET /api/system/info/
    
    機能:
    - システムの基本情報を取得
    - API バージョン情報
    - 利用可能なエンドポイント一覧
    """
    
    def get(self, request):
        """
        システム情報を取得
        
        レスポンス:
        - system_name: システム名
        - version: APIバージョン
        - timestamp: レスポンス生成日時
        - available_endpoints: 利用可能なエンドポイント
        - code_types: 利用可能なコードタイプ
        - sharing_types: 構造共有タイプ
        """
        
        # 利用可能なエンドポイントを取得
        available_endpoints = {
            'code_management': [
                'GET    /api/prefixes/ - プレフィックス一覧取得',
                'POST   /api/prefixes/ - プレフィックス作成',
                'POST   /api/prefixes/{id}/generate_code/ - コード生成',
                'GET    /api/codes/ - コード一覧取得',
                'POST   /api/codes/ - コード作成',
                'GET    /api/code-versions/ - バージョン一覧取得',
                'POST   /api/code-versions/{id}/activate/ - バージョンアクティブ化'
            ],
            'tree_management': [
                'GET    /api/trees/ - ツリー一覧取得',
                'POST   /api/trees/ - ツリー作成',
                'GET    /api/trees/{id}/structure/ - ツリー構造取得',
                'POST   /api/trees/{id}/add_structure/ - 構造追加',
                'POST   /api/trees/{id}/share_structure/ - 構造共有',
                'POST   /api/tree-structures/{id}/update_node/ - ノード更新',
                'POST   /api/tree-structures/{id}/move_structure/ - 構造移動'
            ],
            'monitoring': [
                'GET    /api/code-change-logs/ - コード変更ログ',
                'GET    /api/tree-change-logs/ - ツリー変更ログ',
                'GET    /api/shared-structure-groups/ - 共有グループ一覧'
            ]
        }
        
        return Response({
            'success': True,
            'data': {
                'system_name': '共有ツリー構造システム',
                'version': 'v1.0',
                'timestamp': datetime.datetime.now().isoformat(),
                'available_endpoints': available_endpoints,
                'code_types': {
                    '1': '組',
                    '2': '部品',
                    '3': '購入品'
                },
                'sharing_types': {
                    'independent': '独立構造',
                    'shared': '共有構造'
                },
                'version_statuses': {
                    'draft': '下書き',
                    'active': '有効',
                    'inactive': '無効',
                    'archived': 'アーカイブ'
                }
            }
        })


class HealthCheckView(APIView):
    """
    ヘルスチェックAPI
    APIエンドポイント: GET /api/health/
    
    機能:
    - システムの稼働状況を確認
    - データベース接続状況
    - 基本統計情報
    """
    
    def get(self, request):
        """
        システムのヘルスチェックを実行
        
        レスポンス:
        - status: システム状態
        - timestamp: チェック実行日時
        - database: データベース接続状況
        - statistics: 基本統計情報
        """
        
        try:
            # データベース接続テスト
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            database_status = 'healthy'
            
            # 基本統計情報を取得
            try:
                from .models import Tree, TreeNode, TreeStructure, SharedStructureGroup, Code
                
                statistics = {
                    'total_trees': Tree.objects.count(),
                    'total_nodes': TreeNode.objects.count(),
                    'total_structures': TreeStructure.objects.count(),
                    'shared_groups': SharedStructureGroup.objects.count(),
                    'shared_structures': TreeStructure.objects.filter(sharing_type='shared').count(),
                    'total_codes': Code.objects.count()
                }
                
            except Exception as e:
                statistics = {'error': f'統計情報取得エラー: {str(e)}'}
            
        except Exception as e:
            database_status = f'error: {str(e)}'
            statistics = {'error': 'データベース接続エラーのため統計情報を取得できません'}
        
        return Response({
            'success': True,
            'data': {
                'status': 'healthy' if database_status == 'healthy' else 'unhealthy',
                'timestamp': datetime.datetime.now().isoformat(),
                'database': database_status,
                'statistics': statistics
            }
        })


# ==========================================
# 追加設定とカスタマイズ
# ==========================================

# カスタムエラーハンドラー（必要に応じて）
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    """
    カスタム例外ハンドラー
    すべてのAPI例外を統一フォーマットで返す
    """
    # デフォルトの例外ハンドラーを呼び出し
    response = exception_handler(exc, context)

    if response is not None:
        # カスタムレスポンス形式に変換
        custom_response_data = {
            'success': False,
            'message': str(exc),
            'error_code': response.status_code,
            'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
        }
        response.data = custom_response_data

    return response



class SharedTreeAPIRouter:
    """
    共有ツリー構造システムのAPIルーター
    APIエンドポイントの一元管理と構成を行う
    """
    
    def __init__(self, version='v1'):
        self.router = DefaultRouter()
        self.version = version
        self.register_endpoints()

    def register_endpoints(self):
        """
        全てのAPIエンドポイントを登録
        機能別にグループ化してエンドポイントを定義
        """
        
        # ==========================================
        # Code関連のエンドポイント
        # ==========================================
        code_endpoints = {
            # プレフィックス管理
            # GET    /api/prefixes/                     - プレフィックス一覧取得
            # POST   /api/prefixes/                     - プレフィックス作成
            # GET    /api/prefixes/{id}/                - プレフィックス詳細取得
            # PUT    /api/prefixes/{id}/                - プレフィックス更新
            # DELETE /api/prefixes/{id}/                - プレフィックス削除
            # POST   /api/prefixes/{id}/generate_code/  - コード生成
            # GET    /api/prefixes/{id}/preview_next_code/ - 次のコードプレビュー
            'prefixes': PrefixViewSet,
            
            # コード管理
            # GET    /api/codes/                        - コード一覧取得
            # POST   /api/codes/                        - コード作成
            # GET    /api/codes/{id}/                   - コード詳細取得
            # PUT    /api/codes/{id}/                   - コード更新
            # DELETE /api/codes/{id}/                   - コード削除
            'codes': CodeViewSet,
            
            # コードバージョン管理
            # GET    /api/code-versions/                - コードバージョン一覧取得
            # POST   /api/code-versions/                - コードバージョン作成
            # GET    /api/code-versions/{id}/           - コードバージョン詳細取得
            # PUT    /api/code-versions/{id}/           - コードバージョン更新
            # DELETE /api/code-versions/{id}/           - コードバージョン削除
            # POST   /api/code-versions/{id}/activate/  - バージョンのアクティブ化
            'code-versions': CodeVersionViewSet,
            
            # コード変更ログ（読み取り専用）
            # GET    /api/code-change-logs/             - コード変更ログ一覧取得
            # GET    /api/code-change-logs/{id}/        - コード変更ログ詳細取得
            'code-change-logs': CodeChangeLogViewSet,
            
            # コードメタデータ管理
            # GET    /api/code-metadata/                - コードメタデータ一覧取得
            # POST   /api/code-metadata/                - コードメタデータ作成
            # GET    /api/code-metadata/{id}/           - コードメタデータ詳細取得
            # PUT    /api/code-metadata/{id}/           - コードメタデータ更新
            # DELETE /api/code-metadata/{id}/           - コードメタデータ削除
            'code-metadata': CodeMetadataViewSet,
        }

        # ==========================================
        # Tree関連のエンドポイント
        # ==========================================
        tree_endpoints = {
            # ツリー管理
            # GET    /api/trees/                        - ツリー一覧取得
            # POST   /api/trees/                        - ツリー作成
            # GET    /api/trees/{id}/                   - ツリー詳細取得
            # PUT    /api/trees/{id}/                   - ツリー更新
            # DELETE /api/trees/{id}/                   - ツリー削除
            # GET    /api/trees/{id}/structure/         - ツリー構造取得
            # POST   /api/trees/{id}/add_structure/     - 構造追加
            # POST   /api/trees/{id}/share_structure/   - 構造共有
            'trees': TreeViewSet,
            
            # ツリー構造管理
            # GET    /api/tree-structures/              - ツリー構造一覧取得
            # POST   /api/tree-structures/              - ツリー構造作成
            # GET    /api/tree-structures/{id}/         - ツリー構造詳細取得
            # PUT    /api/tree-structures/{id}/         - ツリー構造更新
            # DELETE /api/tree-structures/{id}/         - ツリー構造削除
            # POST   /api/tree-structures/{id}/update_node/ - ノード情報更新
            # POST   /api/tree-structures/{id}/move_structure/ - 構造移動
            'tree-structures': TreeStructureViewSet,
            
            # ツリーノード管理
            # GET    /api/tree-nodes/                   - ツリーノード一覧取得
            # POST   /api/tree-nodes/                   - ツリーノード作成
            # GET    /api/tree-nodes/{id}/              - ツリーノード詳細取得
            # PUT    /api/tree-nodes/{id}/              - ツリーノード更新
            # DELETE /api/tree-nodes/{id}/              - ツリーノード削除
            'tree-nodes': TreeNodeViewSet,
            
            # 共有構造グループ管理（読み取り専用）
            # GET    /api/shared-structure-groups/      - 共有構造グループ一覧取得
            # GET    /api/shared-structure-groups/{id}/ - 共有構造グループ詳細取得
            # GET    /api/shared-structure-groups/{id}/participating_trees/ - 参加ツリー取得
            'shared-structure-groups': SharedStructureGroupViewSet,
            
            # ツリーバージョン管理
            # GET    /api/tree-versions/                - ツリーバージョン一覧取得
            # POST   /api/tree-versions/                - ツリーバージョン作成
            # GET    /api/tree-versions/{id}/           - ツリーバージョン詳細取得
            # PUT    /api/tree-versions/{id}/           - ツリーバージョン更新
            # DELETE /api/tree-versions/{id}/           - ツリーバージョン削除
            'tree-versions': TreeVersionViewSet,
            
            # ツリーコード数量管理
            # GET    /api/tree-code-quantities/         - ツリーコード数量一覧取得
            # POST   /api/tree-code-quantities/         - ツリーコード数量作成
            # GET    /api/tree-code-quantities/{id}/    - ツリーコード数量詳細取得
            # PUT    /api/tree-code-quantities/{id}/    - ツリーコード数量更新
            # DELETE /api/tree-code-quantities/{id}/    - ツリーコード数量削除
            'tree-code-quantities': TreeCodeQuantityViewSet,
            
            # ツリー変更ログ（読み取り専用）
            # GET    /api/tree-change-logs/             - ツリー変更ログ一覧取得
            # GET    /api/tree-change-logs/{id}/        - ツリー変更ログ詳細取得
            'tree-change-logs': TreeChangeLogViewSet,
        }

        # エンドポイントの登録
        for path, viewset in {**code_endpoints, **tree_endpoints}.items():
            self.router.register(path, viewset)

    @property
    def urls(self):
        """
        ルーターのURLパターンを返す
        """
        return self.router.urls

    def get_api_endpoints(self):
        """
        APIエンドポイントの一覧を取得
        ドキュメント生成やデバッグ用
        """
        endpoints = {}
        for url_pattern in self.router.urls:
            if hasattr(url_pattern, 'pattern'):
                endpoints[str(url_pattern.pattern)] = url_pattern.callback
        return endpoints


# APIルーターのインスタンス作成
api_router = SharedTreeAPIRouter(version='v1')

# URLパターンの定義
urlpatterns = [
    # ==========================================
    # API エンドポイント
    # ==========================================
    
    # メインAPI（全てのエンドポイント）
    path('api/', include(api_router.urls)),
    
    # ==========================================
    # API ドキュメント
    # ==========================================
    
    # API ドキュメント（Django REST Framework提供）
    path('api/docs/', include_docs_urls(title='共有ツリー構造システム API')),
    
    # ==========================================
    # ヘルスチェック・メタデータ
    # ==========================================
    
    # システム情報取得
    path('api/system/info/', SystemInfoView.as_view(), name='system_info'),
    
    # ヘルスチェック
    path('api/health/', HealthCheckView.as_view(), name='health_check'),
]


