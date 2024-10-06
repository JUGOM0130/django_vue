from django.db import models

# Create your models here.

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

class Tree(models.Model):
    code = models.ForeignKey(Code,on_delete=models.CASCADE) # NumberManagementとのリレーション
    group_id = models.CharField(max_length=100)
    deep_level = models.IntegerField(verbose_name="階層")
    parent_id = models.IntegerField(verbose_name="親Id")
    
class RootNode(models.Model):
    node_name = models.CharField(max_length=100,unique=True)
    create_at = models.DateTimeField(blank=False, null=False, auto_now_add=True,verbose_name="作成日時")
    update_at = models.DateTimeField(blank=False, null=False, auto_now=True,verbose_name="更新日時")
   
    def __str__(self):
        return self.node_name