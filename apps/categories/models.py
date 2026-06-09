from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class SousCategorie(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    categorie = models.ForeignKey(
        Categorie, on_delete=models.CASCADE, related_name='sous_categories',
        verbose_name="Catégorie",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"
        unique_together = ('nom', 'categorie')
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.categorie.nom})"
