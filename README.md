# 🤖 LeadContact AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Google Sheets](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)

O **LeadContact AI** é um pipeline inteligente de enriquecimento de dados projetado para automatizar a extração de contatos (telefones e e-mails) de sites institucionais. 

A ferramenta acessa as URLs fornecidas em uma planilha do Google Sheets, faz a varredura e limpeza do HTML de forma assíncrona, e utiliza uma abordagem híbrida (Regex + LLM) para encontrar dados de contato, atualizando a planilha automaticamente em tempo real.

---

## ✨ Destaques da Arquitetura (Por que não é apenas um script comum?)

* **Extração Híbrida (Regex + Gemini 1.5 Flash):** Expressões regulares blindadas garantem a captura determinística de formatos caóticos de telefones brasileiros, enquanto o LLM analisa o contexto semântico para encontrar contatos "escondidos" no texto.
* **Structured Outputs com Pydantic:** Força a API do Gemini a retornar um JSON estrito e validado, eliminando falhas de formatação ("alucinações") do modelo.
* **Scraping Assíncrono:** Utilização de `httpx` e `asyncio` para requisições não-bloqueantes, aumentando drasticamente a velocidade de leitura das páginas.
* **Resiliência e Tolerância a Falhas:** Implementação de lógicas de *retry* com *Exponential Backoff* para lidar com limites de cota de API (HTTP 429) e instabilidades de servidor (HTTP 503).
* **Mapeamento Dinâmico:** O sistema lê o cabeçalho do Google Sheets dinamicamente, evitando quebras estruturais se novas colunas forem adicionadas à planilha.
* **Interface Reativa:** Frontend construído em Streamlit com gerenciamento de estado (`session_state`) para exibição de logs persistentes em tempo real.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Frontend:** Streamlit
* **IA/LLM:** Google Gemini API (`google-genai`)
* **Validação de Dados:** Pydantic
* **Web Scraping:** `httpx`, `asyncio`, `BeautifulSoup4`
* **Integração:** `gspread` (Google Sheets API), `oauth2client`

---

## ⚙️ Como executar o projeto localmente

### 1. Pré-requisitos
* Python 3.10 ou superior.
* Uma conta no Google Cloud Platform (GCP) com a **Google Sheets API** ativada e uma **Service Account** (Conta de Serviço) criada.
* Uma chave de API do **Google AI Studio** (Gemini).

### 2. Instalação
Clone este repositório e instale as dependências:

```bash
git clone [https://github.com/SEU_USUARIO/lead-contact-ia.git](https://github.com/SEU_USUARIO/lead-contact-ia.git)
cd lead-contact-ia
python -m venv venv

# Ative o ambiente virtual (Windows)
.\venv\Scripts\activate
# Ou no Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuração de Variáveis de Ambiente (Secrets)
Crie uma pasta chamada `.streamlit` na raiz do projeto e dentro dela crie um arquivo chamado `secrets.toml`. 

Preencha com as suas credenciais:

```toml
GEMINI_API_KEY = "SUA_CHAVE_GEMINI_AQUI"

[gcp_service_account]
type = "service_account"
project_id = "seu-projeto-id"
private_key_id = "seu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_PRIVADA_AQUI\n-----END PRIVATE KEY-----\n"
client_email = "seu-email-da-service-account@...iam.gserviceaccount.com"
client_id = "seu-client-id"
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "URL_DO_CERTIFICADO"
universe_domain = "googleapis.com"
```

### 4. Configuração da Planilha
1. Crie uma planilha no Google Sheets.
2. Compartilhe a planilha com o e-mail da sua Service Account (`client_email`) dando permissão de **Editor**.
3. Na primeira linha (cabeçalho), crie obrigatoriamente as colunas: `site`, `telefone_ia` e `email_ia`.

### 5. Executando a Aplicação
Com o ambiente virtual ativado, rode:

```bash
streamlit run app.py
```

A aplicação abrirá no seu navegador padrão. Basta inserir o ID da sua planilha (encontrado na URL do Google Sheets) e iniciar o processamento.

---
