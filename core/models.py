from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):
    STATUS_CHOICES = [
        ('lead_novo', 'Lead Novo'),
        ('contato', 'Contato Feito'),
        ('visita', 'Visita Agendada'),
        ('matricula', 'Matriculado'),
        ('perdido', 'Perdido'),
    ]

    nome_cliente = models.CharField(max_length=100)
    telefone_cliente = models.CharField(max_length=20)
    curso_interesse = models.CharField(max_length=100)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_inicio_atendimento = models.DateTimeField(null=True, blank=True)
    atendente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead_novo')
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome_cliente} - {self.status}"

class LeadObservacao(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='historico_observacoes')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Observação de {self.criado_por} em {self.criado_em.strftime("%d/%m/%Y %H:%M")}'


