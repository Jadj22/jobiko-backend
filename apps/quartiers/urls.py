from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuartierViewSet

router = DefaultRouter()
router.register(r'quartiers', QuartierViewSet, basename='quartier')

urlpatterns = [
    path('', include(router.urls)),
]
