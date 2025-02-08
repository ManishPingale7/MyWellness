from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'name', 'age', 'gender', 'height', 'weight', 'occupation']
    list_filter = ['is_staff', 'is_active', 'gender']
    search_fields = ['username', 'email', 'name']
    ordering = ['username']

admin.site.register(CustomUser, CustomUserAdmin)
