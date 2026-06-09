from rest_framework.permissions import BasePermission


class IsRecruteur(BasePermission):
    message = "Seuls les recruteurs peuvent effectuer cette action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'recruteur'


class IsChercheur(BasePermission):
    message = "Seuls les chercheurs de missions peuvent effectuer cette action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'chercheur'


class IsProprietaireMission(BasePermission):
    message = "Vous n'êtes pas le propriétaire de cette mission."

    def has_object_permission(self, request, view, obj):
        return obj.recruteur == request.user
