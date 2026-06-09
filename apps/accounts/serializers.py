import re

from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['telephone', 'password', 'nom_complet', 'role']

    def validate_telephone(self, value):
        if not re.match(r'^\+228\d{8}$', value):
            raise serializers.ValidationError("Le téléphone doit être au format +228XXXXXXXX.")
        if User.objects.filter(telephone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return value

    def validate_nom_complet(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le nom complet est obligatoire.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    telephone = serializers.CharField(min_length=5)
    password = serializers.CharField(min_length=1)


class UserDetailSerializer(serializers.ModelSerializer):
    quartier_nom = serializers.CharField(source='quartier.nom', read_only=True, default=None)

    class Meta:
        model = User
        fields = [
            'id', 'nom_complet', 'telephone', 'role', 'photo',
            'quartier', 'quartier_nom', 'description', 'date_joined',
        ]
        read_only_fields = ['id', 'role', 'date_joined']


class ProfilUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nom_complet', 'photo', 'quartier', 'description']

    def validate_photo(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("L'image ne doit pas dépasser 5 Mo.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("Le fichier doit être une image.")
        return value


class ProfilPublicSerializer(serializers.ModelSerializer):
    quartier_nom = serializers.CharField(source='quartier.nom', read_only=True, default=None)
    note_moyenne = serializers.SerializerMethodField()
    nb_missions_terminees = serializers.SerializerMethodField()
    nb_missions_publiees = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'nom_complet', 'photo', 'quartier', 'quartier_nom',
            'description', 'date_joined', 'role', 'note_moyenne',
            'nb_missions_terminees', 'nb_missions_publiees', 'services',
        ]

    def get_note_moyenne(self, obj):
        evaluations = obj.evaluations_recues.all()
        if not evaluations:
            return None
        return round(sum(e.note for e in evaluations) / evaluations.count(), 1)

    def get_nb_missions_terminees(self, obj):
        from apps.missions.models import Candidature
        return Candidature.objects.filter(
            chercheur=obj, statut='acceptee', mission__statut='terminee',
        ).count()

    def get_nb_missions_publiees(self, obj):
        from apps.missions.models import Mission
        return Mission.objects.filter(recruteur=obj).count()

    def get_services(self, obj):
        from apps.missions.models import ServicePrestataire
        from apps.missions.serializers import ServicePrestataireListSerializer
        services = ServicePrestataire.objects.filter(chercheur=obj, is_active=True)
        return ServicePrestataireListSerializer(services, many=True).data
