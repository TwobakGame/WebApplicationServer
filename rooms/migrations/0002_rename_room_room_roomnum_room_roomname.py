# Generated by Django 5.0 on 2024-01-27 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='room',
            new_name='roomNum',
        ),
        migrations.AddField(
            model_name='room',
            name='roomName',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
    ]
