# Generated by Django 4.2.9 on 2024-10-06 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdm', '0004_rename_children_id_tree_parent_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='RootNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('node_name', models.CharField(max_length=100, unique=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
    ]
