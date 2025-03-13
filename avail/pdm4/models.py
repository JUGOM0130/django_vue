# Create your models here.
from django.db import models, transaction
from django.utils import timezone
from core.models import BaseModel


class Prefix(BaseModel):
    """コード生成のためのプレフィックスモデル"""
    CODE_TYPE_CHOICES = [
        ('1', '組'),
        ('2', '部品'),
        ('3', '購入品'),
    ]
    name = models.CharField(max_length=10, unique=True)  # プレフィックス名
    description = models.TextField(blank=True, null=True)  # プレフィックスの説明
    code_type = models.CharField(max_length=6, choices=CODE_TYPE_CHOICES)  # コードのタイプ
    
    def __str__(self):
        return self.name


class Code(BaseModel):
    """部品コードを表すモデル"""
    name = models.CharField(max_length=100)
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, related_name="codes")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '下書き'),
            ('active', '有効'),
            ('obsolete', '廃止')
        ],
        default='draft'
    )


    def __str__(self):
        return f"{self.name}"


class CodeVersion(BaseModel):
    """コードのバージョン管理モデル"""
    code = models.ForeignKey(
        Code, 
        on_delete=models.CASCADE, 
        related_name='versions',
        verbose_name="部品コード"
    )
    version = models.IntegerField(verbose_name="バージョン番号")
    code_number = models.CharField(
        max_length=50,
        verbose_name="コード番号",
        help_text="生成された完全なコード番号"
    )
    is_current = models.BooleanField(
        default=True,
        verbose_name="現行バージョン",
        help_text="現在有効なバージョンかどうか"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', '下書き'),
            ('review', 'レビュー中'),
            ('approved', '承認済み'),
            ('obsolete', '廃止')
        ],
        default='draft',
        verbose_name="ステータス"
    )
    reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name="変更理由"
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="変更者"
    )
    effective_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="有効開始日"
    )

    class Meta:
        verbose_name = "コードバージョン"
        verbose_name_plural = "コードバージョン"
        ordering = ['-version']
        constraints = [
            # 各コードの現在のバージョンは1つだけ
            models.UniqueConstraint(
                fields=['code'],
                condition=models.Q(is_current=True),
                name='unique_current_version'
            ),
            # 同じコードの同じバージョン番号は存在できない
            models.UniqueConstraint(
                fields=['code', 'version'],
                name='unique_code_version'
            )
        ]
        indexes = [
            models.Index(fields=['code_number']),
            models.Index(fields=['code', '-version']),
            models.Index(fields=['status']),
            models.Index(fields=['effective_date'])
        ]

    def __str__(self):
        return f"{self.code_number} Ver.{self.version:04d}"

class CodeChangeLog(BaseModel):
    """コード変更履歴"""
    code_version = models.ForeignKey(CodeVersion, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    change_type = models.CharField(
        max_length=20,
        choices=[
            ('create', '新規作成'),
            ('version_up', 'バージョンアップ'),
            ('obsolete', '廃止')
        ]
    )
    reason = models.TextField()

class CodeMetadata(BaseModel):
    """コードの基本属性情報"""
    code_version = models.OneToOneField(CodeVersion, on_delete=models.CASCADE)
    
    # 部品の基本属性情報
    unit = models.CharField(
        max_length=20,
        verbose_name="単位",
        default="個",
        help_text="部品の単位（個、m、kg等）"
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="材質"
    )
    
    # その他のメタ情報
    keywords = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "コード基本情報"
        verbose_name_plural = "コード基本情報"
        indexes = [
            models.Index(fields=['unit']),
            models.Index(fields=['material'])
        ]


class Tree(BaseModel):
    """ツリー自体を表すモデル。使い回される"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    # version = models.IntegerField(default=0)  # ツリーバージョン
    
    def save(self, *args, **kwargs):
        """
        ツリー保存時に自動的にルートノードを作成
        djangoadminサイトでもNodeが自動登録されるようにsaveメソッドをオーバーライド
        """
        is_new = self.pk is None  # 新規作成かチェック
        
        with transaction.atomic():
            # 1. まずTreeを保存
            super().save(*args, **kwargs)
            
            # 2. 新規作成時のみ、NodeとTreeStructureも作成
            if is_new:
                # ルートノードを作成
                root_node = Code.objects.create(
                    name=f"{self.name}",
                    description=f"Root node for tree: {self.name}"
                )
                # TreeStructureも作成（必須）
                TreeStructure.objects.create(
                    tree=self,
                    parent=None,  # ルートノードの親はNULL
                    child=root_node,  # ルートノードは自分が親でも子でも同じ
                    level=0
                )


class TreeStructure(BaseModel):
    """親子関係を管理する中間モデル。特定のツリー内での親子関係を表す"""
    parent = models.ForeignKey(Code, null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    child = models.ForeignKey(Code, null=True, blank=True, on_delete=models.CASCADE, related_name='parents')
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='relationships')
    level = models.IntegerField()  # 階層レベル
    

    def __str__(self):
        parent_name = self.parent.name if self.parent else "No Parent"
        child_name = self.child.name if self.child else "No Child"
        tree_name = self.tree.name if self.tree else "No Tree"
        return f"{parent_name} -> {child_name} in {tree_name} (Level: {self.level})"

    class Meta:
        unique_together = ('parent', 'child', 'tree')

class TreeVersion(BaseModel):
    """特定の文脈で使い回されるツリーのバージョン"""
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()  # バージョン番号を追加
    version_name = models.CharField(max_length=100)
    version_description = models.TextField(blank=True, null=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tree', 'version_number'],
                name='unique_tree_version'
            )
        ]
        indexes = [
            models.Index(fields=['-version_number'], name='version_number_desc_idx')
        ]
        ordering = ['-version_number']

    def save(self, *args, **kwargs):
        if not self.version_number:
            latest_version = TreeVersion.objects.filter(tree=self.tree).order_by('-version_number').first()
            self.version_number = (latest_version.version_number + 1) if latest_version else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tree.name} v{self.version_number}: {self.version_name}"
    

class TreeCodeQuantity(BaseModel):
    """ツリー構造における部品の数量情報"""
    tree_structure = models.ForeignKey(TreeStructure, on_delete=models.CASCADE)
    code_version = models.ForeignKey(CodeVersion, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="員数",
        help_text="組立に必要な数量"
    )
    denominator = models.PositiveIntegerField(
        default=1,
        verbose_name="母数",
        help_text="製品1台あたりの使用数"
    )

    class Meta:
        verbose_name = "ツリー内数量情報"
        verbose_name_plural = "ツリー内数量情報"
        unique_together = ['tree_structure', 'code_version']
        indexes = [
            models.Index(fields=['quantity']),
            models.Index(fields=['denominator'])
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantity <= 0:
            raise ValidationError({'quantity': '員数は1以上である必要があります。'})
        if self.denominator <= 0:
            raise ValidationError({'denominator': '母数は1以上である必要があります。'})

    def __str__(self):
        return (f"{self.code_version} in {self.tree_structure} - "
                f"員数:{self.quantity}/母数:{self.denominator}")


