# Generated by Django 4.2.9 on 2025-03-16 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('code', models.CharField(help_text='生成された完全なコード文字列', max_length=20, unique=True, verbose_name='コード')),
                ('name', models.CharField(help_text='部品コードの名称', max_length=100, verbose_name='コード名')),
                ('description', models.TextField(blank=True, help_text='コードの詳細説明', null=True, verbose_name='説明')),
                ('status', models.CharField(choices=[('draft', '下書き'), ('active', '有効'), ('obsolete', '廃止')], default='draft', help_text='コードの現在の状態', max_length=20, verbose_name='ステータス')),
                ('sequential_number', models.IntegerField(help_text='プレフィックス内での採番', verbose_name='連番')),
            ],
            options={
                'verbose_name': '部品コード',
                'verbose_name_plural': '部品コード',
            },
        ),
        migrations.CreateModel(
            name='CodeChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('changed_at', models.DateTimeField(auto_now_add=True, help_text='変更が行われた日時', verbose_name='変更日時')),
                ('change_type', models.CharField(choices=[('create', '新規作成'), ('version_up', 'バージョンアップ'), ('obsolete', '廃止'), ('status_change', 'ステータス変更'), ('review', 'レビュー提出'), ('approve', '承認'), ('reject', '却下')], help_text='実施された変更の種類', max_length=20, verbose_name='変更種別')),
                ('reason', models.TextField(help_text='変更を行った理由の詳細説明', verbose_name='変更理由')),
                ('previous_status', models.CharField(blank=True, choices=[('draft', '下書き'), ('review', 'レビュー中'), ('approved', '承認済み'), ('obsolete', '廃止')], help_text='ステータス変更前の状態', max_length=20, null=True, verbose_name='変更前ステータス')),
                ('new_status', models.CharField(blank=True, choices=[('draft', '下書き'), ('review', 'レビュー中'), ('approved', '承認済み'), ('obsolete', '廃止')], help_text='ステータス変更後の状態', max_length=20, null=True, verbose_name='変更後ステータス')),
                ('additional_info', models.JSONField(blank=True, help_text='変更に関する追加情報をJSON形式で保存', null=True, verbose_name='追加情報')),
            ],
            options={
                'verbose_name': '変更履歴',
                'verbose_name_plural': '変更履歴',
                'ordering': ['-changed_at'],
            },
        ),
        migrations.CreateModel(
            name='CodeMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('unit', models.CharField(choices=[('piece', '個'), ('meter', 'm'), ('kilogram', 'kg'), ('liter', 'L'), ('set', 'セット'), ('sheet', '枚'), ('roll', '巻'), ('other', 'その他')], default='piece', help_text='部品の単位（個、m、kg等）', max_length=20, verbose_name='単位')),
                ('material', models.CharField(blank=True, help_text='部品の材質情報（例：SUS304、A5052等）', max_length=100, null=True, verbose_name='材質')),
                ('keywords', models.CharField(blank=True, help_text='部品の検索用キーワード（カンマ区切りで複数指定可）', max_length=200, verbose_name='キーワード')),
                ('category', models.CharField(choices=[('mechanical', '機械部品'), ('electrical', '電気部品'), ('electronic', '電子部品'), ('hardware', 'ハードウェア'), ('material', '原材料'), ('tool', '工具'), ('consumable', '消耗品'), ('other', 'その他')], default='other', help_text='部品の分類カテゴリ', max_length=50, verbose_name='カテゴリ')),
                ('notes', models.TextField(blank=True, help_text='その他の補足情報', verbose_name='備考')),
                ('specifications', models.JSONField(blank=True, help_text='部品の詳細仕様をJSON形式で保存', null=True, verbose_name='仕様情報')),
                ('weight', models.DecimalField(blank=True, decimal_places=3, help_text='部品の重量', max_digits=10, null=True, verbose_name='重量(kg)')),
                ('dimensions', models.CharField(blank=True, help_text='部品の寸法情報（例：100x200x300mm）', max_length=100, verbose_name='寸法')),
            ],
            options={
                'verbose_name': 'コード基本情報',
                'verbose_name_plural': 'コード基本情報',
            },
        ),
        migrations.CreateModel(
            name='CodeVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('version', models.IntegerField(help_text='コードのバージョン（1から順に増加）', verbose_name='バージョン番号')),
                ('code_number', models.CharField(help_text='生成された完全なコード番号（例：AAA-A0001Z000）', max_length=50, verbose_name='コード番号')),
                ('is_current', models.BooleanField(default=True, help_text='このバージョンが現在有効なバージョンかどうか', verbose_name='現行バージョン')),
                ('status', models.CharField(choices=[('draft', '下書き'), ('review', 'レビュー中'), ('approved', '承認済み'), ('obsolete', '廃止')], default='draft', help_text='このバージョンの承認状態', max_length=20, verbose_name='ステータス')),
                ('reason', models.TextField(blank=True, help_text='このバージョンでの変更内容と理由', null=True, verbose_name='変更理由')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, help_text='このバージョンが有効となる日時', verbose_name='有効開始日')),
            ],
            options={
                'verbose_name': 'コードバージョン',
                'verbose_name_plural': 'コードバージョン',
                'ordering': ['-version'],
            },
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('name', models.CharField(help_text='コード生成時の接頭辞（例：AAA）', max_length=10, verbose_name='プレフィックス')),
                ('description', models.TextField(blank=True, help_text='プレフィックスの用途や使用条件等の説明', null=True, verbose_name='説明')),
                ('code_type', models.CharField(choices=[('1', '組'), ('2', '部品'), ('3', '購入品')], help_text='生成されるコードの種類（組、部品、購入品）', max_length=6, verbose_name='コード種別')),
                ('next_number', models.IntegerField(default=1, help_text='次に割り当てる連番', verbose_name='次の採番')),
            ],
            options={
                'verbose_name': 'プレフィックス',
                'verbose_name_plural': 'プレフィックス',
            },
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('name', models.CharField(help_text='ツリー構造の識別名', max_length=100, unique=True, verbose_name='ツリー名')),
                ('description', models.TextField(blank=True, help_text='ツリーの用途や特徴についての説明', null=True, verbose_name='説明')),
                ('status', models.CharField(choices=[('draft', '作成中'), ('active', '有効'), ('archived', 'アーカイブ'), ('locked', 'ロック中')], default='draft', help_text='ツリーの現在の状態', max_length=20, verbose_name='状態')),
                ('version', models.IntegerField(default=1, help_text='ツリーのバージョン番号', verbose_name='バージョン')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_trees', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('last_modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_trees', to=settings.AUTH_USER_MODEL, verbose_name='最終更新者')),
            ],
            options={
                'verbose_name': 'ツリー',
                'verbose_name_plural': 'ツリー',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TreeVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('version_number', models.IntegerField(help_text='ツリーのバージョンを示す番号（自動採番）', verbose_name='バージョン番号')),
                ('version_name', models.CharField(help_text='このバージョンの識別名', max_length=100, verbose_name='バージョン名')),
                ('version_description', models.TextField(blank=True, help_text='このバージョンでの変更内容や特記事項', null=True, verbose_name='バージョン説明')),
                ('status', models.CharField(choices=[('draft', '作成中'), ('review', 'レビュー中'), ('approved', '承認済'), ('obsolete', '廃止'), ('rejected', '却下')], default='draft', help_text='このバージョンの現在の状態', max_length=20, verbose_name='状態')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, help_text='このバージョンが有効となる日時', verbose_name='有効開始日')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='このバージョンが無効となる日時', null=True, verbose_name='有効終了日')),
                ('review_comments', models.TextField(blank=True, help_text='レビュー時のコメントや指摘事項', null=True, verbose_name='レビューコメント')),
                ('change_summary', models.JSONField(blank=True, help_text='前バージョンからの変更内容のサマリー', null=True, verbose_name='変更サマリー')),
                ('approved_by', models.ForeignKey(blank=True, help_text='このバージョンを承認したユーザー', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_versions', to=settings.AUTH_USER_MODEL, verbose_name='承認者')),
                ('created_by', models.ForeignKey(help_text='このバージョンを作成したユーザー', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_versions', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
                ('tree', models.ForeignKey(help_text='バージョン管理対象のツリー', on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='pdm4.tree', verbose_name='ツリー')),
            ],
            options={
                'verbose_name': 'ツリーバージョン',
                'verbose_name_plural': 'ツリーバージョン',
                'ordering': ['-version_number'],
            },
        ),
        migrations.CreateModel(
            name='TreeStructure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('level', models.IntegerField(help_text='ツリー内での深さ（0がルート）', verbose_name='階層レベル')),
                ('path', models.CharField(help_text='ルートからの経路をIDで表現（例: 1.2.3）', max_length=255, verbose_name='パス')),
                ('sequence', models.IntegerField(default=0, help_text='同じ階層内での表示順序', verbose_name='表示順序')),
                ('relationship_type', models.CharField(choices=[('assembly', '組立'), ('reference', '参照'), ('option', 'オプション'), ('spare', '予備品'), ('alternate', '代替品'), ('phantom', 'ファントム')], default='assembly', help_text='親子関係の種類を指定', max_length=20, verbose_name='関係タイプ')),
                ('is_master', models.BooleanField(default=False, help_text='この構造が共有のマスターかどうか', verbose_name='マスター構造')),
                ('quantity', models.DecimalField(decimal_places=3, default=1.0, help_text='この構造での使用数量', max_digits=10, verbose_name='数量')),
                ('effective_date', models.DateTimeField(blank=True, help_text='この構造が有効となる日時', null=True, verbose_name='有効開始日')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='この構造が無効となる日時', null=True, verbose_name='有効終了日')),
                ('current_node', models.ForeignKey(blank=True, help_text='この構造が表す部品コード', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='pdm4.code', verbose_name='現在のノード')),
                ('parent', models.ForeignKey(blank=True, help_text='上位の部品コード', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pdm4.code', verbose_name='親ノード')),
                ('source_structure', models.ForeignKey(blank=True, help_text='この構造が共有している元の構造', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shared_instances', to='pdm4.treestructure', verbose_name='共有元構造')),
                ('tree', models.ForeignKey(help_text='このノードが属するツリー', on_delete=django.db.models.deletion.CASCADE, related_name='relationships', to='pdm4.tree', verbose_name='所属ツリー')),
            ],
            options={
                'verbose_name': 'ツリー構造',
                'verbose_name_plural': 'ツリー構造',
                'ordering': ['level', 'sequence'],
            },
        ),
        migrations.CreateModel(
            name='TreeCodeQuantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('quantity', models.DecimalField(decimal_places=3, default=1.0, help_text='組立に必要な数量', max_digits=10, verbose_name='員数')),
                ('denominator', models.DecimalField(decimal_places=3, default=1.0, help_text='製品1台あたりの使用数', max_digits=10, verbose_name='母数')),
                ('unit', models.CharField(choices=[('piece', '個'), ('meter', 'm'), ('kilogram', 'kg'), ('liter', 'L'), ('set', 'セット'), ('sheet', '枚'), ('roll', '巻'), ('other', 'その他')], default='piece', help_text='数量の単位（個、m、kg等）', max_length=20, verbose_name='単位')),
                ('loss_rate', models.DecimalField(decimal_places=2, default=0.0, help_text='予期される損失の割合', max_digits=5, verbose_name='ロス率(%)')),
                ('minimum_order', models.DecimalField(blank=True, decimal_places=3, help_text='一度に発注可能な最小数量', max_digits=10, null=True, verbose_name='最小発注量')),
                ('remarks', models.TextField(blank=True, help_text='数量に関する補足情報', verbose_name='備考')),
                ('effective_date', models.DateTimeField(default=django.utils.timezone.now, help_text='この数量情報が有効となる日時', verbose_name='有効開始日')),
                ('expiry_date', models.DateTimeField(blank=True, help_text='この数量情報が無効となる日時', null=True, verbose_name='有効終了日')),
                ('code_version', models.ForeignKey(help_text='数量情報が紐づく部品コードのバージョン', on_delete=django.db.models.deletion.CASCADE, related_name='tree_quantities', to='pdm4.codeversion', verbose_name='コードバージョン')),
                ('tree_structure', models.ForeignKey(help_text='数量情報が紐づくツリー構造', on_delete=django.db.models.deletion.CASCADE, related_name='quantities', to='pdm4.treestructure', verbose_name='ツリー構造')),
            ],
            options={
                'verbose_name': 'ツリー内数量情報',
                'verbose_name_plural': 'ツリー内数量情報',
            },
        ),
        migrations.CreateModel(
            name='TreeChangeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='レコードが作成された日時', verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='レコードが最後に更新された日時', verbose_name='更新日時')),
                ('changed_at', models.DateTimeField(auto_now_add=True, help_text='変更が行われた日時', verbose_name='変更日時')),
                ('change_type', models.CharField(choices=[('add_node', 'ノード追加'), ('remove_node', 'ノード削除'), ('move_node', 'ノード移動'), ('update_quantity', '数量更新'), ('update_relationship', '関係タイプ更新'), ('share_structure', '構造共有'), ('unshare_structure', '構造共有解除'), ('update_metadata', 'メタデータ更新'), ('version_up', 'バージョンアップ'), ('status_change', 'ステータス変更'), ('approval_change', '承認状態変更'), ('comment_add', 'コメント追加')], help_text='実施された変更の種類', max_length=20, verbose_name='変更タイプ')),
                ('description', models.TextField(help_text='変更の詳細な説明', verbose_name='変更内容')),
                ('previous_data', models.JSONField(blank=True, help_text='変更前の状態をJSON形式で保存', null=True, verbose_name='変更前データ')),
                ('new_data', models.JSONField(blank=True, help_text='変更後の状態をJSON形式で保存', null=True, verbose_name='変更後データ')),
                ('significance_level', models.IntegerField(choices=[(0, '軽微'), (1, '通常'), (2, '重要'), (3, '緊急')], default=1, help_text='変更の重要度レベル', verbose_name='重要度')),
                ('reference_documents', models.TextField(blank=True, help_text='変更に関連する文書や図面の参照情報', verbose_name='関連文書')),
                ('requires_approval', models.BooleanField(default=False, help_text='この変更が承認を必要とするかどうか', verbose_name='承認要否')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='承認日時')),
                ('notification_sent', models.BooleanField(default=False, help_text='関係者への通知が送信済みかどうか', verbose_name='通知送信済み')),
                ('affected_node', models.ForeignKey(blank=True, help_text='変更の影響を受けたノード', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tree_changes', to='pdm4.code', verbose_name='影響ノード')),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_changes', to=settings.AUTH_USER_MODEL, verbose_name='承認者')),
                ('changed_by', models.ForeignKey(help_text='変更を実施したユーザー', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tree_changes', to=settings.AUTH_USER_MODEL, verbose_name='変更者')),
                ('tree_version', models.ForeignKey(help_text='変更が発生したツリーのバージョン', on_delete=django.db.models.deletion.CASCADE, related_name='change_logs', to='pdm4.treeversion', verbose_name='ツリーバージョン')),
            ],
            options={
                'verbose_name': 'ツリー変更履歴',
                'verbose_name_plural': 'ツリー変更履歴',
                'ordering': ['-changed_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='prefix',
            constraint=models.UniqueConstraint(fields=('name',), name='pdm4_unique_prefix_name'),
        ),
        migrations.AddField(
            model_name='codeversion',
            name='changed_by',
            field=models.ForeignKey(help_text='このバージョンを作成したユーザー', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='変更者'),
        ),
        migrations.AddField(
            model_name='codeversion',
            name='code',
            field=models.ForeignKey(help_text='バージョン管理対象のコード', on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='pdm4.code', verbose_name='部品コード'),
        ),
        migrations.AddField(
            model_name='codemetadata',
            name='code_version',
            field=models.OneToOneField(help_text='この属性情報が紐づくコードバージョン', on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='pdm4.codeversion', verbose_name='コードバージョン'),
        ),
        migrations.AddField(
            model_name='codechangelog',
            name='changed_by',
            field=models.ForeignKey(help_text='変更を行ったユーザー', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='変更者'),
        ),
        migrations.AddField(
            model_name='codechangelog',
            name='code_version',
            field=models.ForeignKey(help_text='変更が発生したコードバージョン', on_delete=django.db.models.deletion.CASCADE, related_name='change_logs', to='pdm4.codeversion', verbose_name='コードバージョン'),
        ),
        migrations.AddField(
            model_name='code',
            name='prefix',
            field=models.ForeignKey(help_text='このコードが使用するプレフィックス', on_delete=django.db.models.deletion.PROTECT, related_name='codes', to='pdm4.prefix', verbose_name='プレフィックス'),
        ),
        migrations.AddIndex(
            model_name='treeversion',
            index=models.Index(fields=['-version_number'], name='pdm4_tv_number_idx'),
        ),
        migrations.AddIndex(
            model_name='treeversion',
            index=models.Index(fields=['status'], name='pdm4_tv_status_idx'),
        ),
        migrations.AddIndex(
            model_name='treeversion',
            index=models.Index(fields=['effective_date'], name='pdm4_tv_ver_effective_date_idx'),
        ),
        migrations.AddIndex(
            model_name='treeversion',
            index=models.Index(fields=['expiry_date'], name='pdm4_tv_ver_expiry_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='treeversion',
            constraint=models.UniqueConstraint(fields=('tree', 'version_number'), name='pdm4_unique_tree_version'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['tree', 'level'], name='pdm4_tree_level_idx'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['path'], name='pdm4_path_idx'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['is_master'], name='pdm4_master_idx'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['relationship_type'], name='pdm4_rel_type_idx'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['effective_date'], name='pdm4_effective_date_idx'),
        ),
        migrations.AddIndex(
            model_name='treestructure',
            index=models.Index(fields=['expiry_date'], name='pdm4_expiry_date_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='treestructure',
            unique_together={('parent', 'current_node', 'tree')},
        ),
        migrations.AddIndex(
            model_name='treecodequantity',
            index=models.Index(fields=['quantity'], name='pdm4_quantity_idx'),
        ),
        migrations.AddIndex(
            model_name='treecodequantity',
            index=models.Index(fields=['denominator'], name='pdm4_denominator_idx'),
        ),
        migrations.AddIndex(
            model_name='treecodequantity',
            index=models.Index(fields=['unit'], name='pdm4_unit_idx'),
        ),
        migrations.AddIndex(
            model_name='treecodequantity',
            index=models.Index(fields=['effective_date'], name='pdm4_qty_effective_date_idx'),
        ),
        migrations.AddIndex(
            model_name='treecodequantity',
            index=models.Index(fields=['expiry_date'], name='pdm4_qty_expiry_date_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='treecodequantity',
            unique_together={('tree_structure', 'code_version')},
        ),
        migrations.AddIndex(
            model_name='treechangelog',
            index=models.Index(fields=['-changed_at'], name='pdm4_tree_change_date_idx'),
        ),
        migrations.AddIndex(
            model_name='treechangelog',
            index=models.Index(fields=['change_type'], name='pdm4_tree_change_type_idx'),
        ),
        migrations.AddIndex(
            model_name='treechangelog',
            index=models.Index(fields=['significance_level'], name='pdm4_tree_significance_idx'),
        ),
        migrations.AddIndex(
            model_name='treechangelog',
            index=models.Index(fields=['affected_node'], name='pdm4_tree_affected_node_idx'),
        ),
        migrations.AddIndex(
            model_name='treechangelog',
            index=models.Index(fields=['requires_approval', 'approved_by'], name='pdm4_tree_approval_idx'),
        ),
        migrations.AddIndex(
            model_name='tree',
            index=models.Index(fields=['status'], name='pdm4_tree_status_idx'),
        ),
        migrations.AddIndex(
            model_name='tree',
            index=models.Index(fields=['name'], name='pdm4_tree_name_idx'),
        ),
        migrations.AddIndex(
            model_name='codeversion',
            index=models.Index(fields=['code_number'], name='pdm4_cv_number_idx'),
        ),
        migrations.AddIndex(
            model_name='codeversion',
            index=models.Index(fields=['code', '-version'], name='pdm4_cv_version_idx'),
        ),
        migrations.AddIndex(
            model_name='codeversion',
            index=models.Index(fields=['status'], name='pdm4_cv_version_status_idx'),
        ),
        migrations.AddIndex(
            model_name='codeversion',
            index=models.Index(fields=['effective_date'], name='pdm4_cv_effective_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='codeversion',
            constraint=models.UniqueConstraint(condition=models.Q(('is_current', True)), fields=('code',), name='pdm4_unique_current_version'),
        ),
        migrations.AddConstraint(
            model_name='codeversion',
            constraint=models.UniqueConstraint(fields=('code', 'version'), name='pdm4_unique_code_version'),
        ),
        migrations.AddIndex(
            model_name='codemetadata',
            index=models.Index(fields=['unit'], name='pdm4_metadata_unit_idx'),
        ),
        migrations.AddIndex(
            model_name='codemetadata',
            index=models.Index(fields=['material'], name='pdm4_metadata_material_idx'),
        ),
        migrations.AddIndex(
            model_name='codemetadata',
            index=models.Index(fields=['category'], name='pdm4_metadata_category_idx'),
        ),
        migrations.AddIndex(
            model_name='codechangelog',
            index=models.Index(fields=['-changed_at'], name='pdm4_change_log_date_idx'),
        ),
        migrations.AddIndex(
            model_name='codechangelog',
            index=models.Index(fields=['change_type'], name='pdm4_change_type_idx'),
        ),
        migrations.AddIndex(
            model_name='codechangelog',
            index=models.Index(fields=['code_version', '-changed_at'], name='pdm4_version_change_idx'),
        ),
        migrations.AddIndex(
            model_name='code',
            index=models.Index(fields=['status'], name='pdm4_code_status_idx'),
        ),
        migrations.AddIndex(
            model_name='code',
            index=models.Index(fields=['code'], name='pdm4_code_idx'),
        ),
        migrations.AddConstraint(
            model_name='code',
            constraint=models.UniqueConstraint(fields=('prefix', 'sequential_number'), name='pdm4_unique_code_number'),
        ),
        migrations.AddConstraint(
            model_name='code',
            constraint=models.UniqueConstraint(fields=('code',), name='pdm4_unique_code'),
        ),
    ]
