from django.db import models

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    conten =models.CharField(max_length=255)