# Generated by Django 4.2.9 on 2024-08-08 06:54

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pdm", "0003_rename_parent_id_tree_children_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tree",
            old_name="children_id",
            new_name="parent_id",
        ),
    ]
