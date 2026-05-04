from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_ausencias, name='ausencia-list'),
    path('crear/', views.crear_ausencia, name='ausencia-crear'),
    path('<int:ausencia_id>/', views.eliminar_ausencia, name='ausencia-eliminar'),
    path('<int:ausencia_id>/justificar/', views.justificar_ausencia, name='ausencia-justificar'),
    path('fecha/<str:fecha>/', views.ausencias_por_fecha, name='ausencias-por-fecha'),
]
