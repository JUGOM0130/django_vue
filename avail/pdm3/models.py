from django.db import models
from django.utils import timezone

class Node(models.Model):
    """個々のノードを表すモデル。ツリー内のすべてのノードが格納される"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name

class Tree(models.Model):
    """ツリー自体を表すモデル。使い回される"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name

class ParentChild(models.Model):
    """親子関係を管理する中間モデル。特定のツリー内での親子関係を表す"""
    parent = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='children')
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='parents')
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='relationships')
    level = models.IntegerField()  # 階層レベル
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.parent.name} -> {self.child.name} in {self.tree.name}"

    class Meta:
        unique_together = ('parent', 'child', 'tree')


class TreeInstance(models.Model):
    """特定の文脈で使い回されるツリーのインスタンス"""
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='instances')
    instance_name = models.CharField(max_length=100)
    instance_description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.instance_name
