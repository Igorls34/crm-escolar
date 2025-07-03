from django import forms
from .models import Lead
from .models import LeadObservacao
from .models import Curso

class LeadForm(forms.ModelForm):
    cursos_interesse = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        label='Cursos de Interesse'
    )
    class Meta:
        model = Lead
        fields = ['nome_cliente','telefone_cliente','cursos_interesse','status','data_inicio_atendimento','ad_whats','observacoes']
        widgets = {
            'nome_cliente': forms.TextInput(attrs={'class':'form-control'}),
            'telefone_cliente': forms.TextInput(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'data_inicio_atendimento': forms.DateTimeInput(attrs={'class':'form-control', 'type':'datetime-local'}),
            'ad_whats': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'observacoes': forms.Textarea(attrs={'class':'form-control','rows':4}),
        }

class LeadObservacaoForm(forms.ModelForm):
    class Meta:
        model = LeadObservacao
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Digite sua observação...'})
        }