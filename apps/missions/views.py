from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import models
from django.shortcuts import get_object_or_404

from .models import Mission, Candidature, PhotoMission, PhotoService, ServicePrestataire, MissionFavorite
from apps.historique.models import HistoriqueConsultation
from .permissions import IsRecruteur, IsChercheur, IsProprietaireMission
from .serializers import (
    MissionListSerializer, MissionDetailSerializer, MissionCreateSerializer,
    MissionStatutSerializer, CandidatureSerializer, CandidatureActionSerializer,
    PhotoMissionSerializer, PhotoServiceSerializer,
    EvaluationSerializer, ServicePrestataireSerializer,
    MissionFavoriteSerializer,
)


class MissionViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['quartier', 'categorie', 'statut']
    search_fields = ['titre', 'description']
    ordering_fields = ['remuneration', 'date_publication']
    ordering = ['-date_publication']

    def get_serializer_class(self):
        if self.action == 'list':
            return MissionListSerializer
        if self.action == 'create':
            return MissionCreateSerializer
        if self.action in ('update', 'partial_update'):
            return MissionCreateSerializer
        if self.action == 'changer_statut':
            return MissionStatutSerializer
        return MissionDetailSerializer

    def get_queryset(self):
        qs = Mission.objects.filter(is_active=True).select_related(
            'recruteur', 'quartier', 'categorie',
        ).prefetch_related('photos')

        if self.action == 'list':
            user = self.request.user
            if user.is_authenticated and user.role == 'recruteur':
                qs = qs.filter(models.Q(recruteur=user) | models.Q(statut='publiee'))
            else:
                qs = qs.filter(statut='publiee')
            return qs

        user = self.request.user
        if self.action in ('update', 'partial_update', 'destroy', 'changer_statut'):
            qs = qs.filter(recruteur=user)

        return qs

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsRecruteur()]
        if self.action in ('update', 'partial_update', 'destroy', 'changer_statut'):
            return [IsAuthenticated(), IsRecruteur(), IsProprietaireMission()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(recruteur=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = MissionCreateSerializer(
            data=request.data, context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        mission = serializer.save(recruteur=request.user)
        detail_serializer = MissionDetailSerializer(
            mission, context={'request': request},
        )
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        if instance.statut != 'publiee':
            raise PermissionDenied("Seules les missions publiées peuvent être supprimées.")
        instance.is_active = False
        instance.save()

    @action(detail=True, methods=['post'])
    def changer_statut(self, request, pk=None):
        mission = self.get_object()
        serializer = MissionStatutSerializer(
            data=request.data, context={'mission': mission},
        )
        serializer.is_valid(raise_exception=True)
        mission.statut = serializer.validated_data['statut']
        mission.save()
        return Response(MissionDetailSerializer(mission, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def photos(self, request, pk=None):
        mission = self.get_object()
        self.check_object_permissions(request, mission)

        images = request.FILES.getlist('images')
        photos = []
        for idx, image in enumerate(images):
            photo = PhotoMission.objects.create(
                mission=mission, image=image, ordre=idx,
            )
            photos.append(PhotoMissionSerializer(photo).data)
        return Response(photos, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def supprimer_photo(self, request, pk=None, photo_id=None):
        mission = self.get_object()
        self.check_object_permissions(request, mission)
        photo = mission.photos.get(id=photo_id)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favori(self, request, pk=None):
        mission = self.get_object()
        favori, created = MissionFavorite.objects.get_or_create(
            chercheur=request.user, mission=mission,
        )
        if not created:
            favori.delete()
            return Response({'favori': False})
        return Response({'favori': True})

    def retrieve(self, request, *args, **kwargs):
        mission = self.get_object()
        if request.user.role == 'chercheur':
            HistoriqueConsultation.objects.update_or_create(
                chercheur=request.user, mission=mission,
                defaults={'date_consultation': timezone.now()},
            )
        serializer = self.get_serializer(mission)
        return Response(serializer.data)


class CandidatureViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CandidatureSerializer
        return CandidatureSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'chercheur':
            return Candidature.objects.filter(chercheur=user).select_related('mission', 'chercheur')
        return Candidature.objects.filter(mission__recruteur=user).select_related('mission', 'chercheur')

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsChercheur()]
        if self.action in ('accepter', 'refuser'):
            return [IsAuthenticated(), IsRecruteur()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['patch'])
    def accepter(self, request, pk=None):
        candidature = get_object_or_404(
            Candidature.objects.select_related('mission', 'chercheur'), pk=pk,
        )
        if candidature.mission.recruteur != request.user:
            return Response({'detail': 'Action non autorisée.'}, status=status.HTTP_403_FORBIDDEN)
        if candidature.statut != 'en_attente':
            return Response({'detail': 'Cette candidature n\'est plus en attente.'}, status=400)

        candidature.statut = 'acceptee'
        candidature.date_reponse = timezone.now()
        candidature.save()

        candidature.mission.statut = 'en_cours'
        candidature.mission.save()

        candidature.mission.candidatures.exclude(id=candidature.id).filter(
            statut='en_attente',
        ).update(statut='refusee')

        return Response(CandidatureSerializer(candidature).data)

    @action(detail=True, methods=['patch'])
    def refuser(self, request, pk=None):
        candidature = get_object_or_404(
            Candidature.objects.select_related('mission', 'chercheur'), pk=pk,
        )
        if candidature.mission.recruteur != request.user:
            return Response({'detail': 'Action non autorisée.'}, status=status.HTTP_403_FORBIDDEN)
        if candidature.statut != 'en_attente':
            return Response({'detail': 'Cette candidature n\'est plus en attente.'}, status=400)

        candidature.statut = 'refusee'
        candidature.date_reponse = timezone.now()
        candidature.save()
        return Response(CandidatureSerializer(candidature).data)

    @action(detail=True, methods=['patch'])
    def retirer(self, request, pk=None):
        candidature = get_object_or_404(
            Candidature.objects.select_related('mission', 'chercheur'), pk=pk,
        )
        if candidature.chercheur != request.user:
            return Response({'detail': 'Action non autorisée.'}, status=status.HTTP_403_FORBIDDEN)
        if candidature.statut != 'en_attente':
            return Response({'detail': 'Cette candidature ne peut plus être retirée.'}, status=400)

        candidature.statut = 'retiree'
        candidature.save()
        return Response(CandidatureSerializer(candidature).data)


class MissionCandidatureViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CandidatureSerializer

    def get_queryset(self):
        return Candidature.objects.filter(mission_id=self.kwargs['mission_pk']).select_related(
            'chercheur', 'mission',
        )

    def perform_create(self, serializer):
        mission = Mission.objects.get(id=self.kwargs['mission_pk'])
        if mission.statut != 'publiee':
            raise serializers.ValidationError("Cette mission n'accepte plus de candidatures.")
        if Candidature.objects.filter(mission=mission, chercheur=self.request.user).exists():
            raise serializers.ValidationError("Vous avez déjà postulé à cette mission.")
        serializer.save(chercheur=self.request.user, mission=mission)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsChercheur()]
        return [IsAuthenticated(), IsRecruteur()]


class EvaluationViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsRecruteur]
    serializer_class = EvaluationSerializer


class ServicePrestataireViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            from .serializers import ServicePrestataireListSerializer
            return ServicePrestataireListSerializer
        return ServicePrestataireSerializer

    def get_queryset(self):
        return ServicePrestataire.objects.filter(chercheur=self.request.user)

    def perform_create(self, serializer):
        serializer.save(chercheur=self.request.user)

    @action(detail=True, methods=['post'])
    def photos(self, request, pk=None):
        service = self.get_object()
        images = request.FILES.getlist('images')
        photos = []
        for idx, image in enumerate(images):
            photo = PhotoService.objects.create(
                service=service, image=image, ordre=idx,
            )
            photos.append(PhotoServiceSerializer(photo).data)
        return Response(photos, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='photos/(?P<photo_id>[^/.]+)')
    def supprimer_photo(self, request, pk=None, photo_id=None):
        service = self.get_object()
        photo = service.photos.get(id=photo_id)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MissionFavoriteViewSet(ListModelMixin, CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated, IsChercheur]
    serializer_class = MissionFavoriteSerializer

    def get_queryset(self):
        return MissionFavorite.objects.filter(chercheur=self.request.user)
