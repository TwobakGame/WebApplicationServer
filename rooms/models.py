from django.db import models

# Create your models here.

class room(models.Model):
    room = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.room