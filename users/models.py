from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
# Create your models here.

class UserManager(BaseUserManager):

    def _create_user(self, userid, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        user = self.model(
            userid=userid,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    # create_user
    def create_user(self, userid, password,**extra_fields):
        return self._create_user(userid, password, False, False, **extra_fields)
    
    # create_superuser
    def create_superuser(self, userid, password, **extra_fields):
        return self._create_user(userid, password, True, True, **extra_fields)
    

class User(AbstractUser):
    username = None
    userid = models.CharField(unique=True, max_length=255)
    nickname = models.CharField(max_length=50, null=False, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'userid'
    user_name_FIELD ='userid'
    REQUIRED_FIELDS = []

    objects = UserManager()


class RefreshToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='refresh_token')
    token = models.CharField(max_length=511)


class Rank(models.Model):
    user = models.ForeignKey(User,blank=False, null=False, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    score_time = models.DateField(blank=True, null=True)