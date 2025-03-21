from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pdm3', '0006_codeversionhistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreeVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_name', models.CharField(max_length=100)),
                ('version_description', models.TextField(blank=True, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
            ],
        ),
        migrations.RenameModel(
            old_name='ParentChild',
            new_name='TreeStructure',
        ),
        migrations.AddField(
            model_name='codeversionhistory',
            name='node',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='version_histories', to='pdm3.node'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tree',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='TreeInstance',
        ),
        migrations.AddField(
            model_name='treeversion',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='pdm3.tree'),
        ),
    ]
