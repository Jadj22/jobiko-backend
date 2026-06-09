from django.db import models


class Quartier(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        ordering = ['nom']

    def __str__(self):
        return self.nom
