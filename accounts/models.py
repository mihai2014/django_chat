from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # additional fields in here
    address = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.email
        #return self.username