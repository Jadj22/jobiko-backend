from rest_framework import serializers
from .models import Categorie, SousCategorie


class SousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields = ['id', 'nom']


class CategorieSerializer(serializers.ModelSerializer):
    sous_categories = SousCategorieSerializer(many=True, read_only=True)

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'sous_categories']
