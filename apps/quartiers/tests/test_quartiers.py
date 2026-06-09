import pytest
from apps.accounts.models import User

pytestmark = pytest.mark.django_db


class TestQuartiers:
    def test_liste_quartiers(self, api_client):
        user = User.objects.create_user(
            telephone="+22899999999", password="p", nom_complet="Test", role="recruteur",
        )
        refresh = __import__('rest_framework_simplejwt').tokens.RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = api_client.get("/api/quartiers/")
        assert response.status_code == 200
        assert response.data["count"] == 10

    def test_liste_quartiers_avec_missions(self, auth_recruteur, quartier, mission):
        response = auth_recruteur.get("/api/quartiers/")
        assert response.status_code == 200
        assert response.data["count"] == 10
        adidogome = [q for q in response.data["results"] if q["nom"] == "Adidogomé"][0]
        assert adidogome["missions_disponibles"] == 1

    def test_quartier_inactif_cache(self, auth_recruteur, quartier):
        quartier.is_active = False
        quartier.save()
        response = auth_recruteur.get("/api/quartiers/")
        assert response.data["count"] == 9

    def test_non_auth_401(self, api_client):
        response = api_client.get("/api/quartiers/")
        assert response.status_code == 401
