from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Lead
from .sheets_service import excluir_lead_na_planilha

@receiver(post_delete, sender=Lead)
def apagar_lead_no_sheet(sender, instance, **kwargs):
    # se retornar False, nada foi encontrado — você pode logar se quiser
    excluiu = excluir_lead_na_planilha(instance.id)
    if not excluiu:
        # opcional: logger.warning(f"Lead {instance.id} não encontrado na planilha")
        pass
