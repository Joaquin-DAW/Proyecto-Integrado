from django.urls import path
from apps.users import views

urlpatterns = [
    # Datos y acciones del usuario conectado.
    path('me/', views.mi_perfil, name='mi-perfil'),
    path('me/cambiar-password/', views.cambiar_password, name='cambiar-password'),

    # Profesores importados desde el fichero de horarios.
    path('profesores/', views.ProfesorListView.as_view(), name='profesor-list'),
    path('profesores/<int:pk>/', views.ProfesorDetailView.as_view(), name='profesor-detail'),
    path('profesores/<int:profesor_id>/crear-cuenta/', views.crear_cuenta_profesor, name='crear-cuenta-profesor'),

    # Gestion de cuentas, reservada a direccion.
    path('<int:user_id>/', views.actualizar_usuario, name='actualizar-usuario'),
    path('<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar-usuario'),
]
