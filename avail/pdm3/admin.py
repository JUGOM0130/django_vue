from django.contrib import admin
from .models import Node,Tree,TreeStructure,TreeVersion,Prefix,CodeCounter,CodeVersion,CodeVersionHistory



# Nodeモデル用のカスタムAdminクラス
@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    # リスト表示画面でのカラム指定
    list_display = ('id', 'name',"create_at","update_at")
    
    # idをクリックして編集画面に遷移できるように設定
    list_display_links = ('id','name')

    # 検索対象のフィールド
    search_fields = ['name']
    
    # idで並び替え
    # ordering = ('id',)

    # 1ページあたりの表示件数
    list_per_page = 50

# Prefixモデル用のカスタムAdminクラス
@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    # リスト表示画面でのカラム指定
    list_display = ('id', 'name',"create_at","update_at")
    
    # idをクリックして編集画面に遷移できるように設定
    list_display_links = ('id','name')

    # 検索対象のフィールド
    search_fields = ['name']
    
    # idで並び替え
    # ordering = ('id',)

    # 1ページあたりの表示件数
    list_per_page = 50

# TreeStructureモデル用のカスタムAdminクラス
@admin.register(TreeStructure)
class TreeStructureAdmin(admin.ModelAdmin):
    # リスト表示画面でのカラム指定
    list_display = ('id', 'parent','tree','level',)
    
    # idをクリックして編集画面に遷移できるように設定
    list_display_links = ('id','parent')

    # 検索対象のフィールド
    search_fields = ['tree__name']

    # 1ページあたりの表示件数
    list_per_page = 50

# Treeモデル用のカスタムAdminクラス
@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    # リスト表示画面でのカラム指定
    list_display = ('id', 'name',)
    
    # idをクリックして編集画面に遷移できるように設定
    list_display_links = ('id','name')

    # 検索対象のフィールド
    search_fields = ['name']

    # 1ページあたりの表示件数
    list_per_page = 50

# TreeVersionモデル用のカスタムAdminクラス
@admin.register(TreeVersion)
class TreeVersionAdmin(admin.ModelAdmin):
    # リスト表示画面でのカラム指定
    list_display = ('id', 'tree',)
    
    # idをクリックして編集画面に遷移できるように設定
    list_display_links = ('id','tree')

    # 検索対象のフィールド
    search_fields = ['tree__name']

    # 1ページあたりの表示件数
    list_per_page = 50






# Register your models here.
models = [CodeCounter,CodeVersion,CodeVersionHistory]
admin.site.register(models)
