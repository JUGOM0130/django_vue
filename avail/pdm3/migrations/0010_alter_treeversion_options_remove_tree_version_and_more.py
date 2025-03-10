# Generated by Django 4.2.9 on 2025-03-10 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdm3', '0009_alter_treestructure_child_alter_treestructure_parent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='treeversion',
            options={'ordering': ['-version_number']},
        ),
        migrations.RemoveField(
            model_name='tree',
            name='version',
        ),
        migrations.AddField(
            model_name='treeversion',
            name='version_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='treeversion',
            index=models.Index(fields=['-version_number'], name='version_number_desc_idx'),
        ),
        migrations.AddConstraint(
            model_name='treeversion',
            constraint=models.UniqueConstraint(fields=('tree', 'version_number'), name='unique_tree_version'),
        ),
    ]
