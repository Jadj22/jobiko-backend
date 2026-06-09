from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetenceViewSet, MesCompetencesViewSet

router = DefaultRouter()
router.register(r'competences', CompetenceViewSet, basename='competence')
router.register(r'mes-competences', MesCompetencesViewSet, basename='mes-competences')

urlpatterns = [
    path('', include(router.urls)),
]
