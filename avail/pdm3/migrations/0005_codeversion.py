# Generated by Django 4.2.9 on 2024-12-21 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdm3', '0004_prefix_code_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('version', models.IntegerField(default=0)),
            ],
        ),
    ]
