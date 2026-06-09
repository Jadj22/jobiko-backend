from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.categories.models import Categorie


class ChoiceTypeDate(models.TextChoices):
    UNIQUE = 'unique', 'Date unique'
    PLAGE = 'plage', 'Plage de dates'


class ChoiceStatut(models.TextChoices):
    PUBLIEE = 'publiee', 'Publiée'
    EN_COURS = 'en_cours', 'En cours'
    TERMINEE = 'terminee', 'Terminée'
    ANNULEE = 'annulee', 'Annulée'


class Mission(models.Model):
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    recruteur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='missions',
        verbose_name="Recruteur",
    )
    quartier = models.ForeignKey(
        'quartiers.Quartier', on_delete=models.PROTECT, related_name='missions',
        verbose_name="Quartier",
    )
    categorie = models.ForeignKey(
        Categorie, on_delete=models.PROTECT, related_name='missions',
        verbose_name="Catégorie",
    )
    type_date = models.CharField(
        max_length=10, choices=ChoiceTypeDate.choices, default=ChoiceTypeDate.UNIQUE,
        verbose_name="Type de date",
    )
    date_unique = models.DateField(null=True, blank=True, verbose_name="Date unique")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date fin")
    remuneration = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Rémunération (FCFA)",
        validators=[MinValueValidator(1)],
    )
    telephone_contact = models.CharField(max_length=20, verbose_name="Téléphone de contact")
    afficher_appel = models.BooleanField(default=False, verbose_name="Afficher le bouton d'appel")
    afficher_whatsapp = models.BooleanField(default=False, verbose_name="Afficher le bouton WhatsApp")
    statut = models.CharField(
        max_length=20, choices=ChoiceStatut.choices, default=ChoiceStatut.PUBLIEE,
        verbose_name="Statut",
    )
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre


class PhotoMission(models.Model):
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name='photos',
        verbose_name="Mission",
    )
    image = models.ImageField(upload_to='missions/photos/', verbose_name="Image")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"
        ordering = ['ordre']

    def __str__(self):
        return f"Photo {self.ordre + 1} - {self.mission.titre}"


class ChoiceStatutCandidature(models.TextChoices):
    EN_ATTENTE = 'en_attente', 'En attente'
    ACCEPTEE = 'acceptee', 'Acceptée'
    REFUSEE = 'refusee', 'Refusée'
    RETIREE = 'retiree', 'Retirée'


class Candidature(models.Model):
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name='candidatures',
        verbose_name="Mission",
    )
    chercheur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='candidatures',
        verbose_name="Chercheur",
    )
    statut = models.CharField(
        max_length=20, choices=ChoiceStatutCandidature.choices,
        default=ChoiceStatutCandidature.EN_ATTENTE, verbose_name="Statut",
    )
    date_candidature = models.DateTimeField(auto_now_add=True, verbose_name="Date de candidature")
    date_reponse = models.DateTimeField(null=True, blank=True, verbose_name="Date de réponse")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = ('mission', 'chercheur')
        ordering = ['-date_candidature']

    def __str__(self):
        return f"{self.chercheur.nom_complet} → {self.mission.titre}"


class Evaluation(models.Model):
    chercheur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='evaluations_recues',
        verbose_name="Chercheur évalué",
    )
    recruteur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='evaluations_donnees',
        verbose_name="Recruteur",
    )
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name='evaluations',
        verbose_name="Mission",
    )
    note = models.PositiveSmallIntegerField(
        verbose_name="Note", validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
        unique_together = ('mission', 'chercheur')

    def __str__(self):
        return f"{self.note}★ - {self.chercheur.nom_complet}"


class MissionFavorite(models.Model):
    chercheur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='favoris',
        verbose_name="Chercheur",
    )
    mission = models.ForeignKey(
        Mission, on_delete=models.CASCADE, related_name='favoris',
        verbose_name="Mission",
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ('chercheur', 'mission')
        ordering = ['-date']

    def __str__(self):
        return f"{self.chercheur.nom_complet} → {self.mission.titre}"


class ServicePrestataire(models.Model):
    chercheur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='services',
        verbose_name="Chercheur",
    )
    titre = models.CharField(max_length=200, verbose_name="Titre du service")
    description = models.TextField(verbose_name="Description")
    categorie = models.ForeignKey(
        Categorie, on_delete=models.PROTECT, related_name='services',
        verbose_name="Catégorie",
    )
    prix = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Prix (FCFA)",
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")

    class Meta:
        verbose_name = "Service prestataire"
        verbose_name_plural = "Services prestataires"
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre


class PhotoService(models.Model):
    service = models.ForeignKey(
        ServicePrestataire, on_delete=models.CASCADE, related_name='photos',
        verbose_name="Service",
    )
    image = models.ImageField(upload_to='services/photos/', verbose_name="Image")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Photo de service"
        verbose_name_plural = "Photos de services"
        ordering = ['ordre']

    def __str__(self):
        return f"Photo {self.ordre + 1} - {self.service.titre}"
