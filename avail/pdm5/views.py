# views.py
import logging
from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata,
    Tree, TreeNode, TreeStructure, TreeVersion, TreeCodeQuantity, 
    TreeChangeLog, SharedStructureGroup
)
from .serializers import (
    PrefixSerializer, CodeSerializer, CodeVersionSerializer, 
    CodeChangeLogSerializer, CodeMetadataSerializer,
    TreeSerializer, TreeNodeSerializer, TreeStructureSerializer,
    TreeStructureHierarchySerializer, TreeVersionSerializer,
    TreeCodeQuantitySerializer, TreeChangeLogSerializer,
    SharedStructureGroupSerializer, TreeStructureCreateSerializer,
    TreeStructureShareSerializer
)

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    """
    標準的なページネーション設定
    順序付けされていないQuerySetに対する警告を回避
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def paginate_queryset(self, queryset, request, view=None):
        """
        QuerySetが順序付けされていない場合、デフォルトの順序付けを適用
        """
        # QuerySetが順序付けされていない場合のチェック
        if not queryset.ordered:
            # モデルにcreated_atフィールドがある場合は-created_atで順序付け
            if hasattr(queryset.model, 'created_at'):
                queryset = queryset.order_by('-created_at')
            # created_atがない場合はupdated_atで順序付け
            elif hasattr(queryset.model, 'updated_at'):
                queryset = queryset.order_by('-updated_at')
            # どちらもない場合はidで順序付け
            else:
                queryset = queryset.order_by('-id')
        
        return super().paginate_queryset(queryset, request, view)


# ========================================
# Code関連のViewSet
# ========================================

class PrefixViewSet(viewsets.ModelViewSet):
    """
    プレフィックス管理ViewSet
    APIエンドポイント: /api/prefixes/
    
    機能:
    - プレフィックスのCRUD操作
    - コード生成機能
    - 次のコードのプレビュー機能
    """
    queryset = Prefix.objects.all().order_by('-created_at')  # 明示的な順序付けを追加
    serializer_class = PrefixSerializer
    pagination_class = StandardResultsSetPagination
    
    def list(self, request, *args, **kwargs):
        """
        プレフィックス一覧取得
        URL: GET /api/prefixes/
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # ページネーション処理
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': f"プレフィックス一覧を取得しました（{len(serializer.data)}件）",
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"プレフィックス一覧取得中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        プレフィックス作成
        URL: POST /api/prefixes/
        
        リクエストパラメータ:
        - name: プレフィックス名（必須）
        - code_type: コードタイプ（必須、'1'=組, '2'=部品, '3'=購入品）
        - next_number: 次の番号（オプション、デフォルト=1）
        
        レスポンス:
        - success: 成功フラグ
        - message: 結果メッセージ
        - data: 作成されたプレフィックス情報
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            prefix = serializer.save()
            
            return Response({
                'success': True,
                'message': f"プレフィックス「{prefix.name}」を作成しました",
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"プレフィックス作成中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def generate_code(self, request, pk=None):
        """
        指定されたPrefixのIDを使用して新しいコードとバージョンを生成する
        URL: POST /api/prefixes/{prefix_id}/generate_code/
        
        リクエストパラメータ:
        - name: コード名（必須）
        - description: 説明（オプション）
        - status: ステータス（オプション、デフォルトは'draft'）
        
        レスポンス:
        - success: 成功フラグ
        - message: 結果メッセージ
        - data: 生成されたコードとバージョン情報
        """
        prefix = self.get_object()
        
        # リクエストからデータを取得
        name = request.data.get('name', '')
        description = request.data.get('description', '')
        status_value = request.data.get('status', 'draft')
        
        if not name:
            return Response(
                {
                    'success': False,
                    'message': 'コード名は必須です'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 新しいコードを生成
                generated_code = prefix.generate_next_code()
                
                # Codeオブジェクトを作成
                code = Code.objects.create(
                    prefix=prefix,
                    code=generated_code,
                    name=name,
                    description=description
                )
                
                # CodeVersionオブジェクトを作成
                code_version = CodeVersion.objects.create(
                    code=code,
                    version='1.0',
                    status=status_value,
                    description=f'コード「{code.code}」の初期バージョン'
                )
                
                # 変更ログを記録
                CodeChangeLog.objects.create(
                    code=code,
                    action='create',
                    new_value={
                        'code': code.code,
                        'name': code.name,
                        'description': code.description
                    },
                    change_reason='新規コード生成'
                )
                
                response_data = {
                    'success': True,
                    'message': f'コード「{code.code}」を生成しました',
                    'data': {
                        'code': {
                            'id': code.id,
                            'code': code.code,
                            'name': code.name,
                            'description': code.description
                        },
                        'version': {
                            'id': code_version.id,
                            'version': code_version.version,
                            'status': code_version.status,
                            'effective_date': code_version.effective_date.isoformat()
                        }
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'コード生成中にエラーが発生しました: {str(e)}'
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def preview_next_code(self, request, pk=None):
        """
        次に生成されるコードをプレビュー
        URL: GET /api/prefixes/{prefix_id}/preview_next_code/
        
        レスポンス:
        - prefix_id: プレフィックスID
        - prefix_name: プレフィックス名
        - code_type: コードタイプ
        - next_number: 次の番号
        - preview_code: プレビューコード
        """
        prefix = self.get_object()
        
        # コードタイプに応じたフォーマットを取得
        format_map = {
            '1': 'A{:04d}Z000',    # 組
            '2': 'AA{:04d}Z000',   # 部品
            '3': 'A{:04d}Z00'      # 購入品
        }
        
        code_format = format_map.get(prefix.code_type)
        if not code_format:
            return Response(
                {
                    'success': False,
                    'message': '無効なコードタイプです'
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 次のコードをプレビュー
        code_part = code_format.format(prefix.next_number)
        next_code = f"{prefix.name}-{code_part}"
        
        return Response({
            'success': True,
            'message': '次のコードをプレビューしました',
            'data': {
                'prefix_id': prefix.id,
                'prefix_name': prefix.name,
                'code_type': prefix.get_code_type_display(),
                'next_number': prefix.next_number,
                'preview_code': next_code
            }
        })


class CodeViewSet(viewsets.ModelViewSet):
    """
    コード管理ViewSet
    APIエンドポイント: /api/codes/
    
    機能:
    - コードのCRUD操作
    - コード検索機能
    """
    queryset = Code.objects.select_related('prefix').order_by('-created_at')  # created_byを削除
    serializer_class = CodeSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        クエリパラメータに応じてクエリセットをフィルタリング
        """
        queryset = super().get_queryset()
        
        # 検索パラメータ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | 
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # プレフィックスフィルタ
        prefix_id = self.request.query_params.get('prefix_id', None)
        if prefix_id:
            queryset = queryset.filter(prefix_id=prefix_id)
        
        return queryset.order_by('-created_at')


class CodeVersionViewSet(viewsets.ModelViewSet):
    """
    コードバージョン管理ViewSet
    APIエンドポイント: /api/code-versions/
    
    機能:
    - コードバージョンのCRUD操作
    - アクティブバージョンの管理
    """
    queryset = CodeVersion.objects.select_related('code').order_by('-created_at')  # created_byを削除
    serializer_class = CodeVersionSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        指定されたバージョンをアクティブにする
        URL: POST /api/code-versions/{version_id}/activate/
        """
        version = self.get_object()
        
        try:
            with transaction.atomic():
                # 同じコードの他のバージョンを非アクティブにする
                CodeVersion.objects.filter(
                    code=version.code, 
                    status='active'
                ).update(status='inactive')
                
                # 指定されたバージョンをアクティブにする
                version.status = 'active'
                version.save()
                
                return Response({
                    'success': True,
                    'message': f'バージョン {version.version} をアクティブにしました'
                })
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'バージョン変更中にエラーが発生しました: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    コード変更ログViewSet（読み取り専用）
    APIエンドポイント: /api/code-change-logs/
    
    機能:
    - 変更ログの参照
    - 変更履歴の検索
    """
    queryset = CodeChangeLog.objects.select_related('code', 'changed_by').all()
    serializer_class = CodeChangeLogSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        クエリパラメータに応じてクエリセットをフィルタリング
        """
        queryset = super().get_queryset()
        
        # コードIDフィルタ
        code_id = self.request.query_params.get('code_id', None)
        if code_id:
            queryset = queryset.filter(code_id=code_id)
        
        # アクションフィルタ
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-timestamp')


class CodeMetadataViewSet(viewsets.ModelViewSet):
    """
    コードメタデータ管理ViewSet
    APIエンドポイント: /api/code-metadata/
    
    機能:
    - コードメタデータのCRUD操作
    - カスタムフィールドの管理
    """
    queryset = CodeMetadata.objects.select_related('code').order_by('-updated_at')  # 順序付けを追加
    serializer_class = CodeMetadataSerializer
    pagination_class = StandardResultsSetPagination


# ========================================
# Tree関連のViewSet
# ========================================




class TreeViewSet(viewsets.ModelViewSet):
    """
    ツリー管理ViewSet（拡張版）
    自動同期機能付きの共有構造管理
    """
    
    @action(detail=True, methods=['post'])
    def share_structure(self, request, pk=None):
        """
        他のツリーの構造をこのツリーに共有（自動同期機能付き）
        URL: POST /api/trees/{tree_id}/share_structure/
        
        リクエストパラメータ:
        - source_structure_id: 共有元構造ID（必須）
        - parent_id: このツリーでの親構造ID（オプション）
        
        機能:
        1. 構造の共有
        2. 既存の共有ツリーとの自動同期
        3. 双方向同期の確立
        """
        
        target_tree = self.get_object()
        
        serializer = TreeStructureShareSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'リクエストデータが無効です',  
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        source_structure_id = validated_data['source_structure_id']
        parent_id = validated_data.get('parent_id')
        
        try:
            source_structure = TreeStructure.objects.get(id=source_structure_id)
            parent_structure = None
            
            if parent_id:
                parent_structure = TreeStructure.objects.get(id=parent_id)
                if parent_structure.tree.id != target_tree.id:
                    return Response({
                        'success': False,
                        'message': '指定された親構造は別のツリーに属しています'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Step 1: 共有グループの作成または取得
                shared_group = source_structure.shared_group
                
                if not shared_group:
                    # 新しい共有グループを作成
                    shared_group = SharedStructureGroup.objects.create(
                        name=f"{source_structure.node.name}共有グループ",
                        description=f"構造「{source_structure.node.name}」の共有グループ",
                        root_node=source_structure.node
                    )
                    
                    # 元の構造を共有グループに追加
                    self._convert_to_shared_structure(source_structure, shared_group)
                
                # Step 2: ターゲットツリーに共有構造を作成
                new_structure = self._create_shared_structure(
                    target_tree, parent_structure, source_structure, shared_group
                )
                
                # Step 3: 既存の共有ツリーに同期
                sync_count = self._sync_to_existing_shared_trees(
                    shared_group, source_structure, exclude_trees=[target_tree.id, source_structure.tree.id]
                )
                
                # Step 4: 変更ログを記録
                TreeChangeLog.objects.create(
                    tree=target_tree,
                    structure=new_structure,
                    action='share_join',
                    new_value={
                        'shared_group_id': shared_group.id,
                        'source_tree_id': source_structure.tree.id,
                        'source_structure_id': source_structure.id,
                        'synced_trees_count': sync_count
                    },
                    change_reason='構造共有への参加（自動同期付き）'
                )
                
                # レスポンスデータを作成
                structure_serializer = TreeStructureSerializer(new_structure, context={'request': request})
                
                response_data = {
                    'success': True,
                    'message': f"構造「{source_structure.node.name}」を共有しました（{sync_count + 1}個のツリーで同期）",
                    'data': {
                        'structure': structure_serializer.data,
                        'shared_group': {
                            'id': shared_group.id,
                            'name': shared_group.name
                        },
                        'sync_info': {
                            'total_participating_trees': sync_count + 2,  # source + target + others
                            'auto_synced_trees': sync_count,
                            'bidirectional_sync': True
                        }
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except TreeStructure.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定された構造が存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"構造共有エラー: {str(e)}")
            return Response({
                'success': False,
                'message': f'構造共有エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def add_to_shared_structure(self, request, pk=None):
        """
        共有構造に新しいノードを追加（全共有ツリーに自動反映）
        URL: POST /api/trees/{tree_id}/add_to_shared_structure/
        
        リクエストパラメータ:
        - parent_structure_id: 親構造ID（必須、共有構造である必要がある）
        - node_name: ノード名（必須）
        - node_description: ノード説明（オプション）
        - node_type: ノードタイプ（オプション）
        - sequence: 並び順（オプション）
        
        機能:
        共有構造配下に新しいノードを追加し、同じ共有グループの全ツリーに自動反映
        """
        
        tree = self.get_object()
        
        try:
            parent_structure_id = request.data.get('parent_structure_id')
            if not parent_structure_id:
                return Response({
                    'success': False,
                    'message': '親構造IDが必要です'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            parent_structure = TreeStructure.objects.get(
                id=parent_structure_id,
                tree=tree,
                sharing_type='shared'
            )
            
            if not parent_structure.shared_group:
                return Response({
                    'success': False,
                    'message': '指定された構造は共有構造ではありません'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Step 1: 新しいノードを作成
                node = TreeNode.objects.create(
                    name=request.data.get('node_name'),
                    description=request.data.get('node_description', ''),
                    node_type=request.data.get('node_type', 'default')
                )
                
                # Step 2: 現在のツリーに構造を作成
                sequence = request.data.get('sequence', 0)
                new_path = f"{parent_structure.group_relative_path}.{sequence}"
                
                new_structure = TreeStructure.objects.create(
                    tree=tree,
                    parent=parent_structure,
                    node=node,
                    sequence=sequence,
                    sharing_type='shared',
                    shared_group=parent_structure.shared_group,
                    group_relative_path=new_path
                )
                
                # Step 3: 他の全共有ツリーに自動追加
                participating_trees = parent_structure.shared_group.get_participating_trees().exclude(id=tree.id)
                synced_trees = []
                
                for target_tree in participating_trees:
                    # 対応する親構造を見つける
                    target_parent = TreeStructure.objects.filter(
                        tree=target_tree,
                        shared_group=parent_structure.shared_group,
                        group_relative_path=parent_structure.group_relative_path
                    ).first()
                    
                    if target_parent:
                        # 同じ構造を作成
                        synced_structure = TreeStructure.objects.create(
                            tree=target_tree,
                            parent=target_parent,
                            node=node,  # 同じノードを共有
                            sequence=sequence,
                            sharing_type='shared',
                            shared_group=parent_structure.shared_group,
                            group_relative_path=new_path
                        )
                        
                        synced_trees.append({
                            'tree_id': target_tree.id,
                            'tree_name': target_tree.name,
                            'structure_id': synced_structure.id
                        })
                
                # Step 4: 変更ログを記録
                TreeChangeLog.objects.create(
                    tree=tree,
                    structure=new_structure,
                    action='shared_structure_add',
                    new_value={
                        'node_name': node.name,
                        'shared_group_id': parent_structure.shared_group.id,
                        'auto_synced_trees': synced_trees,
                        'total_synced_count': len(synced_trees)
                    },
                    change_reason=f'共有構造への追加（{len(synced_trees)}個のツリーに自動同期）'
                )
                
                # レスポンス
                return Response({
                    'success': True,
                    'message': f"ノード「{node.name}」を共有構造に追加しました（{len(synced_trees) + 1}個のツリーに反映）",
                    'data': {
                        'node': {
                            'id': node.id,
                            'name': node.name,
                            'description': node.description
                        },
                        'structure': {
                            'id': new_structure.id,
                            'tree_id': tree.id,
                            'parent_id': parent_structure.id
                        },
                        'sync_result': {
                            'total_trees': len(synced_trees) + 1,
                            'synced_trees': synced_trees,
                            'shared_group_id': parent_structure.shared_group.id
                        }
                    }
                }, status=status.HTTP_201_CREATED)
                
        except TreeStructure.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定された親構造が存在しないか、共有構造ではありません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"共有構造追加エラー: {str(e)}")
            return Response({
                'success': False,
                'message': f'共有構造への追加中にエラーが発生しました: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _convert_to_shared_structure(self, structure, shared_group):
        """
        既存の構造を共有構造に変換する補助メソッド
        """
        structure.sharing_type = 'shared'
        structure.shared_group = shared_group
        structure.group_relative_path = '0'
        structure.save()
        
        # 子構造も再帰的に処理
        self._add_children_to_shared_group(structure, shared_group)
    
    def _create_shared_structure(self, target_tree, parent_structure, source_structure, shared_group):
        """
        共有構造を作成する補助メソッド
        """
        new_structure = TreeStructure.objects.create(
            tree=target_tree,
            parent=parent_structure,
            node=source_structure.node,  # 同じノードを共有
            sequence=source_structure.sequence,
            sharing_type='shared',
            shared_group=shared_group,
            group_relative_path='0'
        )
        
        # 子構造も再帰的に共有
        self._share_child_structures(source_structure, new_structure, shared_group)
        
        return new_structure
    
    def _sync_to_existing_shared_trees(self, shared_group, source_structure, exclude_trees=None):
        """
        既存の共有ツリーに構造を同期する補助メソッド
        """
        if exclude_trees is None:
            exclude_trees = []
        
        participating_trees = shared_group.get_participating_trees().exclude(id__in=exclude_trees)
        sync_count = 0
        
        for target_tree in participating_trees:
            # 既に同じ構造が存在するかチェック
            existing = TreeStructure.objects.filter(
                tree=target_tree,
                node=source_structure.node,
                shared_group=shared_group
            ).exists()
            
            if not existing:
                # 新しい構造を作成
                self._create_shared_structure(target_tree, None, source_structure, shared_group)
                sync_count += 1
        
        return sync_count
    
    def _add_children_to_shared_group(self, parent_structure, shared_group):
        """
        子構造を共有グループに追加する補助メソッド
        """
        children = TreeStructure.objects.filter(parent=parent_structure)
        
        for i, child in enumerate(children):
            child.sharing_type = 'shared'
            child.shared_group = shared_group
            child.group_relative_path = f"{parent_structure.group_relative_path}.{i}"
            child.save()
            
            # 再帰的に子構造も処理
            self._add_children_to_shared_group(child, shared_group)

    def _share_child_structures(self, source_structure, target_structure, shared_group):
        """
        子ノードを再帰的に共有する補助メソッド
        """
        child_structures = TreeStructure.objects.filter(parent=source_structure).order_by('sequence')
        
        for i, child in enumerate(child_structures):
            # 子ノードの構造を作成（同じノードを共有）
            new_child = TreeStructure.objects.create(
                tree=target_structure.tree,
                parent=target_structure,
                node=child.node,  # 同じノードを共有
                sequence=child.sequence,
                sharing_type='shared',
                shared_group=shared_group,
                group_relative_path=f"{target_structure.group_relative_path}.{i}"
            )
            
            # 再帰的に子構造も共有
            self._share_child_structures(child, new_child, shared_group)


class TreeStructureViewSet(viewsets.ModelViewSet):
    """
    ツリー構造管理ViewSet
    APIエンドポイント: /api/tree-structures/
    
    機能:
    - ツリー構造のCRUD操作
    - 構造の移動・並び替え
    - 共有構造の管理
    """
    queryset = TreeStructure.objects.select_related(
        'tree', 'parent', 'node', 'shared_group'
    ).prefetch_related('children').all()
    serializer_class = TreeStructureSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        クエリパラメータに応じてクエリセットをフィルタリング
        """
        queryset = super().get_queryset()
        
        # ツリーIDフィルタ
        tree_id = self.request.query_params.get('tree_id', None)
        if tree_id:
            queryset = queryset.filter(tree_id=tree_id)
        
        # 共有タイプフィルタ
        sharing_type = self.request.query_params.get('sharing_type', None)
        if sharing_type:
            queryset = queryset.filter(sharing_type=sharing_type)
        
        # レベルフィルタ
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)
        
        return queryset.order_by('level', 'sequence')

    @action(detail=True, methods=['post'])
    def update_node(self, request, pk=None):
        """
        構造のノード情報を更新（共有構造の場合、全ての共有先に反映）
        URL: POST /api/tree-structures/{structure_id}/update_node/
        
        リクエストパラメータ:
        - name: ノード名（オプション）
        - description: ノード説明（オプション）
        - node_type: ノードタイプ（オプション）
        - attributes: ノード属性（オプション、JSON）
        - change_reason: 変更理由（オプション）
        """
        structure = self.get_object()
        
        # 更新対象のフィールドを取得
        update_fields = {}
        if 'name' in request.data:
            update_fields['name'] = request.data['name']
        if 'description' in request.data:
            update_fields['description'] = request.data['description']
        if 'node_type' in request.data:
            update_fields['node_type'] = request.data['node_type']
        if 'attributes' in request.data:
            update_fields['attributes'] = request.data['attributes']
        
        if not update_fields:
            return Response(
                {
                    'success': False,
                    'message': '更新対象のフィールドが指定されていません'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 変更前の値を保存
                old_values = {
                    'name': structure.node.name,
                    'description': structure.node.description,
                    'node_type': structure.node.node_type,
                    'attributes': structure.node.attributes
                }
                
                # ノードを更新（共有されている場合、すべての参照先に反映される）
                for field, value in update_fields.items():
                    setattr(structure.node, field, value)
                
                structure.node.save()
                
                # 変更ログを記録（共有構造の場合、全ツリーに記録）
                if structure.is_shared():
                    # 共有構造の場合、全ての共有先に変更ログを記録
                    sibling_structures = structure.get_sibling_shared_structures()
                    all_structures = [structure] + list(sibling_structures)
                    
                    for struct in all_structures:
                        TreeChangeLog.objects.create(
                            tree=struct.tree,
                            structure=struct,
                            action='node_update',
                            old_value=old_values,
                            new_value=update_fields,
                            change_reason=request.data.get('change_reason', 'ノード情報更新')
                        )
                else:
                    # 独立構造の場合
                    TreeChangeLog.objects.create(
                        tree=structure.tree,
                        structure=structure,
                        action='node_update',
                        old_value=old_values,
                        new_value=update_fields,
                        change_reason=request.data.get('change_reason', 'ノード情報更新')
                    )
                
                # 更新された構造情報を返す
                updated_serializer = TreeStructureSerializer(structure, context={'request': request})
                
                return Response({
                    'success': True,
                    'message': f"ノード「{structure.node.name}」を更新しました",
                    'data': updated_serializer.data,
                    'affected_trees': [struct.tree.name for struct in all_structures] if structure.is_shared() else [structure.tree.name]
                })
                
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ノード更新中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def move_structure(self, request, pk=None):
        """
        構造を別の親の下に移動
        URL: POST /api/tree-structures/{structure_id}/move_structure/
        
        リクエストパラメータ:
        - new_parent_id: 新しい親構造ID（ルートに移動する場合はnull）
        - new_sequence: 新しい並び順（オプション、デフォルト=0）
        """
        structure = self.get_object()
        
        new_parent_id = request.data.get('new_parent_id')
        new_sequence = request.data.get('new_sequence', 0)
        
        try:
            with transaction.atomic():
                old_parent = structure.parent
                
                # 新しい親構造を取得
                new_parent = None
                if new_parent_id:
                    new_parent = TreeStructure.objects.get(id=new_parent_id)
                    
                    # 同じツリー内での移動かチェック
                    if new_parent.tree.id != structure.tree.id:
                        return Response(
                            {
                                'success': False,
                                'message': '異なるツリー間での移動はサポートされていません'
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # 構造を移動
                structure.parent = new_parent
                structure.sequence = new_sequence
                structure.save()  # save()メソッドでパスとレベルが自動更新される
                
                # 変更ログを記録
                TreeChangeLog.objects.create(
                    tree=structure.tree,
                    structure=structure,
                    action='structure_move',
                    old_value={
                        'parent_id': old_parent.id if old_parent else None,
                        'parent_name': old_parent.node.name if old_parent else None,
                        'level': structure.level
                    },
                    new_value={
                        'parent_id': new_parent.id if new_parent else None,
                        'parent_name': new_parent.node.name if new_parent else None,
                        'level': structure.level,
                        'sequence': new_sequence
                    },
                    change_reason='構造移動'
                )
                
                # 更新された構造情報を返す
                updated_serializer = TreeStructureSerializer(structure, context={'request': request})
                
                return Response({
                    'success': True,
                    'message': f"構造「{structure.node.name}」を移動しました",
                    'data': updated_serializer.data
                })
                
        except TreeStructure.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': '指定された親構造が存在しません'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"構造移動中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TreeNodeViewSet(viewsets.ModelViewSet):
    """
    ツリーノード管理ViewSet
    APIエンドポイント: /api/tree-nodes/
    
    機能:
    - ツリーノードのCRUD操作
    - ノードの検索機能
    """
    queryset = TreeNode.objects.select_related('code').all()
    serializer_class = TreeNodeSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        クエリパラメータに応じてクエリセットをフィルタリング
        """
        queryset = super().get_queryset()
        
        # 検索パラメータ
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # ノードタイプフィルタ
        node_type = self.request.query_params.get('node_type', None)
        if node_type:
            queryset = queryset.filter(node_type=node_type)
        
        return queryset.order_by('-created_at')


class SharedStructureGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    共有構造グループ管理ViewSet（読み取り専用）
    APIエンドポイント: /api/shared-structure-groups/
    
    機能:
    - 共有構造グループの参照
    - 参加ツリーの確認
    """
    queryset = SharedStructureGroup.objects.select_related('root_node').all()
    serializer_class = SharedStructureGroupSerializer
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['get'])
    def participating_trees(self, request, pk=None):
        """
        共有グループに参加しているツリーの詳細を取得
        URL: GET /api/shared-structure-groups/{group_id}/participating_trees/
        """
        group = self.get_object()
        
        try:
            participating_trees = group.get_participating_trees()
            tree_serializer = TreeSerializer(participating_trees, many=True, context={'request': request})
            
            return Response({
                'success': True,
                'message': f"共有グループ「{group.name}」の参加ツリーを取得しました",
                'data': {
                    'group': {
                        'id': group.id,
                        'name': group.name,
                        'root_node_name': group.root_node.name
                    },
                    'participating_trees': tree_serializer.data
                }
            })
            
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"参加ツリー取得中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TreeVersionViewSet(viewsets.ModelViewSet):
    """
    ツリーバージョン管理ViewSet
    APIエンドポイント: /api/tree-versions/
    
    機能:
    - ツリーバージョンのCRUD操作
    - バージョンの切り替え
    """
    queryset = TreeVersion.objects.select_related('tree', 'created_by').all()
    serializer_class = TreeVersionSerializer
    pagination_class = StandardResultsSetPagination


class TreeCodeQuantityViewSet(viewsets.ModelViewSet):
    """
    ツリーコード数量管理ViewSet
    APIエンドポイント: /api/tree-code-quantities/
    
    機能:
    - コード数量のCRUD操作
    - 数量の集計機能
    """
    queryset = TreeCodeQuantity.objects.select_related('tree', 'structure', 'code').all()
    serializer_class = TreeCodeQuantitySerializer
    pagination_class = StandardResultsSetPagination


class TreeChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ツリー変更ログViewSet（読み取り専用）
    APIエンドポイント: /api/tree-change-logs/
    
    機能:
    - 変更ログの参照
    - 変更履歴の検索
    """
    queryset = TreeChangeLog.objects.select_related('tree', 'structure', 'changed_by').all()
    serializer_class = TreeChangeLogSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """
        クエリパラメータに応じてクエリセットをフィルタリング
        """
        queryset = super().get_queryset()
        
        # ツリーIDフィルタ
        tree_id = self.request.query_params.get('tree_id', None)
        if tree_id:
            queryset = queryset.filter(tree_id=tree_id)
        
        # アクションフィルタ
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-timestamp')