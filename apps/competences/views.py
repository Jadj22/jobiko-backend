from rest_framework.mixins import ListModelMixin, CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from .models import Competence, CompetenceUser
from .serializers import CompetenceSerializer, CompetenceUserSerializer


class CompetenceViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Competence.objects.filter(is_active=True)
    serializer_class = CompetenceSerializer


class MesCompetencesViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CompetenceUserSerializer

    def get_queryset(self):
        return CompetenceUser.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
