from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


User = get_user_model()
# Create your models here.
class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    License_plate = models.CharField(max_length=50)
    def clean(self):
        if self.user.addresses.count() >=3:
            raise ValidationError('شما فقط می‌توانید تا 3 آدرس ثبت کنید.')
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

