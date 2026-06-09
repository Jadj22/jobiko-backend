from rest_framework import serializers
from .models import Quartier


class QuartierListSerializer(serializers.ModelSerializer):
    missions_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Quartier
        fields = ['id', 'nom', 'missions_disponibles']

    def get_missions_disponibles(self, obj):
        return obj.missions.filter(statut='publiee', is_active=True).count()


class QuartierDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quartier
        fields = ['id', 'nom']
