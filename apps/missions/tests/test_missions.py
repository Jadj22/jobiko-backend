import pytest

pytestmark = pytest.mark.django_db


class TestCreationMission:
    def test_recruteur_peut_publier(self, auth_recruteur, quartier, categorie):
        data = {
            "titre": "Jardinage urgent",
            "description": "Tondre la pelouse",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "unique",
            "date_unique": "2026-07-15",
            "remuneration": 5000,
            "telephone_contact": "+22890123456",
        }
        response = auth_recruteur.post("/api/missions/", data, format="json")
        assert response.status_code == 201

    def test_chercheur_ne_peut_pas_publier(self, auth_chercheur, quartier, categorie):
        data = {
            "titre": "Jardinage urgent",
            "description": "Tondre la pelouse",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "unique",
            "date_unique": "2026-07-15",
            "remuneration": 5000,
            "telephone_contact": "+22898765432",
        }
        response = auth_chercheur.post("/api/missions/", data, format="json")
        assert response.status_code == 403

    def test_non_auth_ne_peut_pas_publier(self, api_client, quartier, categorie):
        data = {
            "titre": "Test",
            "description": "Test",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "unique",
            "date_unique": "2026-07-15",
            "remuneration": 5000,
            "telephone_contact": "+22800000000",
        }
        response = api_client.post("/api/missions/", data, format="json")
        assert response.status_code == 401

    def test_date_plage_valide(self, auth_recruteur, quartier, categorie):
        data = {
            "titre": "Garde d'enfants",
            "description": "Garde du 1 au 5 juillet",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "plage",
            "date_debut": "2026-07-01",
            "date_fin": "2026-07-05",
            "remuneration": 15000,
            "telephone_contact": "+22890123456",
        }
        response = auth_recruteur.post("/api/missions/", data, format="json")
        assert response.status_code == 201

    def test_date_fin_avant_debut_invalide(self, auth_recruteur, quartier, categorie):
        data = {
            "titre": "Test",
            "description": "Test",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "plage",
            "date_debut": "2026-07-10",
            "date_fin": "2026-07-05",
            "remuneration": 5000,
            "telephone_contact": "+22890123456",
        }
        response = auth_recruteur.post("/api/missions/", data, format="json")
        assert response.status_code == 400

    def test_remuneration_zero_invalide(self, auth_recruteur, quartier, categorie):
        data = {
            "titre": "Test",
            "description": "Test",
            "quartier": quartier.id,
            "categorie": categorie.id,
            "type_date": "unique",
            "date_unique": "2026-07-15",
            "remuneration": 0,
            "telephone_contact": "+22890123456",
        }
        response = auth_recruteur.post("/api/missions/", data, format="json")
        assert response.status_code == 400


class TestConsultationMissions:
    def test_liste_missions_publiees(self, auth_chercheur, mission):
        response = auth_chercheur.get("/api/missions/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_liste_cache_missions_non_publiees(self, auth_chercheur, mission_en_cours):
        response = auth_chercheur.get("/api/missions/")
        assert response.data["count"] == 0

    def test_filtre_par_quartier(self, auth_chercheur, mission, quartier):
        response = auth_chercheur.get(f"/api/missions/?quartier={quartier.id}")
        assert response.data["count"] == 1

    def test_filtre_par_categorie(self, auth_chercheur, mission, categorie):
        response = auth_chercheur.get(f"/api/missions/?categorie={categorie.id}")
        assert response.data["count"] == 1

    def test_recherche_texte(self, auth_chercheur, mission):
        response = auth_chercheur.get("/api/missions/?search=déménagement")
        assert response.data["count"] == 1

    def test_detail_mission(self, auth_chercheur, mission):
        response = auth_chercheur.get(f"/api/missions/{mission.id}/")
        assert response.status_code == 200
        assert response.data["titre"] == "Aide déménagement"

    def test_detail_mission_enregistre_consultation(self, auth_chercheur, mission):
        auth_chercheur.get(f"/api/missions/{mission.id}/")
        response = auth_chercheur.get("/api/historique/consultations/")
        assert response.status_code == 200
        assert response.data["count"] == 1


class TestModificationMission:
    def test_proprietaire_peut_modifier(self, auth_recruteur, mission):
        response = auth_recruteur.patch(
            f"/api/missions/{mission.id}/",
            {"titre": "Nouveau titre"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["titre"] == "Nouveau titre"

    def test_non_proprietaire_ne_peut_pas_modifier(self, auth_autre_recruteur, mission):
        response = auth_autre_recruteur.patch(
            f"/api/missions/{mission.id}/",
            {"titre": "Titre volé"},
            format="json",
        )
        assert response.status_code == 404

    def test_chercheur_ne_peut_pas_modifier(self, auth_chercheur, mission):
        response = auth_chercheur.patch(
            f"/api/missions/{mission.id}/",
            {"titre": "Titre"},
            format="json",
        )
        assert response.status_code == 403


class TestChangementStatut:
    def test_publiee_vers_en_cours(self, auth_recruteur, mission):
        response = auth_recruteur.post(
            f"/api/missions/{mission.id}/changer_statut/",
            {"statut": "en_cours"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["statut"] == "en_cours"

    def test_en_cours_vers_terminee(self, auth_recruteur, mission_en_cours):
        response = auth_recruteur.post(
            f"/api/missions/{mission_en_cours.id}/changer_statut/",
            {"statut": "terminee"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["statut"] == "terminee"

    def test_transition_invalide(self, auth_recruteur, mission):
        response = auth_recruteur.post(
            f"/api/missions/{mission.id}/changer_statut/",
            {"statut": "terminee"},
            format="json",
        )
        assert response.status_code == 400

    def test_publiee_vers_annulee(self, auth_recruteur, mission):
        response = auth_recruteur.post(
            f"/api/missions/{mission.id}/changer_statut/",
            {"statut": "annulee"},
            format="json",
        )
        assert response.status_code == 200

    def test_non_proprietaire_statut(self, auth_autre_recruteur, mission):
        response = auth_autre_recruteur.post(
            f"/api/missions/{mission.id}/changer_statut/",
            {"statut": "en_cours"},
            format="json",
        )
        assert response.status_code == 404


class TestSuppressionMission:
    def test_proprietaire_peut_supprimer(self, auth_recruteur, mission):
        response = auth_recruteur.delete(f"/api/missions/{mission.id}/")
        assert response.status_code == 204

    def test_mission_en_cours_non_supprimable(self, auth_recruteur, mission_en_cours):
        response = auth_recruteur.delete(f"/api/missions/{mission_en_cours.id}/")
        assert response.status_code == 403

    def test_non_proprietaire_ne_peut_pas_supprimer(self, auth_autre_recruteur, mission):
        response = auth_autre_recruteur.delete(f"/api/missions/{mission.id}/")
        assert response.status_code == 404


class TestCandidatures:
    def test_chercheur_peut_postuler(self, auth_chercheur, mission):
        response = auth_chercheur.post(
            f"/api/missions/{mission.id}/candidatures/",
            format="json",
        )
        assert response.status_code == 201

    def test_recruteur_ne_peut_pas_postuler(self, auth_recruteur, mission):
        response = auth_recruteur.post(
            f"/api/missions/{mission.id}/candidatures/",
            format="json",
        )
        assert response.status_code == 403

    def test_double_candidature_refusee(self, auth_chercheur, mission, candidature):
        response = auth_chercheur.post(
            f"/api/missions/{mission.id}/candidatures/",
            format="json",
        )
        assert response.status_code == 400

    def test_candidature_sur_mission_en_cours(self, auth_chercheur, mission_en_cours):
        response = auth_chercheur.post(
            f"/api/missions/{mission_en_cours.id}/candidatures/",
            format="json",
        )
        assert response.status_code == 400

    def test_mes_candidatures(self, auth_chercheur, candidature):
        response = auth_chercheur.get("/api/mes-candidatures/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_recruteur_voit_candidatures_recues(self, auth_recruteur, mission, candidature):
        response = auth_recruteur.get(
            f"/api/missions/{mission.id}/candidatures/",
        )
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_recruteur_accepte_candidature(self, auth_recruteur, candidature):
        response = auth_recruteur.patch(
            f"/api/mes-candidatures/{candidature.id}/accepter/",
            format="json",
        )
        assert response.status_code == 200
        candidature.refresh_from_db()
        assert candidature.statut == "acceptee"
        assert candidature.mission.statut == "en_cours"

    def test_recruteur_refuse_candidature(self, auth_recruteur, candidature):
        response = auth_recruteur.patch(
            f"/api/mes-candidatures/{candidature.id}/refuser/",
            format="json",
        )
        assert response.status_code == 200
        candidature.refresh_from_db()
        assert candidature.statut == "refusee"

    def test_chercheur_retire_candidature(self, auth_chercheur, candidature):
        response = auth_chercheur.patch(
            f"/api/mes-candidatures/{candidature.id}/retirer/",
            format="json",
        )
        assert response.status_code == 200
        candidature.refresh_from_db()
        assert candidature.statut == "retiree"

    def test_autre_recruteur_ne_peut_pas_accepter(self, auth_autre_recruteur, candidature):
        response = auth_autre_recruteur.patch(
            f"/api/mes-candidatures/{candidature.id}/accepter/",
            format="json",
        )
        assert response.status_code == 403


class TestHistorique:
    def test_historique_consultations(self, auth_chercheur, mission):
        auth_chercheur.get(f"/api/missions/{mission.id}/")
        response = auth_chercheur.get("/api/historique/consultations/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_historique_publications(self, auth_recruteur, mission):
        response = auth_recruteur.get("/api/historique/publications/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_chercheur_publications_vide(self, auth_chercheur, mission):
        response = auth_chercheur.get("/api/historique/publications/")
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_recruteur_consultations_vide(self, auth_recruteur, mission):
        response = auth_recruteur.get("/api/historique/consultations/")
        assert response.status_code == 200
        assert response.data["count"] == 0
