# core/models.py
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """全モデルの基底クラス"""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
        help_text="レコードが作成された日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
        help_text="レコードが最後に更新された日時"
    )
    class Meta:
        abstract = True  # この設定により、このモデルは実際のテーブルを作成しない
        ordering = ['-created_at']