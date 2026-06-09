from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, ProfilViewSet, PrestataireViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'profil', ProfilViewSet, basename='profil')
router.register(r'prestataires', PrestataireViewSet, basename='prestataire')

urlpatterns = [
    path('', include(router.urls)),
]
