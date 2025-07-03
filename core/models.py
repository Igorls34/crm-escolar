from django.db import models
from django.contrib.auth.models import User

class Lead(models.Model):
    STATUS_CHOICES = [
        ('lead_novo', 'Lead Novo'),
        ('contato', 'Contato Feito'),
        ('visita', 'Visita Agendada'),
        ('matricula', 'Matriculado'),
        ('perdido', 'Perdi do'),
        ("VISITA_AGENDADA_COMPARECEU", "Visita Agendada - Compareceu"),
        ("VISITA_AGENDADA_FALTOU", "Visita Agendada - Faltou"),
    ]

    nome_cliente = models.CharField(max_length=100)
    telefone_cliente = models.CharField(max_length=20)
    cursos_interesse = models.ManyToManyField('Curso', blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_inicio_atendimento = models.DateTimeField(null=True, blank=True)
    atendente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='lead_novo')
    observacoes = models.TextField(blank=True, null=True)
    ad_whats = models.BooleanField('Adicionado no WhatsApp', default=False)

    def __str__(self):
        return f"{self.nome_cliente} - {self.status}"

class LeadObservacao(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='historico_observacoes')
    texto = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Observação de {self.criado_por} em {self.criado_em.strftime("%d/%m/%Y %H:%M")}'

class Curso(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    duracao_horas = models.PositiveIntegerField("Duração (horas)")
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome} ({self.duracao_horas}h) - R$ {self.valor:.2f}"


