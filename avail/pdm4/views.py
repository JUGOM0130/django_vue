from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from .models import (Prefix,
                     Code,
                     CodeVersion,
                     CodeChangeLog,
                     CodeMetadata,
                     Tree,
                     TreeStructure,
                     TreeVersion,
                     TreeCodeQuantity,
                     TreeChangeLog,
                     TreeNode
                     )
from .serializers import (PrefixSerializer,
                          CodeSerializer,
                          CodeVersionSerializer,
                          CodeChangeLogSerializer,
                          CodeMetadataSerializer,
                          TreeSerializer,
                          TreeStructureSerializer,
                          TreeVersionSerializer,
                          TreeCodeQuantitySerializer,
                          TreeChangeLogSerializer,
                          TreeNodeSerializer
                          )


# 基本的な CRUD 操作を提供する ViewSet クラス群
class PrefixViewSet(viewsets.ModelViewSet):
    """Prefixの作成・読取・更新・削除を行うViewSet"""
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer
    @action(detail=True, methods=['post'])
    def generate_code(self, request, pk=None):
        """
        指定されたPrefixのIDを使用して新しいコードとバージョンを生成する
        
        POST パラメータ:
        - name: コード名（必須）
        - description: 説明（オプション）
        - status: ステータス（オプション、デフォルトは'draft'）

        エンドポイント：/api/prefixes/{prefix_id}/generate_code/
        """
        # Prefixオブジェクトを取得
        prefix = self.get_object()
        
        # リクエストからデータを取得
        name = request.data.get('name','')
        description = request.data.get('description', '')
        status_value = request.data.get('status', 'draft')
        
        try:
            # トランザクション開始
            with transaction.atomic():

                # Prefixからコードを生成
                # PrefixModelのgenerate_codeメソッドを使用
                code_string = prefix.generate_code()
                
                # Codeオブジェクトを作成
                code = Code.objects.create(
                    code=code_string,
                    name=name,
                    prefix=prefix,
                    description=description,
                    sequential_number=prefix.next_number - 1,  # generate_codeで既に+1されているため
                    status=status_value
                )
                
                # CodeVersionオブジェクトを作成
                code_version = CodeVersion.objects.create(
                    code=code,
                    version=1,  # 初期バージョン
                    code_number=code_string,
                    is_current=True,
                    status=status_value,
                    reason='初期作成',
                    changed_by=request.user if request.user.is_authenticated else None,
                    effective_date=timezone.now()
                )
                
                # 変更履歴の記録
                change_log = CodeChangeLog.objects.create(
                    code_version=code_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='create',
                    reason='新規コード作成',
                    new_status=status_value
                )
                
                # レスポンスの作成
                response_data = {
                    'success': True,
                    'message': f'コード「{code_string}」を生成しました',
                    'code': {
                        'id': code.id,
                        'code': code.code,
                        'name': code.name,
                        'description': code.description,
                        'status': code.status,
                        'created_at': code.created_at.isoformat() if hasattr(code, 'created_at') else None
                    },
                    'version': {
                        'id': code_version.id,
                        'version': code_version.version,
                        'status': code_version.status,
                        'effective_date': code_version.effective_date.isoformat()
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            # エラー処理
            return Response(
                {'error': f'コード生成中にエラーが発生しました: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def preview_next_code(self, request, pk=None):
        """
        次に生成されるコードをプレビューする
        実際にコードを生成せずに、次に生成されるコードの形式を確認できる

        エンドポイント：/api/prefixes/{prefix_id}/preview_next_code/ 
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
                {'error': '無効なコードタイプです'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 次のコードをプレビュー
        code_part = code_format.format(prefix.next_number)
        next_code = f"{prefix.name}-{code_part}"
        
        return Response({
            'prefix_id': prefix.id,
            'prefix_name': prefix.name,
            'code_type': prefix.get_code_type_display(),
            'next_number': prefix.next_number,
            'preview_code': next_code
        })

class CodeViewSet(viewsets.ModelViewSet):
    """Codeの作成・読取・更新・削除を行うViewSet"""
    queryset = Code.objects.all()
    serializer_class = CodeSerializer

class CodeVersionViewSet(viewsets.ModelViewSet):
    """CodeVersionの作成・読取・更新・削除を行うViewSet"""
    queryset = CodeVersion.objects.all()
    serializer_class = CodeVersionSerializer

class CodeChangeLogViewSet(viewsets.ModelViewSet):
    """CodeChangeLogの作成・読取・更新・削除を行うViewSet"""
    queryset = CodeChangeLog.objects.all()
    serializer_class = CodeChangeLogSerializer

class CodeMetadataViewSet(viewsets.ModelViewSet):
    """CodeMetadataの作成・読取・更新・削除を行うViewSet"""
    queryset = CodeMetadata.objects.all()
    serializer_class = CodeMetadataSerializer



class TreeViewSet(viewsets.ModelViewSet):
    """
    ツリーの作成・読取・更新・削除を行うViewSet
    ツリー作成時に関連するツリーノード、構造、バージョンも自動的に作成
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

    def create(self, request, *args, **kwargs):
        """
        ツリーの新規作成を行い、成功/失敗のメッセージを返す
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            # 成功レスポンスデータの作成
            response_data = {
                'success': True,
                'message': f"ツリー「{serializer.data.get('name')}」を作成しました",
                'data': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            # エラーレスポンスの作成
            return Response(
                {
                    'success': False,
                    'message': f"ツリー作成中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """
        ツリーの更新を行い、成功/失敗のメッセージを返す
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        try:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            # 成功レスポンスデータの作成
            response_data = {
                'success': True,
                'message': f"ツリー「{serializer.data.get('name')}」を更新しました",
                'data': serializer.data
            }
            
            return Response(response_data)
        except Exception as e:
            # エラーレスポンスの作成
            return Response(
                {
                    'success': False,
                    'message': f"ツリー更新中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        ツリーの削除を行い、成功/失敗のメッセージを返す
        """
        instance = self.get_object()
        tree_name = instance.name
        
        try:
            self.perform_destroy(instance)
            return Response(
                {
                    'success': True,
                    'message': f"ツリー「{tree_name}」を削除しました"
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ツリー削除中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        """
        ツリーの一覧取得を行い、成功/失敗のメッセージを返す
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                paginated_data = paginated_response.data
                
                # ページネーションレスポンスに成功メッセージを追加
                response_data = {
                    'success': True,
                    'message': f"ツリー一覧を取得しました（{len(serializer.data)}件）",
                    'count': paginated_data['count'],
                    'next': paginated_data['next'],
                    'previous': paginated_data['previous'],
                    'results': paginated_data['results']
                }
                
                return Response(response_data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': f"ツリー一覧を取得しました（{len(serializer.data)}件）",
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ツリー一覧取得中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    def retrieve(self, request, *args, **kwargs):
        """
        単一ツリーの取得を行い、成功/失敗のメッセージを返す
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'message': f"ツリー「{instance.name}」を取得しました",
                'data': serializer.data
            })
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ツリー取得中にエラーが発生しました: {str(e)}"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def structure(self, request, pk=None):
        """
        指定されたツリーIDの構造データを取得する
        
        エンドポイント: /api/trees/{tree_id}/structure/
        """
        tree = self.get_object()
        
        try:
            # ツリーに関連する全ての構造を取得
            structures = TreeStructure.objects.filter(
                tree=tree
            ).select_related(
                'node', 'parent'
            ).order_by('level', 'sequence')
            
            # シリアライザを使ってレスポンスデータを整形
            serializer = TreeStructureSerializer(structures, many=True, context={'request': request})
            
            return Response(
                {
                    'success': True,
                    'message': f"ツリー「{tree.name}」の構造を取得しました（{len(structures)}件）",
                    'data': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ツリー構造の取得中にエラーが発生しました: {str(e)}"
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def add_node(self, request, pk=None):
        """
        ツリーに新しいノードを追加するアクション
        
        POST パラメータ:
        - parent_id: 親構造のID（必須）
        - code_id: 関連付ける部品コードのID（任意）
        - name: ノード名（必須）
        - description: 説明（任意）
        - node_type: ノードタイプ（任意、デフォルトは'code'）
        - quantity: 数量（任意、デフォルト1.0）
        - relationship_type: 関係タイプ（任意、デフォルト'assembly'）
        - is_master: マスター構造かどうか（任意、デフォルトFalse）
        """
        tree = self.get_object()
        
        # 必須パラメータの確認
        parent_id = request.data.get('parent_id')
        name = request.data.get('name')
        
        if not parent_id:
            return Response(
                {
                    'success': False,
                    'message': '親構造IDは必須です'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not name:
            return Response(
                {
                    'success': False,
                    'message': 'ノード名は必須です'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 親構造を取得
            parent_structure = TreeStructure.objects.get(id=parent_id)
            
            # ツリーの一貫性チェック
            if parent_structure.tree.id != tree.id:
                return Response(
                    {
                        'success': False,
                        'message': '指定された親構造は別のツリーに属しています'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # オプションパラメータの取得
                description = request.data.get('description', '')
                node_type = request.data.get('node_type', 'code')
                code_id = request.data.get('code_id')
                quantity = request.data.get('quantity', 1.0)
                relationship_type = request.data.get('relationship_type', 'assembly')
                is_master = request.data.get('is_master', False)
                
                # コードの取得（指定されている場合）
                code = None
                if code_id:
                    try:
                        code = Code.objects.get(id=code_id)
                        if code.status != 'active':
                            return Response(
                                {
                                    'success': False,
                                    'message': '有効状態のコードのみ追加できます'
                                },
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    except Code.DoesNotExist:
                        return Response(
                            {
                                'success': False,
                                'message': '指定されたコードが存在しません'
                            },
                            status=status.HTTP_404_NOT_FOUND
                        )
                
                # TreeNodeを作成
                node = TreeNode.objects.create(
                    name=name,
                    description=description,
                    node_type=node_type,
                    status='active',
                    code=code
                )
                
                # ツリー構造を作成
                structure = TreeStructure.objects.create(
                    tree=tree,
                    parent=parent_structure,
                    node=node,
                    level=parent_structure.level + 1,
                    path=f"{parent_structure.path}.{node.id}",
                    sequence=TreeStructure.objects.filter(parent=parent_structure).count(),
                    relationship_type=relationship_type,
                    is_master=is_master,
                    quantity=quantity,
                    effective_date=timezone.now()
                )
                
                # 現在アクティブなバージョンを取得
                active_version = TreeVersion.objects.filter(
                    tree=tree,
                    status__in=['draft', 'review', 'approved']
                ).order_by('-version_number').first()
                
                if not active_version:
                    # アクティブなバージョンがなければ新規作成
                    active_version = TreeVersion.objects.create(
                        tree=tree,
                        version_number=1,
                        version_name=f"{tree.name} v1",
                        status='draft',
                        created_by=request.user if request.user.is_authenticated else None,
                        effective_date=timezone.now()
                    )
                
                # 変更ログを作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='add_node',
                    description=f"ノード '{node.name}' を追加しました。親ノード: {parent_structure.node.name}",
                    affected_node=code,
                    significance_level=1,  # 通常
                    new_data={
                        'structure_id': structure.id,
                        'parent_id': parent_structure.id,
                        'node_id': node.id,
                        'node_name': node.name,
                        'node_type': node.node_type,
                        'relationship_type': relationship_type,
                        'quantity': quantity,
                        'is_master': is_master,
                        'code_id': code.id if code else None
                    }
                )
                
                # レスポンスデータを作成
                response_data = {
                    'success': True,
                    'message': f'ノード "{node.name}" を追加しました',
                    'data': {
                        'structure_id': structure.id,
                        'parent_id': parent_structure.id,
                        'node': {
                            'id': node.id,
                            'name': node.name,
                            'type': node.node_type,
                            'code_id': code.id if code else None,
                            'code': code.code if code else None
                        },
                        'level': structure.level,
                        'path': structure.path,
                        'relationship_type': structure.relationship_type,
                        'quantity': float(structure.quantity),
                        'is_master': structure.is_master
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
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
                    'message': f'ノード追加エラー: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def share_structure(self, request, pk=None):
        """
        他のツリーからノード構造を共有するアクション
        
        POST パラメータ:
        - source_structure_id: 共有元のTreeStructure ID（必須）
        - parent_id: このツリーでの親構造ID（必須）
        """
        target_tree = self.get_object()
        
        # 必須パラメータの確認
        source_structure_id = request.data.get('source_structure_id')
        parent_id = request.data.get('parent_id')
        
        if not source_structure_id or not parent_id:
            return Response(
                {
                    'success': False,
                    'message': '共有元構造IDと親構造IDは必須です'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            source_structure = TreeStructure.objects.get(id=source_structure_id)
            parent_structure = TreeStructure.objects.get(id=parent_id)
            
            # ツリーの一貫性チェック
            if parent_structure.tree.id != target_tree.id:
                return Response(
                    {
                        'success': False,
                        'message': '指定された親構造は別のツリーに属しています'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # 共有構造を特定
                master_structure = source_structure if source_structure.is_master else source_structure.source_structure
                
                if not master_structure:
                    return Response(
                        {
                            'success': False,
                            'message': '指定された構造はマスター構造ではありません'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 新しい構造を作成（同じノードを共有）
                new_structure = TreeStructure.objects.create(
                    tree=target_tree,
                    parent=parent_structure,
                    node=master_structure.node,  # 同じノードを共有
                    level=parent_structure.level + 1,
                    path=f"{parent_structure.path}.{master_structure.node.id}",
                    sequence=TreeStructure.objects.filter(parent=parent_structure).count(),
                    relationship_type=master_structure.relationship_type,
                    source_structure=master_structure,
                    is_master=False,  # 共有インスタンスなのでマスターではない
                    quantity=master_structure.quantity,
                    effective_date=timezone.now()
                )
                
                # 現在アクティブなバージョンを取得
                active_version = TreeVersion.objects.filter(
                    tree=target_tree,
                    status__in=['draft', 'review', 'approved']
                ).order_by('-version_number').first()
                
                if not active_version:
                    # アクティブなバージョンがなければ新規作成
                    active_version = TreeVersion.objects.create(
                        tree=target_tree,
                        version_number=1,
                        version_name=f"{target_tree.name} v1",
                        status='draft',
                        created_by=request.user if request.user.is_authenticated else None,
                        effective_date=timezone.now()
                    )
                
                # 変更ログを作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='share_structure',
                    description=f"構造 '{master_structure.node.name}' を共有しました。親ノード: {parent_structure.node.name}",
                    affected_node=master_structure.node.code if hasattr(master_structure.node, 'code') and master_structure.node.code else None,
                    significance_level=2,  # 重要
                    new_data={
                        'structure_id': new_structure.id,
                        'parent_id': parent_structure.id,
                        'source_structure_id': master_structure.id,
                        'source_tree_id': master_structure.tree.id,
                        'source_tree_name': master_structure.tree.name,
                        'node_id': master_structure.node.id,
                        'node_name': master_structure.node.name
                    }
                )
                
                # 子ノードも再帰的に共有
                self._share_child_structures(master_structure, new_structure, active_version)
                
                # レスポンスデータを作成
                response_data = {
                    'success': True,
                    'message': f'構造 "{master_structure.node.name}" を共有しました',
                    'data': {
                        'structure_id': new_structure.id,
                        'parent_id': parent_structure.id,
                        'node': {
                            'id': master_structure.node.id,
                            'name': master_structure.node.name,
                            'type': master_structure.node.node_type
                        },
                        'level': new_structure.level,
                        'path': new_structure.path,
                        'is_shared': True,
                        'source_structure_id': master_structure.id,
                        'source_tree': {
                            'id': master_structure.tree.id,
                            'name': master_structure.tree.name
                        }
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except TreeStructure.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': '指定された構造が存在しません'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f'構造共有エラー: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _share_child_structures(self, source_structure, target_structure, active_version):
            """子ノードを再帰的に共有する補助メソッド"""
            child_structures = TreeStructure.objects.filter(
                tree=source_structure.tree,
                parent=source_structure
            ).order_by('sequence')
            
            for child in child_structures:
                # 子ノードの構造を作成（同じノードを共有）
                new_child = TreeStructure.objects.create(
                    tree=target_structure.tree,
                    parent=target_structure,
                    node=child.node,  # 同じノードを共有
                    level=target_structure.level + 1,
                    path=f"{target_structure.path}.{child.node.id}",
                    sequence=child.sequence,
                    relationship_type=child.relationship_type,
                    source_structure=child if child.is_master else child.source_structure,
                    is_master=False,  # 共有インスタンスなのでマスターではない
                    quantity=child.quantity,
                    effective_date=timezone.now()
                )
                
                # 変更ログを作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=None,  # 自動処理による変更
                    change_type='add_node',
                    description=f"共有構造の一部として '{child.node.name}' を追加しました。",
                    affected_node=child.node.code if hasattr(child.node, 'code') and child.node.code else None,
                    significance_level=0,  # 軽微
                    new_data={
                        'structure_id': new_child.id,
                        'parent_id': target_structure.id,
                        'is_shared': True,
                        'source_structure_id': child.id if child.is_master else (child.source_structure.id if child.source_structure else None)
                    }
                )
                
                # 再帰的に子ノードの処理を続行
                self._share_child_structures(child, new_child, active_version)

    @action(detail=True, methods=['post'])
    def bulk_update(self, request, pk=None):
        """
        ツリー構造を一括で更新する
        """
        tree = self.get_object()
        
        # リクエストからデータ取得
        structures_data = request.data.get('structures', [])
        
        if not structures_data:
            return Response(
                {
                    'success': False,
                    'message': '構造データが提供されていません'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # 現在のバージョンを取得または作成
                active_version = TreeVersion.objects.filter(
                    tree=tree,
                    status__in=['draft', 'review', 'approved']
                ).order_by('-version_number').first()
                
                if not active_version:
                    active_version = TreeVersion.objects.create(
                        tree=tree,
                        version_number=1,
                        version_name=f"{tree.name} v1",
                        status='draft',
                        created_by=request.user if request.user.is_authenticated else None,
                        effective_date=timezone.now()
                    )
                
                # 変更ログを記録 - significance_levelを1に下げて通知が発生しないようにする
                changes_log = TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='update_metadata',
                    description=f"ツリー '{tree.name}' の構造を一括更新しました。",
                    significance_level=1,  # 通常 (2から1に変更)
                    new_data={
                        'structure_count': len(structures_data)
                    }
                )
                
                # 既存のノードマップを作成（効率化のため）
                existing_nodes = TreeNode.objects.filter(
                    structures__tree=tree
                ).distinct()
                node_map = {node.id: node for node in existing_nodes}
                
                # 既存の構造マップを作成
                existing_structures = TreeStructure.objects.filter(tree=tree)
                structure_map = {}
                for structure in existing_structures:
                    if structure.parent:
                        key = f"{structure.parent.node.id}-{structure.node.id}"
                    else:
                        key = f"root-{structure.node.id}"
                    structure_map[key] = structure
                
                # 各構造を処理
                updated_count = 0
                created_count = 0
                
                for item in structures_data:
                    parent_id = item.get('parent')
                    child_id = item.get('child')
                    name = item.get('name')
                    level = item.get('level', 1)
                    node_type = item.get('node_type', 'code')
                    relationship_type = item.get('relationship_type', 'assembly')
                    quantity = item.get('quantity', 1.0)
                    is_master = item.get('is_master', False)
                    
                    if not child_id or not name:
                        continue  # 必須フィールドが欠けている場合はスキップ
                    
                    # ノードの取得または作成
                    node = node_map.get(child_id)
                    if not node:
                        # 新しいノードを作成
                        node = TreeNode.objects.create(
                            name=name,
                            description='',
                            node_type=node_type,
                            status='active'
                        )
                        node_map[node.id] = node
                        
                    # 親構造を取得
                    parent_structure = None
                    if parent_id:
                        parent_node = node_map.get(parent_id)
                        if parent_node:
                            # 親ノードに関連する構造を検索
                            for structure in existing_structures:
                                if structure.node.id == parent_node.id:
                                    parent_structure = structure
                                    break
                    else:
                        # ルートノードを親とする
                        parent_structure = existing_structures.filter(level=0).first()
                    
                    if not parent_structure and level > 1:
                        # 親が見つからないのに階層が1より大きい場合はスキップ
                        continue
                    
                    # 構造の構築キーを作成
                    structure_key = f"root-{node.id}" if not parent_structure else f"{parent_structure.node.id}-{node.id}"
                    
                    # 構造を取得または作成
                    structure = structure_map.get(structure_key)
                    if structure:
                        # 既存の構造を更新
                        structure.level = level
                        structure.relationship_type = relationship_type
                        structure.quantity = quantity
                        structure.is_master = is_master
                        structure.save()
                        updated_count += 1
                    else:
                        # 新しい構造を作成
                        path = str(node.id) if not parent_structure else f"{parent_structure.path}.{node.id}"
                        structure = TreeStructure.objects.create(
                            tree=tree,
                            node=node,
                            parent=parent_structure,
                            level=level,
                            path=path,
                            sequence=TreeStructure.objects.filter(parent=parent_structure).count() if parent_structure else 0,
                            relationship_type=relationship_type,
                            is_master=is_master,
                            quantity=quantity,
                            effective_date=timezone.now()
                        )
                        structure_map[structure_key] = structure
                        created_count += 1
                
                # 変更ログを直接更新し、save()を呼び出さないようにする
                # または、new_dataフィールドを使わずに別のフィールドに情報を保存
                changes_log.description += f" 更新: {updated_count}, 作成: {created_count}"
                
                # save()を呼び出す代わりに、QuerySetのupdateメソッドを使用
                TreeChangeLog.objects.filter(id=changes_log.id).update(
                    description=changes_log.description
                )
                    
                return Response(
                    {
                        'success': True,
                        'message': f"ツリー構造を一括更新しました。更新: {updated_count}, 作成: {created_count}",
                        'data': {
                            'tree_id': tree.id,
                            'updated_count': updated_count,
                            'created_count': created_count,
                            'total_structures': updated_count + created_count
                        }
                    },
                    status=status.HTTP_200_OK
                )
                    
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'message': f"ツリー構造の一括更新中にエラーが発生しました: {str(e)}"
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def save(self, *args, **kwargs):
        """ツリー保存時に自動的にルートノードを作成"""
        is_new = self.pk is None  # 新規作成かチェック
        
        with transaction.atomic():
            # 1. まずTreeを保存
            super().save(*args, **kwargs)
            
            # 2. 新規作成時のみ、ルートノードとツリー構造を作成
            if is_new:
                # 既存のルートノードがないことを確認
                existing_root = TreeNode.objects.filter(
                    node_type='root', 
                    tree_nodes__tree=self
                ).first()
                
                if not existing_root:
                    # ルートノードを作成
                    root_node = TreeNode.objects.create(
                        name=f"{self.name}_ROOT",
                        description=f"ツリー「{self.name}」のルートノード",
                        node_type='root',
                        status='active'
                    )
                    
                    # ツリー構造を作成
                    TreeStructure.objects.create(
                        tree=self,
                        node=root_node,
                        parent=None,
                        level=0,
                        path=str(root_node.id),
                        is_master=True  # ルートノードはマスター
                    )

class TreeStructureViewSet(viewsets.ModelViewSet):
    """TreeStructureの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeStructure.objects.all()
    serializer_class = TreeStructureSerializer

class TreeVersionViewSet(viewsets.ModelViewSet):
    """TreeVersionの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeVersion.objects.all()
    serializer_class = TreeVersionSerializer

class TreeCodeQuantityViewSet(viewsets.ModelViewSet):
    """TreeCodeQuantityの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeCodeQuantity.objects.all()
    serializer_class = TreeCodeQuantitySerializer

class TreeChangeLogViewSet(viewsets.ModelViewSet):
    """TreeChangeLogの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeChangeLog.objects.all()
    serializer_class = TreeChangeLogSerializer

    def get_stakeholders(self):
        """関係者のリストを取得する"""
        stakeholders = []
        
        # ツリーの作成者と最終更新者を追加
        if self.tree_version.tree.created_by:
            stakeholders.append(self.tree_version.tree.created_by)
        if self.tree_version.tree.last_modified_by:
            stakeholders.append(self.tree_version.tree.last_modified_by)
        
        # ツリーバージョンの作成者と承認者を追加
        if self.tree_version.created_by:
            stakeholders.append(self.tree_version.created_by)
        if self.tree_version.approved_by:
            stakeholders.append(self.tree_version.approved_by)
        
        # 重複を削除
        return list(set(stakeholders))