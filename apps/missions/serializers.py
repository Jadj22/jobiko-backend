from rest_framework import serializers
from .models import Mission, PhotoMission, Candidature, Evaluation, MissionFavorite, ServicePrestataire, PhotoService


class PhotoMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoMission
        fields = ['id', 'image', 'ordre']


class MissionListSerializer(serializers.ModelSerializer):
    recruteur_nom = serializers.CharField(source='recruteur.nom_complet', read_only=True)
    quartier_nom = serializers.CharField(source='quartier.nom', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    premiere_photo = serializers.SerializerMethodField()
    nombre_candidatures = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            'id', 'titre', 'description', 'remuneration', 'statut',
            'recruteur',
            'quartier', 'quartier_nom', 'categorie', 'categorie_nom',
            'type_date', 'date_unique', 'date_debut', 'date_fin',
            'recruteur_nom', 'premiere_photo', 'date_publication',
            'afficher_appel', 'afficher_whatsapp',
            'nombre_candidatures',
        ]

    def get_premiere_photo(self, obj):
        photo = obj.photos.order_by('ordre').first()
        return photo.image if photo else None

    def get_nombre_candidatures(self, obj):
        return obj.candidatures.exclude(statut='retiree').count()


class MissionDetailSerializer(serializers.ModelSerializer):
    recruteur_nom = serializers.CharField(source='recruteur.nom_complet', read_only=True)
    recruteur_note_moyenne = serializers.SerializerMethodField()
    recruteur_nb_missions_publiees = serializers.SerializerMethodField()
    quartier_nom = serializers.CharField(source='quartier.nom', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    photos = PhotoMissionSerializer(many=True, read_only=True)
    nombre_candidatures = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = [
            'id', 'titre', 'description', 'recruteur', 'recruteur_nom',
            'recruteur_note_moyenne', 'recruteur_nb_missions_publiees',
            'quartier', 'quartier_nom', 'categorie', 'categorie_nom',
            'type_date', 'date_unique', 'date_debut', 'date_fin',
            'remuneration', 'telephone_contact', 'statut',
            'photos', 'nombre_candidatures', 'date_publication',
            'afficher_appel', 'afficher_whatsapp',
        ]
        read_only_fields = ['recruteur', 'statut', 'date_publication', 'date_modification']

    def get_nombre_candidatures(self, obj):
        return obj.candidatures.exclude(statut='retiree').count()

    def get_recruteur_note_moyenne(self, obj):
        from django.db.models import Avg
        avg = obj.recruteur.evaluations_recues.aggregate(Avg('note'))['note__avg']
        return float(avg) if avg is not None else None

    def get_recruteur_nb_missions_publiees(self, obj):
        return obj.recruteur.missions.filter(is_active=True).count()


class MissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = [
            'titre', 'description', 'quartier', 'categorie',
            'type_date', 'date_unique', 'date_debut', 'date_fin',
            'remuneration', 'telephone_contact',
            'afficher_appel', 'afficher_whatsapp',
        ]

    def validate(self, data):
        type_date = data.get('type_date')
        if type_date == 'unique' and not data.get('date_unique'):
            raise serializers.ValidationError("La date unique est requise.")
        if type_date == 'plage':
            if not data.get('date_debut') or not data.get('date_fin'):
                raise serializers.ValidationError("Les dates début et fin sont requises.")
            if data['date_fin'] < data['date_debut']:
                raise serializers.ValidationError("La date de fin doit être après la date de début.")
        return data

    def create(self, validated_data):
        validated_data['recruteur'] = self.context['request'].user
        return super().create(validated_data)


class MissionStatutSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=[
        ('publiee', 'Publiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ])

    def validate_statut(self, value):
        mission = self.context['mission']
        transitions = {
            'publiee': ['en_cours', 'annulee'],
            'en_cours': ['terminee', 'annulee'],
            'terminee': [],
            'annulee': [],
        }
        if value not in transitions.get(mission.statut, []):
            raise serializers.ValidationError(
                f"Transition impossible de '{mission.statut}' vers '{value}'."
            )
        return value


class CandidatureSerializer(serializers.ModelSerializer):
    chercheur_nom = serializers.CharField(source='chercheur.nom_complet', read_only=True)
    chercheur_photo = serializers.ImageField(source='chercheur.photo', read_only=True, default=None)
    chercheur_note_moyenne = serializers.SerializerMethodField()
    chercheur_nb_missions_terminees = serializers.SerializerMethodField()
    chercheur_quartier_nom = serializers.CharField(source='chercheur.quartier.nom', read_only=True, default=None)
    competences = serializers.SerializerMethodField()
    mission_titre = serializers.CharField(source='mission.titre', read_only=True)
    mission_remuneration = serializers.IntegerField(source='mission.remuneration', read_only=True)
    mission_date_unique = serializers.DateField(source='mission.date_unique', read_only=True)
    mission_date_debut = serializers.DateField(source='mission.date_debut', read_only=True)
    mission_date_fin = serializers.DateField(source='mission.date_fin', read_only=True)
    mission_type_date = serializers.CharField(source='mission.type_date', read_only=True)
    mission_quartier_nom = serializers.CharField(source='mission.quartier.nom', read_only=True, default=None)

    class Meta:
        model = Candidature
        fields = [
            'id', 'mission', 'mission_titre',
            'chercheur', 'chercheur_nom', 'chercheur_photo',
            'chercheur_note_moyenne', 'chercheur_nb_missions_terminees',
            'chercheur_quartier_nom', 'competences',
            'mission_remuneration', 'mission_date_unique', 'mission_date_debut',
            'mission_date_fin', 'mission_type_date', 'mission_quartier_nom',
            'statut', 'date_candidature', 'date_reponse',
        ]
        read_only_fields = ['chercheur', 'mission', 'statut', 'date_candidature', 'date_reponse']

    def get_competences(self, obj):
        return [cu.competence.nom for cu in obj.chercheur.competences.all()]

    def get_chercheur_note_moyenne(self, obj):
        from django.db.models import Avg
        avg = obj.chercheur.evaluations_recues.aggregate(Avg('note'))['note__avg']
        return float(avg) if avg is not None else None

    def get_chercheur_nb_missions_terminees(self, obj):
        return obj.chercheur.candidatures.filter(
            statut='acceptee', mission__statut='terminee'
        ).count()


class CandidatureActionSerializer(serializers.Serializer):
    statut = serializers.ChoiceField(choices=[('acceptee', 'Acceptée'), ('refusee', 'Refusée')])


class EvaluationSerializer(serializers.ModelSerializer):
    recruteur_nom = serializers.CharField(source='recruteur.nom_complet', read_only=True)

    class Meta:
        model = Evaluation
        fields = ['id', 'chercheur', 'recruteur', 'recruteur_nom', 'mission', 'note', 'commentaire', 'date']
        read_only_fields = ['recruteur', 'date']

    def validate_mission(self, value):
        user = self.context['request'].user
        if value.recruteur != user:
            raise serializers.ValidationError("Vous n'êtes pas le recruteur de cette mission.")
        if value.statut != 'terminee':
            raise serializers.ValidationError("La mission doit être terminée pour être évaluée.")
        return value

    def create(self, validated_data):
        validated_data['recruteur'] = self.context['request'].user
        return super().create(validated_data)


class PhotoServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoService
        fields = ['id', 'image', 'ordre']


class ServicePrestataireSerializer(serializers.ModelSerializer):
    photos = PhotoServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePrestataire
        fields = ['id', 'chercheur', 'titre', 'description', 'categorie', 'prix', 'is_active', 'photos', 'date_publication']
        read_only_fields = ['chercheur', 'date_publication']

    def create(self, validated_data):
        validated_data['chercheur'] = self.context['request'].user
        return super().create(validated_data)


class ServicePrestataireListSerializer(serializers.ModelSerializer):
    premiere_photo = serializers.SerializerMethodField()
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)

    class Meta:
        model = ServicePrestataire
        fields = ['id', 'titre', 'prix', 'categorie', 'categorie_nom', 'premiere_photo', 'is_active']

    def get_premiere_photo(self, obj):
        photo = obj.photos.order_by('ordre').first()
        return photo.image.url if photo else None


class MissionFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionFavorite
        fields = ['id', 'mission', 'date']
        read_only_fields = ['chercheur', 'date']

    def create(self, validated_data):
        validated_data['chercheur'] = self.context['request'].user
        return super().create(validated_data)
