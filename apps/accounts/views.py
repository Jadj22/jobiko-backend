from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Count, Avg, Sum
from .models import User
from .serializers import (
    RegisterSerializer, LoginSerializer, UserDetailSerializer, ProfilUpdateSerializer,
    ProfilPublicSerializer,
)
from apps.missions.models import Candidature, Evaluation


class AuthViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def inscription(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserDetailSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def connexion(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            telephone=serializer.validated_data['telephone'],
            password=serializer.validated_data['password'],
        )
        if not user:
            return Response(
                {'detail': 'Téléphone ou mot de passe incorrect.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserDetailSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class ProfilViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update', 'photo'):
            return ProfilUpdateSerializer
        if self.action == 'retrieve':
            return ProfilPublicSerializer
        return UserDetailSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @me.mapping.patch
    def me_update(self, request):
        serializer = ProfilUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(request.user).data)

    @action(detail=False, methods=['post'])
    def photo(self, request):
        user = request.user
        serializer = ProfilUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(user).data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        chercheur = self.get_object()
        candidatures = Candidature.objects.filter(chercheur=chercheur)
        stats = {
            'missions_terminees': candidatures.filter(
                statut='acceptee', mission__statut='terminee',
            ).count(),
            'missions_en_cours': candidatures.filter(
                statut='acceptee', mission__statut='en_cours',
            ).count(),
            'candidatures_envoyees': candidatures.count(),
            'taux_acceptation': round(
                candidatures.filter(statut='acceptee').count() / candidatures.exclude(statut__in=['retiree']).count() * 100
            ) if candidatures.exclude(statut__in=['retiree']).exists() else 0,
            'note_moyenne': Evaluation.objects.filter(chercheur=chercheur).aggregate(Avg('note'))['note__avg'],
            'revenus': candidatures.filter(
                statut='acceptee', mission__statut='terminee',
            ).aggregate(Sum('mission__remuneration'))['mission__remuneration__sum'] or 0,
        }
        return Response(stats)


class PrestataireViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilPublicSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['quartier']
    search_fields = ['nom_complet', 'description', 'quartier__nom']
    ordering_fields = ['date_joined', 'nom_complet']

    def get_queryset(self):
        from apps.missions.models import ServicePrestataire
        chercheur_ids = ServicePrestataire.objects.filter(
            is_active=True, chercheur__role='chercheur',
        ).values_list('chercheur_id', flat=True).distinct()
        qs = User.objects.filter(id__in=chercheur_ids)
        competence = self.request.query_params.get('competence')
        if competence:
            qs = qs.filter(competences__competence_id=competence)
        return qs
