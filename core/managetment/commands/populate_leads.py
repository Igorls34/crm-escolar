from django.core.management.base import BaseCommand
from core.models import Lead
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils.timezone import now

class Command(BaseCommand):
    help = 'Popula o banco com leads de teste'

    def handle(self, *args, **kwargs):
        # Cria alguns atendentes
        atendentes = []
        for nome in ['João', 'Maria', 'Lucas', 'Ana']:
            user, created = User.objects.get_or_create(username=nome)
            atendentes.append(user)

        status_list = ['lead_novo', 'contato', 'visita', 'matricula', 'perdido']
        cursos = ['Inglês', 'Informática', 'Programação', 'Design', 'Administração']

        for i in range(1, 51):
            lead = Lead.objects.create(
                nome_cliente=f'Cliente {i}',
                telefone_cliente=f'(99) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                curso_interesse=random.choice(cursos),
                status=random.choice(status_list),
                atendente=random.choice(atendentes),
                data_inicio_atendimento=now() - timedelta(days=random.randint(0, 30))
            )
            self.stdout.write(self.style.SUCCESS(f'Lead {lead.nome_cliente} criado!'))
