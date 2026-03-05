import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re
import logging

async def fetch_html(url: str) -> Optional[str]:
    """
    Faz uma requisição HTTP assíncrona para a URL fornecida com headers avançados.
    """
    # Headers para "enganar" firewalls básicos e parecer um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Adicionamos follow_redirects para seguir redirecionamentos de http para https
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logging.error(f"Erro ao aceder a {url}: {e}")
        return None
    
def clean_html(html_content: str) -> str:
    """
    Recebe o HTML bruto, remove tags inúteis e devolve apenas o texto limpo.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup(["script", "style", "noscript", "svg", "meta"]):
        element.decompose()

    # Extrair o texto separando os blocos por espaços
    text = soup.get_text(separator=" ", strip=True)
    
    # Limpar múltiplos espaços em branco e quebras de linha para otimizar tokens
    clean_text = re.sub(r'\s+', ' ', text)
    
    return clean_text

async def scrape_website(url: str) -> str:
    """
    Função principal que orquestra o scraping: valida a URL, busca o HTML e limpa o conteúdo.
    """
    # Garantir que a URL tem o protocolo correto
    if not url.strip().startswith("http"):
        url = "https://" + url.strip()

    html = await fetch_html(url)
    if html:
        return clean_html(html)
    return ""