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


class Prefix(models.Model):
    """コード生成のためのプレフィックスモデル"""
    CODE_TYPE_CHOICES = [
        ('1', '組'),
        ('2', '部品'),
        ('3', '購入品'),
    ]
    name = models.CharField(max_length=10, unique=True)  # プレフィックス名
    description = models.TextField(blank=True, null=True)  # プレフィックスの説明
    code_type = models.CharField(max_length=6, choices=CODE_TYPE_CHOICES)  # コードのタイプ
    create_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")  # レコードの作成日時
    update_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")  # レコードの更新日時

    def __str__(self):
        return self.name

class CodeCounter(models.Model):
    """プレフィックスごとのカウンターと版数を管理するモデル"""
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, related_name="counters")  # プレフィックスとの関連
    current_number = models.PositiveIntegerField(default=0)  # 現在の採番値
    current_version = models.PositiveIntegerField(default=0)  # 現在の版数

    def __str__(self):
        return f"{self.prefix.name}: {self.current_number}, Z{self.current_version}"

class CodeVersion(models.Model):
    """各コードごとに履歴管理されるテーブル"""
    code = models.CharField(max_length=50, unique=True)  # コード
    version = models.IntegerField(default=0)  # バージョン番号

    def __str__(self):
        return f"{self.code}, Z{self.version:04d}"

class CodeVersionHistory(models.Model):
    """コードのバージョン履歴を管理するテーブル"""
    code = models.CharField(max_length=50)  # バージョン履歴に含まれるコード
    version = models.IntegerField()  # バージョン番号
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")  # バージョンが作成された日時

    def __str__(self):
        return f"{self.code}, Z{self.version:04d} at {self.datetime_created}"