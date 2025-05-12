from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('findJobApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('admin', 'Admin'),
                    ('employer', 'Employer'),
                    ('candidate', 'Candidate')
                ],
                default='candidate'
            ),
        ),
    ]
