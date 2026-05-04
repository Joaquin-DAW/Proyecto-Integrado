from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_partes, name='parte-list'),
    path('generar/', views.generar_parte, name='parte-generar'),
    path('<int:parte_id>/pdf/', views.descargar_parte, name='parte-pdf'),
    path('<int:parte_id>/enviar/', views.enviar_parte_email, name='parte-enviar'),
]
