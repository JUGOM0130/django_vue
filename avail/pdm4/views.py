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
                     TreeChangeLog
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
                          TreeChangeLogSerializer
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
    """Treeの作成・読取・更新・削除を行うViewSet"""
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

    def create(self, request, *args, **kwargs):
        """
        ツリーを作成すると同時に、関連するTreeVersion、TreeStructure、
        TreeChangeLogなども自動的に作成します。
        """
        with transaction.atomic():
            # 1. 基本的なツリー作成処理
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # ユーザー情報を設定
            current_user = request.user if request.user.is_authenticated else None
            if current_user:
                serializer.validated_data['created_by'] = current_user
                serializer.validated_data['last_modified_by'] = current_user
            
            # ツリーを保存（save処理の中でルートノードも作成される）
            tree = serializer.save()
            
            # 2. TreeVersionを作成
            version_name = request.data.get('version_name', f"{tree.name} 初期バージョン")
            version_description = request.data.get('version_description', "初期作成")
            
            tree_version = TreeVersion.objects.create(
                tree=tree,
                version_number=1,  # 初期バージョン
                version_name=version_name,
                version_description=version_description,
                status='draft',
                created_by=current_user,
                effective_date=timezone.now()
            )
            
            # 3. ルートノードに対するTreeStructureが作成されたので、それを取得
            root_structure = tree.relationships.filter(parent=None).first()
            
            if root_structure:
                # 4. TreeChangeLogを作成
                TreeChangeLog.objects.create(
                    tree_version=tree_version,
                    changed_by=current_user,
                    change_type='add_node',
                    description=f"ツリー '{tree.name}' を作成しました。ルートノードを追加しました。",
                    affected_node=root_structure.current_node,
                    significance_level=1,  # 通常
                    new_data={
                        'tree_id': tree.id,
                        'tree_name': tree.name,
                        'root_node_id': root_structure.current_node.id,
                        'root_node_code': root_structure.current_node.code if hasattr(root_structure.current_node, 'code') else None,
                    }
                )
            
            # 5. レスポンスデータを作成
            response_data = serializer.data
            response_data['version'] = {
                'id': tree_version.id,
                'version_number': tree_version.version_number,
                'version_name': tree_version.version_name,
                'status': tree_version.status
            }
            
            if root_structure:
                response_data['root_node'] = {
                    'id': root_structure.id,
                    'node_id': root_structure.current_node.id,
                    'node_name': root_structure.current_node.name,
                    'level': root_structure.level,
                    'path': root_structure.path
                }
            
            headers = self.get_success_headers(serializer.data)
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def add_node(self, request, pk=None):
        """
        ツリーに新しいノードを追加するアクション
        
        POST パラメータ:
        - parent_id: 親ノードのID（必須）
        - code_id: 追加するノードのコードID（必須）
        - quantity: 数量（任意、デフォルト1.0）
        - relationship_type: 関係タイプ（任意、デフォルト'assembly'）
        - is_master: マスター構造かどうか（任意、デフォルトFalse）
        - sequence: 表示順序（任意）
        """
        tree = self.get_object()
        
        # 必須パラメータの確認
        parent_id = request.data.get('parent_id')
        code_id = request.data.get('code_id')
        
        if not parent_id or not code_id:
            return Response(
                {'error': '親ノードIDとコードIDは必須です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            parent_node = Code.objects.get(id=parent_id)
            code = Code.objects.get(id=code_id)
            
            if code.status != 'active':
                return Response(
                    {'error': '有効状態のコードのみ追加できます'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # 親ノードのTreeStructureを取得
                parent_structure = TreeStructure.objects.filter(
                    tree=tree,
                    current_node=parent_node
                ).first()
                
                if not parent_structure:
                    return Response(
                        {'error': '指定された親ノードがこのツリーに存在しません'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # オプションパラメータの取得
                quantity = request.data.get('quantity', 1.0)
                relationship_type = request.data.get('relationship_type', 'assembly')
                is_master = request.data.get('is_master', False)
                sequence = request.data.get('sequence', 0)
                
                # 新しいTreeStructureを作成
                new_structure = TreeStructure.objects.create(
                    tree=tree,
                    parent=parent_node,
                    current_node=code,
                    level=parent_structure.level + 1,
                    path=f"{parent_structure.path}.{code.id}",
                    sequence=sequence,
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
                
                # コードの最新バージョンを取得
                latest_code_version = CodeVersion.objects.filter(
                    code=code,
                    is_current=True
                ).first()
                
                if latest_code_version:
                    # TreeCodeQuantityを作成
                    TreeCodeQuantity.objects.create(
                        tree_structure=new_structure,
                        code_version=latest_code_version,
                        quantity=float(quantity),
                        unit=latest_code_version.metadata.unit if hasattr(latest_code_version, 'metadata') else 'piece',
                        effective_date=timezone.now()
                    )
                
                # 変更ログを作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='add_node',
                    description=f"ノード '{code.name}' を追加しました。親ノード: {parent_node.name}",
                    affected_node=code,
                    significance_level=1,  # 通常
                    new_data={
                        'structure_id': new_structure.id,
                        'parent_id': parent_node.id,
                        'code_id': code.id,
                        'relationship_type': relationship_type,
                        'quantity': quantity,
                        'is_master': is_master
                    }
                )
                
                # レスポンスデータを作成
                response_data = {
                    'success': True,
                    'message': f'ノード "{code.name}" を追加しました',
                    'node': {
                        'id': new_structure.id,
                        'parent_id': parent_node.id,
                        'code_id': code.id,
                        'code_name': code.name,
                        'level': new_structure.level,
                        'path': new_structure.path,
                        'relationship_type': new_structure.relationship_type,
                        'quantity': float(new_structure.quantity)
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Code.DoesNotExist:
            return Response(
                {'error': '指定されたコードが存在しません'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'ノード追加エラー: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def share_structure(self, request, pk=None):
        """
        ツリー間で構造を共有するアクション
        
        他のツリーの構造をこのツリーにも追加し、変更が連動するようにします
        
        POST パラメータ:
        - source_structure_id: 共有元のTreeStructure ID（必須）
        - parent_id: このツリーでの親ノードID（必須）
        - sequence: 表示順序（任意）
        """
        target_tree = self.get_object()
        
        # 必須パラメータの確認
        source_structure_id = request.data.get('source_structure_id')
        parent_id = request.data.get('parent_id')
        
        if not source_structure_id or not parent_id:
            return Response(
                {'error': '共有元構造IDと親ノードIDは必須です'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            source_structure = TreeStructure.objects.get(id=source_structure_id)
            parent_node = Code.objects.get(id=parent_id)
            
            with transaction.atomic():
                # 親ノードのTreeStructureを取得
                parent_structure = TreeStructure.objects.filter(
                    tree=target_tree,
                    current_node=parent_node
                ).first()
                
                if not parent_structure:
                    return Response(
                        {'error': '指定された親ノードがこのツリーに存在しません'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # オプションパラメータの取得
                sequence = request.data.get('sequence', 0)
                
                # 共有構造を特定
                master_structure = source_structure if source_structure.is_master else source_structure.source_structure
                
                if not master_structure:
                    return Response(
                        {'error': '指定された構造はマスター構造ではありません'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # 新しいTreeStructureを作成
                new_structure = TreeStructure.objects.create(
                    tree=target_tree,
                    parent=parent_node,
                    current_node=master_structure.current_node,
                    level=parent_structure.level + 1,
                    path=f"{parent_structure.path}.{master_structure.current_node.id}",
                    sequence=sequence,
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
                
                # 変更ログを作成
                TreeChangeLog.objects.create(
                    tree_version=active_version,
                    changed_by=request.user if request.user.is_authenticated else None,
                    change_type='share_structure',
                    description=f"構造 '{master_structure.current_node.name}' を共有しました。親ノード: {parent_node.name}",
                    affected_node=master_structure.current_node,
                    significance_level=2,  # 重要
                    new_data={
                        'structure_id': new_structure.id,
                        'parent_id': parent_node.id,
                        'source_structure_id': master_structure.id,
                        'source_tree_id': master_structure.tree.id,
                        'source_tree_name': master_structure.tree.name
                    }
                )
                
                # 子ノードも再帰的にコピー
                self._copy_child_structures(master_structure, new_structure, target_tree, active_version)
                
                # レスポンスデータを作成
                response_data = {
                    'success': True,
                    'message': f'構造 "{master_structure.current_node.name}" を共有しました',
                    'structure': {
                        'id': new_structure.id,
                        'parent_id': parent_node.id,
                        'node_id': master_structure.current_node.id,
                        'node_name': master_structure.current_node.name,
                        'level': new_structure.level,
                        'path': new_structure.path,
                        'is_shared': True,
                        'source_structure_id': master_structure.id,
                        'source_tree_id': master_structure.tree.id,
                        'source_tree_name': master_structure.tree.name
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except TreeStructure.DoesNotExist:
            return Response(
                {'error': '指定された構造が存在しません'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Code.DoesNotExist:
            return Response(
                {'error': '指定されたコードが存在しません'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'構造共有エラー: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _copy_child_structures(self, source_structure, target_structure, target_tree, active_version):
        """子ノードを再帰的にコピーする補助メソッド"""
        child_structures = TreeStructure.objects.filter(
            tree=source_structure.tree,
            parent=source_structure.current_node
        ).order_by('sequence')
        
        for child in child_structures:
            # 子ノードの構造を作成
            new_child = TreeStructure.objects.create(
                tree=target_tree,
                parent=target_structure.current_node,
                current_node=child.current_node,
                level=target_structure.level + 1,
                path=f"{target_structure.path}.{child.current_node.id}",
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
                description=f"共有構造の一部として '{child.current_node.name}' を追加しました。",
                affected_node=child.current_node,
                significance_level=0,  # 軽微
                new_data={
                    'structure_id': new_child.id,
                    'parent_id': target_structure.current_node.id,
                    'is_shared': True,
                    'source_structure_id': child.id if child.is_master else child.source_structure.id
                }
            )
            
            # 再帰的に子ノードの処理を続行
            self._copy_child_structures(child, new_child, target_tree, active_version)

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