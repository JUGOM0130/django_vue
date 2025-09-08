# models.py
from django.db import models
from django.utils import timezone


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
        db_table = 'pdm_system_prefix'
        verbose_name = "プレフィックス"
        verbose_name_plural = "プレフィックス"
    
    def __str__(self):
        return f"{self.name}"
    
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
        db_table = 'pdm_system_code'
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
        db_table = 'pdm_system_code_version'
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
        db_table = 'pdm_system_code_change_log'
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
        db_table = 'pdm_system_code_metadata'
        verbose_name = "コードメタデータ"
        verbose_name_plural = "コードメタデータ"
    
    def __str__(self):
        return f"{self.code.code} - メタデータ"
