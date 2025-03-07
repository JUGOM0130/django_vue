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
            parent_node = Node.objects.get(id=parent_id)
            
            # 親ノードがこのツリーに属しているか確認
            if not TreeStructure.objects.filter(
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
                parent_level = TreeStructure.objects.get(
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