from django.core.management.base import BaseCommand
from core.models import Lead, LeadObservacao
from django.utils.timezone import now
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Popula observações de teste nos leads existentes'

    def handle(self, *args, **kwargs):
        textos_possiveis = [
            'Cliente interessado no curso de inglês.',
            'Ligação feita, cliente pediu retorno na próxima semana.',
            'Visitou a escola, mas não fechou matrícula.',
            'Lead frio, difícil contato.',
            'Cliente demonstrou grande interesse.',
            'Precisa de desconto para fechar.',
            'Aguardando confirmação de horário de visita.',
            'Cliente já conhece a escola de outra unidade.',
            'Cliente indicou que deve fechar na próxima semana.',
            'Possível perda de lead, sem resposta nos últimos contatos.'
        ]

        leads = Lead.objects.all()

        for lead in leads:
            num_obs = random.randint(1, 5)  # De 1 a 5 observações por lead

            for _ in range(num_obs):
                texto = random.choice(textos_possiveis)
                obs = LeadObservacao.objects.create(
                    lead=lead,
                    texto=texto,
                    criado_em=now() - timedelta(days=random.randint(0, 30))
                )
                self.stdout.write(self.style.SUCCESS(f'Obs criada para {lead.nome_cliente}: "{texto}"'))

        self.stdout.write(self.style.SUCCESS('✅ Observações populadas com sucesso!'))
