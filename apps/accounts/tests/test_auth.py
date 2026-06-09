import pytest

pytestmark = pytest.mark.django_db


class TestAuth:
    def test_inscription_chercheur(self, api_client):
        data = {
            "telephone": "+22899123456",
            "password": "secret123",
            "nom_complet": "Nouvel Utilisateur",
            "role": "chercheur",
        }
        response = api_client.post("/api/auth/inscription/", data, format="json")
        assert response.status_code == 201
        assert response.data["user"]["telephone"] == "+22899123456"
        assert response.data["user"]["role"] == "chercheur"
        assert "access" in response.data
        assert "refresh" in response.data

    def test_inscription_recruteur(self, api_client):
        data = {
            "telephone": "+22899123457",
            "password": "secret123",
            "nom_complet": "Nouveau Recruteur",
            "role": "recruteur",
        }
        response = api_client.post("/api/auth/inscription/", data, format="json")
        assert response.status_code == 201
        assert response.data["user"]["role"] == "recruteur"

    def test_inscription_telephone_duplicate(self, api_client, recruteur):
        data = {
            "telephone": recruteur.telephone,
            "password": "secret123",
            "nom_complet": "Doublon",
            "role": "chercheur",
        }
        response = api_client.post("/api/auth/inscription/", data, format="json")
        assert response.status_code == 400

    def test_inscription_password_trop_court(self, api_client):
        data = {
            "telephone": "+22899123458",
            "password": "ab",
            "nom_complet": "Test",
            "role": "chercheur",
        }
        response = api_client.post("/api/auth/inscription/", data, format="json")
        assert response.status_code == 400

    def test_connexion_succes(self, api_client, recruteur):
        data = {"telephone": recruteur.telephone, "password": "testpass123"}
        response = api_client.post("/api/auth/connexion/", data, format="json")
        assert response.status_code == 200
        assert "access" in response.data
        assert response.data["user"]["nom_complet"] == recruteur.nom_complet

    def test_connexion_mauvais_mot_de_passe(self, api_client, recruteur):
        data = {"telephone": recruteur.telephone, "password": "wrongpass"}
        response = api_client.post("/api/auth/connexion/", data, format="json")
        assert response.status_code == 401

    def test_connexion_inexistant(self, api_client):
        data = {"telephone": "+22800000001", "password": "testpass123"}
        response = api_client.post("/api/auth/connexion/", data, format="json")
        assert response.status_code == 401


class TestProfil:
    def test_get_profil(self, auth_recruteur, recruteur):
        response = auth_recruteur.get("/api/profil/me/")
        assert response.status_code == 200
        assert response.data["nom_complet"] == recruteur.nom_complet
        assert response.data["role"] == "recruteur"

    def test_get_profil_non_auth(self, api_client):
        response = api_client.get("/api/profil/me/")
        assert response.status_code == 401

    def test_update_profil(self, auth_recruteur, quartier):
        response = auth_recruteur.patch(
            "/api/profil/me/",
            {"description": "Nouvelle description", "quartier": quartier.id},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["description"] == "Nouvelle description"
