# Generated by Django 4.2.4 on 2024-02-22 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_user_nickname_alter_user_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refreshtoken',
            name='token',
            field=models.CharField(max_length=511),
        ),
    ]
