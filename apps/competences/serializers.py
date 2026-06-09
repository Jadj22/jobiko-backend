from rest_framework import serializers
from .models import Competence, CompetenceUser


class CompetenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competence
        fields = ['id', 'nom']


class CompetenceUserSerializer(serializers.ModelSerializer):
    competence_nom = serializers.CharField(source='competence.nom', read_only=True)

    class Meta:
        model = CompetenceUser
        fields = ['id', 'competence', 'competence_nom']
