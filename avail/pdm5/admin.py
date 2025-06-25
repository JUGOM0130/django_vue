# admin.py
"""
Django共有ツリー構造システム - 管理画面設定
管理者がWebインターフェースからデータを管理できるようにする
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.contrib.admin import SimpleListFilter

from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata,
    Tree, TreeNode, TreeStructure, TreeVersion, TreeCodeQuantity, 
    TreeChangeLog, SharedStructureGroup
)


# ==========================================
# カスタムフィルタークラス
# ==========================================

class SharedStructureFilter(SimpleListFilter):
    """
    共有構造フィルター
    構造が共有されているかどうかでフィルタリング
    """
    title = '共有状態'
    parameter_name = 'is_shared'

    def lookups(self, request, model_admin):
        return (
            ('shared', '共有構造'),
            ('independent', '独立構造'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'shared':
            return queryset.filter(sharing_type='shared')
        if self.value() == 'independent':
            return queryset.filter(sharing_type='independent')
        return queryset


class ActiveVersionFilter(SimpleListFilter):
    """
    アクティブバージョンフィルター
    """
    title = 'バージョン状態'
    parameter_name = 'version_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'アクティブ'),
            ('draft', '下書き'),
            ('inactive', '無効'),
            ('archived', 'アーカイブ'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


# ==========================================
# Code関連の管理画面
# ==========================================

@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    """
    プレフィックス管理画面
    コード生成時のプレフィックスを管理
    """
    list_display = [
        'name', 'get_code_type_display', 'next_number', 
        'get_generated_codes_count', 'created_at'
    ]
    list_filter = ['code_type', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'code_type', 'next_number')
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_generated_codes_count(self, obj):
        """
        このプレフィックスで生成されたコード数を取得
        """
        count = obj.code_set.count()
        if count > 0:
            url = reverse('admin:shared_tree_code_changelist') + f'?prefix__id__exact={obj.id}'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_generated_codes_count.short_description = '生成コード数'
    get_generated_codes_count.admin_order_field = 'code_set__count'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            code_count=Count('code_set')
        )


@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    """
    コード管理画面
    システム内のコードを管理
    """
    list_display = [
        'code', 'name', 'prefix', 'get_latest_version', 
        'get_versions_count', 'created_at'
    ]
    list_filter = ['prefix', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['prefix']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('prefix', 'code', 'name', 'description')
        }),
        ('作成情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_latest_version(self, obj):
        """
        最新バージョンを取得
        """
        latest = obj.versions.filter(status='active').first()
        if latest:
            return f"{latest.version} ({latest.get_status_display()})"
        return "バージョンなし"
    
    get_latest_version.short_description = '最新バージョン'
    
    def get_versions_count(self, obj):
        """
        バージョン数を取得
        """
        count = obj.versions.count()
        if count > 0:
            url = reverse('admin:shared_tree_codeversion_changelist') + f'?code__id__exact={obj.id}'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_versions_count.short_description = 'バージョン数'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'prefix'
        ).prefetch_related('versions')


@admin.register(CodeVersion)
class CodeVersionAdmin(admin.ModelAdmin):
    """
    コードバージョン管理画面
    コードのバージョン情報を管理
    """
    list_display = [
        'get_code_display', 'version', 'status', 'effective_date', 'created_at'
    ]
    list_filter = [ActiveVersionFilter, 'effective_date', 'created_at']
    search_fields = ['code__code', 'code__name', 'version', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['code']
    date_hierarchy = 'effective_date'
    
    fieldsets = (
        ('バージョン情報', {
            'fields': ('code', 'version', 'status', 'effective_date')
        }),
        ('詳細情報', {
            'fields': ('description',)
        }),
        ('作成情報', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_code_display(self, obj):
        """
        コード表示用フォーマット
        """
        return f"{obj.code.code} - {obj.code.name}"
    
    get_code_display.short_description = 'コード'
    get_code_display.admin_order_field = 'code__code'
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """
        選択されたバージョンをアクティブにする
        """
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} 件のバージョンをアクティブにしました。')
    
    make_active.short_description = '選択されたバージョンをアクティブにする'
    
    def make_inactive(self, request, queryset):
        """
        選択されたバージョンを無効にする
        """
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} 件のバージョンを無効にしました。')
    
    make_inactive.short_description = '選択されたバージョンを無効にする'


@admin.register(CodeChangeLog)
class CodeChangeLogAdmin(admin.ModelAdmin):
    """
    コード変更ログ管理画面（読み取り専用）
    コードの変更履歴を参照
    """
    list_display = [
        'get_code_display', 'get_action_display', 'timestamp'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['code__code', 'code__name', 'change_reason']
    readonly_fields = ['code', 'action', 'old_value', 'new_value', 'change_reason', 'timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def get_code_display(self, obj):
        """
        コード表示用フォーマット
        """
        return f"{obj.code.code} - {obj.code.name}"
    
    get_code_display.short_description = 'コード'
    get_code_display.admin_order_field = 'code__code'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CodeMetadata)
class CodeMetadataAdmin(admin.ModelAdmin):
    """
    コードメタデータ管理画面
    コードの追加情報を管理
    """
    list_display = [
        'get_code_display', 'category', 'priority', 'external_id', 'updated_at'
    ]
    list_filter = ['category', 'priority', 'created_at', 'updated_at']
    search_fields = ['code__code', 'code__name', 'category', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['code']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('code', 'category', 'priority', 'external_id')
        }),
        ('詳細情報', {
            'fields': ('tags', 'custom_fields')
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_code_display(self, obj):
        """
        コード表示用フォーマット
        """
        return f"{obj.code.code} - {obj.code.name}"
    
    get_code_display.short_description = 'コード'
    get_code_display.admin_order_field = 'code__code'


# ==========================================
# Tree関連の管理画面
# ==========================================

@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    """
    ツリー管理画面
    ツリーの基本情報を管理
    """
    list_display = [
        'name', 'is_active', 'get_structures_count', 'get_shared_structures_count',
        'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('作成情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_structures_count(self, obj):
        """
        構造数を取得
        """
        count = obj.structures.count()
        if count > 0:
            url = reverse('admin:shared_tree_treestructure_changelist') + f'?tree__id__exact={obj.id}'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_structures_count.short_description = '構造数'
    
    def get_shared_structures_count(self, obj):
        """
        共有構造数を取得
        """
        count = obj.structures.filter(sharing_type='shared').count()
        if count > 0:
            url = reverse('admin:shared_tree_treestructure_changelist') + f'?tree__id__exact={obj.id}&sharing_type=shared'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_shared_structures_count.short_description = '共有構造数'
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """
        選択されたツリーをアクティブにする
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} 件のツリーをアクティブにしました。')
    
    make_active.short_description = '選択されたツリーをアクティブにする'
    
    def make_inactive(self, request, queryset):
        """
        選択されたツリーを無効にする
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} 件のツリーを無効にしました。')
    
    make_inactive.short_description = '選択されたツリーを無効にする'


@admin.register(TreeNode)
class TreeNodeAdmin(admin.ModelAdmin):
    """
    ツリーノード管理画面
    ツリーの実際のノードデータを管理
    """
    list_display = [
        'name', 'node_type', 'get_code_display', 'get_structures_count', 'created_at'
    ]
    list_filter = ['node_type', 'created_at']
    search_fields = ['name', 'description', 'code__code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['code']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'description', 'node_type', 'code')
        }),
        ('属性情報', {
            'fields': ('attributes',)
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_code_display(self, obj):
        """
        関連コード表示
        """
        if obj.code:
            return f"{obj.code.code} - {obj.code.name}"
        return "コードなし"
    
    get_code_display.short_description = '関連コード'
    
    def get_structures_count(self, obj):
        """
        このノードを使用している構造数を取得
        """
        count = obj.treestructure_set.count()
        if count > 0:
            url = reverse('admin:shared_tree_treestructure_changelist') + f'?node__id__exact={obj.id}'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_structures_count.short_description = '使用構造数'


@admin.register(TreeStructure)
class TreeStructureAdmin(admin.ModelAdmin):
    """
    ツリー構造管理画面
    ツリー内でのノード配置と関係性を管理
    """
    list_display = [
        'get_tree_node_display', 'tree', 'level', 'sequence', 
        'get_sharing_type_display', 'get_shared_group_display', 'created_at'
    ]
    list_filter = [SharedStructureFilter, 'level', 'tree', 'created_at']
    search_fields = ['tree__name', 'node__name', 'path']
    readonly_fields = ['level', 'path', 'created_at', 'updated_at']
    ordering = ['tree', 'level', 'sequence']
    raw_id_fields = ['tree', 'parent', 'node', 'shared_group']
    
    fieldsets = (
        ('構造情報', {
            'fields': ('tree', 'parent', 'node', 'sequence')
        }),
        ('共有情報', {
            'fields': ('sharing_type', 'shared_group', 'group_relative_path')
        }),
        ('自動生成情報', {
            'fields': ('level', 'path', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_tree_node_display(self, obj):
        """
        ツリーとノードの表示
        """
        return f"{obj.tree.name} - {obj.node.name}"
    
    get_tree_node_display.short_description = 'ツリー - ノード'
    
    def get_shared_group_display(self, obj):
        """
        共有グループ表示
        """
        if obj.shared_group:
            url = reverse('admin:shared_tree_sharedstructuregroup_change', args=[obj.shared_group.id])
            return format_html('<a href="{}">{}</a>', url, obj.shared_group.name)
        return "共有なし"
    
    get_shared_group_display.short_description = '共有グループ'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tree', 'parent', 'node', 'shared_group'
        )


@admin.register(SharedStructureGroup)
class SharedStructureGroupAdmin(admin.ModelAdmin):
    """
    共有構造グループ管理画面
    構造の共有グループ情報を管理
    """
    list_display = [
        'name', 'get_root_node_display', 'get_participating_trees_count', 
        'get_structures_count', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['name', 'description', 'root_node__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['root_node']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'description', 'root_node')
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_root_node_display(self, obj):
        """
        ルートノード表示
        """
        return f"{obj.root_node.name} ({obj.root_node.node_type})"
    
    get_root_node_display.short_description = 'ルートノード'
    
    def get_participating_trees_count(self, obj):
        """
        参加ツリー数を取得
        """
        count = obj.get_participating_trees().count()
        return f"{count} 件"
    
    get_participating_trees_count.short_description = '参加ツリー数'
    
    def get_structures_count(self, obj):
        """
        関連構造数を取得
        """
        count = TreeStructure.objects.filter(shared_group=obj).count()
        if count > 0:
            url = reverse('admin:shared_tree_treestructure_changelist') + f'?shared_group__id__exact={obj.id}'
            return format_html('<a href="{}">{} 件</a>', url, count)
        return '0 件'
    
    get_structures_count.short_description = '関連構造数'


@admin.register(TreeVersion)
class TreeVersionAdmin(admin.ModelAdmin):
    """
    ツリーバージョン管理画面
    ツリーのバージョン情報を管理
    """
    list_display = [
        'get_tree_version_display', 'status', 'created_at'
    ]
    list_filter = [ActiveVersionFilter, 'created_at']
    search_fields = ['tree__name', 'version', 'description']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    raw_id_fields = ['tree']
    
    fieldsets = (
        ('バージョン情報', {
            'fields': ('tree', 'version', 'status')
        }),
        ('詳細情報', {
            'fields': ('description', 'snapshot_data')
        }),
        ('作成情報', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_tree_version_display(self, obj):
        """
        ツリーバージョン表示
        """
        return f"{obj.tree.name} v{obj.version}"
    
    get_tree_version_display.short_description = 'ツリー - バージョン'
    get_tree_version_display.admin_order_field = 'tree__name'


@admin.register(TreeCodeQuantity)
class TreeCodeQuantityAdmin(admin.ModelAdmin):
    """
    ツリーコード数量管理画面
    ツリー内のコード数量情報を管理
    """
    list_display = [
        'get_tree_display', 'get_structure_display', 'get_code_display', 
        'quantity', 'unit', 'updated_at'
    ]
    list_filter = ['unit', 'tree', 'created_at', 'updated_at']
    search_fields = ['tree__name', 'structure__node__name', 'code__code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    raw_id_fields = ['tree', 'structure', 'code']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('tree', 'structure', 'code')
        }),
        ('数量情報', {
            'fields': ('quantity', 'unit', 'notes')
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_tree_display(self, obj):
        return obj.tree.name
    
    get_tree_display.short_description = 'ツリー'
    get_tree_display.admin_order_field = 'tree__name'
    
    def get_structure_display(self, obj):
        return obj.structure.node.name
    
    get_structure_display.short_description = '構造'
    get_structure_display.admin_order_field = 'structure__node__name'
    
    def get_code_display(self, obj):
        return f"{obj.code.code} - {obj.code.name}"
    
    get_code_display.short_description = 'コード'
    get_code_display.admin_order_field = 'code__code'


@admin.register(TreeChangeLog)
class TreeChangeLogAdmin(admin.ModelAdmin):
    """
    ツリー変更ログ管理画面（読み取り専用）
    ツリーの変更履歴を参照
    """
    list_display = [
        'get_tree_display', 'get_structure_display', 'get_action_display', 
        'timestamp'
    ]
    list_filter = ['action', 'timestamp', 'tree']
    search_fields = ['tree__name', 'structure__node__name', 'change_reason']
    readonly_fields = ['tree', 'structure', 'action', 'old_value', 'new_value', 'change_reason', 'timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def get_tree_display(self, obj):
        return obj.tree.name
    
    get_tree_display.short_description = 'ツリー'
    get_tree_display.admin_order_field = 'tree__name'
    
    def get_structure_display(self, obj):
        if obj.structure:
            return obj.structure.node.name
        return "構造なし"
    
    get_structure_display.short_description = '構造'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================
# 管理画面のカスタマイズ
# ==========================================

# 管理画面のタイトルをカスタマイズ
admin.site.site_header = '共有ツリー構造システム 管理画面'
admin.site.site_title = '共有ツリー構造システム'
admin.site.index_title = 'システム管理'

# 管理画面にカスタムCSSを追加（オプション）
class SharedTreeAdminConfig:
    """
    管理画面の追加設定
    """
    
    class Media:
        css = {
            'all': ('admin/css/shared_tree_admin.css',)
        }
        js = ('admin/js/shared_tree_admin.js',)


# インライン管理設定
class CodeVersionInline(admin.TabularInline):
    """
    コード詳細画面内でバージョンを管理するインライン
    """
    model = CodeVersion
    extra = 0
    readonly_fields = ['created_at']
    fields = ['version', 'status', 'description', 'effective_date', 'created_by']


class TreeStructureInline(admin.TabularInline):
    """
    ツリー詳細画面内で構造を管理するインライン
    """
    model = TreeStructure
    extra = 0
    readonly_fields = ['level', 'path', 'created_at']
    fields = ['parent', 'node', 'sequence', 'sharing_type', 'level']
    raw_id_fields = ['parent', 'node']


# 既存の管理クラスにインラインを追加
CodeAdmin.inlines = [CodeVersionInline]
TreeAdmin.inlines = [TreeStructureInline]