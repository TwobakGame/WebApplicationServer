from django.db import models
from users.models import User

# Create your models here.

class room(models.Model):
    user = models.ForeignKey(User,blank=True, null=True ,on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, null=True)
