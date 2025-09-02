from django.db import models

# Create your models here.
# shops/models.py
from django.db import models


class Shop(models.Model):
 name = models.CharField(max_length=120)
 contact_phone = models.CharField(max_length=30, blank=True)
 latitude = models.FloatField(null=True, blank=True)
 longitude = models.FloatField(null=True, blank=True)


def __str__(self):
 return self.name