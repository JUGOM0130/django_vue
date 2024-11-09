from rest_framework import serializers
from pdm2.models import CodeHeader,Code,Tree,Node,ParentChild

class CodeHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeHeader
        fields = ['id', 'code_header','create_at','update_at']

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ['id','code_header','en_number','number','kind','code','create_at']

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ['name','description','create_at','update_at']

class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = ['name','description','create_at','update_at']

class ParentChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChild
        fields = ['parent','child','tree','level','create_at','update_at']