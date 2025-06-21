from django import forms
from .models import Lead
from .models import LeadObservacao

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['nome_cliente', 'telefone_cliente', 'curso_interesse', 'data_inicio_atendimento', 'status']
        widgets = {
            'data_inicio_atendimento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class LeadObservacaoForm(forms.ModelForm):
    class Meta:
        model = LeadObservacao
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Digite sua observação...'})
        }