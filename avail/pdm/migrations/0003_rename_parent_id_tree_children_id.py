# Generated by Django 4.2.9 on 2024-08-08 06:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pdm", "0002_alter_codeheader_code_header"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tree",
            old_name="parent_id",
            new_name="children_id",
        ),
    ]
