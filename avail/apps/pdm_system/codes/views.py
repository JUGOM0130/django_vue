# views.py
"""
コード管理システムのViewSet
REST APIのエンドポイントとビジネスロジックを提供
"""
from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata
)
from .serializers import (
    PrefixSerializer, CodeSerializer, CodeVersionSerializer,
    CodeChangeLogSerializer, CodeMetadataSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """
    標準的なページネーション設定
    
    機能説明:
    - デフォルトのページサイズを20件に設定
    - 最大ページサイズを100件に制限
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PrefixViewSet(viewsets.ModelViewSet):
    """
    プレフィックス管理ViewSet
    
    機能説明:
    - プレフィックスのCRUD操作を提供
    - コード生成機能
    - 次のコードのプレビュー機能
    
    APIエンドポイント:
    - GET    /api/prefixes/                    - プレフィックス一覧取得
    - POST   /api/prefixes/                    - プレフィックス作成
    - GET    /api/prefixes/{id}/               - プレフィックス詳細取得
    - PUT    /api/prefixes/{id}/               - プレフィックス更新
    - DELETE /api/prefixes/{id}/               - プレフィックス削除
    - POST   /api/prefixes/{id}/generate_code/ - コード生成
    - GET    /api/prefixes/{id}/preview_code/  - 次のコードプレビュー
    """
    queryset = Prefix.objects.all().order_by('-created_at')
    serializer_class = PrefixSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def generate_code(self, request, pk=None):
        """
        新しいコード生成
        
        機能説明:
        指定されたプレフィックスを使用して新しいコードを生成し、
        コードバージョンも同時に作成する
        
        APIエンドポイント: POST /api/prefixes/{id}/generate_code/
        
        リクエストパラメータ:
        {
            "name": "サンプルコード",           # (required, str) コード名
            "description": "コードの説明",      # (optional, str) コードの説明
            "version": "1.0",                 # (optional, str) 初期バージョン
            "status": "draft"                 # (optional, str) 初期ステータス
        }
        
        レスポンス:
        {
            "success": true,
            "message": "コードが正常に生成されました",
            "data": {
                "code": {コード情報},
                "version": {バージョン情報},
                "generated_code": "TEST-A0005Z000"
            }
        }
        """
        try:
            prefix = self.get_object()
            
            # リクエストデータの取得
            name = request.data.get('name', '').strip()
            if not name:
                return Response({
                    'success': False,
                    'message': 'コード名は必須です'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            description = request.data.get('description', '')
            version_number = request.data.get('version', '1.0')
            version_status = request.data.get('status', 'draft')
            
            # トランザクション内でコードとバージョンを作成
            with transaction.atomic():
                # コード生成
                generated_code = prefix.generate_next_code()
                
                # Codeオブジェクト作成
                code_obj = Code.objects.create(
                    prefix=prefix,
                    code=generated_code,
                    name=name,
                    description=description
                )
                
                # CodeVersionオブジェクト作成
                version_obj = CodeVersion.objects.create(
                    code=code_obj,
                    version=version_number,
                    status=version_status,
                    description='初期バージョン',
                    effective_date=timezone.now()
                )
                
                # 変更ログの記録
                CodeChangeLog.objects.create(
                    code=code_obj,
                    action='create',
                    new_value={
                        'code': generated_code,
                        'name': name,
                        'version': version_number
                    },
                    change_reason='新規コード生成'
                )
            
            # レスポンスデータの構築
            code_serializer = CodeSerializer(code_obj)
            version_serializer = CodeVersionSerializer(version_obj)
            
            return Response({
                'success': True,
                'message': 'コードが正常に生成されました',
                'data': {
                    'code': code_serializer.data,
                    'version': version_serializer.data,
                    'generated_code': generated_code
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'コード生成に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def preview_code(self, request, pk=None):
        """
        次のコードプレビュー
        
        機能説明:
        プレフィックスから生成される次のコードを、実際に生成せずにプレビュー表示する
        
        APIエンドポイント: GET /api/prefixes/{id}/preview_code/
        
        レスポンス:
        {
            "success": true,
            "message": "プレビューコードを取得しました",
            "data": {
                "prefix_name": "TEST",
                "code_type": "1",
                "current_next_number": 5,
                "preview_code": "TEST-A0005Z000"
            }
        }
        """
        try:
            prefix = self.get_object()
            
            # プレビューコード生成（実際のnext_numberは更新しない）
            format_map = {
                '1': 'A{:04d}Z000',    # 組
                '2': 'AA{:04d}Z000',   # 部品
                '3': 'A{:04d}Z00'      # 購入品
            }
            
            code_format = format_map.get(prefix.code_type)
            if not code_format:
                return Response({
                    'success': False,
                    'message': f'無効なコードタイプ: {prefix.code_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            code_part = code_format.format(prefix.next_number)
            preview_code = f"{prefix.name}-{code_part}"
            
            return Response({
                'success': True,
                'message': 'プレビューコードを取得しました',
                'data': {
                    'prefix_name': prefix.name,
                    'code_type': prefix.code_type,
                    'current_next_number': prefix.next_number,
                    'preview_code': preview_code
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'コードプレビューの取得に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CodeViewSet(viewsets.ModelViewSet):
    """
    コード管理ViewSet
    
    機能説明:
    - コードのCRUD操作を提供
    - バージョン管理機能
    - 履歴検索機能
    
    APIエンドポイント:
    - GET    /api/codes/                       - コード一覧取得
    - POST   /api/codes/                       - コード作成
    - GET    /api/codes/{id}/                  - コード詳細取得
    - PUT    /api/codes/{id}/                  - コード更新
    - DELETE /api/codes/{id}/                  - コード削除
    - GET    /api/codes/{id}/versions/         - コードのバージョン一覧取得
    - GET    /api/codes/{id}/change_history/   - コードの変更履歴取得
    """
    queryset = Code.objects.select_related('prefix').prefetch_related('versions', 'change_logs').order_by('-created_at')
    serializer_class = CodeSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """
        コードのバージョン一覧取得
        
        機能説明:
        指定されたコードに関連するすべてのバージョン情報を取得
        
        APIエンドポイント: GET /api/codes/{id}/versions/
        
        リクエストパラメータ:
        - status (str, optional): ステータスでフィルター
        
        レスポンス:
        {
            "success": true,
            "message": "バージョン一覧を取得しました",
            "data": [バージョン情報のリスト]
        }
        """
        try:
            code = self.get_object()
            versions = code.versions.all().order_by('-created_at')
            
            # ステータスフィルター
            status_filter = request.query_params.get('status')
            if status_filter:
                versions = versions.filter(status=status_filter)
            
            serializer = CodeVersionSerializer(versions, many=True)
            
            return Response({
                'success': True,
                'message': 'バージョン一覧を取得しました',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'バージョン一覧の取得に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def change_history(self, request, pk=None):
        """
        コードの変更履歴取得
        
        機能説明:
        指定されたコードの変更履歴を時系列順で取得
        
        APIエンドポイント: GET /api/codes/{id}/change_history/
        
        リクエストパラメータ:
        - action (str, optional): 操作タイプでフィルター
        - limit (int, optional): 取得件数制限 (最大: 100)
        
        レスポンス:
        {
            "success": true,
            "message": "変更履歴を取得しました",
            "data": [変更履歴のリスト]
        }
        """
        try:
            code = self.get_object()
            
            # 変更履歴取得
            change_logs = code.change_logs.all().order_by('-timestamp')
            
            # アクションフィルター
            action_filter = request.query_params.get('action')
            if action_filter:
                change_logs = change_logs.filter(action=action_filter)
            
            # 件数制限
            limit = request.query_params.get('limit')
            if limit:
                try:
                    limit = int(limit)
                    if limit > 100:
                        limit = 100
                    change_logs = change_logs[:limit]
                except ValueError:
                    pass
            
            serializer = CodeChangeLogSerializer(change_logs, many=True)
            
            return Response({
                'success': True,
                'message': '変更履歴を取得しました',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': '変更履歴の取得に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CodeVersionViewSet(viewsets.ModelViewSet):
    """
    コードバージョン管理ViewSet
    
    機能説明:
    - コードバージョンのCRUD操作を提供
    - バージョンのアクティブ化機能
    - ステータス変更機能
    
    APIエンドポイント:
    - GET    /api/code-versions/                  - バージョン一覧取得
    - POST   /api/code-versions/                  - バージョン作成
    - GET    /api/code-versions/{id}/             - バージョン詳細取得
    - PUT    /api/code-versions/{id}/             - バージョン更新
    - DELETE /api/code-versions/{id}/             - バージョン削除
    - POST   /api/code-versions/{id}/activate/    - バージョンアクティブ化
    - POST   /api/code-versions/{id}/archive/     - バージョンアーカイブ
    """
    queryset = CodeVersion.objects.select_related('code', 'code__prefix').order_by('-created_at')
    serializer_class = CodeVersionSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        コードバージョンのアクティブ化
        
        機能説明:
        指定されたバージョンをアクティブ状態にし、
        同じコードの他のバージョンを無効状態に変更
        
        APIエンドポイント: POST /api/code-versions/{id}/activate/
        
        リクエストパラメータ:
        {
            "reason": "バージョンアップのため"    # (optional, str) アクティブ化理由
        }
        
        レスポンス:
        {
            "success": true,
            "message": "バージョン 2.0 がアクティブになりました",
            "data": {アクティブ化されたバージョン情報}
        }
        """
        try:
            version = self.get_object()
            reason = request.data.get('reason', 'ステータス変更')
            
            # 既にアクティブかチェック
            if version.status == 'active':
                return Response({
                    'success': False,
                    'message': 'このバージョンは既にアクティブです'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # 同じコードの他のバージョンを無効化
                CodeVersion.objects.filter(
                    code=version.code,
                    status='active'
                ).update(status='inactive')
                
                # 指定バージョンをアクティブ化
                version.status = 'active'
                version.effective_date = timezone.now()
                version.save()
                
                # 変更ログ記録
                CodeChangeLog.objects.create(
                    code=version.code,
                    action='update',
                    old_value={'status': 'inactive'},
                    new_value={'status': 'active', 'version': version.version},
                    change_reason=f'バージョン {version.version} をアクティブ化: {reason}'
                )
            
            serializer = self.get_serializer(version)
            
            return Response({
                'success': True,
                'message': f'バージョン {version.version} がアクティブになりました',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'バージョンのアクティブ化に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        コードバージョンのアーカイブ
        
        機能説明:
        指定されたバージョンをアーカイブ状態に変更
        
        APIエンドポイント: POST /api/code-versions/{id}/archive/
        
        リクエストパラメータ:
        {
            "reason": "使用終了のため"    # (optional, str) アーカイブ理由
        }
        
        レスポンス:
        {
            "success": true,
            "message": "バージョンがアーカイブされました",
            "data": {アーカイブされたバージョン情報}
        }
        """
        try:
            version = self.get_object()
            reason = request.data.get('reason', 'アーカイブ')
            
            # アクティブなバージョンはアーカイブできない
            if version.status == 'active':
                return Response({
                    'success': False,
                    'message': 'アクティブなバージョンはアーカイブできません'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            old_status = version.status
            version.status = 'archived'
            version.save()
            
            # 変更ログ記録
            CodeChangeLog.objects.create(
                code=version.code,
                action='update',
                old_value={'status': old_status},
                new_value={'status': 'archived'},
                change_reason=f'バージョン {version.version} をアーカイブ: {reason}'
            )
            
            serializer = self.get_serializer(version)
            
            return Response({
                'success': True,
                'message': 'バージョンがアーカイブされました',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'バージョンのアーカイブに失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CodeChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    コード変更ログViewSet（読み取り専用）
    
    機能説明:
    - コードの変更履歴を読み取り専用で提供
    - 変更ログの検索・フィルター機能
    
    APIエンドポイント:
    - GET    /api/code-change-logs/             - 変更ログ一覧取得
    - GET    /api/code-change-logs/{id}/        - 変更ログ詳細取得
    """
    queryset = CodeChangeLog.objects.select_related('code', 'code__prefix').order_by('-timestamp')
    serializer_class = CodeChangeLogSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        QuerySetのカスタマイズ
        
        機能説明:
        フィルタリング条件に基づいてQuerySetを調整
        
        Returns:
            QuerySet: フィルタリングされたCodeChangeLogのQuerySet
        """
        queryset = super().get_queryset()
        
        # コードIDでフィルター
        code_id = self.request.query_params.get('code_id')
        if code_id:
            queryset = queryset.filter(code_id=code_id)
        
        # アクションタイプでフィルター
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset


class CodeMetadataViewSet(viewsets.ModelViewSet):
    """
    コードメタデータ管理ViewSet
    
    機能説明:
    - コードの追加情報をCRUD操作で管理
    - カスタムフィールドの動的管理
    
    APIエンドポイント:
    - GET    /api/code-metadata/               - メタデータ一覧取得
    - POST   /api/code-metadata/               - メタデータ作成
    - GET    /api/code-metadata/{id}/          - メタデータ詳細取得
    - PUT    /api/code-metadata/{id}/          - メタデータ更新
    - DELETE /api/code-metadata/{id}/          - メタデータ削除
    - POST   /api/code-metadata/{id}/add_tag/  - タグ追加
    """
    queryset = CodeMetadata.objects.select_related('code').order_by('-created_at')
    serializer_class = CodeMetadataSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """
        タグ追加
        
        機能説明:
        既存のメタデータに新しいタグを追加
        
        APIエンドポイント: POST /api/code-metadata/{id}/add_tag/
        
        リクエストパラメータ:
        {
            "tag": "new_tag"    # (required, str) 追加するタグ
        }
        
        レスポンス:
        {
            "success": true,
            "message": "タグが追加されました",
            "data": {更新後のメタデータ情報}
        }
        """
        try:
            metadata = self.get_object()
            new_tag = request.data.get('tag', '').strip()
            
            if not new_tag:
                return Response({
                    'success': False,
                    'message': 'タグは必須です'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 既存のタグリストに追加
            if new_tag not in metadata.tags:
                metadata.tags.append(new_tag)
                metadata.save()
            
            serializer = self.get_serializer(metadata)
            
            return Response({
                'success': True,
                'message': 'タグが追加されました',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'タグの追加に失敗しました',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)