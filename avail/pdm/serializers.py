from rest_framework import serializers
from pdm.models import CodeHeader,Code,Tree,RootNode
from datetime import datetime


class CodeHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeHeader
        fields = ['id', 'code_header','create_at','update_at']

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = ['id','code_header','en_number','number','kind','code','create_at']

class RootNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RootNode
        fields = ['id','node_name','create_at','update_at']