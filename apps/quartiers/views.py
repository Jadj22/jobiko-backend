from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from .models import Quartier
from .serializers import QuartierListSerializer, QuartierDetailSerializer


class QuartierViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Quartier.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return QuartierListSerializer
        return QuartierDetailSerializer
