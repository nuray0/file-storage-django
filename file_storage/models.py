from django.db import models
from django.utils import timezone


class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('upload', 'Upload'),
        ('download', 'Download'),
    ]

    user_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    filename = models.CharField(
        max_length=255
    )  # The saved zip or restored file
    original_filename = models.CharField(
        max_length=255, null=True, blank=True
    )  # New field
    file_extension = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'[{self.timestamp}] {self.action_type} - {self.filename}'
