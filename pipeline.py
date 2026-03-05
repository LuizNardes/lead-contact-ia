import asyncio
from typing import AsyncGenerator, Dict, Any

import google_sheets
import scraper
import ai_extractor

async def process_single_lead(
    worksheet, 
    row_index: int, 
    site_url: str, 
    col_telefone_idx: int, 
    col_email_idx: int
) -> Dict[str, str]:
    
    if not site_url:
        return {"url": "Vazia", "status": "Ignorado", "detalhe": "Nenhuma URL fornecida."}

    # 1. Scraping Assíncrono do site
    html_limpo = await scraper.scrape_website(site_url)
    if not html_limpo:
        return {"url": site_url, "status": "Erro", "detalhe": "Falha no scraping ou site inacessível."}

    # 2. Extração com Gemini
    dados_extraidos = ai_extractor.extract_contacts_with_gemini(html_limpo)
    
    telefones = ", ".join(dados_extraidos.get("telefones", []))
    emails = ", ".join(dados_extraidos.get("emails", []))

    if not telefones and not emails:
         return {"url": site_url, "status": "Sem Dados", "detalhe": "Nenhum contato encontrado pela IA."}

    # 3. Atualiza o Google Sheets dinamicamente
    google_sheets.update_sheet_row(
        worksheet=worksheet,
        row_index=row_index,
        col_telefone=col_telefone_idx,
        col_email=col_email_idx,
        telefone=telefones,
        email=emails
    )

    return {"url": site_url, "status": "Sucesso", "detalhe": f"Tel: {telefones} | Email: {emails}"}

async def run_pipeline_generator(
    spreadsheet_id: str, 
    max_rows: int = 0
) -> AsyncGenerator[Dict[str, Any], None]:
    
    try:
        client = google_sheets.authenticate_gspread()
        worksheet, records = google_sheets.get_sheet_data(client, spreadsheet_id)
        
        if not records:
            yield {"current": 0, "total": 0, "resultado": {"url": "Aviso", "status": "Erro", "detalhe": "A planilha está vazia."}}
            return

        # ==========================================
        # 🧠 MAPEAMENTO DINÂMICO DE COLUNAS
        # ==========================================
        headers = worksheet.row_values(1)
        
        try:
            col_telefone_idx = headers.index("telefone_ia") + 1
            col_email_idx = headers.index("email_ia") + 1
        except ValueError:
            yield {
                "current": 0, 
                "total": 0, 
                "resultado": {
                    "url": "Erro de Estrutura", 
                    "status": "Erro", 
                    "detalhe": "Crie as colunas exatas 'telefone_ia' e 'email_ia' na linha 1 da planilha."
                }
            }
            return
        # ==========================================

        if max_rows > 0:
            records = records[:max_rows]
            
        total_rows = len(records)
        
        for i, row in enumerate(records):
            row_index = i + 2 
            site_url = str(row.get("Site", "")).strip()
            
            resultado = await process_single_lead(
                worksheet=worksheet,
                row_index=row_index,
                site_url=site_url,
                col_telefone_idx=col_telefone_idx,
                col_email_idx=col_email_idx
            )
            
            yield {
                "current": i + 1,
                "total": total_rows,
                "resultado": resultado
            }
            
    except Exception as e:
        erro_real = f"{type(e).__name__}: {str(e)}"
        if not str(e).strip():
            erro_real = repr(e)
            
        yield {
            "current": 0, 
            "total": 0, 
            "resultado": {"url": "Erro Fatal", "status": "Erro", "detalhe": erro_real}
        }