from django.db import models
from django.utils import timezone

class Node(models.Model):
    """個々のノードを表すモデル。ツリー内のすべてのノードが格納される"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")
    def __str__(self):
        return self.name

class Tree(models.Model):
    """ツリー自体を表すモデル"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")
    def __str__(self):
        return self.name

class ParentChild(models.Model):
    """親子関係を管理する中間モデル。特定のツリー内での親子関係を表す"""
    parent = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='children')
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='parents')
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='relationships')
    level = models.IntegerField()
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")

    def __str__(self):
        return f"{self.parent.name} -> {self.child.name} in {self.tree.name}"

    class Meta:
        unique_together = ('parent', 'child', 'tree')



class CodeHeader(models.Model):
    code_header = models.CharField(max_length=100,unique=True,verbose_name="カテゴリ名")
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")
    def __str__(self):
        return self.code_header
    
class Code(models.Model):
    code_header = models.ForeignKey(CodeHeader,on_delete=models.CASCADE) # CodeHeaderとのリレーション
    en_number = models.IntegerField(verbose_name="英番号")
    number = models.IntegerField(verbose_name="採番")
    kind = models.IntegerField(verbose_name="コード種別")
    code = models.CharField(max_length=100,unique=True,verbose_name="コード")
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")
    def __str__(self):
        return "kind={} en_number={} number={}".format(self.kind,self.en_number,self.number)
