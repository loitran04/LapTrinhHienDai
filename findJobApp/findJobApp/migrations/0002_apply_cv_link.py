# Generated by Django 4.2.11 on 2025-05-17 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findJobApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apply',
            name='cv_link',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
    ]
