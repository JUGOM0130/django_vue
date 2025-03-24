from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata,
    Tree, TreeNode, TreeStructure, TreeVersion, 
    TreeCodeQuantity, TreeChangeLog
)

# Prefix Admin
@admin.register(Prefix)
class PrefixAdmin(admin.ModelAdmin):
    """管理画面でのPrefixモデルの表示設定"""
    list_display = ('name', 'code_type', 'code_type_display', 'next_number', 'format_example')
    list_filter = ('code_type',)
    search_fields = ('name', 'description')
    actions = ['reset_number']

    def format_example(self, obj):
        """コード生成例を表示"""
        return obj.format_example
    format_example.short_description = 'コード生成例'

    def reset_number(self, request, queryset):
        """選択されたPrefixの採番をリセット"""
        for prefix in queryset:
            prefix.reset_number()
        self.message_user(request, f'{queryset.count()}個のPrefixの採番をリセットしました。')
    reset_number.short_description = '採番のリセット'

# Code Admin
@admin.register(Code)
class CodeAdmin(admin.ModelAdmin):
    """管理画面でのCodeモデルの表示設定"""
    list_display = ('code', 'name', 'prefix', 'status', 'status_display', 'version_count')
    list_filter = ('status', 'prefix')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('code', 'created_at', 'updated_at')
    actions = ['activate_codes', 'obsolete_codes']

    def version_count(self, obj):
        """バージョン数を表示"""
        return obj.version_count
    version_count.short_description = 'バージョン数'

    def activate_codes(self, request, queryset):
        """選択されたコードを有効化"""
        for code in queryset:
            if code.status == 'draft':
                code.activate()
        self.message_user(request, f'{queryset.count()}個のコードを有効化しました。')
    activate_codes.short_description = 'コードを有効化'

    def obsolete_codes(self, request, queryset):
        """選択されたコードを廃止"""
        for code in queryset:
            if code.status == 'active':
                code.obsolete()
        self.message_user(request, f'{queryset.count()}個のコードを廃止しました。')
    obsolete_codes.short_description = 'コードを廃止'

# CodeVersion Admin
@admin.register(CodeVersion)
class CodeVersionAdmin(admin.ModelAdmin):
    """管理画面でのCodeVersionモデルの表示設定"""
    list_display = ('__str__', 'version', 'code_number', 'status', 'is_current', 'effective_date')
    list_filter = ('status', 'is_current')
    search_fields = ('code__name', 'code_number')
    readonly_fields = ('code_number', 'created_at', 'updated_at')
    actions = ['submit_for_review', 'approve_versions', 'make_obsolete']

    def submit_for_review(self, request, queryset):
        """選択されたバージョンをレビューに提出"""
        for version in queryset:
            if version.status == 'draft':
                version.submit_for_review(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンをレビューに提出しました。')
    submit_for_review.short_description = 'レビューに提出'

    def approve_versions(self, request, queryset):
        """選択されたバージョンを承認"""
        for version in queryset:
            if version.status == 'review':
                version.approve(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンを承認しました。')
    approve_versions.short_description = 'バージョンを承認'

    def make_obsolete(self, request, queryset):
        """選択されたバージョンを廃止"""
        for version in queryset:
            if version.status in ['approved', 'review']:
                version.make_obsolete(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンを廃止しました。')
    make_obsolete.short_description = 'バージョンを廃止'

# CodeChangeLog Admin
@admin.register(CodeChangeLog)
class CodeChangeLogAdmin(admin.ModelAdmin):
    """管理画面でのCodeChangeLogモデルの表示設定"""
    list_display = ('code_version', 'changed_at', 'changed_by', 'change_type', 'reason')
    list_filter = ('change_type', 'changed_at')
    search_fields = ('code_version__code__name', 'reason')
    readonly_fields = ('changed_at', 'changed_by', 'code_version')

# CodeMetadata Admin
@admin.register(CodeMetadata)
class CodeMetadataAdmin(admin.ModelAdmin):
    """管理画面でのCodeMetadataモデルの表示設定"""
    list_display = ('code_version', 'category', 'unit', 'material', 'weight')
    list_filter = ('category', 'unit', 'material')
    search_fields = ('code_version__code__name', 'keywords', 'material')

# Tree Admin
@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    """管理画面でのTreeモデルの表示設定"""
    list_display = ('name', 'status', 'version', 'created_by', 'last_modified_by')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    actions = ['activate_trees', 'archive_trees']

    def activate_trees(self, request, queryset):
        """選択されたツリーを有効化"""
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()}個のツリーを有効化しました。')
    activate_trees.short_description = 'ツリーを有効化'

    def archive_trees(self, request, queryset):
        """選択されたツリーをアーカイブ"""
        queryset.update(status='archived')
        self.message_user(request, f'{queryset.count()}個のツリーをアーカイブしました。')
    archive_trees.short_description = 'ツリーをアーカイブ'

# TreeNode Admin
@admin.register(TreeNode)
class TreeNodeAdmin(admin.ModelAdmin):
    """管理画面でのTreeNodeモデルの表示設定"""
    list_display = ('name', 'node_type', 'status', 'code', 'display_code_details')
    list_filter = ('node_type', 'status')
    search_fields = ('name', 'description')

    def display_code_details(self, obj):
        """コードの詳細を表示"""
        if obj.code:
            return format_html(
                '<span title="{}">{}</span>',
                obj.code.description or '',
                obj.code.code
            )
        return '-'
    display_code_details.short_description = 'コード'

# TreeStructure Admin
@admin.register(TreeStructure)
class TreeStructureAdmin(admin.ModelAdmin):
    """管理画面でのTreeStructureモデルの表示設定"""
    list_display = ('tree', 'node', 'parent', 'level', 'relationship_type', 'quantity', 'is_master')
    list_filter = ('tree', 'level', 'relationship_type', 'is_master')
    search_fields = ('node__name', 'tree__name')

# TreeVersion Admin
@admin.register(TreeVersion)
class TreeVersionAdmin(admin.ModelAdmin):
    """管理画面でのTreeVersionモデルの表示設定"""
    list_display = ('tree', 'version_number', 'version_name', 'status', 'effective_date', 'expiry_date')
    list_filter = ('status', 'effective_date', 'expiry_date')
    search_fields = ('tree__name', 'version_name')
    actions = ['submit_for_review', 'approve_versions', 'make_obsolete']

    def submit_for_review(self, request, queryset):
        """選択されたバージョンをレビューに提出"""
        for version in queryset:
            if version.status == 'draft':
                version.submit_for_review(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンをレビューに提出しました。')
    submit_for_review.short_description = 'レビューに提出'

    def approve_versions(self, request, queryset):
        """選択されたバージョンを承認"""
        for version in queryset:
            if version.status == 'review':
                version.approve(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンを承認しました。')
    approve_versions.short_description = 'バージョンを承認'

    def make_obsolete(self, request, queryset):
        """選択されたバージョンを廃止"""
        for version in queryset:
            if version.status in ['approved', 'review']:
                version.make_obsolete(request.user)
        self.message_user(request, f'{queryset.count()}個のバージョンを廃止しました。')
    make_obsolete.short_description = 'バージョンを廃止'

# TreeCodeQuantity Admin
@admin.register(TreeCodeQuantity)
class TreeCodeQuantityAdmin(admin.ModelAdmin):
    """管理画面でのTreeCodeQuantityモデルの表示設定"""
    list_display = ('tree_structure', 'code_version', 'quantity', 'unit', 'loss_rate', 'minimum_order')
    list_filter = ('unit', 'effective_date', 'expiry_date')
    search_fields = ('tree_structure__node__name', 'code_version__code__name')

# TreeChangeLog Admin
@admin.register(TreeChangeLog)
class TreeChangeLogAdmin(admin.ModelAdmin):
    """管理画面でのTreeChangeLogモデルの表示設定"""
    list_display = ('tree_version', 'changed_at', 'changed_by', 'change_type', 'significance_level', 'requires_approval')
    list_filter = ('change_type', 'significance_level', 'requires_approval', 'changed_at')
    search_fields = ('tree_version__tree__name', 'description')
    readonly_fields = ('changed_at', 'changed_by', 'tree_version')