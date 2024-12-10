from rest_framework import serializers
from .models import Node, Tree, ParentChild, TreeInstance

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
