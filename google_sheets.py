import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any

# Escopos de permissão necessários para a API do Google Sheets e Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def authenticate_gspread() -> gspread.client.Client:
    """
    Autentica na API do Google usando as credenciais salvas no st.secrets.
    Retorna o cliente gspread autenticado.
    """
    try:
        # Puxa o dicionário de credenciais do secrets.toml
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Erro na autenticação com o Google Sheets: {e}")
        raise e

def get_sheet_data(client: gspread.client.Client, spreadsheet_id: str, worksheet_name: str = "Dados") -> tuple[gspread.Worksheet, List[Dict[str, Any]]]:
    """
    Abre a planilha pelo ID e retorna o objeto da aba e todos os registros como uma lista de dicionários.
    """
    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.worksheet(worksheet_name)
        # get_all_records() já mapeia a primeira linha como chave do dicionário
        records = worksheet.get_all_records()
        return worksheet, records
    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
        raise e

def update_sheet_row(worksheet: gspread.Worksheet, row_index: int, col_telefone: int, col_email: int, telefone: str, email: str) -> None:
    """
    Atualiza células específicas (telefone e email) em uma linha da planilha.
    row_index: O índice da linha na planilha do Google (normalmente começa em 2, pulando o cabeçalho).
    """
    try:
        # Atualiza a célula do telefone
        worksheet.update_cell(row_index, col_telefone, telefone)
        # Atualiza a célula do email
        worksheet.update_cell(row_index, col_email, email)
    except Exception as e:
        st.error(f"Erro ao atualizar a linha {row_index}: {e}")
        raise e