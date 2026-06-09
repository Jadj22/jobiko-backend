from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from .models import HistoriqueConsultation
from .serializers import HistoriqueConsultationSerializer
from apps.missions.models import Mission
from apps.missions.serializers import MissionListSerializer


class ConsultationViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HistoriqueConsultationSerializer

    def get_queryset(self):
        return HistoriqueConsultation.objects.filter(
            chercheur=self.request.user,
        ).select_related('mission', 'mission__quartier').order_by('-date_consultation')


class PublicationViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MissionListSerializer

    def get_queryset(self):
        return Mission.objects.filter(
            recruteur=self.request.user, is_active=True,
        ).select_related('recruteur', 'quartier', 'categorie').prefetch_related('photos')
