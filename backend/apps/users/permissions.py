"""
Permisos reutilizables de la API.

Asi las vistas no tienen que repetir a mano las comprobaciones de rol en cada
endpoint.
"""
from rest_framework.permissions import BasePermission


class IsEquipoDireccion(BasePermission):
    """Acceso reservado a usuarios con rol de direccion."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_equipo_directivo
        )


class IsEquipoDireccionOrReadOwn(BasePermission):
    """
    Direccion tiene acceso completo.
    El profesorado solo puede trabajar con objetos propios.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_equipo_directivo:
            return True
        # En ausencias, el dueño real se obtiene desde la entrada de horario.
        if hasattr(obj, 'horario_entry'):
            return (
                hasattr(request.user, 'profesor')
                and obj.horario_entry.profesor == request.user.profesor
            )
        return False
