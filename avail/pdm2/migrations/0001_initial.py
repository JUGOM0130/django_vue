# Generated by Django 4.2.9 on 2024-11-09 07:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CodeHeader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_header', models.CharField(max_length=100, unique=True, verbose_name='カテゴリ名')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('en_number', models.IntegerField(verbose_name='英番号')),
                ('number', models.IntegerField(verbose_name='採番')),
                ('kind', models.IntegerField(verbose_name='コード種別')),
                ('code', models.CharField(max_length=100, unique=True, verbose_name='コード')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('code_header', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdm2.codeheader')),
            ],
        ),
        migrations.CreateModel(
            name='ParentChild',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='pdm2.node')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pdm2.node')),
                ('tree', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relationships', to='pdm2.tree')),
            ],
            options={
                'unique_together': {('parent', 'child', 'tree')},
            },
        ),
    ]
