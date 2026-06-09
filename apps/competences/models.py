from django.db import models


class Competence(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class CompetenceUser(models.Model):
    user = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='competences',
        verbose_name="Utilisateur",
    )
    competence = models.ForeignKey(
        Competence, on_delete=models.CASCADE, related_name='utilisateurs',
        verbose_name="Compétence",
    )

    class Meta:
        verbose_name = "Compétence utilisateur"
        verbose_name_plural = "Compétences utilisateur"
        unique_together = ('user', 'competence')

    def __str__(self):
        return f"{self.user.nom_complet} - {self.competence.nom}"
