from rest_framework import serializers
from .models import Node, Tree, ParentChild, TreeInstance,Prefix,CodeVersion,CodeVersionHistory
from .models import Prefix

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'

class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'

class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = '__all__'

class TreeInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreeInstance
        fields = '__all__'



#
# コード生成に関して
#
#
class PrefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prefix
        fields = '__all__'

class CodeGenerationSerializer(serializers.Serializer):
    """{"prefix":"AAA"}"""
    prefix = serializers.CharField(max_length=10, help_text="Prefix for generating the code. Example: 'AAA'")

class CodeUpdateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50, help_text="Code to update. Example: 'AAA-A0001Z0000'")

class CodeVersionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeVersionHistory
        fields = '__all__'