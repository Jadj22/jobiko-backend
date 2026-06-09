from django.contrib import admin
from .models import HistoriqueConsultation


@admin.register(HistoriqueConsultation)
class HistoriqueConsultationAdmin(admin.ModelAdmin):
    list_display = ('chercheur', 'mission', 'date_consultation')
    search_fields = ('chercheur__nom_complet', 'mission__titre')
    readonly_fields = ('date_consultation',)
