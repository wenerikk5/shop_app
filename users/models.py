from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    address = models.TextField(max_length=300, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    postal_code = models.CharField(max_length=12, blank=True, null=True)
