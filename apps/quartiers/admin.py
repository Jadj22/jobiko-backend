from django.contrib import admin
from .models import Quartier


@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('nom',)
