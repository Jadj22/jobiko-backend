from django.contrib import admin
from .models import Categorie, SousCategorie


class SousCategorieInline(admin.TabularInline):
    model = SousCategorie
    extra = 1


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('nom',)
    inlines = [SousCategorieInline]


@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'is_active')
    list_filter = ('categorie', 'is_active')
    search_fields = ('nom',)
