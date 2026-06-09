from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MissionViewSet, CandidatureViewSet, MissionCandidatureViewSet,
    EvaluationViewSet, ServicePrestataireViewSet, MissionFavoriteViewSet,
)

router = DefaultRouter()
router.register(r'missions', MissionViewSet, basename='mission')
router.register(r'mes-candidatures', CandidatureViewSet, basename='candidature')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
router.register(r'services', ServicePrestataireViewSet, basename='service')
router.register(r'mes-favoris', MissionFavoriteViewSet, basename='favori')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'missions/<int:mission_pk>/candidatures/',
        MissionCandidatureViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='mission-candidatures',
    ),
]
