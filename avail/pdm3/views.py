from rest_framework import viewsets
from .models import (Node,
                    Tree,
                    TreeStructure,
                    TreeVersion,
                    Prefix,
                    CodeVersion,
                    CodeVersionHistory
                    )

from .serializers import (NodeSerializer,
                          TreeSerializer,
                          TreeStructureSerializer,
                          TreeVersionSerializer,
                          PrefixSerializer,
                          CodeUpdateSerializer,
                          CodeVersionHistorySerializer
                          )

class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class TreeViewSet(viewsets.ModelViewSet):
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

class TreeStructureViewSet(viewsets.ModelViewSet):
    queryset = TreeStructure.objects.all()
    serializer_class = TreeStructureSerializer

class TreeVersionViewSet(viewsets.ModelViewSet):
    queryset = TreeVersion.objects.all()
    serializer_class = TreeVersionSerializer

class PrefixViewSet(viewsets.ModelViewSet):
    """Prefix を登録する API"""
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer




"""
特殊なクラスベースビュー
"""
from rest_framework import viewsets, status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Prefix, CodeCounter, CodeVersion, CodeVersionHistory
from .serializers import PrefixSerializer, CodeGenerationSerializer, CodeUpdateSerializer, CodeVersionHistorySerializer
from .utils import generate_code,logger  # 必要な関数として用いる

class PrefixViewSet(viewsets.ModelViewSet):
    """Prefix の CRUD を提供する APIビュー"""
    queryset = Prefix.objects.all()
    serializer_class = PrefixSerializer


class CodeGenerationView(APIView):
    """
    Prefixに基づいてコードを生成し、CodeVersionモデルに登録するAPIビュー
    """
    def post(self, request, *args, **kwargs):
        serializer = CodeGenerationSerializer(data=request.data)
        if serializer.is_valid():
            prefix_id = serializer.validated_data["prefix"]
            try:
                prefix = Prefix.objects.get(id=prefix_id)
            except Prefix.DoesNotExist:
                return Response({"error": "Prefix not found"}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                code = generate_code(prefix)
                CodeVersion.objects.create(code=code, version=0)
                
                # 新しいノードを作成
                node = Node.objects.create(name=code, description=f"")
                
                # CodeVersionHistory にノードの ID を設定
                CodeVersionHistory.objects.create(code=code, version=0, node_id=node.id)
                
                return Response({"code": code}, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CodeVersion, CodeVersionHistory
from .serializers import CodeUpdateSerializer

class CodeUpdateView(APIView):
    """
    特定のコードのバージョンをインクリメントし、新しいコードを生成するAPIビュー。
    """
    def post(self, request, *args, **kwargs):
        # クライアントからのリクエストデータをシリアライズ
        serializer = CodeUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # シリアライズが成功した場合にコードを取得
            code = serializer.validated_data["code"]
            try:
                # 指定されたコードが存在するかをデータベースから確認
                code_version = CodeVersion.objects.get(code=code)
                
                # ログ出力 (デバッグ用)
                logger.debug(code_version)
                
                # バージョンをインクリメント
                code_version.version += 1
                
                # ログ出力 (デバッグ用)
                logger.debug(code_version.version)
                logger.debug("code[:-4]={}".format(code[:-4]))
                logger.debug(f"code_version.version:04d={code_version.version:04d}")
                
                # バージョン番号を更新した新しいコードを生成
                updated_code = f"{code[:-4]}{code_version.version:04d}"
                
                # 更新されたコードに置き換え
                code_version.code = updated_code
                code_version.save()
                
                # バージョン履歴に新しいコードを登録
                CodeVersionHistory.objects.create(code=updated_code, version=code_version.version)
                
                # 成功レスポンスを返す
                return Response({"updated_code": updated_code}, status=status.HTTP_200_OK)
            
            except CodeVersion.DoesNotExist:
                # 指定されたコードが存在しない場合のエラーレスポンス
                return Response({"error": "Code not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # シリアライズが失敗した場合のエラーレスポンス
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CodeVersionHistoryView(generics.ListAPIView):
    """
    特定のコードのバージョン履歴を取得するAPIビュー
    """
    serializer_class = CodeVersionHistorySerializer

    def get_queryset(self):
        code = self.kwargs['code']
        return CodeVersionHistory.objects.filter(code=code).order_by('-datetime_created')

class AllCodeVersionHistoryView(generics.ListAPIView):
    """
    全てのコードのバージョン履歴を取得するAPIビュー
    """
    queryset = CodeVersionHistory.objects.all().order_by('-datetime_created')
    serializer_class = CodeVersionHistorySerializer