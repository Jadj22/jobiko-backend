from rest_framework import serializers
from .models import HistoriqueConsultation


class HistoriqueConsultationSerializer(serializers.ModelSerializer):
    mission_titre = serializers.CharField(source='mission.titre', read_only=True)
    mission_remuneration = serializers.DecimalField(
        source='mission.remuneration', max_digits=10, decimal_places=0, read_only=True,
    )
    quartier_nom = serializers.CharField(source='mission.quartier.nom', read_only=True)

    class Meta:
        model = HistoriqueConsultation
        fields = [
            'id', 'mission', 'mission_titre', 'mission_remuneration',
            'quartier_nom', 'date_consultation',
        ]
