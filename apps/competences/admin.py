from django.contrib import admin
from .models import Competence, CompetenceUser


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('nom',)


@admin.register(CompetenceUser)
class CompetenceUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'competence')
    list_filter = ('competence',)
    search_fields = ('user__nom_complet', 'competence__nom')
