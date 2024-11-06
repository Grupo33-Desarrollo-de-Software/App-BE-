from django.db import models

# Create your models here.
class Album(models.Model):
    title = models.CharField(max_length=100)
    tags = models.CharField(max_length=100)
    releaseDate = models.DateField()
    length = models.IntegerField()  
    cover = models.CharField(max_length=300)
    playcount = models.PositiveBigIntegerField(null=True)

