# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction


class Prefix(models.Model):
    """
    コードのプレフィックス管理モデル
    コード生成時のプレフィックス（接頭辞）とコードタイプを管理する
    """
    CODE_TYPE_CHOICES = [
        ('1', '組'),
        ('2', '部品'),
        ('3', '購入品'),
    ]
    
    name = models.CharField(max_length=50, unique=True, verbose_name="プレフィックス名")
    code_type = models.CharField(max_length=1, choices=CODE_TYPE_CHOICES, verbose_name="コードタイプ")
    next_number = models.IntegerField(default=1, verbose_name="次の番号")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'prefix'
        verbose_name = "プレフィックス"
        verbose_name_plural = "プレフィックス"
    
    def __str__(self):
        return f"{self.name} ({self.get_code_type_display()})"
    
    def generate_next_code(self):
        """
        次のコードを生成し、next_numberをインクリメント
        Returns: str - 生成されたコード
        """
        format_map = {
            '1': 'A{:04d}Z000',    # 組
            '2': 'AA{:04d}Z000',   # 部品
            '3': 'A{:04d}Z00'      # 購入品
        }
        
        code_format = format_map.get(self.code_type)
        if not code_format:
            raise ValueError(f"無効なコードタイプ: {self.code_type}")
        
        code_part = code_format.format(self.next_number)
        full_code = f"{self.name}-{code_part}"
        
        # next_numberをインクリメント
        self.next_number += 1
        self.save()
        
        return full_code


class Code(models.Model):
    """
    コード管理モデル
    システム内で使用される一意のコードを管理する
    """
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, verbose_name="プレフィックス")
    code = models.CharField(max_length=100, unique=True, verbose_name="コード")
    name = models.CharField(max_length=200, verbose_name="コード名")
    description = models.TextField(blank=True, verbose_name="説明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'code'
        verbose_name = "コード"
        verbose_name_plural = "コード"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class CodeVersion(models.Model):
    """
    コードのバージョン管理モデル
    コードの変更履歴とバージョン管理を行う
    """
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '有効'),
        ('inactive', '無効'),
        ('archived', 'アーカイブ'),
    ]
    
    code = models.ForeignKey(Code, on_delete=models.CASCADE, related_name='versions', verbose_name="コード")
    version = models.CharField(max_length=50, verbose_name="バージョン")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="ステータス")
    description = models.TextField(blank=True, verbose_name="変更内容")
    effective_date = models.DateTimeField(default=timezone.now, verbose_name="有効日")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        db_table = 'code_version'
        verbose_name = "コードバージョン"
        verbose_name_plural = "コードバージョン"
        unique_together = [['code', 'version']]
    
    def __str__(self):
        return f"{self.code.code} v{self.version}"


class CodeChangeLog(models.Model):
    """
    コード変更ログモデル
    コードに対する変更操作のログを記録する
    """
    ACTION_CHOICES = [
        ('create', '作成'),
        ('update', '更新'),
        ('delete', '削除'),
        ('version_create', 'バージョン作成'),
    ]
    
    code = models.ForeignKey(Code, on_delete=models.CASCADE, related_name='change_logs', verbose_name="コード")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作")
    old_value = models.JSONField(null=True, blank=True, verbose_name="変更前の値")
    new_value = models.JSONField(null=True, blank=True, verbose_name="変更後の値")
    change_reason = models.TextField(blank=True, verbose_name="変更理由")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="変更日時")  # auto_now_addをdefaultに変更
    
    class Meta:
        db_table = 'code_change_log'
        verbose_name = "コード変更ログ"
        verbose_name_plural = "コード変更ログ"
    
    def __str__(self):
        return f"{self.code.code} - {self.get_action_display()} ({self.timestamp})"


class CodeMetadata(models.Model):
    """
    コードメタデータモデル
    コードに関する追加情報やメタデータを格納する
    """
    code = models.OneToOneField(Code, on_delete=models.CASCADE, related_name='metadata', verbose_name="コード")
    category = models.CharField(max_length=100, blank=True, verbose_name="カテゴリ")
    tags = models.JSONField(default=list, blank=True, verbose_name="タグ")
    custom_fields = models.JSONField(default=dict, blank=True, verbose_name="カスタムフィールド")
    priority = models.IntegerField(default=0, verbose_name="優先度")
    external_id = models.CharField(max_length=100, blank=True, verbose_name="外部ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'code_metadata'
        verbose_name = "コードメタデータ"
        verbose_name_plural = "コードメタデータ"
    
    def __str__(self):
        return f"{self.code.code} - メタデータ"


class Tree(models.Model):
    """
    ツリー管理モデル
    階層構造を持つツリーの基本情報を管理する
    """
    name = models.CharField(max_length=200, verbose_name="ツリー名")
    description = models.TextField(blank=True, verbose_name="説明")
    is_active = models.BooleanField(default=True, verbose_name="有効フラグ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'tree'
        verbose_name = "ツリー"
        verbose_name_plural = "ツリー"
    
    def __str__(self):
        return self.name
    
    def get_root_structures(self):
        """
        ツリーのルート構造（親がないもの）を取得
        Returns: QuerySet - ルート構造のクエリセット
        """
        return self.structures.filter(parent__isnull=True).order_by('sequence')


class SharedStructureGroup(models.Model):
    """
    共有構造グループモデル
    複数のツリー間で共有される構造のグループを管理する
    """
    name = models.CharField(max_length=200, verbose_name="グループ名")
    description = models.TextField(blank=True, verbose_name="説明")
    root_node = models.ForeignKey('TreeNode', on_delete=models.CASCADE, verbose_name="ルートノード")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'shared_structure_group'
        verbose_name = "共有構造グループ"
        verbose_name_plural = "共有構造グループ"
    
    def __str__(self):
        return f"共有グループ: {self.name}"
    
    def get_participating_trees(self):
        """
        このグループに参加しているツリーを取得
        Returns: QuerySet - 参加ツリーのクエリセット
        """
        return Tree.objects.filter(
            structures__shared_group=self
        ).distinct()


class TreeNode(models.Model):
    """
    ツリーノードモデル
    ツリー構造の実際のノード（データ）を管理する
    共有される実体データを格納する
    """
    name = models.CharField(max_length=200, verbose_name="ノード名")
    description = models.TextField(blank=True, verbose_name="説明")
    node_type = models.CharField(max_length=50, default='default', verbose_name="ノードタイプ")
    attributes = models.JSONField(default=dict, blank=True, verbose_name="属性")
    code = models.ForeignKey(Code, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="関連コード")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'tree_node'
        verbose_name = "ツリーノード"
        verbose_name_plural = "ツリーノード"
    
    def __str__(self):
        return self.name
    
    def get_shared_structures(self):
        """
        このノードを使用している全ての構造を取得
        Returns: QuerySet - 構造のクエリセット
        """
        return TreeStructure.objects.filter(node=self)


class TreeStructure(models.Model):
    """
    ツリー構造モデル
    ツリー内でのノードの配置と関係性を管理する
    共有構造の参照情報も含む
    """
    SHARING_TYPE_CHOICES = [
        ('independent', '独立'),
        ('shared', '共有'),
    ]
    
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='structures', verbose_name="ツリー")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name="親構造")
    node = models.ForeignKey(TreeNode, on_delete=models.CASCADE, verbose_name="ノード")
    level = models.IntegerField(default=0, verbose_name="階層レベル")
    sequence = models.IntegerField(default=0, verbose_name="並び順")
    path = models.CharField(max_length=500, blank=True, verbose_name="パス")
    sharing_type = models.CharField(max_length=20, choices=SHARING_TYPE_CHOICES, 
                                   default='independent', verbose_name="共有タイプ")
    shared_group = models.ForeignKey(SharedStructureGroup, on_delete=models.CASCADE, 
                                    null=True, blank=True, verbose_name="共有グループ")
    group_relative_path = models.CharField(max_length=200, blank=True, verbose_name="グループ内相対パス")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'tree_structure'
        verbose_name = "ツリー構造"
        verbose_name_plural = "ツリー構造"
        unique_together = [['tree', 'parent', 'sequence']]
    
    def __str__(self):
        return f"{self.tree.name} - {self.node.name} (Lv.{self.level})"
    
    def save(self, *args, **kwargs):
        """
        保存時にパスとレベルを自動計算
        """
        if self.parent:
            self.level = self.parent.level + 1
            if self.parent.path:
                self.path = f"{self.parent.path}.{self.parent.id}"
            else:
                self.path = str(self.parent.id)
        else:
            self.level = 0
            self.path = ""
        
        super().save(*args, **kwargs)
    
    def get_descendants(self):
        """
        この構造の全ての子孫構造を取得
        Returns: QuerySet - 子孫構造のクエリセット
        """
        return TreeStructure.objects.filter(
            tree=self.tree,
            path__startswith=f"{self.path}.{self.id}" if self.path else str(self.id)
        ).order_by('level', 'sequence')
    
    def is_shared(self):
        """
        この構造が共有構造かどうかを判定
        Returns: bool - 共有構造の場合True
        """
        return self.sharing_type == 'shared' and self.shared_group is not None
    
    def get_sibling_shared_structures(self):
        """
        同じ共有グループに属する他のツリーの対応構造を取得
        Returns: QuerySet - 兄弟共有構造のクエリセット
        """
        if not self.is_shared():
            return TreeStructure.objects.none()
        
        return TreeStructure.objects.filter(
            shared_group=self.shared_group,
            group_relative_path=self.group_relative_path
        ).exclude(id=self.id)


class TreeVersion(models.Model):
    """
    ツリーバージョン管理モデル
    ツリー全体の変更履歴とバージョンを管理する
    """
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '有効'),
        ('archived', 'アーカイブ'),
    ]
    
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='versions', verbose_name="ツリー")
    version = models.CharField(max_length=50, verbose_name="バージョン")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="ステータス")
    description = models.TextField(blank=True, verbose_name="変更内容")
    snapshot_data = models.JSONField(default=dict, verbose_name="スナップショットデータ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    
    class Meta:
        db_table = 'tree_version'
        verbose_name = "ツリーバージョン"
        verbose_name_plural = "ツリーバージョン"
        unique_together = [['tree', 'version']]
    
    def __str__(self):
        return f"{self.tree.name} v{self.version}"


class TreeCodeQuantity(models.Model):
    """
    ツリーコード数量モデル
    ツリー内の各コードの数量情報を管理する
    """
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, verbose_name="ツリー")
    structure = models.ForeignKey(TreeStructure, on_delete=models.CASCADE, verbose_name="構造")
    code = models.ForeignKey(Code, on_delete=models.CASCADE, verbose_name="コード")
    quantity = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="数量")
    unit = models.CharField(max_length=20, default='個', verbose_name="単位")
    notes = models.TextField(blank=True, verbose_name="備考")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    
    class Meta:
        db_table = 'tree_code_quantity'
        verbose_name = "ツリーコード数量"
        verbose_name_plural = "ツリーコード数量"
        unique_together = [['tree', 'structure', 'code']]
    
    def __str__(self):
        return f"{self.tree.name} - {self.code.code}: {self.quantity}{self.unit}"


class TreeChangeLog(models.Model):
    """
    ツリー変更ログモデル
    ツリーの構造変更操作のログを記録する
    """
    ACTION_CHOICES = [
        ('structure_add', '構造追加'),
        ('structure_remove', '構造削除'),
        ('structure_move', '構造移動'),
        ('node_update', 'ノード更新'),
        ('share_create', '共有作成'),
        ('share_join', '共有参加'),
        ('share_leave', '共有離脱'),
    ]
    
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='change_logs', verbose_name="ツリー")
    structure = models.ForeignKey(TreeStructure, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="対象構造")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作")
    old_value = models.JSONField(null=True, blank=True, verbose_name="変更前の値")
    new_value = models.JSONField(null=True, blank=True, verbose_name="変更後の値")
    change_reason = models.TextField(blank=True, verbose_name="変更理由")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="変更日時")  # auto_now_addをdefaultに変更
    
    class Meta:
        db_table = 'tree_change_log'
        verbose_name = "ツリー変更ログ"
        verbose_name_plural = "ツリー変更ログ"
    
    def __str__(self):
        return f"{self.tree.name} - {self.get_action_display()} ({self.timestamp})"