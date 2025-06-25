# avail/pdm5/management/commands/sync_shared_structures.py
"""
管理コマンド: 共有構造の整合性チェックと修復
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from avail.pdm5.models import SharedStructureGroup, TreeStructure
from avail.pdm5.signals import sync_existing_shared_structures


class Command(BaseCommand):
    """
    共有構造の整合性をチェックし、必要に応じて修復する管理コマンド
    
    使用方法:
    python manage.py sync_shared_structures
    python manage.py sync_shared_structures --group-id=1
    python manage.py sync_shared_structures --dry-run
    """
    
    help = '共有構造の整合性チェックと自動修復'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group-id',
            type=int,
            help='特定の共有グループのみを処理',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='実際の変更を行わず、チェックのみ実行',
        )

    def handle(self, *args, **options):
        """
        コマンド実行のメインロジック
        """
        
        group_id = options['group_id']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN モード: 実際の変更は行いません')
            )
        
        # 処理対象の共有グループを取得
        if group_id:
            try:
                shared_groups = [SharedStructureGroup.objects.get(id=group_id)]
                self.stdout.write(f'共有グループ {group_id} を処理します')
            except SharedStructureGroup.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'共有グループ {group_id} が見つかりません')
                )
                return
        else:
            shared_groups = SharedStructureGroup.objects.all()
            self.stdout.write(f'{shared_groups.count()} 個の共有グループを処理します')
        
        total_synced = 0
        total_errors = 0
        
        for shared_group in shared_groups:
            try:
                synced_count = self._sync_shared_group(shared_group, dry_run)
                total_synced += synced_count
                
                if synced_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'共有グループ "{shared_group.name}": {synced_count} 個の構造を同期'
                        )
                    )
                else:
                    self.stdout.write(
                        f'共有グループ "{shared_group.name}": 同期不要'
                    )
                    
            except Exception as e:
                total_errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'共有グループ "{shared_group.name}" の処理でエラー: {e}'
                    )
                )
        
        # 結果サマリー
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'処理完了:')
        self.stdout.write(f'  - 同期された構造: {total_synced} 個')
        self.stdout.write(f'  - エラー: {total_errors} 個')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('※ DRY RUN モードのため実際の変更は行われていません')
            )

    def _sync_shared_group(self, shared_group, dry_run=False):
        """
        特定の共有グループの整合性をチェックし、同期する
        """
        
        participating_trees = shared_group.get_participating_trees()
        if participating_trees.count() < 2:
            return 0  # 参加ツリーが1個以下の場合は同期不要
        
        # 基準となるツリー（最初のツリー）を取得
        base_tree = participating_trees.first()
        base_structures = TreeStructure.objects.filter(
            tree=base_tree,
            shared_group=shared_group
        ).order_by('group_relative_path')
        
        synced_count = 0
        
        if not dry_run:
            with transaction.atomic():
                # 他のツリーと同期
                for target_tree in participating_trees.exclude(id=base_tree.id):
                    for base_structure in base_structures:
                        # 対応する構造が存在するかチェック
                        existing = TreeStructure.objects.filter(
                            tree=target_tree,
                            node=base_structure.node,
                            shared_group=shared_group,
                            group_relative_path=base_structure.group_relative_path
                        ).exists()
                        
                        if not existing:
                            # 親構造を見つける
                            parent_structure = None
                            if base_structure.parent:
                                parent_structure = TreeStructure.objects.filter(
                                    tree=target_tree,
                                    shared_group=shared_group,
                                    group_relative_path=base_structure.parent.group_relative_path
                                ).first()
                            
                            # 構造を作成
                            TreeStructure.objects.create(
                                tree=target_tree,
                                parent=parent_structure,
                                node=base_structure.node,
                                sequence=base_structure.sequence,
                                sharing_type='shared',
                                shared_group=shared_group,
                                group_relative_path=base_structure.group_relative_path
                            )
                            
                            synced_count += 1
        else:
            # DRY RUN: 不整合をカウントするだけ
            for target_tree in participating_trees.exclude(id=base_tree.id):
                for base_structure in base_structures:
                    existing = TreeStructure.objects.filter(
                        tree=target_tree,
                        node=base_structure.node,
                        shared_group=shared_group,
                        group_relative_path=base_structure.group_relative_path
                    ).exists()
                    
                    if not existing:
                        synced_count += 1
        
        return synced_count