# Generated by Django 5.1.7 on 2025-03-07 14:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdm3', '0008_alter_codeversionhistory_node'),
    ]

    operations = [
        migrations.AlterField(
            model_name='treestructure',
            name='child',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='pdm3.node'),
        ),
        migrations.AlterField(
            model_name='treestructure',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='pdm3.node'),
        ),
    ]
