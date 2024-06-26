# Generated by Django 4.2.9 on 2024-04-22 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
            ],
        ),
        migrations.CreateModel(
            name='CodeHeader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_header', models.CharField(max_length=100, verbose_name='カテゴリ名')),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_id', models.CharField(max_length=100)),
                ('deep_level', models.IntegerField(verbose_name='階層')),
                ('parent_id', models.IntegerField(verbose_name='親Id')),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdm.code')),
            ],
        ),
        migrations.AddField(
            model_name='code',
            name='code_header',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pdm.codeheader'),
        ),
    ]
