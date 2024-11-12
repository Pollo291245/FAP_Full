from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'notifications_enabled', 'created_at']
    list_filter = ['role', 'notifications_enabled', 'dark_mode']
    search_fields = ['user__email', 'user__username', 'phone', 'bio']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Información de Usuario', {
            'fields': ['user', 'role', 'bio']
        }),
        ('Información de Contacto', {
            'fields': ['phone', 'address']
        }),
        ('Preferencias', {
            'fields': ['notifications_enabled', 'dark_mode']
        }),
        ('Información del Sistema', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]