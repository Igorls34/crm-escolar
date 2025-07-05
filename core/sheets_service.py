import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
from .models import Lead as LeadModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
SHEET_NAME = "teste_cadastro_tele"  # Nome exato da sua planilha
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credencial_google.json')


def conectar_planilha():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet


def salvar_lead_na_planilha(lead):
    sheet = conectar_planilha()

    # 1) Data de primeiro contato
    data_contato = lead.data_inicio_atendimento.strftime('%d/%m/%Y %H:%M') if lead.data_inicio_atendimento else ''

    # 2) Nome do contato
    contato = lead.nome_cliente

    # 3) Ad. Whats?
    ad_whats = 'Sim' if getattr(lead, 'ad_whats', False) else 'Não'

    # 4) Telefone
    telefone = lead.telefone_cliente or ''

    # 5) Cursos de interesse
    cursos = ', '.join([c.nome for c in lead.cursos_interesse.all()])

    # 6) Remarketing: já existia antes deste cadastro?
    existe_anterior = LeadModel.objects.filter(
        telefone_cliente=lead.telefone_cliente
    ).exclude(pk=lead.pk).exists()
    remarketing = 'Sim' if existe_anterior else 'Não'

    # 7-11) Status 1 a Status 5 (funil)
    # Aqui usamos booleanos indicando se o lead já atingiu cada etapa
    status1 = 'Sim' if lead.status == 'lead_novo' else 'Não'
    status2 = 'Sim' if lead.status in ['contato'] else 'Não'
    status3 = 'Sim' if lead.status in ['visita', 'VISITA_AGENDADA_COMPARECEU', 'VISITA_AGENDADA_FALTOU'] else 'Não'
    status4 = 'Sim' if lead.status == 'matricula' else 'Não'
    status5 = 'Sim' if lead.status == 'perdido' else 'Não'

    # Monta a linha na ordem das colunas da planilha
    row = [
        data_contato,  # Coluna A: Data
        contato,       # Coluna B: Contato
        ad_whats,      # Coluna C: Ad. Whats?
        telefone,      # Coluna D: Telefone
        cursos,        # Coluna E: Curso
        remarketing,   # Coluna F: Remarketing
        status1,       # Coluna G: Status 1
        status2,       # Coluna H: Status 2
        status3,       # Coluna I: Status 3
        status4,       # Coluna J: Status 4
        status5,       # Coluna K: Status 5
    ]

    # Adiciona ao final da planilha
    sheet.append_row(row)


def excluir_lead_na_planilha(lead_id):
    sheet = conectar_planilha()
    all_rows = sheet.get_all_values()
    # Se você tiver cabeçalho na linha 1, comece em 2:
    for idx, row in enumerate(all_rows, start=1):
        # pula a linha de cabeçalho, se existir:
        if idx == 1 and not row[0].isdigit():
            continue
        if row and row[0] == str(lead_id):
            # delete_row é o método singular mais comum do gspread
            sheet.delete_row(idx)
            return True
    return False


def editar_lead_na_planilha(lead):
    sheet = conectar_planilha()
    all_records = sheet.get_all_records()
    row_to_update = None
    # Procura pelo ID na primeira coluna
    for idx, rec in enumerate(all_records, start=2):
        if rec.get('ID') == lead.id:
            row_to_update = idx
            break

    if not row_to_update:
        return

    # Regerar valores
    data_contato = lead.data_inicio_atendimento.strftime('%d/%m/%Y %H:%M') if lead.data_inicio_atendimento else ''
    contato = lead.nome_cliente
    ad_whats = 'Sim' if getattr(lead, 'ad_whats', False) else 'Não'
    telefone = lead.telefone_cliente or ''
    cursos = ', '.join([c.nome for c in lead.cursos_interesse.all()])
    existe_anterior = LeadModel.objects.filter(
        telefone_cliente=lead.telefone_cliente
    ).exclude(pk=lead.pk).exists()
    remarketing = 'Sim' if existe_anterior else 'Não'
    status1 = 'Sim' if lead.status == 'lead_novo' else 'Não'
    status2 = 'Sim' if lead.status in ['contato'] else 'Não'
    status3 = 'Sim' if lead.status in ['visita', 'VISITA_AGENDADA_COMPARECEU', 'VISITA_AGENDADA_FALTOU'] else 'Não'
    status4 = 'Sim' if lead.status == 'matricula' else 'Não'
    status5 = 'Sim' if lead.status == 'perdido' else 'Não'

    updated = [
        data_contato,
        contato,
        ad_whats,
        telefone,
        cursos,
        remarketing,
        status1,
        status2,
        status3,
        status4,
        status5,
    ]
    # Atualiza o intervalo A:K da linha encontrada
    sheet.update(f'A{row_to_update}:K{row_to_update}', [updated])