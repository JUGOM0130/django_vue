# core/models.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField('作成日時', auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField('更新日時', auto_now=True, verbose_name="更新日時")

    class Meta:
        abstract = True  # この設定により、このモデルは実際のテーブルを作成しない