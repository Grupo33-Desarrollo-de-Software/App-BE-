from django.db import models

# Create your models here.
class Album(models.Model):
    title = models.CharField(max_length=100)
    genre = models.TextChoices("Rock", "Metal", "Pop", "Jazz", "Classical", "Reggae", "Reggaeton", "Rap", "Trap")
    releaseDate = models.DateField()
    length = models.DurationField()  
#   cover = models.ImageField(upload_to='album_covers/', null=True, blank=True)
    country = models.CharField(max_length=50)
#   rating = models.FloatField()
    released = models.BooleanField(default=False)
    playcount = models.PositiveBigIntegerField(null=True)

