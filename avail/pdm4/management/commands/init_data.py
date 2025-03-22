from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from rest_framework import status
from django.core.management.base import BaseCommand

from pdm4.models import (
    Prefix, 
    Code, 
    CodeVersion, 
    CodeMetadata, 
    CodeChangeLog,
    Tree,
    TreeNode,
    TreeStructure,
    TreeVersion,
    TreeChangeLog,
    TreeCodeQuantity
)


def initialize_tables():
    """
    テーブルを初期化する関数
    依存関係を考慮した順序でテーブルをクリア
    """
    with transaction.atomic():
        # 変更履歴を最初に削除
        TreeChangeLog.objects.all().delete()
        CodeChangeLog.objects.all().delete()

        # ツリー関連テーブルを削除
        TreeCodeQuantity.objects.all().delete()
        TreeVersion.objects.all().delete()
        TreeStructure.objects.all().delete()
        TreeNode.objects.all().delete()
        Tree.objects.all().delete()

        # コード関連テーブルを削除
        CodeMetadata.objects.all().delete()
        CodeVersion.objects.all().delete()
        Code.objects.all().delete()

        # プレフィックスを最後に削除
        Prefix.objects.all().delete()


def create_test_data():
    """
    テストデータを作成する関数
    APIエンドポイントと同様の処理で追加
    """
    try:
        # 管理ユーザーを取得または作成
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )

    # テーブルを初期化
    initialize_tables()

    # トランザクション内で処理
    with transaction.atomic():
        # プレフィックスの作成
        prefixes = _create_prefixes()
        
        # コードの作成
        codes = _create_codes(prefixes, admin_user)
        
        # ツリーの作成
        trees = _create_trees(codes, admin_user)
        
        return {
            'prefixes': prefixes,
            'codes': codes,
            'trees': trees
        }

def _create_prefixes():
    """プレフィックスを作成"""
    prefix_data = [
        {
            'name': 'AAA', 
            'description': '組立部品用プレフィックス',
            'code_type': '1'  # 組
        },
        {
            'name': 'BBB', 
            'description': '電子部品用プレフィックス',
            'code_type': '2'  # 部品
        },
        {
            'name': 'CCC', 
            'description': '購入品用プレフィックス',
            'code_type': '3'  # 購入品
        }
    ]
    
    prefixes = []
    for data in prefix_data:
        prefix, _ = Prefix.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'code_type': data['code_type'],
                'next_number': 1
            }
        )
        prefixes.append(prefix)
    
    return prefixes

def _create_codes(prefixes, user):
    """コードを作成"""
    code_data = [
        {
            'prefix_name': 'AAA',
            'name': '製品A',
            'description': '最終製品A',
            'metadata': {
                'unit': 'piece',
                'category': 'mechanical',
                'weight': 5.000,
                'dimensions': '200x150x100mm'
            }
        },
        {
            'prefix_name': 'AAA',
            'name': 'サブアセンブリB',
            'description': '製品Aのサブアセンブリ',
            'metadata': {
                'unit': 'piece',
                'category': 'mechanical',
                'weight': 2.500,
                'dimensions': '150x100x50mm'
            }
        }
    ]
    
    codes = []
    for data in code_data:
        # プレフィックスを取得
        prefix = next((p for p in prefixes if p.name == data['prefix_name']), None)
        if not prefix:
            continue
        
        # コードを生成
        code_string = prefix.generate_code()
        
        # Codeモデルを作成
        code = Code.objects.create(
            code=code_string,
            name=data['name'],
            prefix=prefix,
            description=data['description'],
            sequential_number=prefix.next_number - 1,
            status='active'
        )
        
        # CodeVersionを作成
        code_version = CodeVersion.objects.create(
            code=code,
            version=1,
            code_number=code_string,
            is_current=True,
            status='approved',
            reason='初期作成',
            changed_by=user,
            effective_date=timezone.now()
        )
        
        # メタデータを作成
        metadata = data.get('metadata', {})
        if metadata:
            CodeMetadata.objects.create(
                code_version=code_version,
                unit=metadata.get('unit', 'piece'),
                category=metadata.get('category', 'other'),
                weight=metadata.get('weight'),
                dimensions=metadata.get('dimensions', '')
            )
        
        # 変更履歴を作成
        CodeChangeLog.objects.create(
            code_version=code_version,
            changed_by=user,
            change_type='create',
            reason='テストデータ登録',
            new_status='approved'
        )
        
        codes.append(code)
    
    return codes

def _create_trees(self, codes, user=None):
    """ツリーを作成"""
    tree_data = [
        {
            'name': '製品Aツリー',
            'description': '製品Aの構成ツリー',
            'status': 'active'
        }
    ]
    
    trees = []
    for data in tree_data:
        # ツリーを作成（Viewsの処理に委ねる）
        tree = Tree.objects.create(
            name=data['name'],
            description=data['description'],
            status=data['status'],
            created_by=user,
            last_modified_by=user
        )
        trees.append(tree)
    
    return trees

# Django Management Commandとして使用する場合
class Command(BaseCommand):
    help = 'テストデータを登録します'

    def handle(self, *args, **options):
        try:
            # テストデータ作成
            result = create_test_data()
            
            # 結果を出力
            self.stdout.write(self.style.SUCCESS('テストデータの登録が完了しました。'))
            self.stdout.write(f'- プレフィックス: {len(result["prefixes"])}件')
            self.stdout.write(f'- コード: {len(result["codes"])}件')
            self.stdout.write(f'- ツリー: {len(result["trees"])}件')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'テストデータ登録中にエラーが発生しました: {str(e)}'))
