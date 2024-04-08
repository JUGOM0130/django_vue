from django.db import models

# Create your models here.
class FruitCategoryMasta(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

    class Meta:
        verbose_name = 'フルーツカテゴリマスタ' # 複数系
        verbose_name_plural='フルーツカテゴリマスタ'    # 任意の複数系(管理画面で複数系にならないように指定)
