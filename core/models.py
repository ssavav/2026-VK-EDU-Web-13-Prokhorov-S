import uuid
import os
from django.db import models
from django.contrib.auth.models import User

def avatar_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join('avatars/', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'