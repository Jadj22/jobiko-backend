from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class RoleChoices(models.TextChoices):
    RECRUTEUR = 'recruteur', 'Recruteur'
    CHERCHEUR = 'chercheur', 'Chercheur'


class UserManager(BaseUserManager):
    def create_user(self, telephone, password=None, **extra_fields):
        if not telephone:
            raise ValueError('Le numéro de téléphone est obligatoire')
        user = self.model(telephone=telephone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, telephone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoices.RECRUTEUR)
        return self.create_user(telephone, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = None

    nom_complet = models.CharField(max_length=150, verbose_name="Nom complet")
    role = models.CharField(max_length=20, choices=RoleChoices.choices, verbose_name="Rôle")
    telephone = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='profils/', null=True, blank=True, verbose_name="Photo")
    quartier = models.ForeignKey(
        'quartiers.Quartier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Quartier",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    objects = UserManager()

    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['nom_complet', 'role']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.nom_complet} ({self.get_role_display()})"
