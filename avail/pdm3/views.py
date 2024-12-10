from rest_framework import viewsets
from .models import Node, Tree, ParentChild, TreeInstance
from .serializers import NodeSerializer, TreeSerializer, ParentChildSerializer, TreeInstanceSerializer

class NodeViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class TreeViewSet(viewsets.ModelViewSet):
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

class ParentChildViewSet(viewsets.ModelViewSet):
    queryset = ParentChild.objects.all()
    serializer_class = ParentChildSerializer

class TreeInstanceViewSet(viewsets.ModelViewSet):
    queryset = TreeInstance.objects.all()
    serializer_class = TreeInstanceSerializer
