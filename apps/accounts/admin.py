from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('telephone', 'nom_complet', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('telephone', 'nom_complet')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('telephone', 'password')}),
        ('Informations personnelles', {'fields': ('nom_complet', 'photo', 'description', 'quartier')}),
        ('Rôle', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telephone', 'nom_complet', 'role', 'password1', 'password2'),
        }),
    )
