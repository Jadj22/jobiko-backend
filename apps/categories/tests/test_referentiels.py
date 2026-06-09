import pytest

pytestmark = pytest.mark.django_db


class TestCategories:
    def test_liste_categories(self, auth_recruteur, categorie):
        response = auth_recruteur.get("/api/categories/")
        assert response.status_code == 200
        assert response.data["count"] == 5

    def test_categorie_inactive_cachee(self, auth_recruteur, categorie):
        categorie.is_active = False
        categorie.save()
        response = auth_recruteur.get("/api/categories/")
        assert response.data["count"] == 4


class TestCompetences:
    def test_liste_competences(self, auth_chercheur, competence):
        response = auth_chercheur.get("/api/competences/")
        assert response.status_code == 200
        assert response.data["count"] == 20

    def test_competence_inactive_cachee(self, auth_chercheur, competence):
        competence.is_active = False
        competence.save()
        response = auth_chercheur.get("/api/competences/")
        assert response.data["count"] == 19
