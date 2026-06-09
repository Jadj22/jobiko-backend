from django.contrib import admin
from .models import Mission, PhotoMission, Candidature


class PhotoMissionInline(admin.TabularInline):
    model = PhotoMission
    extra = 0


class CandidatureInline(admin.TabularInline):
    model = Candidature
    extra = 0
    readonly_fields = ('date_candidature',)


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'recruteur', 'quartier', 'categorie', 'statut', 'remuneration', 'date_publication')
    list_filter = ('statut', 'quartier', 'categorie', 'type_date')
    search_fields = ('titre', 'description', 'recruteur__nom_complet')
    readonly_fields = ('date_publication', 'date_modification')
    inlines = [PhotoMissionInline, CandidatureInline]


@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):
    list_display = ('mission', 'chercheur', 'statut', 'date_candidature')
    list_filter = ('statut',)
    search_fields = ('mission__titre', 'chercheur__nom_complet')
    readonly_fields = ('date_candidature',)
