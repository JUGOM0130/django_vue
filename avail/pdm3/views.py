from django.db import transaction
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Node, Tree, TreeStructure, TreeVersion, Prefix,
    CodeVersion, CodeVersionHistory, CodeCounter
)
from .serializers import (
    NodeSerializer, TreeSerializer, TreeStructureSerializer,
    TreeVersionSerializer, PrefixSerializer, CodeGenerationSerializer,
    CodeUpdateSerializer, CodeVersionHistorySerializer
)
from .utils import generate_code, logger

# 基本的な CRUD 操作を提供する ViewSet クラス群
class NodeViewSet(viewsets.ModelViewSet):
    """ノードの作成・読取・更新・削除を行うViewSet"""
    queryset = Node.objects.all()
    serializer_class = NodeSerializer


class TreeStructureViewSet(viewsets.ModelViewSet):
    """ツリー構造の作成・読取・更新・削除を行うViewSet"""
    queryset = TreeStructure.objects.all()
    serializer_class = TreeStructureSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        複数のツリー構造を一括で作成または更新するカスタムアクション

        POST /api/tree-structure/bulk_create/
        """
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Expected a list of items"}, status=status.HTTP_400_BAD_REQUEST)

        # データの検証
        for item in data:
            if 'parent' not in item or 'child' not in item:
                return Response({"error": "Each item must contain 'parent' and 'child' fields"}, status=status.HTTP_400_BAD_REQUEST)
            # parentとchildがNULLを許容するように変更
            if item['parent'] is None and item['child'] is None:
                return Response({"error": "'parent' and 'child' fields cannot both be null"}, status=status.HTTP_400_BAD_REQUEST)

        # データの処理
        for item in data:
            if 'id' in item and item['id']:
                # IDが存在する場合は更新
                try:
                    tree_structure = TreeStructure.objects.get(id=item['id'])
                    serializer = self.get_serializer(tree_structure, data=item)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except TreeStructure.DoesNotExist:
                    return Response({"error": f"TreeStructure with id {item['id']} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            else:
                # IDが存在しない場合は新規作成
                serializer = self.get_serializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"status": "success"}, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        """
        一括作成を実行するメソッド
        """
        with transaction.atomic():
            serializer.save()


    @action(detail=True, methods=['get'])
    def get_tree_structure(self, request, pk=None):
        """
        特定のツリーIDに関連するツリー構造を取得するカスタムアクション

        GET /api/tree-structure/{id}/get_tree_structure/
        """
        tree_id = pk
        tree_structures = TreeStructure.objects.filter(tree_id=tree_id)
        serializer = self.get_serializer(tree_structures, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def get_root_structure_detail(self, request):
        try:
            node_id = request.query_params.get('node_id')
            
            if not node_id:
                return Response(
                    {"error": "node_id parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 条件に合致するTreeStructureを配列として取得
            root_structures = TreeStructure.objects.filter(
                child_id=node_id,
                parent__isnull=True
            ).select_related('child', 'tree')

            # レスポンスデータの作成
            response_data = {
                'tree_structures': [],
                'node': None,
                'trees': [],
                'children_count': TreeStructure.objects.filter(
                    parent_id=node_id
                ).count()
            }

            if root_structures.exists():
                first_structure = root_structures.first()
                response_data['node'] = {
                    'id': first_structure.child.id,
                    'name': first_structure.child.name,
                    'description': first_structure.child.description
                }

                # 関連するツリーIDを取得
                tree_ids = root_structures.values_list('tree_id', flat=True)

                # 同じツリーに属する全TreeStructureを取得（Nodeの情報も含める）
                all_tree_structures = (TreeStructure.objects
                    .filter(tree_id__in=tree_ids)
                    .select_related('child', 'tree', 'parent'))

                # TreeStructureとノード情報をまとめて取得
                nodes_dict = {
                    ts.child.id: ts.child.name 
                    for ts in all_tree_structures
                }

                # 全TreeStructureの情報を追加
                for structure in all_tree_structures:
                    structure_data = {
                        'id': structure.id,
                        'child': structure.child.id,
                        'parent': structure.parent_id,
                        'tree': structure.tree.id,
                        'level': structure.level,
                        'name': nodes_dict.get(structure.child.id, '')  # 対応するNode名を設定
                    }
                    response_data['tree_structures'].append(structure_data)

                # Tree情報を追加
                trees = Tree.objects.filter(id__in=tree_ids)
                for tree in trees:
                    response_data['trees'].append({
                        'id': tree.id,
                        'name': tree.name
                    })

            return Response(response_data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class TreeVersionViewSet(viewsets.ModelViewSet):
    """ツリーバージョンの作成・読取・更新・削除を行うViewSet"""
    queryset = TreeVersion.objects.all()
    serializer_class = TreeVersionSerializer

class PrefixViewSet(viewsets.ModelViewSet):
    """プレフィックスの作成・読取・更新・削除を行うViewSet"""
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer

# 通常のViewSetにカスタムを加えたもの
class TreeViewSet(viewsets.ModelViewSet):
    """
    ツリーの作成・読取・更新・削除を行うViewSet
    """
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

    # createメソッドは削除（Treeモデルのsaveメソッドで自動処理されるため）

    def destroy(self, request, *args, **kwargs):
        """
        ツリーを削除するメソッド
        関連するTreeStructureとNodeも適切に処理される
        """
        with transaction.atomic():
            tree = self.get_object()
            tree.delete()  # CASCADE設定により関連するTreeStructureも自動的に削除される

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def get_root(self, request, pk=None):
        """
        特定のツリーのルートノードを取得するカスタムアクション

        GET /api/trees/{id}/get_root/   # ルートノード取得
        """
        tree = self.get_object()
        try:
            root_structure = TreeStructure.objects.get(
                tree=tree,
                level=0
            )
            root_node = root_structure.child
            serializer = NodeSerializer(root_node)
            return Response(serializer.data)
        except TreeStructure.DoesNotExist:
            return Response(
                {"error": "Root node not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def add_node(self, request, pk=None):
        """
        ツリーに新しいノードを追加するカスタムアクション

        POST /api/trees/{id}/add_node/  # 新しいノード追加
        """
        tree = self.get_object()
        
        parent_id = request.data.get('parent_id')
        name = request.data.get('name')
        description = request.data.get('description', '')

        try:
            parent_node = Node.objects.get(id=parent_id) if parent_id else None
            
            # 親ノードが指定されている場合、そのノードがこのツリーに属しているか確認
            if parent_node and not TreeStructure.objects.filter(
                tree=tree,
                child=parent_node
            ).exists():
                return Response(
                    {"error": "Parent node does not belong to this tree"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                # 新しいノードを作成
                new_node = Node.objects.create(
                    name=name,
                    description=description
                )

                # 親ノードのレベルを取得して新しいノードを関連付け
                parent_level = 0 if parent_node is None else TreeStructure.objects.get(
                    tree=tree,
                    child=parent_node
                ).level

                TreeStructure.objects.create(
                    parent=parent_node,
                    child=new_node,
                    tree=tree,
                    level=parent_level + 1
                )

                return Response(
                    NodeSerializer(new_node).data,
                    status=status.HTTP_201_CREATED
                )

        except Node.DoesNotExist:
            return Response(
                {"error": "Parent node not found"},
                status=status.HTTP_404_NOT_FOUND
            )     

# 特殊な機能を提供する APIView クラス群
class CodeGenerationView(APIView):
    """
    コード生成を行うAPIView
    
    目的：
        プレフィックスに基づいて新しい一意のコードを生成し、
        関連する全てのモデル（CodeVersion, Node, CodeVersionHistory）を作成する
    """
    def post(self, request, *args, **kwargs):
        """
        コード生成のPOSTリクエストを処理するメソッド

        処理フロー：
        1. リクエストデータのバリデーション
        2. プレフィックスの取得と存在確認
        3. 新しいコードの生成
        4. 関連モデルの作成
        """
        # 1. リクエストデータのバリデーション
        serializer = CodeGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            # バリデーションエラーの場合、エラーメッセージを返す
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. プレフィックスIDの取得
        prefix_id = serializer.validated_data["prefix"]
        
        try:
            # 3. プレフィックスの存在確認と取得
            prefix = Prefix.objects.get(id=prefix_id)
            
            # 4. 新しいコードの生成（utils.pyのgenerate_code関数を使用）
            code = generate_code(prefix)
            
            # 5. 関連モデルの作成（トランザクション的な処理）
            # 5.1 コードバージョンの作成（初期バージョン=0）
            code_version = CodeVersion.objects.create(code=code, version=0)
            
            # 5.2 対応するノードの作成
            node = Node.objects.create(name=code, description="")
            
            # 5.3 コードのバージョン履歴を作成
            CodeVersionHistory.objects.create(
                code=code,
                version=0,
                node_id=node.id
            )
            
            # 6. 生成されたコードとIDを含むレスポンスを返す
            return Response({"code": code, "id": code_version.id}, status=status.HTTP_201_CREATED)
            
        except Prefix.DoesNotExist:
            # プレフィックスが存在しない場合のエラーハンドリング
            return Response(
                {"error": "Prefix not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            # コード生成時のエラーハンドリング
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
class CodeUpdateView(APIView):
    """
    既存コードのバージョンを更新するAPIView
    
    目的：
        既存のコードのバージョンをインクリメントし、
        新しいバージョン番号を持つコードを生成する
    """
    def post(self, request, *args, **kwargs):
        """
        コードバージョン更新のPOSTリクエストを処理するメソッド

        処理フロー：
        1. リクエストデータのバリデーション
        2. 既存コードの検索と更新
        3. バージョン履歴の作成
        """
        # 1. リクエストデータのバリデーション
        serializer = CodeUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. 更新対象のコードを取得
        code = serializer.validated_data["code"]
        
        try:
            # 3. 既存のコードバージョンを取得
            code_version = CodeVersion.objects.get(code=code)
            
            # 4. バージョン番号をインクリメント
            code_version.version += 1
            
            # 5. 新しいコードの生成（末尾4桁がバージョン番号）
            updated_code = f"{code[:-4]}{code_version.version:04d}"
            code_version.code = updated_code
            code_version.save()
            
            # 6. バージョン履歴の作成
            CodeVersionHistory.objects.create(
                code=updated_code,
                version=code_version.version
            )
            
            # 7. 更新されたコードを含むレスポンスを返す
            return Response(
                {"updated_code": updated_code},
                status=status.HTTP_200_OK
            )
            
        except CodeVersion.DoesNotExist:
            # コードが存在しない場合のエラーハンドリング
            return Response(
                {"error": "Code not found."},
                status=status.HTTP_404_NOT_FOUND
            )
class CodeVersionHistoryView(generics.ListAPIView):
    """
    特定のコードのバージョン履歴を取得するAPIView
    
    目的：
        指定されたコードの全バージョン履歴を時系列順で取得する
    """
    serializer_class = CodeVersionHistorySerializer

    def get_queryset(self):
        """
        特定のコードの履歴を取得するメソッド
        
        処理：
        1. URLパラメータからコードを取得
        2. そのコードに関連する全履歴を取得
        3. 作成日時の降順でソート
        """
        code = self.kwargs['code']
        return CodeVersionHistory.objects.filter(
            code=code
        ).order_by('-datetime_created')  # 最新の履歴が先頭に来るようにソート

class AllCodeVersionHistoryView(generics.ListAPIView):
    """
    全てのコードのバージョン履歴を取得するAPIView
    
    目的：
        システム内の全てのコードバージョン履歴を
        時系列順で取得する
    """
    # 全ての履歴を作成日時の降順で取得
    queryset = CodeVersionHistory.objects.all().order_by('-datetime_created')
    serializer_class = CodeVersionHistorySerializer