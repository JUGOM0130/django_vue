# avail/pdm5/signals.py
"""
Django Signalsを使用した自動同期機能
TreeStructureの作成・更新・削除時に他の共有ツリーに自動反映する
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db import transaction
from .models import TreeStructure, TreeNode, SharedStructureGroup, TreeChangeLog
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=TreeStructure)
def auto_sync_shared_structure_create(sender, instance, created, **kwargs):
    """
    TreeStructure作成時の自動同期
    共有構造に新しいノードが追加された場合、同じ共有グループの他のツリーにも自動追加
    
    Args:
        sender: TreeStructure model
        instance: 作成されたTreeStructureインスタンス
        created: 新規作成の場合True
        **kwargs: その他のパラメータ
    """
    
    # 新規作成で共有構造の場合のみ処理
    if not created or instance.sharing_type != 'shared' or not instance.shared_group:
        return
    
    # 無限ループ防止：すでに同期処理中の場合はスキップ
    if hasattr(instance, '_is_syncing'):
        return
    
    try:
        with transaction.atomic():
            # 同じ共有グループの他のツリーを取得
            other_trees = instance.shared_group.get_participating_trees().exclude(
                id=instance.tree.id
            )
            
            for target_tree in other_trees:
                # 対象ツリーに同じ相対位置の親構造を見つける
                parent_structure = None
                if instance.parent:
                    try:
                        parent_structure = TreeStructure.objects.get(
                            tree=target_tree,
                            shared_group=instance.shared_group,
                            group_relative_path=instance.parent.group_relative_path
                        )
                    except TreeStructure.DoesNotExist:
                        logger.warning(f"親構造が見つかりません: Tree={target_tree.id}, Path={instance.parent.group_relative_path}")
                        continue
                
                # 同じ構造が既に存在するかチェック
                existing_structure = TreeStructure.objects.filter(
                    tree=target_tree,
                    node=instance.node,
                    shared_group=instance.shared_group,
                    group_relative_path=instance.group_relative_path
                ).first()
                
                if existing_structure:
                    continue  # 既に存在する場合はスキップ
                
                # 新しい構造を作成（同じノードを参照）
                new_structure = TreeStructure.objects.create(
                    tree=target_tree,
                    parent=parent_structure,
                    node=instance.node,  # 同じノードを共有
                    sequence=instance.sequence,
                    sharing_type='shared',
                    shared_group=instance.shared_group,
                    group_relative_path=instance.group_relative_path
                )
                
                # 同期フラグを設定して無限ループを防止
                new_structure._is_syncing = True
                
                # 変更ログを記録
                TreeChangeLog.objects.create(
                    tree=target_tree,
                    structure=new_structure,
                    action='share_auto_sync',
                    new_value={
                        'source_tree_id': instance.tree.id,
                        'source_structure_id': instance.id,
                        'node_name': instance.node.name,
                        'sync_reason': 'auto_sync_from_shared_group'
                    },
                    change_reason=f'共有グループからの自動同期: {instance.tree.name}から追加'
                )
                
                logger.info(f"自動同期完了: {instance.node.name} を {target_tree.name} に追加")
                
    except Exception as e:
        logger.error(f"自動同期エラー: {str(e)}")


@receiver(post_delete, sender=TreeStructure)
def auto_sync_shared_structure_delete(sender, instance, **kwargs):
    """
    TreeStructure削除時の自動同期
    共有構造からノードが削除された場合、同じ共有グループの他のツリーからも削除
    
    Args:
        sender: TreeStructure model
        instance: 削除されたTreeStructureインスタンス
        **kwargs: その他のパラメータ
    """
    
    # 共有構造の場合のみ処理
    if instance.sharing_type != 'shared' or not instance.shared_group:
        return
    
    # 無限ループ防止
    if hasattr(instance, '_is_syncing'):
        return
    
    try:
        with transaction.atomic():
            # 同じ共有グループの他のツリーから同じ構造を削除
            other_structures = TreeStructure.objects.filter(
                shared_group=instance.shared_group,
                node=instance.node,
                group_relative_path=instance.group_relative_path
            ).exclude(id=instance.id)
            
            for structure in other_structures:
                # 同期フラグを設定
                structure._is_syncing = True
                
                # 変更ログを記録
                TreeChangeLog.objects.create(
                    tree=structure.tree,
                    structure=None,  # 削除後なのでNone
                    action='share_auto_sync_delete',
                    old_value={
                        'source_tree_id': instance.tree.id,
                        'node_name': instance.node.name,
                        'deleted_structure_id': instance.id
                    },
                    change_reason=f'共有グループからの自動同期削除: {instance.tree.name}から削除'
                )
                
                # 構造を削除
                structure.delete()
                
                logger.info(f"自動同期削除完了: {instance.node.name} を {structure.tree.name} から削除")
                
    except Exception as e:
        logger.error(f"自動同期削除エラー: {str(e)}")


@receiver(post_save, sender=TreeNode)
def auto_sync_shared_node_update(sender, instance, created, **kwargs):
    """
    TreeNode更新時の自動同期
    共有ノードの情報が更新された場合、すべての共有先に反映される
    （これは同じノードインスタンスを参照しているため、自動的に反映されるが、ログ記録のため）
    
    Args:
        sender: TreeNode model
        instance: 更新されたTreeNodeインスタンス
        created: 新規作成の場合True
        **kwargs: その他のパラメータ
    """
    
    # 更新の場合のみ処理（新規作成は除外）
    if created:
        return
    
    try:
        # このノードを使用している共有構造を取得
        shared_structures = TreeStructure.objects.filter(
            node=instance,
            sharing_type='shared'
        ).select_related('tree', 'shared_group')
        
        if not shared_structures.exists():
            return  # 共有構造でない場合は処理しない
        
        # 各共有構造に対してログを記録
        for structure in shared_structures:
            TreeChangeLog.objects.create(
                tree=structure.tree,
                structure=structure,
                action='node_update',
                new_value={
                    'node_name': instance.name,
                    'node_description': instance.description,
                    'node_type': instance.node_type,
                    'updated_from_shared': True
                },
                change_reason='共有ノードの更新による自動反映'
            )
            
        logger.info(f"共有ノード更新: {instance.name} ({shared_structures.count()}個のツリーに反映)")
        
    except Exception as e:
        logger.error(f"共有ノード更新同期エラー: {str(e)}")


def sync_existing_shared_structures(shared_group_id, source_tree_id):
    """
    既存の共有構造を他のツリーに同期する補助関数
    新しいツリーが共有グループに参加した際に使用
    
    Args:
        shared_group_id: 共有グループID
        source_tree_id: 同期元のツリーID
    """
    
    try:
        with transaction.atomic():
            shared_group = SharedStructureGroup.objects.get(id=shared_group_id)
            source_tree = shared_group.get_participating_trees().exclude(id=source_tree_id).first()
            
            if not source_tree:
                return
            
            # ソースツリーの共有構造を取得
            source_structures = TreeStructure.objects.filter(
                tree=source_tree,
                shared_group=shared_group
            ).order_by('group_relative_path')
            
            # 参加ツリーの共有構造を取得
            participating_trees = shared_group.get_participating_trees().exclude(id=source_tree.id)
            
            for target_tree in participating_trees:
                for source_structure in source_structures:
                    # 既に存在するかチェック
                    existing = TreeStructure.objects.filter(
                        tree=target_tree,
                        node=source_structure.node,
                        group_relative_path=source_structure.group_relative_path,
                        shared_group=shared_group
                    ).exists()
                    
                    if not existing:
                        # 親構造を見つける
                        parent_structure = None
                        if source_structure.parent:
                            parent_structure = TreeStructure.objects.filter(
                                tree=target_tree,
                                shared_group=shared_group,
                                group_relative_path=source_structure.parent.group_relative_path
                            ).first()
                        
                        # 新しい構造を作成
                        TreeStructure.objects.create(
                            tree=target_tree,
                            parent=parent_structure,
                            node=source_structure.node,
                            sequence=source_structure.sequence,
                            sharing_type='shared',
                            shared_group=shared_group,
                            group_relative_path=source_structure.group_relative_path
                        )
                        
        logger.info(f"既存共有構造の同期完了: Group={shared_group_id}")
        
    except Exception as e:
        logger.error(f"既存共有構造同期エラー: {str(e)}")


# apps.pyで登録するための設定
def register_signals():
    """
    シグナルを登録する関数
    apps.pyのready()メソッドで呼び出す
    """
    pass  # この関数が読み込まれることでシグナルが自動登録される