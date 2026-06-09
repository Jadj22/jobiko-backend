import pytest

pytestmark = pytest.mark.django_db

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import User
from apps.quartiers.models import Quartier
from apps.categories.models import Categorie
from apps.competences.models import Competence
from apps.missions.models import Mission, Candidature


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def quartier():
    obj, _ = Quartier.objects.get_or_create(nom="Adidogomé")
    return obj


@pytest.fixture
def categorie():
    obj, _ = Categorie.objects.get_or_create(nom="Transport")
    return obj


@pytest.fixture
def competence():
    obj, _ = Competence.objects.get_or_create(nom="Livraison")
    return obj


@pytest.fixture
def recruteur(quartier):
    user = User.objects.create_user(
        telephone="+22890123456",
        password="testpass123",
        nom_complet="Jean Recruteur",
        role="recruteur",
        quartier=quartier,
    )
    return user


@pytest.fixture
def chercheur(quartier, competence):
    user = User.objects.create_user(
        telephone="+22898765432",
        password="testpass123",
        nom_complet="Kofi Chercheur",
        role="chercheur",
        quartier=quartier,
    )
    user.competences.create(user=user, competence=competence)
    return user


@pytest.fixture
def autre_recruteur(quartier):
    return User.objects.create_user(
        telephone="+22811111111",
        password="testpass123",
        nom_complet="Autre Recruteur",
        role="recruteur",
    )


@pytest.fixture
def mission(recruteur, quartier, categorie):
    return Mission.objects.create(
        titre="Aide déménagement",
        description="Déplacer des meubles",
        recruteur=recruteur,
        quartier=quartier,
        categorie=categorie,
        type_date="unique",
        date_unique="2026-07-01",
        remuneration=10000,
        telephone_contact="+22890123456",
    )


@pytest.fixture
def mission_en_cours(mission):
    mission.statut = "en_cours"
    mission.save()
    return mission


@pytest.fixture
def candidature(mission, chercheur):
    return Candidature.objects.create(
        mission=mission,
        chercheur=chercheur,
    )


@pytest.fixture
def auth_recruteur(api_client, recruteur):
    refresh = RefreshToken.for_user(recruteur)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_chercheur(api_client, chercheur):
    refresh = RefreshToken.for_user(chercheur)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def auth_autre_recruteur(api_client, autre_recruteur):
    refresh = RefreshToken.for_user(autre_recruteur)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client
