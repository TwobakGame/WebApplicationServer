# Generated by Django 5.0 on 2024-02-02 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_user_score_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='score_time',
            field=models.DateField(blank=True, null=True),
        ),
    ]