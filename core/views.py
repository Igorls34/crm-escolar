from django.shortcuts import render, redirect, get_object_or_404
from .models import Lead
from django.contrib.auth.decorators import login_required
from .forms import LeadForm
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta
import json
import csv
from .forms import LeadObservacaoForm
from .models import LeadObservacao
from django.db.models import Count
# MIGRAÇÕES
from django.http import HttpResponse
from django.core.management import call_command
# view de migração
def run_migrations(request):
    try:
        call_command('migrate')
        return HttpResponse('✅ Migrações aplicadas com sucesso!')
    except Exception as e:
        return HttpResponse(f'❌ Erro ao rodar as migrações: {e}')

@login_required
def lead_list(request):
    status_filter = request.GET.get('status')
    atendente_filter = request.GET.get('atendente')
    busca = request.GET.get('busca') or ''
    data_inicial = request.GET.get('data_inicial') or ''
    data_final = request.GET.get('data_final') or ''

    leads = Lead.objects.all()

    if status_filter and status_filter != 'todos':
        leads = leads.filter(status=status_filter)

    if atendente_filter and atendente_filter != 'todos':
        leads = leads.filter(atendente__username=atendente_filter)

    if busca:
        leads = leads.filter(
            Q(nome_cliente__icontains=busca) |
            Q(telefone_cliente__icontains=busca)
        )

    if data_inicial:
        try:
            data_inicio = datetime.strptime(data_inicial, '%Y-%m-%d')
            leads = leads.filter(data_inicio_atendimento__date__gte=data_inicio)
        except ValueError:
            pass

    if data_final:
        try:
            data_fim = datetime.strptime(data_final, '%Y-%m-%d')
            leads = leads.filter(data_inicio_atendimento__date__lte=data_fim)
        except ValueError:
            pass

    atendentes = Lead.objects.values_list('atendente__username', flat=True).distinct()

    paginator = Paginator(leads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'lead_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'atendente_filter': atendente_filter,
        'busca': busca,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'atendentes': atendentes,
    })

@login_required
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.atendente = request.user
            lead.save()
            return redirect('lead_list')
    else:
        form = LeadForm()
    return render(request, 'lead_form.html', {'form': form})

@login_required
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.atendente = request.user
            lead.save()
            return redirect('lead_list')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'lead_form.html', {'form': form})

@login_required
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        lead.delete()
        return redirect('lead_list')
    return render(request, 'lead_confirm_delete.html', {'lead': lead})

@login_required
def lead_report(request):
    total_leads = Lead.objects.count()
    total_matriculados = Lead.objects.filter(status='matricula').count()
    taxa_conversao = (total_matriculados / total_leads * 100) if total_leads > 0 else 0

    sete_dias_atras = now() - timedelta(days=7)
    trinta_dias_atras = now() - timedelta(days=30)

    leads_ultimos_7_dias = Lead.objects.filter(data_inicio_atendimento__gte=sete_dias_atras).count()
    leads_ultimo_mes = Lead.objects.filter(data_inicio_atendimento__gte=trinta_dias_atras).count()

    ultimo_lead = Lead.objects.order_by('-data_inicio_atendimento').first()

    # Contagem por Status
    status_counts = Lead.objects.values('status').annotate(total=Count('status'))
    status_labels = [item['status'] for item in status_counts]
    status_data = [item['total'] for item in status_counts]

    # Contagem por Atendente
    atendente_counts = Lead.objects.values('atendente__username').annotate(total=Count('id'))
    atendente_labels = [item['atendente__username'] if item['atendente__username'] else 'Sem Atendente' for item in atendente_counts]
    atendente_data = [item['total'] for item in atendente_counts]

    # Contagem por Curso de Interesse
    cursos_counts = Lead.objects.values('curso_interesse').annotate(total=Count('id'))
    cursos_labels = [item['curso_interesse'] for item in cursos_counts]
    cursos_data = [item['total'] for item in cursos_counts]

    # Funil de Conversão (Total de cada etapa)
    funil_data = [
        total_leads,
        Lead.objects.filter(status='contato').count(),
        Lead.objects.filter(status='visita').count(),
        total_matriculados
    ]

    context = {
        'total_leads': total_leads,
        'taxa_conversao': taxa_conversao,
        'leads_ultimos_7_dias': leads_ultimos_7_dias,
        'leads_ultimo_mes': leads_ultimo_mes,
        'ultimo_lead': ultimo_lead,

        # Dados por status
        'status_counts': status_counts,
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),

        # Dados por atendente
        'atendente_counts': atendente_counts,
        'atendente_labels': json.dumps(atendente_labels),
        'atendente_data': json.dumps(atendente_data),

        # Dados por curso
        'cursos_labels': json.dumps(cursos_labels),
        'cursos_data': json.dumps(cursos_data),

        # Funil
        'funil_data': json.dumps(funil_data),
    }

    return render(request, 'lead_report.html', context)

@login_required
def lead_kanban(request):
    status_list = [
        ('lead_novo', 'Lead Novo'),
        ('contato', 'Contato Feito'),
        ('visita', 'Visita Agendada'),
        ('matricula', 'Matriculado'),
        ('perdido', 'Perdido'),
    ]

    status_dict = dict(status_list)

    status_colors = {
        'Lead Novo': 'bg-primary',
        'Contato Feito': 'bg-info',
        'Visita Agendada': 'bg-warning',
        'Matriculado': 'bg-success',
        'Perdido': 'bg-danger',
    }

    busca = request.GET.get('busca') or ''

    status_leads = {}

    for status_code, status_name in status_list:
        leads = Lead.objects.filter(status=status_code)

        if busca:
            leads = leads.filter(
                Q(nome_cliente__icontains=busca) |
                Q(telefone_cliente__icontains=busca)
            )

        status_leads[status_name] = leads.order_by('-data_inicio_atendimento')[:50]

    return render(request, 'lead_kanban.html', {
        'status_leads': status_leads,
        'status_colors': status_colors,
        'status_list': status_list,
        'status_dict': status_dict,
        'busca': busca,
    })

@csrf_exempt
def mover_lead(request):
    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        novo_status = request.POST.get('novo_status')

        try:
            lead = Lead.objects.get(id=lead_id)
            lead.status = novo_status
            lead.save()
            return JsonResponse({'success': True})
        except Lead.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Lead não encontrado'})
    else:
        return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required
def exportar_leads_csv(request):
    status_filter = request.GET.get('status')
    atendente_filter = request.GET.get('atendente')
    busca = request.GET.get('busca') or ''
    data_inicial = request.GET.get('data_inicial') or ''
    data_final = request.GET.get('data_final') or ''

    leads = Lead.objects.all()

    if status_filter and status_filter != 'todos':
        leads = leads.filter(status=status_filter)

    if atendente_filter and atendente_filter != 'todos':
        leads = leads.filter(atendente__username=atendente_filter)

    if busca:
        leads = leads.filter(
            Q(nome_cliente__icontains=busca) |
            Q(telefone_cliente__icontains=busca)
        )

    if data_inicial:
        try:
            data_inicio = datetime.strptime(data_inicial, '%Y-%m-%d')
            leads = leads.filter(data_inicio_atendimento__date__gte=data_inicio)
        except ValueError:
            pass

    if data_final:
        try:
            data_fim = datetime.strptime(data_final, '%Y-%m-%d')
            leads = leads.filter(data_inicio_atendimento__date__lte=data_fim)
        except ValueError:
            pass

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads_filtrados.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nome', 'Telefone', 'Curso', 'Status', 'Atendente', 'Data de Início'])

    for lead in leads:
        writer.writerow([
            lead.nome_cliente,
            lead.telefone_cliente,
            lead.curso_interesse,
            lead.get_status_display(),
            lead.atendente.username if lead.atendente else 'Sem Atendente',
            lead.data_inicio_atendimento.strftime('%d/%m/%Y %H:%M') if lead.data_inicio_atendimento else '',
        ])

    return response

def home(request):
    return render(request, 'home.html')

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    return render(request, 'lead_detail.html', {'lead': lead})

@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    observacoes = lead.historico_observacoes.order_by('-criado_em')

    if request.method == 'POST':
        form = LeadObservacaoForm(request.POST)
        if form.is_valid():
            nova_obs = form.save(commit=False)
            nova_obs.lead = lead
            nova_obs.criado_por = request.user
            nova_obs.save()
            return redirect('lead_detail', pk=pk)
    else:
        form = LeadObservacaoForm()

    return render(request, 'lead_detail.html', {
        'lead': lead,
        'observacoes': observacoes,
        'form': form
    })

# Funil
funil_data = [
    Lead.objects.count(),
    Lead.objects.filter(status='contato').count(),
    Lead.objects.filter(status='visita').count(),
    Lead.objects.filter(status='matricula').count(),
]

# Cursos
cursos_qs = Lead.objects.values('curso_interesse').annotate(total=Count('id'))
cursos_labels = [c['curso_interesse'] for c in cursos_qs]
cursos_data = [c['total'] for c in cursos_qs]

context = {}  # <- precisa disso antes de usar o context.update()

context.update({
    'funil_data': funil_data,
    'cursos_labels': cursos_labels,
    'cursos_data': cursos_data,
})
