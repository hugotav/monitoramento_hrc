from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.tela_login, name='login'),
    path('logout/', views.fazer_logout, name='logout'),
    path('', views.aba_cadastro, name='aba_cadastro'), # A página inicial será o Cadastro
    path('dados/', views.aba_dados, name='aba_dados'),
    path('metricas/', views.aba_metricas, name='aba_metricas'),
    path('editar/<int:prontuario>/', views.editar_paciente, name='editar_paciente'), 
    path('status/<int:prontuario>/', views.alternar_status_paciente, name='alternar_status_paciente'),
]