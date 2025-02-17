from django.db import models

class Log(models.Model):
    logtype = models.CharField(max_length=10)
    body = models.CharField(max_length=255)
