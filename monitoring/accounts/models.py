# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Additional field for storing the cloud API password
    cloud_api_password = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
