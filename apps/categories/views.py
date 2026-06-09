from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from .models import Categorie
from .serializers import CategorieSerializer


class CategorieViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Categorie.objects.filter(is_active=True)
    serializer_class = CategorieSerializer
