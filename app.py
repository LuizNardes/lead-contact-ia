import streamlit as st
import asyncio

import pipeline

st.set_page_config(
    page_title="LeadContact AI",
    page_icon="🤖",
    layout="wide"
)

def main() -> None:
    st.title("🤖 LeadContact AI")
    st.markdown("Enriqueça sua base de leads com IA e Web Scraping Assíncrono.")

    # 1. Inicializa os estados
    if "is_running" not in st.session_state:
        st.session_state.is_running = False
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "finished" not in st.session_state:
        st.session_state.finished = False

    sheet_id = st.text_input(
        "ID da Planilha do Google Sheets", 
        placeholder="Ex: 1A2b3C4d5E6f7G8h9I0j..."
    )

    st.info("💡 Certifique-se de que a planilha possui as colunas 'Site', 'telefone_ia' e 'email_ia' na primeira linha.")

    # 2. Área de Logs Persistente
    st.markdown("### Logs de Execução")
    log_container = st.container(height=350)
    log_box = log_container.empty()
    
    if st.session_state.logs:
        log_box.markdown("  \n".join(st.session_state.logs))

    if st.session_state.finished:
        st.success("🎉 Processo de enriquecimento concluído!")

    # 3. Função de Callback (Muda o estado ANTES de rodar o código pesado)
    def iniciar_processo():
        st.session_state.is_running = True
        st.session_state.finished = False
        st.session_state.logs = []

    # 4. Botão Inteligente
    # Fica desabilitado se estiver rodando OU se o campo de ID estiver vazio
    btn_disabled = st.session_state.is_running or not sheet_id.strip()
    texto_botao = "⏳ Processando..." if st.session_state.is_running else "Iniciar Enriquecimento"

    st.button(
        texto_botao, 
        disabled=btn_disabled, 
        on_click=iniciar_processo
    )

    # 5. O Fluxo de Execução (Só entra aqui porque o callback mudou a variável)
    if st.session_state.is_running:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        async def run_process() -> None:
            async for step in pipeline.run_pipeline_generator(spreadsheet_id=sheet_id, max_rows=3):
                current = step.get("current", 0)
                total = step.get("total", 0)
                resultado = step.get("resultado", {})
                
                if total > 0:
                    progress_percentage = int((current / total) * 100)
                    progress_bar.progress(progress_percentage)
                
                status_text.text(f"Processando lead {current} de {total}...")
                
                icone = "✅" if resultado["status"] == "Sucesso" else "⚠️" if resultado["status"] == "Sem Dados" else "❌"
                log_msg = f"{icone} **{resultado['url']}** -> {resultado['detalhe']}"
                
                st.session_state.logs.append(log_msg)
                log_box.markdown("  \n".join(st.session_state.logs))
            
            st.session_state.finished = True
            st.balloons()

        # Roda a função assíncrona
        try:
            asyncio.run(run_process())
        except Exception as e:
            st.error(f"Erro crítico na execução: {e}")
        finally:
            st.session_state.is_running = False
            # O rerun aqui garante que a tela recarregue e o botão volte ao normal
            st.rerun()

if __name__ == "__main__":
    main()