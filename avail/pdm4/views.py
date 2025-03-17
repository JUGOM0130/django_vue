from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status, generics
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