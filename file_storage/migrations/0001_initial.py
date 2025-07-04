# file_storage/migrations/0001_initial.py

from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ActionLog',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID'
                    ),
                ),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                (
                    'action_type',
                    models.CharField(
                        choices=[
                            ('upload', 'Upload'),
                            ('download', 'Download'),
                        ],
                        max_length=10
                    ),
                ),
                ('filename', models.CharField(max_length=255)),
                ('file_extension', models.CharField(max_length=10, blank=True, null=True)),
                ('original_filename', models.CharField(max_length=255, blank=True, null=True)),
            ],
        ),
    ]