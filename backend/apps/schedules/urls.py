from django.urls import path
from . import views

urlpatterns = [
    path('', views.HorarioListView.as_view(), name='horario-list'),
    path('mi-horario/', views.mi_horario, name='mi-horario'),
    path('importar/', views.importar_horario, name='horario-importar'),
]
