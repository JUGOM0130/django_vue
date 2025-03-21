# management/commands/initialize_pdm_data.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

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
    TreeChangeLog
)

class Command(BaseCommand):
    help = 'PDMシステムの初期データを登録します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='既存データを確認せずに初期化します',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        # 既存データの確認
        if not force and self._check_existing_data():
            self.stdout.write(self.style.WARNING('既存データが存在します。--forceオプションを使用して上書きしてください。'))
            return
        
        try:
            with transaction.atomic():
                # 管理ユーザーの作成または取得
                admin_user = self._get_or_create_admin_user()
                
                # プレフィックスの初期化
                prefixes = self._initialize_prefixes()
                
                # サンプルコードの作成
                sample_codes = []
                try:
                    sample_codes = self._create_sample_codes(prefixes, admin_user)
                except Exception as code_error:
                    self.stdout.write(self.style.WARNING(f'サンプルコードの作成中にエラーが発生しました: {str(code_error)}'))
                
                # サンプルツリーの作成
                sample_trees = self._create_sample_trees(sample_codes, admin_user)
                
                self.stdout.write(self.style.SUCCESS('初期データの登録が完了しました。'))
                self.stdout.write(f'- プレフィックス: {len(prefixes)}件')
                self.stdout.write(f'- サンプルコード: {len(sample_codes)}件')
                self.stdout.write(f'- サンプルツリー: {len(sample_trees)}件')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'初期データの登録中にエラーが発生しました: {str(e)}'))
    
    def _check_existing_data(self):
        """既存データの存在を確認"""
        return (
            Prefix.objects.exists() or 
            Code.objects.exists() or
            Tree.objects.exists()
        )
    
    def _get_or_create_admin_user(self):
        """管理ユーザーを取得または作成"""
        try:
            admin = User.objects.get(username='admin')
            self.stdout.write('既存の管理ユーザーを使用します。')
        except User.DoesNotExist:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            self.stdout.write('新しい管理ユーザーを作成しました。')
        return admin
    
    def _initialize_prefixes(self):

        """プレフィックスの初期化"""
        self.stdout.write('プレフィックスを初期化しています...')
        
        prefixes = []
        
        # プレフィックスの定義
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
            },
            {
                'name': 'ROOT', 
                'description': 'ツリーのルートノード用プレフィックス',
                'code_type': '1'  # 組
            }
        ]
        
        for data in prefix_data:
            prefix, created = Prefix.objects.update_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'code_type': data['code_type'],
                    'next_number': 1
                }
            )
            prefixes.append(prefix)
            action = '作成' if created else '更新'
            self.stdout.write(f'- プレフィックス "{prefix.name}" を{action}しました。')
        
        return prefixes
    
        """サンプルコードの作成"""
        self.stdout.write('サンプルコードを作成しています...')
        
        sample_codes = []
        
        # サンプルコードの定義
        code_data = [
            # 組立部品
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
            },
            # 電子部品
            {
                'prefix_name': 'BBB',
                'name': '基板X',
                'description': '制御基板',
                'metadata': {
                    'unit': 'piece',
                    'category': 'electronic',
                    'material': 'FR-4',
                    'weight': 0.120,
                    'dimensions': '100x80x1.6mm'
                }
            },
            {
                'prefix_name': 'BBB',
                'name': 'コネクタY',
                'description': 'USB Type-Cコネクタ',
                'metadata': {
                    'unit': 'piece',
                    'category': 'electronic',
                    'material': 'メタル+プラスチック',
                    'weight': 0.005
                }
            },
            # 購入品
            {
                'prefix_name': 'CCC',
                'name': 'ネジM3x10',
                'description': 'M3x10mm六角穴付きボルト',
                'metadata': {
                    'unit': 'piece',
                    'category': 'hardware',
                    'material': 'SUS304',
                    'weight': 0.002
                }
            },
            {
                'prefix_name': 'CCC',
                'name': 'ケーブルUSB',
                'description': 'USB Type-Cケーブル 1m',
                'metadata': {
                    'unit': 'piece',
                    'category': 'consumable',
                    'weight': 0.050,
                    'dimensions': '1000mm'
                }
            }
        ]
        
        for data in code_data:
            # プレフィックスを取得
            prefix = next((p for p in prefixes if p.name == data['prefix_name']), None)
            if not prefix:
                self.stdout.write(self.style.WARNING(f'プレフィックス "{data["prefix_name"]}" が見つかりません。スキップします。'))
                continue
            
            # コード生成
            code_string = prefix.generate_code()
            
            # Codeモデル作成
            code = Code.objects.create(
                code=code_string,
                name=data['name'],
                prefix=prefix,
                description=data['description'],
                sequential_number=prefix.next_number - 1,
                status='active'
            )
            
            # CodeVersionモデル作成
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
            
            # CodeMetadataモデル作成
            metadata = data.get('metadata', {})
            if metadata:
                CodeMetadata.objects.create(
                    code_version=code_version,
                    unit=metadata.get('unit', 'piece'),
                    material=metadata.get('material'),
                    category=metadata.get('category', 'other'),
                    keywords=metadata.get('keywords', ''),
                    weight=metadata.get('weight'),
                    dimensions=metadata.get('dimensions', ''),
                    notes=metadata.get('notes', '')
                )
            
            # 変更履歴を作成
            CodeChangeLog.objects.create(
                code_version=code_version,
                changed_by=user,
                change_type='create',
                reason='初期データ登録',
                new_status='approved'
            )
            
            sample_codes.append(code)
            self.stdout.write(f'- コード "{code.code}" ({code.name}) を作成しました。')
        
        return sample_codes

    def _create_sample_codes(self, prefixes, user):
        """サンプルコードの作成"""
        self.stdout.write('サンプルコードを作成しています...')
        
        # すべての関連データを削除
        CodeChangeLog.objects.all().delete()
        CodeMetadata.objects.all().delete()
        CodeVersion.objects.all().delete()
        Code.objects.all().delete()
        
        # 各プレフィックスのシーケンシャル番号を追跡
        prefix_sequential_numbers = {}
        
        sample_codes = []
        
        # サンプルコードの定義
        code_data = [
            # 組立部品
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
            },
            # 電子部品
            {
                'prefix_name': 'BBB',
                'name': '基板X',
                'description': '制御基板',
                'metadata': {
                    'unit': 'piece',
                    'category': 'electronic',
                    'material': 'FR-4',
                    'weight': 0.120,
                    'dimensions': '100x80x1.6mm'
                }
            },
            {
                'prefix_name': 'BBB',
                'name': 'コネクタY',
                'description': 'USB Type-Cコネクタ',
                'metadata': {
                    'unit': 'piece',
                    'category': 'electronic',
                    'material': 'メタル+プラスチック',
                    'weight': 0.005
                }
            },
            # 購入品
            {
                'prefix_name': 'CCC',
                'name': 'ネジM3x10',
                'description': 'M3x10mm六角穴付きボルト',
                'metadata': {
                    'unit': 'piece',
                    'category': 'hardware',
                    'material': 'SUS304',
                    'weight': 0.002
                }
            },
            {
                'prefix_name': 'CCC',
                'name': 'ケーブルUSB',
                'description': 'USB Type-Cケーブル 1m',
                'metadata': {
                    'unit': 'piece',
                    'category': 'consumable',
                    'weight': 0.050,
                    'dimensions': '1000mm'
                }
            }
        ]
        
        for data in code_data:
            # プレフィックスを取得
            prefix = next((p for p in prefixes if p.name == data['prefix_name']), None)
            if not prefix:
                self.stdout.write(self.style.WARNING(f'プレフィックス "{data["prefix_name"]}" が見つかりません。スキップします。'))
                continue
            
            # 各プレフィックスの次のシーケンシャル番号を管理
            if prefix.name not in prefix_sequential_numbers:
                prefix_sequential_numbers[prefix.name] = 1
            
            # コードを生成
            # 手動で一意のコードを生成（プレフィックスを直接操作）
            code_format_map = {
                '1': 'A{:04d}Z000',    # 組
                '2': 'AA{:04d}Z000',   # 部品
                '3': 'A{:04d}Z00'      # 購入品
            }
            
            # 現在のシーケンシャル番号を使用してコードを生成
            number_format = code_format_map.get(prefix.code_type)
            sequential_number = prefix_sequential_numbers[prefix.name]
            code_part = number_format.format(sequential_number)
            code_string = f"{prefix.name}-{code_part}"
            
            # Codeモデル作成
            code = Code.objects.create(
                code=code_string,
                name=data['name'],
                prefix=prefix,
                description=data['description'],
                sequential_number=sequential_number,
                status='active'
            )
            
            # シーケンシャル番号をインクリメント
            prefix_sequential_numbers[prefix.name] += 1
            
            # CodeVersionモデル作成
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
            
            # メタデータ作成
            metadata = data.get('metadata', {})
            if metadata:
                CodeMetadata.objects.create(
                    code_version=code_version,
                    unit=metadata.get('unit', 'piece'),
                    material=metadata.get('material'),
                    category=metadata.get('category', 'other'),
                    keywords=metadata.get('keywords', ''),
                    weight=metadata.get('weight'),
                    dimensions=metadata.get('dimensions', ''),
                    notes=metadata.get('notes', '')
                )
            
            # 変更履歴を作成
            CodeChangeLog.objects.create(
                code_version=code_version,
                changed_by=user,
                change_type='create',
                reason='初期データ登録',
                new_status='approved'
            )
            
            sample_codes.append(code)
            self.stdout.write(f'- コード "{code.code}" ({code.name}) を作成しました。')
        
        return sample_codes



    def _create_sample_trees(self, sample_codes, user):
        """サンプルツリーの作成"""
        self.stdout.write('サンプルツリーを作成しています...')
        
        # 既存のツリー関連データを削除
        TreeChangeLog.objects.all().delete()
        TreeVersion.objects.all().delete()
        TreeStructure.objects.all().delete()
        TreeNode.objects.all().delete()
        Tree.objects.all().delete()
        
        sample_trees = []
        
        # ツリーの定義
        tree_data = [
            {
                'name': '製品Aツリー',
                'description': '製品Aの構成ツリー',
                'status': 'active'
            },
            {
                'name': '部品管理ツリー',
                'description': '部品の分類管理ツリー',
                'status': 'active'
            }
        ]
        
        for data in tree_data:
            # ツリー作成
            tree = Tree.objects.create(
                name=data['name'],
                description=data['description'],
                status=data['status'],
                created_by=user,
                last_modified_by=user
            )
            
            # ルートノードを作成
            root_node = TreeNode.objects.create(
                name=f"{tree.name}_ROOT",
                description=f"ツリー「{tree.name}」のルートノード",
                node_type='root',
                status='active'
            )
            
            # ツリー構造を作成
            root_structure = TreeStructure.objects.create(
                tree=tree,
                node=root_node,
                parent=None,
                level=0,
                path=str(root_node.id),
                is_master=True
            )
            
            # TreeVersionを作成
            tree_version = TreeVersion.objects.create(
                tree=tree,
                version_number=1,
                version_name=f"{data['name']} 初期バージョン",
                version_description="初期作成",
                status='approved',
                created_by=user,
                approved_by=user,
                effective_date=timezone.now()
            )
            
            sample_trees.append(tree)
            self.stdout.write(f'- ツリー "{tree.name}" を作成しました。')
            
            # サンプルコードが存在し、十分な数がある場合のみ階層構造を作成
            if sample_codes and len(sample_codes) >= 5 and tree.name == '製品Aツリー':
                # 製品A（最初のコード）のツリーノードを作成
                product_a = sample_codes[0]
                product_a_node = TreeNode.objects.create(
                    name=product_a.name,
                    description=product_a.description,
                    node_type='code',
                    status='active',
                    code=product_a
                )
                
                # ツリー構造作成
                level1 = TreeStructure.objects.create(
                    tree=tree,
                    parent=root_structure,
                    node=product_a_node,
                    level=1,
                    path=f"{root_structure.path}.{product_a_node.id}",
                    relationship_type='assembly',
                    is_master=True
                )
                self.stdout.write(f'  - ノード "{product_a.name}" を追加しました。')
                
                # サブアセンブリB（2番目のコード）のツリーノードを作成
                sub_assembly = sample_codes[1]
                sub_assembly_node = TreeNode.objects.create(
                    name=sub_assembly.name,
                    description=sub_assembly.description,
                    node_type='code',
                    status='active',
                    code=sub_assembly
                )
                
                # ツリー構造作成
                level2 = TreeStructure.objects.create(
                    tree=tree,
                    parent=level1,
                    node=sub_assembly_node,
                    level=2,
                    path=f"{level1.path}.{sub_assembly_node.id}",
                    relationship_type='assembly',
                    quantity=2.0,
                    is_master=True
                )
                self.stdout.write(f'  - ノード "{sub_assembly.name}" を追加しました。')
                
                # 基板X（3番目のコード）のツリーノードを作成
                board = sample_codes[2]
                board_node = TreeNode.objects.create(
                    name=board.name,
                    description=board.description,
                    node_type='code',
                    status='active',
                    code=board
                )
                
                # ツリー構造作成
                level3a = TreeStructure.objects.create(
                    tree=tree,
                    parent=level2,
                    node=board_node,
                    level=3,
                    path=f"{level2.path}.{board_node.id}",
                    relationship_type='assembly',
                    is_master=True
                )
                self.stdout.write(f'  - ノード "{board.name}" を追加しました。')
                
                # コネクタY（4番目のコード）のツリーノードを作成
                connector = sample_codes[3]
                connector_node = TreeNode.objects.create(
                    name=connector.name,
                    description=connector.description,
                    node_type='code',
                    status='active',
                    code=connector
                )
                
                # ツリー構造作成
                level3b = TreeStructure.objects.create(
                    tree=tree,
                    parent=level2,
                    node=connector_node,
                    level=3,
                    path=f"{level2.path}.{connector_node.id}",
                    relationship_type='assembly',
                    quantity=4.0,
                    is_master=True
                )
                self.stdout.write(f'  - ノード "{connector.name}" を追加しました。')
                
                # ネジ（5番目のコード）のツリーノードを作成
                screw = sample_codes[4]
                screw_node = TreeNode.objects.create(
                    name=screw.name,
                    description=screw.description,
                    node_type='code',
                    status='active',
                    code=screw
                )
                
                # ツリー構造作成
                level2b = TreeStructure.objects.create(
                    tree=tree,
                    parent=level1,
                    node=screw_node,
                    level=2,
                    path=f"{level1.path}.{screw_node.id}",
                    relationship_type='assembly',
                    quantity=10.0,
                    is_master=True
                )
                self.stdout.write(f'  - ノード "{screw.name}" を追加しました。')
        
        return sample_trees




