from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)