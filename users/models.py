import string
import uuid
import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from users.sender import send_otp


# Create your models here.
class User(AbstractUser):
    pass
class OtpRequestQuerySet(models.QuerySet):
    def is_valid(self,receiver,password,request):
        current_time = timezone.now()
        return self.filter(
            receiver=receiver,
            request_id = request,
            password = password,
            created__lt=current_time,
            created__gt=current_time - timedelta(seconds=120),
        ).exists()



class OtpManager(models.Manager):
    def get_queryset(self):
        return OtpRequestQuerySet(self.model, using=self._db)
    def is_valid(self,receiver,password,request):
        return self.get_queryset().is_valid(receiver,password,request)

    def generate(self,data):
        otp = self.model(receiver=data['receiver'],channel=data['channel'])
        send_otp(otp)
        otp.save(using=self._db)
        return otp
def Generateotp():
    rand = random.SystemRandom()
    digits = rand.choices(string.digits, k=4)
    return ''.join(digits)





class OtpRequest(models.Model):
    class OtpChannel(models.TextChoices):
        PHONE = 'phone'
        EMAIL = 'email'
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.CharField(max_length=10, choices=OtpChannel.choices, default=OtpChannel.PHONE)
    receiver = models.CharField(max_length=50)
    password = models.CharField(max_length=4,default=Generateotp)
    created = models.DateTimeField(auto_now_add=True)
    objects = OtpManager()