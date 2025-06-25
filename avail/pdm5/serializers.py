# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Prefix, Code, CodeVersion, CodeChangeLog, CodeMetadata,
    Tree, TreeNode, TreeStructure, TreeVersion, TreeCodeQuantity, 
    TreeChangeLog, SharedStructureGroup
)


class UserSerializer(serializers.ModelSerializer):
    """
    ユーザー情報のシリアライザー
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class PrefixSerializer(serializers.ModelSerializer):
    """
    プレフィックス管理のシリアライザー
    コード生成時のプレフィックス情報をシリアライズ
    """
    code_type_display = serializers.CharField(source='get_code_type_display', read_only=True)
    
    class Meta:
        model = Prefix
        fields = [
            'id', 'name', 'code_type', 'code_type_display', 
            'next_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """
        プレフィックス名の重複チェック
        """
        if Prefix.objects.filter(name=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("このプレフィックス名は既に使用されています。")
        return value


class CodeSerializer(serializers.ModelSerializer):
    """
    コード管理のシリアライザー
    コードの基本情報をシリアライズ
    """
    prefix_name = serializers.CharField(source='prefix.name', read_only=True)
    
    class Meta:
        model = Code
        fields = [
            'id', 'prefix', 'prefix_name', 'code', 'name', 
            'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_code(self, value):
        """
        コードの重複チェック
        """
        if Code.objects.filter(code=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("このコードは既に使用されています。")
        return value


class CodeVersionSerializer(serializers.ModelSerializer):
    """
    コードバージョン管理のシリアライザー
    コードのバージョン情報をシリアライズ
    """
    code_name = serializers.CharField(source='code.name', read_only=True)
    code_code = serializers.CharField(source='code.code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CodeVersion
        fields = [
            'id', 'code', 'code_name', 'code_code', 'version', 
            'status', 'status_display', 'description', 'effective_date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CodeChangeLogSerializer(serializers.ModelSerializer):
    """
    コード変更ログのシリアライザー
    コードの変更履歴をシリアライズ
    """
    code_name = serializers.CharField(source='code.name', read_only=True)
    code_code = serializers.CharField(source='code.code', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = CodeChangeLog
        fields = [
            'id', 'code', 'code_name', 'code_code', 'action', 'action_display',
            'old_value', 'new_value', 'change_reason', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class CodeMetadataSerializer(serializers.ModelSerializer):
    """
    コードメタデータのシリアライザー
    コードの追加情報をシリアライズ
    """
    code_name = serializers.CharField(source='code.name', read_only=True)
    code_code = serializers.CharField(source='code.code', read_only=True)
    
    class Meta:
        model = CodeMetadata
        fields = [
            'id', 'code', 'code_name', 'code_code', 'category', 
            'tags', 'custom_fields', 'priority', 'external_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreeNodeSerializer(serializers.ModelSerializer):
    """
    ツリーノードのシリアライザー
    ツリーの実際のノードデータをシリアライズ
    """
    code_name = serializers.CharField(source='code.name', read_only=True)
    code_code = serializers.CharField(source='code.code', read_only=True)
    shared_structures_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeNode
        fields = [
            'id', 'name', 'description', 'node_type', 'attributes',
            'code', 'code_name', 'code_code', 'shared_structures_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_shared_structures_count(self, obj):
        """
        このノードを使用している構造の数を取得
        """
        return obj.get_shared_structures().count()


class SharedStructureGroupSerializer(serializers.ModelSerializer):
    """
    共有構造グループのシリアライザー
    構造の共有グループ情報をシリアライズ
    """
    root_node_name = serializers.CharField(source='root_node.name', read_only=True)
    participating_trees_count = serializers.SerializerMethodField()
    participating_trees = serializers.SerializerMethodField()
    
    class Meta:
        model = SharedStructureGroup
        fields = [
            'id', 'name', 'description', 'root_node', 'root_node_name',
            'participating_trees_count', 'participating_trees',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participating_trees_count(self, obj):
        """
        グループに参加しているツリーの数を取得
        """
        return obj.get_participating_trees().count()
    
    def get_participating_trees(self, obj):
        """
        グループに参加しているツリーの一覧を取得
        """
        trees = obj.get_participating_trees()
        return [{'id': tree.id, 'name': tree.name} for tree in trees]


class TreeStructureSerializer(serializers.ModelSerializer):
    """
    ツリー構造のシリアライザー
    ツリー内でのノード配置と関係性をシリアライズ
    """
    tree_name = serializers.CharField(source='tree.name', read_only=True)
    parent_name = serializers.CharField(source='parent.node.name', read_only=True)
    node_name = serializers.CharField(source='node.name', read_only=True)
    node_description = serializers.CharField(source='node.description', read_only=True)
    sharing_type_display = serializers.CharField(source='get_sharing_type_display', read_only=True)
    shared_group_name = serializers.CharField(source='shared_group.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    is_shared_flag = serializers.SerializerMethodField()
    sibling_shared_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeStructure
        fields = [
            'id', 'tree', 'tree_name', 'parent', 'parent_name', 
            'node', 'node_name', 'node_description', 'level', 'sequence', 'path',
            'sharing_type', 'sharing_type_display', 'shared_group', 'shared_group_name',
            'group_relative_path', 'children_count', 'is_shared_flag', 'sibling_shared_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'level', 'path', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """
        この構造の直接の子構造数を取得
        """
        return obj.children.count()
    
    def get_is_shared_flag(self, obj):
        """
        共有構造かどうかのフラグを取得
        """
        return obj.is_shared()
    
    def get_sibling_shared_count(self, obj):
        """
        同じ共有グループに属する他ツリーの構造数を取得
        """
        return obj.get_sibling_shared_structures().count()


class TreeStructureHierarchySerializer(serializers.ModelSerializer):
    """
    ツリー構造の階層表示用シリアライザー
    子構造を含めた階層構造をシリアライズ
    """
    node_name = serializers.CharField(source='node.name', read_only=True)
    node_description = serializers.CharField(source='node.description', read_only=True)
    sharing_type_display = serializers.CharField(source='get_sharing_type_display', read_only=True)
    shared_group_name = serializers.CharField(source='shared_group.name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = TreeStructure
        fields = [
            'id', 'node', 'node_name', 'node_description', 'level', 'sequence',
            'sharing_type', 'sharing_type_display', 'shared_group', 'shared_group_name',
            'children'
        ]
    
    def get_children(self, obj):
        """
        子構造を再帰的に取得してシリアライズ
        """
        children = obj.children.all().order_by('sequence')
        return TreeStructureHierarchySerializer(children, many=True, context=self.context).data


class TreeSerializer(serializers.ModelSerializer):
    """
    ツリー管理のシリアライザー
    ツリーの基本情報をシリアライズ
    """
    structures_count = serializers.SerializerMethodField()
    root_structures_count = serializers.SerializerMethodField()
    shared_structures_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tree
        fields = [
            'id', 'name', 'description', 'is_active',
            'structures_count', 'root_structures_count', 'shared_structures_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_structures_count(self, obj):
        """
        ツリー内の全構造数を取得
        """
        return obj.structures.count()
    
    def get_root_structures_count(self, obj):
        """
        ルート構造の数を取得
        """
        return obj.get_root_structures().count()
    
    def get_shared_structures_count(self, obj):
        """
        共有構造の数を取得
        """
        return obj.structures.filter(sharing_type='shared').count()


class TreeVersionSerializer(serializers.ModelSerializer):
    """
    ツリーバージョン管理のシリアライザー
    ツリーのバージョン情報をシリアライズ
    """
    tree_name = serializers.CharField(source='tree.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TreeVersion
        fields = [
            'id', 'tree', 'tree_name', 'version', 'status', 'status_display',
            'description', 'snapshot_data', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TreeCodeQuantitySerializer(serializers.ModelSerializer):
    """
    ツリーコード数量のシリアライザー
    ツリー内のコード数量情報をシリアライズ
    """
    tree_name = serializers.CharField(source='tree.name', read_only=True)
    structure_node_name = serializers.CharField(source='structure.node.name', read_only=True)
    code_name = serializers.CharField(source='code.name', read_only=True)
    code_code = serializers.CharField(source='code.code', read_only=True)
    
    class Meta:
        model = TreeCodeQuantity
        fields = [
            'id', 'tree', 'tree_name', 'structure', 'structure_node_name',
            'code', 'code_name', 'code_code', 'quantity', 'unit', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreeChangeLogSerializer(serializers.ModelSerializer):
    """
    ツリー変更ログのシリアライザー
    ツリーの変更履歴をシリアライズ
    """
    tree_name = serializers.CharField(source='tree.name', read_only=True)
    structure_node_name = serializers.CharField(source='structure.node.name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = TreeChangeLog
        fields = [
            'id', 'tree', 'tree_name', 'structure', 'structure_node_name',
            'action', 'action_display', 'old_value', 'new_value', 'change_reason',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class TreeStructureCreateSerializer(serializers.Serializer):
    """
    ツリー構造作成用のシリアライザー
    新しい構造をツリーに追加する際のリクエストデータを処理
    """
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    node_name = serializers.CharField(max_length=200)
    node_description = serializers.CharField(required=False, allow_blank=True)
    node_type = serializers.CharField(required=False, default='default')
    node_attributes = serializers.JSONField(required=False, default=dict)
    code_id = serializers.IntegerField(required=False, allow_null=True)
    sequence = serializers.IntegerField(required=False, default=0)
    
    def validate_parent_id(self, value):
        """
        親構造の存在チェック
        """
        if value is not None:
            try:
                TreeStructure.objects.get(id=value)
            except TreeStructure.DoesNotExist:
                raise serializers.ValidationError("指定された親構造が存在しません。")
        return value
    
    def validate_code_id(self, value):
        """
        コードの存在チェック
        """
        if value is not None:
            try:
                Code.objects.get(id=value)
            except Code.DoesNotExist:
                raise serializers.ValidationError("指定されたコードが存在しません。")
        return value


class TreeStructureShareSerializer(serializers.Serializer):
    """
    ツリー構造共有用のシリアライザー
    既存構造を他のツリーと共有する際のリクエストデータを処理
    """
    source_structure_id = serializers.IntegerField()
    parent_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_source_structure_id(self, value):
        """
        共有元構造の存在チェック
        """
        try:
            TreeStructure.objects.get(id=value)
        except TreeStructure.DoesNotExist:
            raise serializers.ValidationError("指定された共有元構造が存在しません。")
        return value
    
    def validate_parent_id(self, value):
        """
        親構造の存在チェック
        """
        if value is not None:
            try:
                TreeStructure.objects.get(id=value)
            except TreeStructure.DoesNotExist:
                raise serializers.ValidationError("指定された親構造が存在しません。")
        return value