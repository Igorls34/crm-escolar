from django.shortcuts import render, redirect, get_object_or_404
from .models import Lead
from django.contrib.auth.decorators import login_required
from .forms import LeadForm, LeadObservacaoForm
from django.db.models import Count, Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.core.paginator import Paginator
from django.utils.timezone import now, timedelta
from django.core.management import call_command
import json
import csv
from .sheets_service import salvar_lead_na_planilha
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from .models import Lead, Curso
from django.contrib import messages
from django.views.decorators.http import require_POST
from .sheets_service import salvar_lead_na_planilha, excluir_lead_na_planilha
from .sheets_service import editar_lead_na_planilha


# View de migração manual (gambiarra pro Render Free Plan)
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
            form.save_m2m()
            salvar_lead_na_planilha(lead)
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
            form.save_m2m()
            salvar_lead_na_planilha(lead)
            return redirect('lead_list')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'lead_form.html', {'form': form})

@login_required
def lead_delete(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        excluir_lead_na_planilha(lead.id)
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
    cursos_counts = Lead.objects.values('cursos_interesse__nome').annotate(total=Count('id'))
    cursos_labels = [item['cursos_interesse__nome'] or 'Não informado' for item in cursos_counts]
    cursos_counts = Lead.objects.values('cursos_interesse').annotate(total=Count('id'))
    cursos_labels = [item['cursos_interesse'] for item in cursos_counts]
    cursos_data = [item['total'] for item in cursos_counts]

    # Funil de Conversão
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

        'status_counts': status_counts,
        'status_labels': json.dumps(status_labels),
        'status_data': json.dumps(status_data),

        'atendente_counts': atendente_counts,
        'atendente_labels': json.dumps(atendente_labels),
        'atendente_data': json.dumps(atendente_data),

        'cursos_labels': json.dumps(cursos_labels),
        'cursos_data': json.dumps(cursos_data),

        'funil_data': json.dumps(funil_data),
    }

    return render(request, 'lead_report.html', context)

@login_required
def dashboard(request):
    funil_data = [
        Lead.objects.count(),
        Lead.objects.filter(status='contato').count(),
        Lead.objects.filter(status='visita').count(),
        Lead.objects.filter(status='matricula').count(),
    ]

    cursos_qs = Lead.objects.values('cursos_interesse__nome').annotate(total=Count('id'))
    cursos_labels = [c['cursos_interesse__nome'] or 'Não informado' for c in cursos_qs]
    cursos_qs = Lead.objects.values('curso_interesse').annotate(total=Count('id'))
    cursos_labels = [c['curso_interesse'] for c in cursos_qs]
    cursos_data = [c['total'] for c in cursos_qs]

    context = {
        'funil_data': funil_data,
        'cursos_labels': cursos_labels,
        'cursos_data': cursos_data,
    }

    return render(request, 'dashboard.html', context)

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from .models import Lead
from .templatetags.dict_filters import dict_get
from django.db.models import Count

@login_required
def lead_kanban(request):
    # Se for POST, é o drop do JS
    if request.method == "POST" and request.is_ajax():
        lead_id      = request.POST.get("lead_id")
        novo_status  = request.POST.get("novo_status")
        try:
            lead = Lead.objects.get(pk=lead_id)
            lead.status = novo_status
            lead.save()
            return JsonResponse({"success": True})
        except Lead.DoesNotExist:
            return JsonResponse({"success": False, "error": "Lead não encontrado"})
    
    # Caso contrário, GET: monta o board
    status_list    = Lead.STATUS_CHOICES  # ou de onde você carrega
    status_colors  = {display: css for code, display, css in ...}  # como estiver
    busca          = request.GET.get("busca", "")
    all_leads      = Lead.objects.filter(
                        nome_cliente__icontains=busca
                    ).order_by("data_cadastro")  # evite UnorderedObjectListWarning
    status_leads   = {
        name: all_leads.filter(status=code)
        for code, name in status_list
    }

    return render(request, "lead_kanban.html", {
        "status_list":    [(code, name) for code, name in status_list],
        "status_colors":  status_colors,
        "status_leads":   status_leads,
        "busca":          busca,
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
    cursos_nomes = ', '.join([c.nome for c in lead.cursos_interesse.all()]),
    for lead in leads:
        writer.writerow([
            lead.nome_cliente,
            lead.telefone_cliente,
            lead.cursos_nomes,
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

@csrf_exempt
def webhook_google_sheets(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)

            nome = payload.get('nome')
            telefone = payload.get('telefone')
            curso = payload.get('curso')
            status = payload.get('status')
            observacoes = payload.get('observacoes', '')

            lead, created = Lead.objects.get_or_create(
                nome_cliente=nome,
                telefone_cliente=telefone,
                defaults={
                    'curso_interesse': curso,
                    'status': status,
                    'observacoes': observacoes,
                }
            )

            if not created:
                lead.curso_interesse = curso
                lead.status = status
                lead.observacoes = observacoes
                lead.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'error': 'Método não permitido'}, status=405)

def is_admin(user):
    return user.is_superuser  # Só quem for admin vê a página

@login_required
@user_passes_test(is_admin)
def user_admin(request):
    users = User.objects.all().order_by('-is_superuser', 'username')

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        is_staff = bool(request.POST.get("is_staff"))
        is_superuser = bool(request.POST.get("is_superuser"))

        if username and password:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            return redirect('user_admin')

    return render(request, 'user_admin.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        username = request.POST.get("username")
        email = request.POST.get("email")
        is_staff = bool(request.POST.get("is_staff"))
        is_superuser = bool(request.POST.get("is_superuser"))

        if username:
            user.username = username
            user.email = email
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save()
            return redirect('user_admin')
    return render(request, 'user_edit.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # Protege para não deletar o próprio usuário logado
    if user == request.user:
        # Você pode mostrar uma mensagem ou redirecionar de volta com aviso
        return render(request, 'user_delete_confirm.html', {
            'user': user,
            'erro': 'Você não pode excluir o próprio usuário logado!'
        })

    if request.method == "POST":
        user.delete()
        return redirect('user_admin')
    return render(request, 'user_delete_confirm.html', {'user': user})

@login_required
@user_passes_test(is_admin)
def curso_list(request):
    cursos = Curso.objects.all()
    return render(request, 'curso_list.html', {'cursos': cursos})

@login_required
@user_passes_test(is_admin)
def curso_create(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        duracao = request.POST['duracao_horas']
        valor = request.POST['valor']
        Curso.objects.create(nome=nome, duracao_horas=duracao, valor=valor)
        return redirect('curso_list')
    return render(request, 'curso_form.html')

@login_required
@user_passes_test(is_admin)
def curso_edit(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        curso.nome = request.POST['nome']
        curso.duracao_horas = request.POST['duracao_horas']
        curso.valor = request.POST['valor']
        curso.save()
        return redirect('curso_list')
    return render(request, 'curso_form.html', {'curso': curso})

@require_POST
def curso_delete(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    curso_nome = curso.nome
    curso.delete()
    messages.success(request, f'O curso "{curso_nome}" foi excluído com sucesso!')
    return redirect('curso_list')

@login_required
def lead_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.atendente = request.user
            lead.save()
            editar_lead_na_planilha(lead)   # <-- CHAMA AQUI
            messages.success(request, "Lead atualizado com sucesso!")
            return redirect('lead_list')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'lead_form.html', {'form': form})
