# serializers.py
"""
コード管理システムのシリアライザー
APIのリクエスト/レスポンスデータの変換とバリデーションを担当
"""
from rest_framework import serializers
from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata
)


class PrefixSerializer(serializers.ModelSerializer):
    """
    プレフィックス管理のシリアライザー
    
    機能説明:
    - コード生成時のプレフィックス情報をシリアライズ
    - 全フィールドを対象とした基本的なCRUD操作をサポート
    """
    
    class Meta:
        model = Prefix
        fields = '__all__'


class CodeSerializer(serializers.ModelSerializer):
    """
    コード管理のシリアライザー
    
    機能説明:
    - コードの基本情報をシリアライズ
    - 全フィールドを対象とした基本的なCRUD操作をサポート
    """
    
    class Meta:
        model = Code
        fields = '__all__'


class CodeVersionSerializer(serializers.ModelSerializer):
    """
    コードバージョン管理のシリアライザー
    
    機能説明:
    - コードのバージョン情報をシリアライズ
    - 全フィールドを対象とした基本的なCRUD操作をサポート
    """
    
    class Meta:
        model = CodeVersion
        fields = '__all__'


class CodeChangeLogSerializer(serializers.ModelSerializer):
    """
    コード変更ログのシリアライザー
    
    機能説明:
    - コードの変更履歴をシリアライズ
    - 全フィールドを対象とした基本的なCRUD操作をサポート
    """
    
    class Meta:
        model = CodeChangeLog
        fields = '__all__'


class CodeMetadataSerializer(serializers.ModelSerializer):
    """
    コードメタデータのシリアライザー
    
    機能説明:
    - コードの追加情報をシリアライズ
    - 全フィールドを対象とした基本的なCRUD操作をサポート
    """
    
    class Meta:
        model = CodeMetadata
        fields = '__all__'