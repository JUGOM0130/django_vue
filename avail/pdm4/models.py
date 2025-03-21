# Create your models here.
from django.db import models, transaction
from django.utils import timezone
from core.models import BaseModel
import math
"""
PDMシステムを作成します
プログラムコードを提示するときはコメントを記載してください。どんな処理をしているか
バックエンドはDjango Rest Frameworkを使用して作成します。
  レスポンスには必ずsuccessとmessageを返すようにしてください
  successはTrueかFalseで返し、messageはエラーメッセージや成功メッセージを返してください
フロントエンドはVuejs3のCompositionAPIを使用して作成します。
constraintsを使用してくださいuniquetogetherは非推奨です
verbose_nameやhelp_text等記載してください
modelのアプリ名にはPrefixとしてアプリケーション名を付加してください
【仕様】
コードの体系は下記
  PREFIX-A0001Z000  組
  PREFIX-AA0001Z000 部品
  PREFIX-A0001Z00   購入品
Prefixからコードを生成する機能
Code採番する機能
Codeの履歴管理をする機能
Treeを作成する機能(フロントエンド側で構築)
Treeの構造を別のツリーでも使い回せる機能
例)  Tree1
       AAA-A0001Z000
         AAA-A0002Z000
       AAA-A0010Z000
         AAA-A0011Z000
Tree1を登録した際にAAA-A0001Z000を他のツリーでも使い回せるようにしたい
Tree2でAAA-A0001Z000をノードに追加すると下記にようになるようにDB設計が必要
例)  Tree2
       AAA-A0001Z000
         AAA-A0002Z000
またTree2でAAA-A0001Z000の下位ノードを追加したり、変更したりした場合は他のツリー(Tree1)にもその変更が反映されるようにしたい

"""

class Prefix(BaseModel):
    """コード生成のためのプレフィックスモデル"""
    CODE_TYPE_CHOICES = [
        ('1', '組'),  # A0001Z000形式
        ('2', '部品'), # AA0001Z000形式
        ('3', '購入品'), # A0001Z00形式
    ]

    name = models.CharField(
        max_length=10, 
        verbose_name="プレフィックス",
        help_text="コード生成時の接頭辞（例：AAA）"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="説明",
        help_text="プレフィックスの用途や使用条件等の説明"
    )
    code_type = models.CharField(
        max_length=6,
        choices=CODE_TYPE_CHOICES,
        verbose_name="コード種別",
        help_text="生成されるコードの種類（組、部品、購入品）"
    )
    next_number = models.IntegerField(
        default=1,
        verbose_name="次の採番",
        help_text="次に割り当てる連番"
    )
    
    class Meta:
        verbose_name = "プレフィックス"
        verbose_name_plural = "プレフィックス"
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='pdm4_unique_prefix_name'
            )
        ]

    def __str__(self):
        return self.name

    def generate_code(self):
        """
        プレフィックスに基づいて新しいコードを生成する
        """
        # コードタイプに応じたフォーマットを定義
        format_map = {
            '1': 'A{:04d}Z000',    # 組
            '2': 'AA{:04d}Z000',   # 部品
            '3': 'A{:04d}Z00'      # 購入品
        }
        
        number_format = format_map.get(self.code_type)
        if not number_format:
            raise ValueError("無効なコードタイプです")
        
        # コードを生成
        code_part = number_format.format(self.next_number)
        full_code = f"{self.name}-{code_part}"
        
        # 次の番号を更新
        self.next_number += 1
        self.save()
        
        return full_code

    def reset_number(self, new_start=1):
        """
        採番をリセットする
        """
        self.next_number = new_start
        self.save()

    @property
    def code_type_display(self):
        """
        コードタイプの表示名を返す
        """
        return dict(self.CODE_TYPE_CHOICES).get(self.code_type, '')

    @property
    def format_example(self):
        """
        生成されるコードの例を返す
        """
        format_map = {
            '1': 'A0001Z000',    # 組
            '2': 'AA0001Z000',   # 部品
            '3': 'A0001Z00'      # 購入品
        }
        example = format_map.get(self.code_type, '')
        return f"{self.name}-{example}" if example else ""


class Code(BaseModel):
    """部品コードを表すモデル"""
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '有効'),
        ('obsolete', '廃止')
    ]

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="コード",
        help_text="生成された完全なコード文字列"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="コード名",
        help_text="部品コードの名称"
    )
    prefix = models.ForeignKey(
        Prefix,
        on_delete=models.PROTECT,  # プレフィックスの削除を禁止
        related_name="codes",
        verbose_name="プレフィックス",
        help_text="このコードが使用するプレフィックス"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="説明",
        help_text="コードの詳細説明"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="ステータス",
        help_text="コードの現在の状態"
    )
    sequential_number = models.IntegerField(
        verbose_name="連番",
        help_text="プレフィックス内での採番"
    )

    class Meta:
        verbose_name = "部品コード"
        verbose_name_plural = "部品コード"
        constraints = [
            models.UniqueConstraint(
                fields=['prefix', 'sequential_number'],
                name='pdm4_unique_code_number'
            ),
            models.UniqueConstraint(
                fields=['code'],
                name='pdm4_unique_code'
            )
        ]
        indexes = [
            models.Index(fields=['status'], name='pdm4_code_status_idx'),
            models.Index(fields=['code'], name='pdm4_code_idx')
        ]

    def __str__(self):
        return f"{self.code}: {self.name}"

    @classmethod
    def generate_new_code(cls, prefix, name, description=None):
        """
        新しいコードを生成して保存する
        """
        code_string = prefix.generate_code()
        return cls.objects.create(
            code=code_string,
            name=name,
            prefix=prefix,
            description=description,
            sequential_number=prefix.next_number - 1
        )

    def activate(self):
        """コードを有効化する"""
        if self.status == 'draft':
            self.status = 'active'
            self.save()
        else:
            raise ValueError("下書き状態のコードのみ有効化できます")

    def obsolete(self):
        """コードを廃止する"""
        if self.status == 'active':
            self.status = 'obsolete'
            self.save()
        else:
            raise ValueError("有効なコードのみ廃止できます")

    def get_current_version(self):
        """
        現在のバージョンを取得する
        """
        return self.versions.filter(is_current_version=True).first()

    def get_latest_version(self):
        """
        最新のバージョンを取得する
        """
        return self.versions.order_by('-version_number').first()

    def create_new_version(self, name=None, description=None, effective_date=None):
        """
        新しいバージョンを作成する
        """
        from django.utils import timezone
        
        latest_version = self.get_latest_version()
        new_version_number = 1 if not latest_version else latest_version.version_number + 1
        
        if not name:
            name = self.name
        if not description:
            description = self.description
        if not effective_date:
            effective_date = timezone.now()

        from .models import CodeVersion
        return CodeVersion.objects.create(
            code=self,
            version_number=new_version_number,
            name=name,
            description=description,
            effective_date=effective_date
        )

    @property
    def status_display(self):
        """ステータスの表示名を返す"""
        return dict(self.STATUS_CHOICES).get(self.status, '')

    @property
    def code_type(self):
        """コードタイプを返す"""
        return self.prefix.get_code_type_display()

    @property
    def version_count(self):
        """バージョン数を返す"""
        return self.versions.count()


class CodeVersion(BaseModel):
    """コードのバージョン管理モデル"""
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('review', 'レビュー中'),
        ('approved', '承認済み'),
        ('obsolete', '廃止')
    ]

    code = models.ForeignKey(
        Code, 
        on_delete=models.CASCADE, 
        related_name='versions',
        verbose_name="部品コード",
        help_text="バージョン管理対象のコード"
    )
    version = models.IntegerField(
        verbose_name="バージョン番号",
        help_text="コードのバージョン（1から順に増加）"
    )
    code_number = models.CharField(
        max_length=50,
        verbose_name="コード番号",
        help_text="生成された完全なコード番号（例：AAA-A0001Z000）"
    )
    is_current = models.BooleanField(
        default=True,
        verbose_name="現行バージョン",
        help_text="このバージョンが現在有効なバージョンかどうか"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="ステータス",
        help_text="このバージョンの承認状態"
    )
    reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name="変更理由",
        help_text="このバージョンでの変更内容と理由"
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="変更者",
        help_text="このバージョンを作成したユーザー"
    )
    effective_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="有効開始日",
        help_text="このバージョンが有効となる日時"
    )

    class Meta:
        verbose_name = "コードバージョン"
        verbose_name_plural = "コードバージョン"
        ordering = ['-version']
        constraints = [
            models.UniqueConstraint(
                fields=['code'],
                condition=models.Q(is_current=True),
                name='pdm4_unique_current_version'
            ),
            models.UniqueConstraint(
                fields=['code', 'version'],
                name='pdm4_unique_code_version'
            )
        ]
        indexes = [
            models.Index(fields=['code_number'], name='pdm4_cv_number_idx'),
            models.Index(fields=['code', '-version'], name='pdm4_cv_version_idx'),
            models.Index(fields=['status'], name='pdm4_cv_version_status_idx'),
            models.Index(fields=['effective_date'], name='pdm4_cv_effective_date_idx')
        ]

    def __str__(self):
        return f"{self.code_number} Ver.{self.version:04d}"

    def save(self, *args, **kwargs):
        """
        保存時の処理
        - 現行バージョンが変更された場合、他のバージョンの現行フラグを更新
        - 初回保存時にコード番号を設定
        """
        if not self.code_number:
            self.code_number = self.code.code

        if self.is_current:
            # 他のバージョンの現行フラグをオフにする
            CodeVersion.objects.filter(
                code=self.code,
                is_current=True
            ).exclude(id=self.id).update(is_current=False)

        super().save(*args, **kwargs)

    def approve(self, user):
        """バージョンを承認する"""
        if self.status != 'review':
            raise ValueError("レビュー中のバージョンのみ承認できます")
        self.status = 'approved'
        self.changed_by = user
        self.save()

    def submit_for_review(self, user):
        """レビューに提出する"""
        if self.status != 'draft':
            raise ValueError("下書き状態のバージョンのみレビューに提出できます")
        self.status = 'review'
        self.changed_by = user
        self.save()

    def make_obsolete(self, user, reason=None):
        """バージョンを廃止する"""
        if self.status not in ['approved', 'review']:
            raise ValueError("承認済みまたはレビュー中のバージョンのみ廃止できます")
        self.status = 'obsolete'
        if reason:
            self.reason = reason
        self.changed_by = user
        self.save()

    @property
    def status_display(self):
        """ステータスの表示名を返す"""
        return dict(self.STATUS_CHOICES).get(self.status, '')

    @property
    def is_editable(self):
        """編集可能かどうかを返す"""
        return self.status in ['draft']

    @property
    def is_reviewable(self):
        """レビュー可能かどうかを返す"""
        return self.status in ['review']

    @property
    def is_approvable(self):
        """承認可能かどうかを返す"""
        return self.status == 'review'

    def get_change_history(self):
        """変更履歴を取得する"""
        return {
            'version': self.version,
            'status': self.status_display,
            'changed_by': self.changed_by.get_full_name() if self.changed_by else None,
            'effective_date': self.effective_date,
            'reason': self.reason
        }


class CodeChangeLog(BaseModel):
    """コード変更履歴"""
    CHANGE_TYPE_CHOICES = [
        ('create', '新規作成'),
        ('version_up', 'バージョンアップ'),
        ('obsolete', '廃止'),
        ('status_change', 'ステータス変更'),
        ('review', 'レビュー提出'),
        ('approve', '承認'),
        ('reject', '却下')
    ]

    code_version = models.ForeignKey(
        CodeVersion,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name="コードバージョン",
        help_text="変更が発生したコードバージョン"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="変更日時",
        help_text="変更が行われた日時"
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="変更者",
        help_text="変更を行ったユーザー"
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        verbose_name="変更種別",
        help_text="実施された変更の種類"
    )
    reason = models.TextField(
        verbose_name="変更理由",
        help_text="変更を行った理由の詳細説明"
    )
    previous_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=CodeVersion.STATUS_CHOICES,
        verbose_name="変更前ステータス",
        help_text="ステータス変更前の状態"
    )
    new_status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=CodeVersion.STATUS_CHOICES,
        verbose_name="変更後ステータス",
        help_text="ステータス変更後の状態"
    )
    additional_info = models.JSONField(
        null=True,
        blank=True,
        verbose_name="追加情報",
        help_text="変更に関する追加情報をJSON形式で保存"
    )

    class Meta:
        verbose_name = "変更履歴"
        verbose_name_plural = "変更履歴"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['-changed_at'], name='pdm4_change_log_date_idx'),
            models.Index(fields=['change_type'], name='pdm4_change_type_idx'),
            models.Index(fields=['code_version', '-changed_at'], name='pdm4_version_change_idx')
        ]

    def __str__(self):
        return f"{self.code_version} - {self.get_change_type_display()} at {self.changed_at}"

    @classmethod
    def log_change(cls, code_version, user, change_type, reason, **kwargs):
        """
        変更履歴を記録する
        """
        additional_info = kwargs.pop('additional_info', None)
        previous_status = kwargs.pop('previous_status', None)
        new_status = kwargs.pop('new_status', None)

        return cls.objects.create(
            code_version=code_version,
            changed_by=user,
            change_type=change_type,
            reason=reason,
            previous_status=previous_status,
            new_status=new_status,
            additional_info=additional_info
        )

    @property
    def change_summary(self):
        """変更の要約を返す"""
        summary = {
            'type': self.get_change_type_display(),
            'date': self.changed_at,
            'user': self.changed_by.get_full_name() if self.changed_by else None,
            'reason': self.reason
        }

        if self.previous_status and self.new_status:
            summary['status_change'] = {
                'from': dict(CodeVersion.STATUS_CHOICES).get(self.previous_status),
                'to': dict(CodeVersion.STATUS_CHOICES).get(self.new_status)
            }

        if self.additional_info:
            summary['additional_info'] = self.additional_info

        return summary

    def get_formatted_change_info(self):
        """
        フォーマットされた変更情報を返す
        """
        change_info = f"{self.get_change_type_display()} - {self.changed_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        change_info += f"変更者: {self.changed_by.get_full_name() if self.changed_by else '未設定'}\n"
        
        if self.previous_status and self.new_status:
            change_info += f"ステータス変更: {dict(CodeVersion.STATUS_CHOICES).get(self.previous_status)} → {dict(CodeVersion.STATUS_CHOICES).get(self.new_status)}\n"
        
        change_info += f"理由: {self.reason}"
        return change_info

    @classmethod
    def get_version_history(cls, code_version):
        """
        特定のバージョンの変更履歴を全て取得
        """
        return cls.objects.filter(code_version=code_version).order_by('-changed_at')

    @classmethod
    def get_code_history(cls, code):
        """
        コードに関連する全バージョンの変更履歴を取得
        """
        return cls.objects.filter(
            code_version__code=code
        ).order_by('-changed_at')  


class CodeMetadata(BaseModel):
    """コードの基本属性情報"""
    UNIT_CHOICES = [
        ('piece', '個'),
        ('meter', 'm'),
        ('kilogram', 'kg'),
        ('liter', 'L'),
        ('set', 'セット'),
        ('sheet', '枚'),
        ('roll', '巻'),
        ('other', 'その他')
    ]

    CATEGORY_CHOICES = [
        ('mechanical', '機械部品'),
        ('electrical', '電気部品'),
        ('electronic', '電子部品'),
        ('hardware', 'ハードウェア'),
        ('material', '原材料'),
        ('tool', '工具'),
        ('consumable', '消耗品'),
        ('other', 'その他')
    ]

    code_version = models.OneToOneField(
        CodeVersion, 
        on_delete=models.CASCADE,
        related_name='metadata',
        verbose_name="コードバージョン",
        help_text="この属性情報が紐づくコードバージョン"
    )
    
    # 部品の基本属性情報
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default='piece',
        verbose_name="単位",
        help_text="部品の単位（個、m、kg等）"
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="材質",
        help_text="部品の材質情報（例：SUS304、A5052等）"
    )
    
    # その他のメタ情報
    keywords = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="キーワード",
        help_text="部品の検索用キーワード（カンマ区切りで複数指定可）"
    )
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="カテゴリ",
        help_text="部品の分類カテゴリ"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="備考",
        help_text="その他の補足情報"
    )
    specifications = models.JSONField(
        null=True,
        blank=True,
        verbose_name="仕様情報",
        help_text="部品の詳細仕様をJSON形式で保存"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="重量(kg)",
        help_text="部品の重量"
    )
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="寸法",
        help_text="部品の寸法情報（例：100x200x300mm）"
    )

    class Meta:
        verbose_name = "コード基本情報"
        verbose_name_plural = "コード基本情報"
        indexes = [
            models.Index(fields=['unit'], name='pdm4_metadata_unit_idx'),
            models.Index(fields=['material'], name='pdm4_metadata_material_idx'),
            models.Index(fields=['category'], name='pdm4_metadata_category_idx')
        ]

    def __str__(self):
        return f"{self.code_version} - {self.get_category_display()}"

    @property
    def keyword_list(self):
        """キーワードをリストとして取得"""
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    def get_specifications_value(self, key, default=None):
        """
        指定されたキーの仕様値を取得
        """
        if not self.specifications:
            return default
        return self.specifications.get(key, default)

    def update_specifications(self, updates):
        """
        仕様情報を更新
        """
        if not self.specifications:
            self.specifications = {}
        self.specifications.update(updates)
        self.save()

    def to_dict(self):
        """
        メタデータを辞書形式で取得
        """
        return {
            'unit': self.get_unit_display(),
            'material': self.material,
            'category': self.get_category_display(),
            'keywords': self.keyword_list,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'specifications': self.specifications or {},
            'notes': self.notes
        }

    @classmethod
    def get_by_material(cls, material):
        """
        指定された材質のメタデータを検索
        """
        return cls.objects.filter(material__icontains=material)

    @classmethod
    def get_by_category(cls, category):
        """
        指定されたカテゴリのメタデータを検索
        """
        return cls.objects.filter(category=category)

    @classmethod
    def search_by_keyword(cls, keyword):
        """
        キーワードでメタデータを検索
        """
        return cls.objects.filter(keywords__icontains=keyword)

    def copy_to_new_version(self, new_code_version):
        """
        新しいバージョンにメタデータをコピー
        """
        self.pk = None
        self.code_version = new_code_version
        self.save()
        return self


""
"Tree関係"
""
""
class Tree(BaseModel):
    """ツリー構造全体を管理するモデル（リファクタリング版）"""
    STATUS_CHOICES = [
        ('draft', '作成中'),
        ('active', '有効'),
        ('archived', 'アーカイブ'),
        ('locked', 'ロック中')
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ツリー名",
        help_text="ツリー構造の識別名"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="説明",
        help_text="ツリーの用途や特徴についての説明"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="状態",
        help_text="ツリーの現在の状態"
    )
    version = models.IntegerField(
        default=1,
        verbose_name="バージョン",
        help_text="ツリーのバージョン番号"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_trees',
        verbose_name="作成者"
    )
    last_modified_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_trees',
        verbose_name="最終更新者"
    )
    
    class Meta:
        verbose_name = "ツリー"
        verbose_name_plural = "ツリー"
        ordering = ['name']
        indexes = [
            models.Index(fields=['status'], name='pdm4_tree_status_idx'),
            models.Index(fields=['name'], name='pdm4_tree_name_idx')
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def save(self, *args, **kwargs):
        """ツリー保存時に自動的にルートノードを作成"""
        is_new = self.pk is None  # 新規作成かチェック
        
        with transaction.atomic():
            # 1. まずTreeを保存
            super().save(*args, **kwargs)
            
            # 2. 新規作成時のみ、ルートノードとツリー構造を作成
            if is_new:
                # ルートノードを作成
                root_node = TreeNode.objects.create(
                    name=f"{self.name}_ROOT",
                    description=f"ツリー「{self.name}」のルートノード",
                    node_type='root',
                    status='active'
                )
                
                # ツリー構造を作成
                TreeStructure.objects.create(
                    tree=self,
                    node=root_node,
                    parent=None,
                    level=0,
                    path=str(root_node.id),
                    is_master=True  # ルートノードはマスター
                )

class TreeNode(BaseModel):
    """ツリー構造のノードを表すモデル"""
    NODE_TYPE_CHOICES = [
        ('root', 'ルートノード'),
        ('code', 'コードノード'),   # 部品コードに関連付けられたノード
        ('group', 'グループノード')  # 単なるグループ化のためのノード
    ]
    
    STATUS_CHOICES = [
        ('draft', '下書き'),
        ('active', '有効'),
        ('obsolete', '廃止')
    ]

    name = models.CharField(
        max_length=100,
        verbose_name="ノード名",
        help_text="このノードの表示名"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="説明",
        help_text="このノードの説明"
    )
    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPE_CHOICES,
        default='code',
        verbose_name="ノードタイプ",
        help_text="ノードの種類（ルート、コード、グループ）"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="状態",
        help_text="ノードの現在の状態"
    )
    code = models.ForeignKey(
        'Code',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tree_nodes',
        verbose_name="関連コード",
        help_text="このノードに関連付けられた部品コード（ある場合）"
    )

    class Meta:
        verbose_name = "ツリーノード"
        verbose_name_plural = "ツリーノード"
        indexes = [
            models.Index(fields=['node_type'], name='pdm4_node_type_idx'),
            models.Index(fields=['status'], name='pdm4_node_status_idx'),
        ]

    def __str__(self):
        code_str = f" ({self.code.code})" if self.code else ""
        return f"{self.name}{code_str} - {self.get_node_type_display()}"
    
    @property
    def is_root(self):
        """ルートノードかどうかを判定"""
        return self.node_type == 'root'
    
    @property
    def is_group(self):
        """グループノードかどうかを判定"""
        return self.node_type == 'group'
    
    @property
    def has_code(self):
        """コードが関連付けられているかどうかを判定"""
        return self.code is not None



class TreeStructure(BaseModel):
    """ツリー構造の親子関係を管理するモデル（リファクタリング版）"""
    RELATIONSHIP_CHOICES = [
        ('assembly', '組立'),
        ('reference', '参照'),
        ('option', 'オプション'), 
        ('spare', '予備品'),
        ('alternate', '代替品'),
        ('phantom', 'ファントム')
    ]

    tree = models.ForeignKey(
        'Tree',
        on_delete=models.CASCADE,
        related_name='nodes',  # 関連名を変更
        verbose_name="所属ツリー",
        help_text="このノードが属するツリー"
    )
    node = models.ForeignKey(
        TreeNode,
        on_delete=models.CASCADE,
        related_name='structures',
        verbose_name="ノード",
        help_text="このツリー構造のノード"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="親構造",
        help_text="親ノードの構造（ルートノードの場合はnull）"
    )
    level = models.IntegerField(
        verbose_name="階層レベル",
        help_text="ツリー内での深さ（0がルート）"
    )
    path = models.CharField(
        max_length=255,
        verbose_name="パス",
        help_text="ルートからの経路をIDで表現（例: 1.2.3）"
    )
    sequence = models.IntegerField(
        default=0,
        verbose_name="表示順序",
        help_text="同じ階層内での表示順序"
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='assembly',
        verbose_name="関係タイプ",
        help_text="親子関係の種類を指定"
    )
    source_structure = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='shared_instances',
        verbose_name="共有元構造",
        help_text="この構造が共有している元の構造"
    )
    is_master = models.BooleanField(
        default=False,
        verbose_name="マスター構造",
        help_text="この構造が共有のマスターかどうか"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1.000,
        verbose_name="数量",
        help_text="この構造での使用数量"
    )
    effective_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="有効開始日",
        help_text="この構造が有効となる日時"
    )
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="有効終了日",
        help_text="この構造が無効となる日時"
    )

    class Meta:
        verbose_name = "ツリー構造"
        verbose_name_plural = "ツリー構造"
        unique_together = ('tree', 'node', 'parent')
        ordering = ['level', 'sequence']
        indexes = [
            models.Index(fields=['tree', 'level'], name='pdm4_tree_level_idx'),
            models.Index(fields=['path'], name='pdm4_path_idx'),
            models.Index(fields=['is_master'], name='pdm4_master_idx'),
        ]

    def __str__(self):
        parent_str = f" (親:{self.parent.node.name})" if self.parent else " (ルート)"
        return f"{self.tree.name} - {self.node.name}{parent_str}"

    def save(self, *args, **kwargs):
        """保存前の処理"""
        if not self.path and self.parent:
            # パスが未設定で親がある場合、親のパスを基に設定
            self.path = f"{self.parent.path}.{self.node.id}"
        elif not self.path:
            # ルートノードの場合
            self.path = str(self.node.id)
        
        super().save(*args, **kwargs)
class TreeVersion(BaseModel):
    """特定の文脈で使い回されるツリーのバージョン管理モデル"""
    STATUS_CHOICES = [
        ('draft', '作成中'),
        ('review', 'レビュー中'),
        ('approved', '承認済'),
        ('obsolete', '廃止'),
        ('rejected', '却下')
    ]

    tree = models.ForeignKey(
        Tree,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name="ツリー",
        help_text="バージョン管理対象のツリー"
    )
    version_number = models.IntegerField(
        verbose_name="バージョン番号",
        help_text="ツリーのバージョンを示す番号（自動採番）"
    )
    version_name = models.CharField(
        max_length=100,
        verbose_name="バージョン名",
        help_text="このバージョンの識別名"
    )
    version_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="バージョン説明",
        help_text="このバージョンでの変更内容や特記事項"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="状態",
        help_text="このバージョンの現在の状態"
    )
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_versions',
        verbose_name="作成者",
        help_text="このバージョンを作成したユーザー"
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_versions',
        verbose_name="承認者",
        help_text="このバージョンを承認したユーザー"
    )
    effective_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="有効開始日",
        help_text="このバージョンが有効となる日時"
    )
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="有効終了日",
        help_text="このバージョンが無効となる日時"
    )
    review_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name="レビューコメント",
        help_text="レビュー時のコメントや指摘事項"
    )
    change_summary = models.JSONField(
        null=True,
        blank=True,
        verbose_name="変更サマリー",
        help_text="前バージョンからの変更内容のサマリー"
    )

    class Meta:
        verbose_name = "ツリーバージョン"
        verbose_name_plural = "ツリーバージョン"
        constraints = [
            models.UniqueConstraint(
                fields=['tree', 'version_number'],
                name='pdm4_unique_tree_version'
            )
        ]
        indexes = [
            models.Index(fields=['-version_number'], name='pdm4_tv_number_idx'),
            models.Index(fields=['status'], name='pdm4_tv_status_idx'),
            models.Index(fields=['effective_date'], name='pdm4_tv_ver_effective_date_idx'),
            models.Index(fields=['expiry_date'], name='pdm4_tv_ver_expiry_date_idx')
        ]
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.tree.name} v{self.version_number}: {self.version_name}"

    def save(self, *args, **kwargs):
        """バージョン番号の自動採番処理"""
        if not self.version_number:
            latest_version = TreeVersion.objects.filter(
                tree=self.tree
            ).order_by('-version_number').first()
            self.version_number = (latest_version.version_number + 1) if latest_version else 1
        super().save(*args, **kwargs)

    def submit_for_review(self, user, comments=None):
        """レビューに提出"""
        if self.status != 'draft':
            raise ValueError("作成中のバージョンのみレビュー提出できます")
        self.status = 'review'
        if comments:
            self.review_comments = comments
        self.save()

    def approve(self, user, comments=None):
        """承認処理"""
        if self.status != 'review':
            raise ValueError("レビュー中のバージョンのみ承認できます")
        self.status = 'approved'
        self.approved_by = user
        if comments:
            self.review_comments = comments
        self.save()

    def reject(self, user, reason):
        """却下処理"""
        if self.status != 'review':
            raise ValueError("レビュー中のバージョンのみ却下できます")
        self.status = 'rejected'
        self.review_comments = reason
        self.save()

    def make_obsolete(self, user, reason=None):
        """廃止処理"""
        if self.status not in ['approved', 'review']:
            raise ValueError("承認済みまたはレビュー中のバージョンのみ廃止できます")
        self.status = 'obsolete'
        if reason:
            self.review_comments = reason
        self.expiry_date = timezone.now()
        self.save()

    def is_active(self):
        """現在有効かどうかを判定"""
        now = timezone.now()
        return (
            self.status == 'approved' and
            self.effective_date <= now and
            (not self.expiry_date or self.expiry_date > now)
        )

    def get_change_history(self):
        """変更履歴を取得"""
        return {
            'version_number': self.version_number,
            'version_name': self.version_name,
            'status': self.get_status_display(),
            'created_by': self.created_by.get_full_name() if self.created_by else None,
            'approved_by': self.approved_by.get_full_name() if self.approved_by else None,
            'effective_date': self.effective_date,
            'expiry_date': self.expiry_date,
            'description': self.version_description,
            'review_comments': self.review_comments,
            'changes': self.change_summary
        }

    def clone_to_new_version(self, user, version_name=None, description=None):
        """新しいバージョンとしてクローン"""
        new_version = TreeVersion.objects.create(
            tree=self.tree,
            version_name=version_name or f"{self.version_name} (Copy)",
            version_description=description,
            created_by=user,
            status='draft'
        )
        return new_version

class TreeCodeQuantity(BaseModel):
    """ツリー構造における部品の数量管理モデル"""
    UNIT_CHOICES = [
        ('piece', '個'),
        ('meter', 'm'),
        ('kilogram', 'kg'),
        ('liter', 'L'),
        ('set', 'セット'),
        ('sheet', '枚'),
        ('roll', '巻'),
        ('other', 'その他')
    ]

    tree_structure = models.ForeignKey(
        TreeStructure,
        on_delete=models.CASCADE,
        related_name='quantities',
        verbose_name="ツリー構造",
        help_text="数量情報が紐づくツリー構造"
    )
    code_version = models.ForeignKey(
        CodeVersion,
        on_delete=models.CASCADE,
        related_name='tree_quantities',
        verbose_name="コードバージョン",
        help_text="数量情報が紐づく部品コードのバージョン"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1.000,
        verbose_name="員数",
        help_text="組立に必要な数量"
    )
    denominator = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=1.000,
        verbose_name="母数",
        help_text="製品1台あたりの使用数"
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="piece",
        verbose_name="単位",
        help_text="数量の単位（個、m、kg等）"
    )
    loss_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name="ロス率(%)",
        help_text="予期される損失の割合"
    )
    minimum_order = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="最小発注量",
        help_text="一度に発注可能な最小数量"
    )
    remarks = models.TextField(
        blank=True,
        verbose_name="備考",
        help_text="数量に関する補足情報"
    )
    effective_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="有効開始日",
        help_text="この数量情報が有効となる日時"
    )
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="有効終了日",
        help_text="この数量情報が無効となる日時"
    )

    class Meta:
        verbose_name = "ツリー内数量情報"
        verbose_name_plural = "ツリー内数量情報"
        unique_together = ['tree_structure', 'code_version']
        indexes = [
            models.Index(fields=['quantity'], name='pdm4_quantity_idx'),
            models.Index(fields=['denominator'], name='pdm4_denominator_idx'),
            models.Index(fields=['unit'], name='pdm4_unit_idx'),
            models.Index(fields=['effective_date'], name='pdm4_qty_effective_date_idx'),
            models.Index(fields=['expiry_date'], name='pdm4_qty_expiry_date_idx')
        ]

    def clean(self):
        """バリデーション処理"""
        from django.core.exceptions import ValidationError
        
        if self.quantity <= 0:
            raise ValidationError({
                'quantity': '員数は0より大きい値である必要があります。'
            })
        if self.denominator <= 0:
            raise ValidationError({
                'denominator': '母数は0より大きい値である必要があります。'
            })
        if self.loss_rate < 0 or self.loss_rate > 100:
            raise ValidationError({
                'loss_rate': 'ロス率は0%から100%の間である必要があります。'
            })
        if self.minimum_order is not None and self.minimum_order <= 0:
            raise ValidationError({
                'minimum_order': '最小発注量は0より大きい値である必要があります。'
            })
        if self.effective_date and self.expiry_date:
            if self.effective_date >= self.expiry_date:
                raise ValidationError('有効開始日は有効終了日より前である必要があります。')

    def get_total_quantity(self):
        """総使用数量を計算（ロス率考慮）"""
        base_quantity = self.quantity / self.denominator
        return base_quantity * (1 + self.loss_rate / 100)

    def get_required_order_quantity(self, required_amount):
        """必要発注数量を計算"""
        total_needed = required_amount * self.get_total_quantity()
        
        if self.minimum_order:
            # 最小発注量以上になるように調整
            return max(
                self.minimum_order,
                math.ceil(total_needed * 1000) / 1000  # 小数第3位で切り上げ
            )
        return math.ceil(total_needed * 1000) / 1000

    def is_valid_at(self, date):
        """指定日時での有効性を判定"""
        return (
            self.effective_date <= date and
            (not self.expiry_date or self.expiry_date > date)
        )

    def copy_to_new_version(self, new_tree_structure, new_code_version):
        """新しいバージョンに数量情報をコピー"""
        self.pk = None
        self.tree_structure = new_tree_structure
        self.code_version = new_code_version
        self.effective_date = timezone.now()
        self.expiry_date = None
        self.save()
        return self

    def get_conversion_factor(self, target_unit):
        """単位変換係数を取得（未実装）"""
        # TODO: 単位変換テーブルを参照して変換係数を返す
        raise NotImplementedError("単位変換機能は未実装です")

    def __str__(self):
        return (
            f"{self.code_version} in {self.tree_structure} - "
            f"員数:{self.quantity}{self.get_unit_display()}/母数:{self.denominator} "
            f"(ロス率:{self.loss_rate}%)"
        )


class TreeChangeLog(BaseModel):
    """ツリー構造の変更履歴を管理するモデル"""

    # 変更タイプの選択肢を定数として定義
    CHANGE_TYPE_CHOICES = [
        ('add_node', 'ノード追加'),
        ('remove_node', 'ノード削除'),
        ('move_node', 'ノード移動'),
        ('update_quantity', '数量更新'),
        ('update_relationship', '関係タイプ更新'),
        ('share_structure', '構造共有'),
        ('unshare_structure', '構造共有解除'),
        ('update_metadata', 'メタデータ更新'),
        ('version_up', 'バージョンアップ'),
        ('status_change', 'ステータス変更'),
        ('approval_change', '承認状態変更'),
        ('comment_add', 'コメント追加')
    ]

    # 変更の重要度レベル
    SIGNIFICANCE_LEVELS = [
        (0, '軽微'),
        (1, '通常'),
        (2, '重要'),
        (3, '緊急')
    ]

    tree_version = models.ForeignKey(
        TreeVersion,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name="ツリーバージョン",
        help_text="変更が発生したツリーのバージョン"
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="変更日時",
        help_text="変更が行われた日時"
    )
    changed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='tree_changes',
        verbose_name="変更者",
        help_text="変更を実施したユーザー"
    )
    change_type = models.CharField(
        max_length=20,
        choices=CHANGE_TYPE_CHOICES,
        verbose_name="変更タイプ",
        help_text="実施された変更の種類"
    )
    description = models.TextField(
        verbose_name="変更内容",
        help_text="変更の詳細な説明"
    )
    affected_node = models.ForeignKey(
        Code,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='tree_changes',
        verbose_name="影響ノード",
        help_text="変更の影響を受けたノード"
    )
    previous_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="変更前データ",
        help_text="変更前の状態をJSON形式で保存"
    )
    new_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="変更後データ",
        help_text="変更後の状態をJSON形式で保存"
    )
    significance_level = models.IntegerField(
        choices=SIGNIFICANCE_LEVELS,
        default=1,
        verbose_name="重要度",
        help_text="変更の重要度レベル"
    )
    reference_documents = models.TextField(
        blank=True,
        verbose_name="関連文書",
        help_text="変更に関連する文書や図面の参照情報"
    )
    requires_approval = models.BooleanField(
        default=False,
        verbose_name="承認要否",
        help_text="この変更が承認を必要とするかどうか"
    )
    approved_by = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_changes',
        verbose_name="承認者"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="承認日時"
    )
    notification_sent = models.BooleanField(
        default=False,
        verbose_name="通知送信済み",
        help_text="関係者への通知が送信済みかどうか"
    )

    class Meta:
        verbose_name = "ツリー変更履歴"
        verbose_name_plural = "ツリー変更履歴"
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['-changed_at'], name='pdm4_tree_change_date_idx'),
            models.Index(fields=['change_type'], name='pdm4_tree_change_type_idx'),
            models.Index(fields=['significance_level'], name='pdm4_tree_significance_idx'),
            models.Index(fields=['affected_node'], name='pdm4_tree_affected_node_idx'),
            models.Index(fields=['requires_approval', 'approved_by'], name='pdm4_tree_approval_idx')
        ]

    def __str__(self):
        return f"{self.tree_version} - {self.get_change_type_display()} ({self.get_significance_level_display()}) at {self.changed_at}"

    def save(self, *args, **kwargs):
        """保存時の処理"""
        # 重要な変更タイプの場合、重要度と承認要否を自動設定
        if self.change_type in ['remove_node', 'share_structure', 'version_up']:
            self.significance_level = 2  # 重要
            self.requires_approval = True
        elif self.change_type in ['move_node', 'update_relationship']:
            self.significance_level = 1  # 通常
            self.requires_approval = True
        
        super().save(*args, **kwargs)
        
        # 重要な変更の場合は通知を送信
        if self.significance_level >= 2 and not self.notification_sent:
            self.notify_stakeholders()
            self.notification_sent = True
            self.save(update_fields=['notification_sent'])

    def get_change_summary(self):
        """変更の要約を生成"""
        return {
            'change_type': self.get_change_type_display(),
            'changed_by': str(self.changed_by),
            'changed_at': self.changed_at,
            'significance': self.get_significance_level_display(),
            'description': self.description,
            'affected_node': str(self.affected_node) if self.affected_node else None,
            'requires_approval': self.requires_approval,
            'approval_status': self.get_approval_status(),
            'reference_documents': self.reference_documents
        }

    def get_approval_status(self):
        """承認状態を取得"""
        if not self.requires_approval:
            return 'not_required'
        if self.approved_by:
            return 'approved'
        return 'pending'

    def notify_stakeholders(self):
        """関係者への通知処理"""
        from django.core.mail import send_mail
        stakeholders = self.get_stakeholders()
        
        subject = f"重要な変更通知: {self.get_change_type_display()}"
        message = self.get_notification_message()
        
        for stakeholder in stakeholders:
            send_mail(subject, message, None, [stakeholder.email])

    def get_notification_message(self):
        """通知メッセージ"""
    