import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_escolar.settings')
django.setup()

from core.models import Lead
from django.contrib.auth.models import User

# Dados base pra gerar os leads
cursos = ['Informática', 'Design Gráfico', 'Administração', 'Inglês', 'Excel Avançado', 'Programação', 'Marketing Digital', 'TI', 'Gestão', 'Vendas']
status_list = ['lead_novo', 'contato', 'visita', 'matricula', 'perdido']
nomes = ['Lucas', 'Amanda', 'Rafael', 'Juliana', 'Pedro', 'Larissa', 'Carlos', 'Beatriz', 'Felipe', 'Mariana',
         'Gabriel', 'Camila', 'Bruno', 'Fernanda', 'Thiago', 'Letícia', 'Eduardo', 'Carolina', 'Diego', 'Isabela']

# Pega os usuários existentes pra atribuir como atendente
atendentes = list(User.objects.all())

if not atendentes:
    print('❌ Não há usuários cadastrados! Crie ao menos um usuário antes de rodar o script.')
    exit()

# Gerar 100 leads
for i in range(100):
    nome = random.choice(nomes) + f' Teste{i}'
    telefone = f'(11) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}'
    curso = random.choice(cursos)
    status = random.choice(status_list)

    dias_atras = random.randint(0, 60)
    data_cadastro = datetime.now() - timedelta(days=dias_atras)

    data_inicio = data_cadastro + timedelta(days=random.randint(0, 7))
    atendente = random.choice(atendentes)

    lead = Lead(
        nome_cliente=nome,
        telefone_cliente=telefone,
        curso_interesse=curso,
        status=status,
        data_cadastro=data_cadastro,
        data_inicio_atendimento=data_inicio,
        atendente=atendente
    )
    lead.save()

print('✅ 100 Leads criados com sucesso!')
