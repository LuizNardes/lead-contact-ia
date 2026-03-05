import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
import json
import time
import re
from typing import Dict, Any, Tuple

class ContatosExtraidos(BaseModel):
    telefones: list[str]
    emails: list[str]

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("Chave GEMINI_API_KEY não encontrada no secrets.toml.")

def extract_with_regex(text: str) -> Tuple[list[str], list[str]]:
    """
    Camada de segurança determinística com Regex focado nas loucuras da formatação brasileira.
    """
    # Encontra e-mails 
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    
    # Regex para Telefones BR:
    # Captura opcional de +55, parênteses no DDD, e aceita pontos, traços e espaços no meio do número.
    padrao_telefone = r'(?:\+55\s?)?\(?\d{2}\)?\s*(?:9[.\-\s]?)?\d{4}[.\-\s]?\d{4}|0800[.\-\s]?\d{3}[.\-\s]?\d{4}'
    telefones_brutos = re.findall(padrao_telefone, text)
    
    telefones_limpos = []
    for t in telefones_brutos:
        # Pega a string encontrada e remove os espaços das pontas
        t_strip = t.strip()
        
        # Validação extra de segurança: só aceita se tiver pelo menos 10 números (DDD + 8 dígitos)
        so_numeros = re.sub(r'\D', '', t_strip)
        if len(so_numeros) >= 10:
            telefones_limpos.append(t_strip)
    
    return list(set(telefones_limpos)), list(set(emails))

def extract_contacts_with_gemini(text: str) -> Dict[str, Any]:
    time.sleep(4.5)

    if not text or len(text) < 15:
        return {"telefones": [], "emails": []}

    prompt = f"""
    Extraia TODOS os números de telefone e e-mails corporativos do texto abaixo.
    TEXTO:
    {text[:15000]}
    """

    # 1. Extração via Inteligência Artificial
    ai_telefones = []
    ai_emails = []
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ContatosExtraidos,
                temperature=0.0, 
            ),
        )
        data = json.loads(response.text)
        ai_telefones = data.get("telefones", [])
        ai_emails = data.get("emails", [])
    except Exception as e:
        print(f"[ERRO GEMINI]: {e}")

    # 2. Extração via Expressão Regular (Regex)
    regex_telefones, regex_emails = extract_with_regex(text)

    # 3. O Merge (Unindo forças e removendo duplicatas)
    final_telefones = list(set(ai_telefones + regex_telefones))
    final_emails = list(set(ai_emails + regex_emails))

    return {"telefones": final_telefones, "emails": final_emails}