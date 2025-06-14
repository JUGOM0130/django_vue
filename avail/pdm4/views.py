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
            
            for structure in structures:
                # 各構造のノード情報を取得
                print(f"\t構造ID: {structure.id},\t ノード名: {structure.node.name},\t 親ID: {structure.parent.id if structure.parent else 'なし'},\t レベル: {structure.level},\t パス: {structure.path}")

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

    # views.pyのbulk_updateメソッド(またはsimilar name)の修正案
    @action(detail=True, methods=['post'])
    def bulk_update(self, request, pk=None):
        """
        ツリー構造を一括で更新する - 重複防止と堅牢な処理
        """
        # ロガーの設定
        import logging
        logger = logging.getLogger(__name__)

        tree = self.get_object()
        
        # リクエストからデータ取得
        structures_data = request.data.get('structures', [])
        print(f"Bulk update for tree {tree.id}: {len(structures_data)} structures")
        print(f"Structures data: {structures_data}")

        if not structures_data:
            return Response(
                {
                    'success': False,
                    'message': '構造データが提供されていません'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 循環参照チェック関数
        def check_circular_reference(parent_id, node_id, processed_nodes):
            if parent_id == node_id:
                return True  # 循環参照あり
            
            if parent_id in processed_nodes:
                parent_node = processed_nodes[parent_id]
                return check_circular_reference(parent_node['parent_id'], node_id, processed_nodes)
            
            return False  # 循環参照なし

        # 循環参照のチェック
        processed_nodes = {}
        for item in structures_data:

            print("処理中のitem:",item)
            # 同名ノードの存在をチェック
            existing_nodes = TreeNode.objects.filter(
                name=item.get('name'),
                node_type=item.get('node_type')
            )
            print(f"同名ノード: {list(existing_nodes.values('id', 'name'))}")
            
            # 既存の構造をチェック
            existing_structures = TreeStructure.objects.filter(
                tree_id=tree.id,
                node__name=item.get('name'),
                level=item.get('level')
            )
            print(f"同レベルの既存構造: {list(existing_structures.values('id', 'node__name', 'level'))}")

            node_id = item.get('child')
            parent_id = item.get('parent')
            
            # 自己参照のチェック
            if node_id == parent_id:
                return Response(
                    {
                        'success': False, 
                        'message': f'ノードID {node_id} が自身を親に持っています。循環参照は許可されません。'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 循環参照のチェック
            if parent_id and check_circular_reference(parent_id, node_id, processed_nodes):
                return Response(
                    {
                        'success': False, 
                        'message': f'ノードID {node_id} は循環参照の一部です。これは許可されません。'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            processed_nodes[node_id] = {'parent_id': parent_id}

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
                
                # 変更ログを記録
                changes_log = TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='update_metadata',
                    description=f"ツリー '{tree.name}' の構造を一括更新しました。",
                    significance_level=1,
                    new_data={
                        'structure_count': len(structures_data)
                    }
                )
                
                # 既存のノードとその構造を効率的に取得
                existing_nodes = TreeNode.objects.filter(
                    structures__tree=tree
                ).distinct()
                node_map = {node.id: node for node in existing_nodes}
                
                # 既存の構造を詳細にマッピング
                existing_structures = TreeStructure.objects.filter(tree=tree)
                structure_map = {}
                for structure in existing_structures:
                    key = (
                        structure.parent.id if structure.parent else None, 
                        structure.node.id, 
                        structure.level
                    )
                    structure_map[key] = structure
                
                # ルートノードの確認と作成
                root_node = TreeNode.objects.filter(
                    node_type='root',
                    structures__tree=tree,
                    structures__parent__isnull=True
                ).first()
                
                if not root_node:
                    root_node = TreeNode.objects.create(
                        name=f"{tree.name}_ROOT",
                        description=f"ツリー「{tree.name}」のルートノード",
                        node_type='root',
                        status='active'
                    )
                    
                    root_structure = TreeStructure.objects.create(
                        tree=tree,
                        node=root_node,
                        parent=None,
                        level=0,
                        path=str(root_node.id),
                        is_master=True
                    )
                    node_map[root_node.id] = root_node
                    structure_map[(None, root_node.id, 0)] = root_structure
                
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
                    
                    # ROOTノードとレベル0は処理をスキップ
                    if node_type == 'root' or level == 0:
                        continue
                    
                    if not child_id or not name:
                        continue  # 必須フィールドが欠けている場合はスキップ
                    
                    # ノードの取得または作成
                    node, node_created = TreeNode.objects.get_or_create(
                        id=child_id,
                        defaults={
                            'name': name,
                            'description': '',
                            'node_type': node_type,
                            'status': 'active'
                        }
                    )
                    
                    if node_created:
                        node_map[node.id] = node
                    
                    # 親構造の取得
                    parent_structure = None
                    if parent_id:
                        parent_node = node_map.get(parent_id)
                        if parent_node:
                            for structure in existing_structures:
                                if structure.node.id == parent_node.id:
                                    parent_structure = structure
                                    break
                    else:
                        # ルートノードを親とする
                        for structure in existing_structures:
                            if structure.level == 0:
                                parent_structure = structure
                                break
                    
                    if not parent_structure and level > 1:
                        continue
                    
                    # 構造の重複チェックと作成/更新
                    structure_key = (
                        parent_structure.id if parent_structure else None, 
                        node.id, 
                        level
                    )
                    
                    existing_structure = structure_map.get(structure_key)
                    if existing_structure:
                        # 既存の構造を更新
                        existing_structure.relationship_type = relationship_type
                        existing_structure.quantity = quantity
                        existing_structure.is_master = is_master
                        existing_structure.save()
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
                
                # 変更ログの説明を更新
                changes_log.description += f" 更新: {updated_count}, 作成: {created_count}"
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
            logger.error(f"Bulk update error: {str(e)}")
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


    
    @action(detail=True, methods=['post'])
    def add_existing_structure_shared(self, request, pk=None):
        """
        既存ノード構造を共有参照として追加するAPIエンドポイント
        
        エンドポイント: POST /api/trees/{tree_id}/add_existing_structure_shared/
        
        機能説明:
        - 他のツリーから既存のノード構造を真の共有として追加
        - 同じTreeNodeオブジェクトを複数のツリーで共有参照
        - 元のツリーでの変更が全ての共有先に自動反映される
        - 子ノードも含めて再帰的に共有可能
        
        リクエストパラメータ:
        - source_tree_id (int, 必須): コピー元ツリーのID
        - source_structure_id (int, 必須): コピー元構造のID
        - parent_id (int, 必須): このツリーでの親構造ID
        - include_children (bool, 任意): 子ノードも含めるか (デフォルト: True)
        - relationship_type (str, 任意): 関係タイプ (デフォルト: 'assembly')
                                     選択肢: 'assembly', 'reference', 'option', 'spare', 'alternate', 'phantom'
        - quantity (float, 任意): 数量 (デフォルト: 1.0)
        - is_master (bool, 任意): マスター構造かどうか (デフォルト: False)
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ
        - data (object): 処理結果データ
          - shared_count (int): 共有された構造の数
          - is_true_sharing (bool): 真の共有であることを示すフラグ
          - source_tree (object): ソースツリー情報
            - id (int): ツリーID
            - name (str): ツリー名
          - shared_structures (array): 共有された構造のリスト
            - id (int): 構造ID
            - node_id (int): ノードID（複数ツリーで同じIDが使用される）
            - node_name (str): ノード名
            - level (int): 階層レベル
            - path (str): パス情報
            - source_structure_id (int): 共有元構造ID
        
        エラーレスポンス:
        - 400: 必須パラメータ不足
        - 404: 指定されたリソースが存在しない
        - 500: サーバー内部エラー
        """
        target_tree = self.get_object()
        
        # パラメータ取得（前回と同じ）
        source_tree_id = request.data.get('source_tree_id')
        source_structure_id = request.data.get('source_structure_id')
        parent_id = request.data.get('parent_id')
        include_children = request.data.get('include_children', True)
        relationship_type = request.data.get('relationship_type', 'assembly')
        quantity = request.data.get('quantity', 1.0)
        is_master = request.data.get('is_master', False)
        
        if not all([source_tree_id, source_structure_id, parent_id]):
            return Response({
                'success': False,
                'message': 'ソースツリーID、ソース構造ID、親構造IDは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            source_tree = Tree.objects.get(id=source_tree_id)
            source_structure = TreeStructure.objects.get(
                id=source_structure_id,
                tree=source_tree
            )
            parent_structure = TreeStructure.objects.get(
                id=parent_id,
                tree=target_tree
            )
            
            with transaction.atomic():
                # アクティブバージョン取得（前回と同じ）
                active_version = TreeVersion.objects.filter(
                    tree=target_tree,
                    status__in=['draft', 'review', 'approved']
                ).order_by('-version_number').first()
                
                if not active_version:
                    active_version = TreeVersion.objects.create(
                        tree=target_tree,
                        version_number=1,
                        version_name=f"{target_tree.name} v1",
                        status='draft',
                        created_by=request.user if request.user.is_authenticated else None,
                        effective_date=timezone.now()
                    )
                
                # 共有構造を作成（真の共有版）
                shared_structures = self._create_shared_structure_recursively(
                    source_structure=source_structure,
                    target_tree=target_tree,
                    target_parent=parent_structure,
                    include_children=include_children,
                    relationship_type=relationship_type,
                    quantity=quantity,
                    is_master=is_master,
                    user=request.user if request.user.is_authenticated else None,
                    active_version=active_version
                )
                
                # 変更ログ作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='share_structure',
                    description=f"構造 '{source_structure.node.name}' をツリー '{source_tree.name}' から共有しました。",
                    affected_node=source_structure.node.code if hasattr(source_structure.node, 'code') and source_structure.node.code else None,
                    significance_level=2,  # 重要
                    new_data={
                        'source_tree_id': source_tree.id,
                        'source_tree_name': source_tree.name,
                        'source_structure_id': source_structure.id,
                        'shared_structures_count': len(shared_structures),
                        'include_children': include_children,
                        'is_true_sharing': True  # 真の共有であることを示すフラグ
                    }
                )
                
                response_data = {
                    'success': True,
                    'message': f'ノード構造 "{source_structure.node.name}" を共有しました（{len(shared_structures)}個の構造）',
                    'data': {
                        'shared_count': len(shared_structures),
                        'is_true_sharing': True,
                        'source_tree': {
                            'id': source_tree.id,
                            'name': source_tree.name
                        },
                        'shared_structures': [
                            {
                                'id': struct.id,
                                'node_id': struct.node.id,  # 同じnode.idが複数のツリーで使われる
                                'node_name': struct.node.name,
                                'level': struct.level,
                                'path': struct.path,
                                'source_structure_id': struct.source_structure.id if struct.source_structure else None
                            } for struct in shared_structures
                        ]
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'共有構造追加エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_shared_structure_recursively(self, source_structure, target_tree, target_parent,
                                           include_children=True, relationship_type='assembly',
                                           quantity=1.0, is_master=False, user=None,
                                           active_version=None):
        """
        真の共有構造を再帰的に作成する補助メソッド
        
        機能説明:
        - 同じTreeNodeオブジェクトを複数のツリーで参照する構造を作成
        - 新しいTreeNodeは作成せず、既存のTreeNodeを直接参照
        - 子ノードも含めて再帰的に共有構造を作成
        
        パラメータ:
        - source_structure (TreeStructure): コピー元の構造オブジェクト
        - target_tree (Tree): コピー先のツリーオブジェクト
        - target_parent (TreeStructure): コピー先での親構造
        - include_children (bool): 子ノードも含めるかどうか
        - relationship_type (str): 関係タイプ
        - quantity (float): 数量
        - is_master (bool): マスター構造かどうか
        - user (User): 実行ユーザー
        - active_version (TreeVersion): アクティブなバージョン
        
        戻り値:
        - list[TreeStructure]: 作成された共有構造のリスト
        
        注意事項:
        - 真の共有のため、同じTreeNodeオブジェクトを複数の構造で参照
        - source_structureフィールドで共有元を記録
        - 共有インスタンスは is_master=False に設定
        """
        shared_structures = []
        
        try:
            # 重要：新しいTreeNodeは作成せず、既存のnodeを直接参照
            new_structure = TreeStructure.objects.create(
                tree=target_tree,
                parent=target_parent,
                node=source_structure.node,  # 同じTreeNodeオブジェクトを参照！
                level=target_parent.level + 1,
                path=f"{target_parent.path}.{source_structure.node.id}",
                sequence=TreeStructure.objects.filter(parent=target_parent).count(),
                relationship_type=relationship_type,
                source_structure=source_structure,  # 共有元の構造を記録
                is_master=False,  # 共有インスタンスはマスターではない
                quantity=quantity,
                effective_date=timezone.now()
            )
            shared_structures.append(new_structure)
            
            # 子ノードも共有する場合
            if include_children:
                child_structures = TreeStructure.objects.filter(
                    tree=source_structure.tree,
                    parent=source_structure
                ).order_by('sequence')
                
                for child in child_structures:
                    child_shared = self._create_shared_structure_recursively(
                        source_structure=child,
                        target_tree=target_tree,
                        target_parent=new_structure,
                        include_children=True,
                        relationship_type=child.relationship_type,
                        quantity=child.quantity,
                        is_master=False,
                        user=user,
                        active_version=active_version
                    )
                    shared_structures.extend(child_shared)
                    
        except Exception as e:
            print(f"Error creating shared structure {source_structure.id}: {str(e)}")
            raise
        
        return shared_structures

    @action(detail=True, methods=['post'])
    def update_shared_node(self, request, pk=None):
        """
        共有ノードを更新し、全ての共有先に変更を反映するAPIエンドポイント
        
        エンドポイント: POST /api/trees/{tree_id}/update_shared_node/
        
        機能説明:
        - 共有されているTreeNodeの情報を更新
        - 更新内容が同じTreeNodeを参照している全てのツリーに自動反映
        - 各ツリーの変更ログに更新履歴を記録
        - トランザクション処理により安全に更新
        
        リクエストパラメータ:
        - node_id (int, 必須): 更新対象のTreeNode ID
        - name (str, 任意): 新しいノード名
        - description (str, 任意): 新しい説明（nullを送信すると空文字に設定）
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ（影響を受けたツリー数を含む）
        - data (object): 処理結果データ
          - node_id (int): 更新されたノードID
          - updated_name (str): 更新後のノード名
          - updated_description (str): 更新後の説明
          - affected_trees (array): 影響を受けたツリーのリスト
            - id (int): ツリーID
            - name (str): ツリー名
        
        エラーレスポンス:
        - 400: ノードIDが未指定
        - 404: 指定されたノードが存在しない
        - 500: サーバー内部エラー
        
        注意事項:
        - 一つのノードの変更が複数のツリーに影響するため、慎重に使用
        - 変更前の値も変更ログに記録される
        """
        tree = self.get_object()
        
        node_id = request.data.get('node_id')
        name = request.data.get('name')
        description = request.data.get('description')
        
        if not node_id:
            return Response({
                'success': False,
                'message': 'ノードIDは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # TreeNodeを更新
                node = TreeNode.objects.get(id=node_id)
                old_name = node.name
                old_description = node.description
                
                if name:
                    node.name = name
                if description is not None:
                    node.description = description
                node.save()
                
                # このノードを使用している全てのツリーを取得
                affected_trees = Tree.objects.filter(
                    structures__node=node
                ).distinct()
                
                # 各ツリーの変更ログを作成
                for affected_tree in affected_trees:
                    active_version = TreeVersion.objects.filter(
                        tree=affected_tree,
                        status__in=['draft', 'review', 'approved']
                    ).order_by('-version_number').first()
                    
                    if active_version:
                        TreeChangeLog.objects.create(
                            tree_version=active_version,
                            changed_by=request.user if request.user.is_authenticated else None,
                            change_type='update_metadata',
                            description=f"共有ノード '{node.name}' が更新されました。",
                            affected_node=node.code if hasattr(node, 'code') and node.code else None,
                            significance_level=1,
                            previous_data={
                                'name': old_name,
                                'description': old_description
                            },
                            new_data={
                                'name': node.name,
                                'description': node.description
                            }
                        )
                
                return Response({
                    'success': True,
                    'message': f'共有ノード "{node.name}" を更新しました。{len(affected_trees)}個のツリーに反映されました。',
                    'data': {
                        'node_id': node.id,
                        'updated_name': node.name,
                        'updated_description': node.description,
                        'affected_trees': [
                            {
                                'id': tree.id,
                                'name': tree.name
                            } for tree in affected_trees
                        ]
                    }
                }, status=status.HTTP_200_OK)
                
        except TreeNode.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定されたノードが存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'共有ノード更新エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_shared_usage(self, request, pk=None):
        """
        ノードの共有使用状況を確認するAPIエンドポイント
        
        エンドポイント: GET /api/trees/{tree_id}/get_shared_usage/?node_id={node_id}
        
        機能説明:
        - 指定されたTreeNodeがどのツリーで使用されているかを確認
        - 共有ノードの使用状況と依存関係を把握
        - ノード削除前の影響範囲確認に使用
        - 各使用箇所の詳細情報（レベル、パス等）も取得可能
        
        クエリパラメータ:
        - node_id (int, 必須): 確認対象のTreeNode ID
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ（使用箇所数を含む）
        - data (object): 使用状況データ
          - node (object): ノード基本情報
            - id (int): ノードID
            - name (str): ノード名
            - node_type (str): ノードタイプ
          - usage_count (int): 使用箇所の総数
          - used_in_trees (array): 使用されているツリーと構造のリスト
            - tree_id (int): ツリーID
            - tree_name (str): ツリー名
            - structure_id (int): 構造ID
            - level (int): 階層レベル
            - is_master (bool): マスター構造かどうか
            - path (str): ツリー内でのパス
        
        エラーレスポンス:
        - 400: node_idパラメータが未指定
        - 404: 指定されたノードが存在しない
        - 500: サーバー内部エラー
        
        使用例:
        - ノード削除前の影響範囲確認
        - 共有ノードの依存関係分析
        - データ整合性チェック
        """
        tree = self.get_object()
        node_id = request.query_params.get('node_id')
        
        if not node_id:
            return Response({
                'success': False,
                'message': 'ノードIDは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            node = TreeNode.objects.get(id=node_id)
            
            # このノードを使用している全ての構造を取得
            structures = TreeStructure.objects.filter(node=node).select_related('tree')
            
            usage_data = {
                'node': {
                    'id': node.id,
                    'name': node.name,
                    'node_type': node.node_type
                },
                'usage_count': len(structures),
                'used_in_trees': [
                    {
                        'tree_id': structure.tree.id,
                        'tree_name': structure.tree.name,
                        'structure_id': structure.id,
                        'level': structure.level,
                        'is_master': structure.is_master,
                        'path': structure.path
                    } for structure in structures
                ]
            }
            
            return Response({
                'success': True,
                'message': f'ノード "{node.name}" は {len(structures)} 個の場所で使用されています',
                'data': usage_data
            }, status=status.HTTP_200_OK)
            
        except TreeNode.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定されたノードが存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'使用状況取得エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    @action(detail=True, methods=['post'])
    def add_shared_tree_structure(self, request, pk=None):
        """
        既存ツリーの全構造を真の共有として新規ツリーに追加するAPIエンドポイント
        
        エンドポイント: POST /api4/tree/{target_tree_id}/add_shared_tree_structure/
        
        機能説明:
        - Tree1の全構造をTree2で真の共有として使用
        - 同じTreeNodeオブジェクトを複数のツリーで共有参照
        - Tree1での変更（ノード名、説明等）がTree2にも自動的に反映
        - 階層構造も完全に保持
        
        重要な特徴:
        - TreeNodeオブジェクトは1つだけ存在し、複数のTreeStructureから参照
        - Tree1でノード名を変更すると、Tree2でも即座に同じ変更が見える
        - Tree1でノードを削除すると、Tree2でも削除される
        - 真の共有により、データの整合性が自動的に保たれる
        
        リクエストパラメータ:
        - source_tree_id (int, 必須): 共有元ツリーのID
        - parent_structure_id (int, 必須): 共有先での親構造ID
        - include_root (bool, 任意): ルートノードも含めるかどうか (デフォルト: False)
        - relationship_type (str, 任意): 親との関係タイプ (デフォルト: 'assembly')
                                       選択肢: 'assembly', 'reference', 'option', 'spare', 'alternate', 'phantom'
        - quantity (float, 任意): 数量 (デフォルト: 1.0)
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ
        - data (object): 処理結果データ
          - shared_structures_count (int): 共有された構造の数
          - sharing_mode (str): 共有モード（常に'true_sharing'）
          - auto_sync_enabled (bool): 自動同期が有効かどうか（常にTrue）
          - include_root (bool): ルートノードを含むかどうか
          - source_tree (object): 共有元ツリー情報
            - id (int): ツリーID
            - name (str): ツリー名
            - note (str): 変更元ツリーの説明
          - target_tree (object): 共有先ツリー情報
            - id (int): ツリーID
            - name (str): ツリー名
            - note (str): 共有先ツリーの説明
          - parent_structure (object): 親構造情報
            - id (int): 構造ID
            - node_name (str): 親ノード名
          - shared_structures (array): 共有された構造のリスト（最初の20件）
            - structure_id (int): 構造ID
            - node_id (int): ノードID（複数ツリーで同じIDが使用される）
            - node_name (str): ノード名
            - level (int): 階層レベル
            - path (str): ツリー内パス
            - is_true_sharing (bool): 真の共有であることを示すフラグ
            - source_structure_id (int): 共有元構造ID
          - sharing_explanation (object): 共有機能の説明
            - how_it_works (str): 動作原理の説明
            - auto_sync (str): 自動同期の説明
            - data_consistency (str): データ整合性の説明
            - deletion_impact (str): 削除時の影響説明
        
        エラーレスポンス:
        - 400: 必須パラメータ不足
        - 404: 指定されたリソースが存在しない
        - 500: サーバー内部エラー
        """
        target_tree = self.get_object()
        
        # リクエストデータの取得
        source_tree_id = request.data.get('source_tree_id')
        parent_structure_id = request.data.get('parent_structure_id')
        include_root = request.data.get('include_root', False)
        relationship_type = request.data.get('relationship_type', 'assembly')
        quantity = request.data.get('quantity', 1.0)
        
        # バリデーション
        if not source_tree_id:
            return Response({
                'success': False,
                'message': 'source_tree_idは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not parent_structure_id:
            return Response({
                'success': False,
                'message': 'parent_structure_idは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # ソースツリーと親構造の存在確認
            source_tree = Tree.objects.get(id=source_tree_id)
            parent_structure = TreeStructure.objects.get(
                id=parent_structure_id,
                tree=target_tree
            )
            
            with transaction.atomic():
                # アクティブバージョンの取得
                active_version = TreeVersion.objects.filter(
                    tree=target_tree,
                    status__in=['draft', 'review', 'approved']
                ).order_by('-version_number').first()
                
                if not active_version:
                    active_version = TreeVersion.objects.create(
                        tree=target_tree,
                        version_number=1,
                        version_name=f"{target_tree.name} v1",
                        status='draft',
                        created_by=request.user if request.user.is_authenticated else None,
                        effective_date=timezone.now()
                    )
                
                # 真の共有として構造をコピー
                shared_structures = self._create_true_shared_structure(
                    source_tree=source_tree,
                    target_tree=target_tree,
                    parent_structure=parent_structure,
                    include_root=include_root,
                    relationship_type=relationship_type,
                    quantity=quantity,
                    user=request.user if request.user.is_authenticated else None,
                    active_version=active_version
                )
                
                # 変更ログ記録
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='share_structure',
                    description=f"ツリー「{source_tree.name}」の全構造を真の共有として追加しました（{len(shared_structures)}個のノード）",
                    significance_level=2,  # 重要
                    new_data={
                        'source_tree_id': source_tree.id,
                        'source_tree_name': source_tree.name,
                        'shared_count': len(shared_structures),
                        'sharing_mode': 'true_sharing',
                        'auto_sync_enabled': True,
                        'include_root': include_root,
                        'parent_structure_id': parent_structure.id,
                        'note': 'Tree1での変更がTree2に自動反映されます'
                    }
                )
                
                # レスポンスデータ構築
                response_data = {
                    'success': True,
                    'message': f"ツリー「{source_tree.name}」の構造を真の共有として追加しました（{len(shared_structures)}個のノード）。Tree1での変更がTree2に自動反映されます。",
                    'data': {
                        'shared_structures_count': len(shared_structures),
                        'sharing_mode': 'true_sharing',
                        'auto_sync_enabled': True,
                        'include_root': include_root,
                        'source_tree': {
                            'id': source_tree.id,
                            'name': source_tree.name,
                            'note': '変更元ツリー（このツリーでの変更が他の共有先にも反映）'
                        },
                        'target_tree': {
                            'id': target_tree.id,
                            'name': target_tree.name,
                            'note': '共有先ツリー（変更元の変更が自動反映される）'
                        },
                        'parent_structure': {
                            'id': parent_structure.id,
                            'node_name': parent_structure.node.name
                        },
                        'shared_structures': [
                            {
                                'structure_id': struct.id,
                                'node_id': struct.node.id,  # 同じnode.idが複数ツリーで使用される
                                'node_name': struct.node.name,
                                'level': struct.level,
                                'path': struct.path,
                                'is_true_sharing': True,
                                'source_structure_id': struct.source_structure.id if struct.source_structure else None
                            } for struct in shared_structures[:20]  # 最初の20件のみ返却
                        ],
                        'sharing_explanation': {
                            'how_it_works': 'Tree1とTree2で同じTreeNodeオブジェクトを共有参照',
                            'auto_sync': 'Tree1でのノード名変更、説明変更等がTree2にも即座に反映',
                            'data_consistency': '両ツリーで常に同じデータが表示される',
                            'deletion_impact': 'Tree1でノード削除すると、Tree2でも削除される'
                        }
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Tree.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定されたソースツリーが存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except TreeStructure.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定された親構造が存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'真の共有構造追加エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_true_shared_structure(self, source_tree, target_tree, parent_structure,
                                    include_root=False, relationship_type='assembly',
                                    quantity=1.0, user=None, active_version=None):
        """
        真の共有構造を作成する補助メソッド
        
        重要：
        - 新しいTreeNodeは作成しない
        - 既存のTreeNodeオブジェクトを直接参照する
        - これにより、Tree1での変更がTree2にも自動反映される
        """
        shared_structures = []
        structure_mapping = {}  # 元構造ID -> 新構造ID のマッピング
        
        # ソース構造を階層順で取得
        source_structures_query = TreeStructure.objects.filter(
            tree=source_tree
        ).select_related('node').order_by('level', 'sequence')
        
        if not include_root:
            source_structures_query = source_structures_query.exclude(level=0)
        
        source_structures = list(source_structures_query)
        
        for source_structure in source_structures:
            # 親構造の決定
            if source_structure.level == 0 or (source_structure.level == 1 and not include_root):
                # ルートまたは最上位レベル
                current_parent = parent_structure
                current_level = parent_structure.level + 1
            else:
                # 子ノード：親構造をマッピングから取得
                source_parent_id = source_structure.parent.id if source_structure.parent else None
                if source_parent_id in structure_mapping:
                    parent_structure_id = structure_mapping[source_parent_id]
                    current_parent = TreeStructure.objects.get(id=parent_structure_id)
                    current_level = current_parent.level + 1
                else:
                    continue  # 親が見つからない場合はスキップ
            
            # 新しいTreeStructureを作成（同じTreeNodeを参照）
            # 重要：source_structure.nodeをそのまま使用（新しいTreeNodeは作成しない）
            new_structure = TreeStructure.objects.create(
                tree=target_tree,
                parent=current_parent,
                node=source_structure.node,  # ★ 同じTreeNodeオブジェクトを参照！
                level=current_level,
                path=f"{current_parent.path}.{source_structure.node.id}",
                sequence=TreeStructure.objects.filter(parent=current_parent).count(),
                relationship_type=relationship_type if source_structure.level == 0 or (source_structure.level == 1 and not include_root) else source_structure.relationship_type,
                source_structure=source_structure,  # 共有元を記録
                is_master=False,  # 共有インスタンスはマスターではない
                quantity=quantity if source_structure.level == 0 or (source_structure.level == 1 and not include_root) else source_structure.quantity,
                effective_date=timezone.now()
            )
            
            # マッピングに追加
            structure_mapping[source_structure.id] = new_structure.id
            shared_structures.append(new_structure)
        
        return shared_structures


    @action(detail=False, methods=['post'])
    def update_shared_node(self, request):
        """
        共有ノードを更新し、全ての共有先に変更を自動反映するAPIエンドポイント
        
        エンドポイント: POST /api/trees/update_shared_node/
        
        機能説明:
        - TreeNodeオブジェクトを直接更新
        - 同じTreeNodeを参照している全てのTreeStructureに即座に反映
        - Tree1で実行すると、Tree2, Tree3... 全ての共有先で変更が見える
        - リアルタイム同期により、データの不整合を防止
        
        リクエストパラメータ:
        - node_id (int, 必須): 更新対象のTreeNode ID
        - name (str, 任意): 新しいノード名
        - description (str, 任意): 新しい説明（nullを送信すると空文字に設定）
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ（影響を受けたツリー数を含む）
        - data (object): 処理結果データ
          - node_id (int): 更新されたノードID
          - updated_name (str): 更新後のノード名
          - updated_description (str): 更新後の説明
          - affected_trees_count (int): 影響を受けたツリーの数
          - affected_trees (array): 影響を受けたツリーのリスト
            - id (int): ツリーID
            - name (str): ツリー名
            - structures_count (int): そのツリー内での使用箇所数
          - sync_status (str): 同期状態（常に'completed'）
          - sync_explanation (object): 同期処理の説明
            - immediate_effect (str): 即座に反映される旨の説明
            - no_delay (str): 遅延なしの説明
            - data_consistency (str): データ整合性の説明
        
        エラーレスポンス:
        - 400: node_idが未指定
        - 404: 指定されたノードが存在しない
        - 500: サーバー内部エラー
        
        注意事項:
        - 一つのノードの変更が複数のツリーに影響するため、慎重に使用
        - 変更前の値も変更ログに記録される
        - 各ツリーの変更履歴に自動同期による更新が記録される
        """
        node_id = request.data.get('node_id')
        name = request.data.get('name')
        description = request.data.get('description')
        
        if not node_id:
            return Response({
                'success': False,
                'message': 'node_idは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                # 更新対象のTreeNodeを取得
                node = TreeNode.objects.get(id=node_id)
                old_name = node.name
                old_description = node.description
                
                # TreeNodeを更新（これだけで全ての共有先に反映される）
                if name:
                    node.name = name
                if description is not None:
                    node.description = description
                node.save()
                
                # このノードを使用している全てのツリーを取得
                affected_structures = TreeStructure.objects.filter(
                    node=node
                ).select_related('tree').distinct()
                
                affected_trees = {}
                for structure in affected_structures:
                    tree = structure.tree
                    if tree.id not in affected_trees:
                        affected_trees[tree.id] = {
                            'tree': tree,
                            'structures_count': 0
                        }
                    affected_trees[tree.id]['structures_count'] += 1
                
                # 各ツリーの変更ログを作成
                for tree_data in affected_trees.values():
                    tree = tree_data['tree']
                    active_version = TreeVersion.objects.filter(
                        tree=tree,
                        status__in=['draft', 'review', 'approved']
                    ).order_by('-version_number').first()
                    
                    if active_version:
                        TreeChangeLog.objects.create(
                            tree_version=active_version,
                            changed_by=request.user if request.user.is_authenticated else None,
                            change_type='update_metadata',
                            description=f"共有ノード '{node.name}' が更新されました（自動同期）。",
                            affected_node=node.code if hasattr(node, 'code') and node.code else None,
                            significance_level=1,
                            previous_data={
                                'name': old_name,
                                'description': old_description
                            },
                            new_data={
                                'name': node.name,
                                'description': node.description
                            },
                            additional_info={
                                'sync_type': 'automatic',
                                'sharing_enabled': True
                            }
                        )
                
                response_data = {
                    'success': True,
                    'message': f'共有ノード「{node.name}」を更新しました。{len(affected_trees)}個のツリーに自動反映されました。',
                    'data': {
                        'node_id': node.id,
                        'updated_name': node.name,
                        'updated_description': node.description,
                        'affected_trees_count': len(affected_trees),
                        'affected_trees': [
                            {
                                'id': tree_data['tree'].id,
                                'name': tree_data['tree'].name,
                                'structures_count': tree_data['structures_count']
                            } for tree_data in affected_trees.values()
                        ],
                        'sync_status': 'completed',
                        'sync_explanation': {
                            'immediate_effect': '変更は即座に全ツリーで反映済み',
                            'no_delay': 'リアルタイム同期のため遅延なし',
                            'data_consistency': '全ツリーで同じデータが表示される'
                        }
                    }
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except TreeNode.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定されたノードが存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'共有ノード更新エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=['get'])
    def check_node_sharing_status(self, request):
        """
        ノードの共有状況と影響範囲を確認するAPIエンドポイント
        
        エンドポイント: GET /api/trees/check_node_sharing_status/?node_id={node_id}
        
        機能説明:
        - 指定されたTreeNodeがどのツリーで使用されているかを確認
        - 共有状況の詳細分析
        - 変更時の影響範囲を事前把握
        - データ整合性の確認
        
        クエリパラメータ:
        - node_id (int, 必須): 確認対象のTreeNode ID
        
        レスポンスパラメータ:
        - success (bool): 処理の成功/失敗
        - message (str): 処理結果メッセージ（使用箇所数を含む）
        - data (object): 共有状況データ
          - node (object): ノード基本情報
            - id (int): ノードID
            - name (str): ノード名
            - node_type (str): ノードタイプ
            - description (str): ノードの説明
            - status (str): ノードのステータス
            - code_info (object): 関連コード情報（存在する場合）
              - id (int): コードID
              - code (str): コード文字列
              - name (str): コード名
          - is_shared (bool): 複数ツリーで共有されているかどうか
          - usage_count (int): 使用箇所の総数
          - trees_count (int): 使用されているツリーの数
          - sharing_details (array): 使用されているツリーと構造のリスト
            - tree_id (int): ツリーID
            - tree_name (str): ツリー名
            - tree_status (str): ツリーのステータス
            - usage_count_in_tree (int): そのツリー内での使用回数
            - structures (array): そのツリー内での構造情報
              - structure_id (int): 構造ID
              - level (int): 階層レベル
              - path (str): ツリー内でのパス
              - relationship_type (str): 関係タイプ
              - is_master (bool): マスター構造かどうか
              - source_structure_id (int): 共有元構造ID
          - impact_analysis (object): 影響分析情報
            - is_truly_shared (bool): 真の共有状態かどうか
            - sharing_type (str): 共有タイプ（'true_sharing' または 'single_use'）
            - change_impact (object): 変更時の影響
              - affected_trees (int): 影響を受けるツリー数
              - affected_structures (int): 影響を受ける構造数
              - automatic_sync (bool): 自動同期されるかどうか
              - risk_level (str): リスクレベル（'low', 'medium', 'high'）
            - recommendations (array): 推奨事項のリスト
          - sync_explanation (object): 同期機能の説明（共有されている場合）
            - how_sharing_works (str): 共有の仕組み説明
            - change_propagation (str): 変更伝播の説明
            - data_consistency (str): データ整合性の説明
            - automatic_sync (str): 自動同期の説明
        
        エラーレスポンス:
        - 400: node_idパラメータが未指定
        - 404: 指定されたノードが存在しない
        - 500: サーバー内部エラー
        
        使用例:
        - ノード削除前の影響範囲確認
        - 共有ノードの依存関係分析
        - データ整合性チェック
        - 変更前のリスクアセスメント
        """
        node_id = request.query_params.get('node_id')
        
        if not node_id:
            return Response({
                'success': False,
                'message': 'node_idパラメータは必須です'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            node = TreeNode.objects.get(id=node_id)
            
            # このノードを使用している全ての構造を取得
            structures = TreeStructure.objects.filter(
                node=node
            ).select_related('tree').order_by('tree__name', 'level')
            
            # ツリー別の使用状況を集計
            trees_usage = {}
            for structure in structures:
                tree_id = structure.tree.id
                if tree_id not in trees_usage:
                    trees_usage[tree_id] = {
                        'tree': structure.tree,
                        'structures': [],
                        'count': 0
                    }
                trees_usage[tree_id]['structures'].append(structure)
                trees_usage[tree_id]['count'] += 1
            
            # 共有詳細データの構築
            sharing_details = []
            for tree_data in trees_usage.values():
                tree = tree_data['tree']
                structures = tree_data['structures']
                
                sharing_details.append({
                    'tree_id': tree.id,
                    'tree_name': tree.name,
                    'tree_status': tree.status,
                    'usage_count_in_tree': len(structures),
                    'structures': [
                        {
                            'structure_id': struct.id,
                            'level': struct.level,
                            'path': struct.path,
                            'relationship_type': struct.relationship_type,
                            'is_master': struct.is_master,
                            'source_structure_id': struct.source_structure.id if struct.source_structure else None,
                        } for struct in structures
                    ]
                })
            
            # 影響分析
            total_usage = len(structures)
            trees_count = len(trees_usage)
            is_shared = trees_count > 1
            
            impact_analysis = {
                'is_truly_shared': is_shared,
                'sharing_type': 'true_sharing' if is_shared else 'single_use',
                'change_impact': {
                    'affected_trees': trees_count,
                    'affected_structures': total_usage,
                    'automatic_sync': is_shared,
                    'risk_level': 'high' if trees_count > 3 else 'medium' if trees_count > 1 else 'low'
                },
                'recommendations': []
            }
            
            if is_shared:
                impact_analysis['recommendations'].extend([
                    'このノードの変更は複数のツリーに影響します',
                    '変更前に関係者への通知を推奨',
                    'バックアップを事前に取得してください'
                ])
            else:
                impact_analysis['recommendations'].append('単一ツリーでのみ使用されているため、変更の影響は限定的です')
            
            response_data = {
                'success': True,
                'message': f'ノード「{node.name}」の共有状況を取得しました（{trees_count}個のツリーで使用）',
                'data': {
                    'node': {
                        'id': node.id,
                        'name': node.name,
                        'node_type': node.node_type,
                        'description': node.description or '',
                        'status': node.status,
                        'code_info': {
                            'id': node.code.id,
                            'code': node.code.code,
                            'name': node.code.name
                        } if node.code else None
                    },
                    'is_shared': is_shared,
                    'usage_count': total_usage,
                    'trees_count': trees_count,
                    'sharing_details': sharing_details,
                    'impact_analysis': impact_analysis,
                    'sync_explanation': {
                        'how_sharing_works': '同じTreeNodeオブジェクトを複数のTreeStructureが参照',
                        'change_propagation': 'TreeNodeの変更は即座に全ての参照先に反映',
                        'data_consistency': '全ツリーで常に同じデータが表示される',
                        'automatic_sync': 'システムによる自動同期（手動同期不要）'
                    } if is_shared else {
                        'sharing_status': '現在共有されていません（単一ツリーでのみ使用）'
                    }
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except TreeNode.DoesNotExist:
            return Response({
                'success': False,
                'message': '指定されたノードが存在しません'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'共有状況確認エラー: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    
class TreeNodeViewSet(viewsets.ModelViewSet):
    """TreeNodeの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeNode.objects.all()
    serializer_class = TreeNodeSerializer
