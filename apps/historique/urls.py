from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultationViewSet, PublicationViewSet

router = DefaultRouter()
router.register(r'historique/consultations', ConsultationViewSet, basename='consultation')
router.register(r'historique/publications', PublicationViewSet, basename='publication')

urlpatterns = [
    path('', include(router.urls)),
]
