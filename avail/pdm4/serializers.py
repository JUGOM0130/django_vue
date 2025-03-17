from rest_framework import serializers
from .models import Prefix,Code,CodeVersion,CodeChangeLog,CodeMetadata
from .models import Tree,TreeStructure,TreeVersion,TreeCodeQuantity,TreeChangeLog


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 全シリアライザで共通の設定
        fields = '__all__'
        # abstract = True  # これを設定すると、このクラス自体はシリアライザーとして使用できなくなります

class PrefixSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Prefix

class CodeSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Code

class CodeVersionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = CodeVersion

class CodeChangeLogSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = CodeChangeLog

class CodeMetadataSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = CodeMetadata

class TreeSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Tree

class TreeStructureSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TreeStructure

class TreeVersionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TreeVersion

class TreeCodeQuantitySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TreeCodeQuantity

class TreeChangeLogSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TreeChangeLog
