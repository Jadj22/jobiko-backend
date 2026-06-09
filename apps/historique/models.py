from django.db import models


class HistoriqueConsultation(models.Model):
    chercheur = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='consultations',
        verbose_name="Chercheur",
    )
    mission = models.ForeignKey(
        'missions.Mission', on_delete=models.CASCADE, related_name='consultations',
        verbose_name="Mission",
    )
    date_consultation = models.DateTimeField(auto_now=True, verbose_name="Date de consultation")

    class Meta:
        verbose_name = "Historique de consultation"
        verbose_name_plural = "Historiques de consultation"
        unique_together = ('chercheur', 'mission')
        ordering = ['-date_consultation']

    def __str__(self):
        return f"{self.chercheur.nom_complet} a consulté {self.mission.titre}"
