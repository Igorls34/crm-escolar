from django.urls import path
from . import views
from .views import run_migrations #url de migração
from django.http import HttpResponse

urlpatterns = [
    path('', views.home, name='home'),
    path('leads/', views.lead_list, name='lead_list'),
    path('leads/novo/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/editar/', views.lead_update, name='lead_update'),
    path('leads/<int:pk>/deletar/', views.lead_delete, name='lead_delete'),
    path('relatorio/', views.lead_report, name='lead_report'),
    path('kanban/', views.lead_kanban, name='lead_kanban'),
    path('mover-lead/', views.mover_lead, name='mover_lead'),
    path('exportar-leads/', views.exportar_leads_csv, name='exportar_leads_csv'),
    path('lead/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('run-migrations/', run_migrations), # url de migração
    path('webhook-sheets/', views.webhook_google_sheets, name='webhook_google_sheets'),
    path('usuarios/', views.user_admin, name='user_admin'),
    path('debug/', lambda request: HttpResponse('Funcionando!')),
    path('usuarios/<int:user_id>/editar/', views.user_edit, name='user_edit'),
    path('usuarios/<int:user_id>/excluir/', views.user_delete, name='user_delete'),
    path('cursos/', views.curso_list, name='curso_list'),
    path('cursos/novo/', views.curso_create, name='curso_create'),
    path('cursos/<int:curso_id>/editar/', views.curso_edit, name='curso_edit'),
    path('cursos/<int:pk>/excluir/', views.curso_delete, name='curso_delete'),
]