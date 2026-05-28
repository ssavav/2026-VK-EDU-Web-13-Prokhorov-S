import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

def avatar_upload_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    now = timezone.now()
    return os.path.join(f'avatars/{now.year}/{now.month:02d}/{now.day:02d}/', filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True, verbose_name='Аватар')
    nickname = models.SlugField(max_length=50, null=True, blank=True, verbose_name='Никнейм')

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'