from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.pdm_system.codes.models import Prefix  # Replace 'your_app' with your actual app name


class Command(BaseCommand):
    help = 'Create predefined prefixes for code generation'

    @transaction.atomic
    def handle(self, *args, **options):
        # 固定で作成するプレフィックスのリスト
        prefixes_to_create = [
            'AAA', 'BBB', 'CCC',
        ]
        
         # 既存のプレフィックスを一括削除
        deleted_count, _ = Prefix.objects.all().delete()
        if deleted_count > 0:
            self.stdout.write(
                self.style.WARNING(f"既存の{deleted_count}個のプレフィックスを削除しました。")
            )
        else:
            self.stdout.write("削除対象のプレフィックスはありませんでした。")
            
        # 既存のプレフィックス名を取得
        existing_names = set(
            Prefix.objects.filter(name__in=prefixes_to_create).values_list('name', flat=True)
        )
        
        # 作成するプレフィックスオブジェクトのリスト
        prefixes_to_bulk_create = []
        skipped_names = []
        
        current_time = timezone.now()
        
        for index, name in enumerate(prefixes_to_create):
            if name in existing_names:
                skipped_names.append(name)
                continue
            
            prefix = Prefix(
                name=name,
                code_type=str(index + 1),  # '1' for '組'
                next_number= 1,
                created_at=current_time,
                updated_at=current_time
            )
            prefixes_to_bulk_create.append(prefix)
        
        # bulk_createで一括作成
        if prefixes_to_bulk_create:
            Prefix.objects.bulk_create(prefixes_to_bulk_create)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"{len(prefixes_to_bulk_create)}個のプレフィックスを一括作成しました："
                )
            )
            for prefix in prefixes_to_bulk_create:
                self.stdout.write(f"  ✓ {prefix.name}")
        
        # スキップしたプレフィックスの表示
        if skipped_names:
            self.stdout.write(
                self.style.WARNING(
                    f"\n{len(skipped_names)}個の既存プレフィックスをスキップしました："
                )
            )
            for name in skipped_names:
                self.stdout.write(f"  - {name}")
        
        # 結果のサマリー表示
        if prefixes_to_bulk_create or skipped_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n完了: {len(prefixes_to_bulk_create)}個作成、{len(skipped_names)}個スキップ"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("作成対象のプレフィックスがありませんでした。")
            )