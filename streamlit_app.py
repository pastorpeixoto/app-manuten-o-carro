import pandas as pd
import streamlit as st

st.set_page_config(page_title="Salvcar - Gestão de Manutenções", page_icon="🚗", layout="wide")

# 1. LINK DA PLANILHA PUBLICADA NA WEB (formato CSV):
URL_PUBLICADA_CSV = r"""https://docs.google.com/spreadsheets/d/e/2PACX-1vTpcVNInjDdwUZ5E0tgRARfXn63Bx3zBRgFngEW4ffivNPv1bICkbeDfeO-74vUESMg93pj0-Ppyu9p/pub?output=csv"""

st.title("🚗 Salvcar - Controle de Manutenções")

def carregar_dados():
    if "PASTE_AQUI" in URL_PUBLICADA_CSV:
        st.warning("Cole o link gerado em 'Publicar na web' na linha 8 do seu código no GitHub.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(URL_PUBLICADA_CSV)
        return df
    except Exception as e:
        st.error("Não foi possível carregar a planilha. Verifique se o link publicado na web foi copiado corretamente.")
        return pd.DataFrame()

st.sidebar.header("Menu de Navegação")
opcao = st.sidebar.radio("Selecione uma opção:", ["Cadastrar Manutenção", "Ver Relatório"])

if opcao == "Cadastrar Manutenção":
    st.header("Cadastrar Nova Manutenção")
    
    with st.form("form_manutencao"):
        data = st.date_input("Data do Serviço")
        veiculo = st.text_input("Placa / Modelo do Veículo")
        
        lista_servicos = [
            "Troca de Óleo e Filtros",
            "Sistemas de Freios (Pastilhas/Discos)",
            "Alinhamento e Balanceamento",
            "Troca de Pneus",
            "Suspensão e Amortecedores",
            "Correia Dentada / Correias",
            "Bateria e Sistema Elétrico",
            "Ar Condicionado",
            "Embreagem",
            "Revisão Geral / Outro"
        ]
        
        servico = st.selectbox("Descrição do Serviço / Peça", lista_servicos)
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        observacoes = st.text_area("Observações (detalhes das peças trocadas, marca, etc.)")
        
        submetido = st.form_submit_button("Salvar Manutenção")
        
        if submetido:
            if veiculo and servico:
                st.success("Formulário enviado! Consulte a planilha para o histórico atualizado.")
            else:
                st.error("Por favor, preencha os campos obrigatórios (Veículo e Serviço).")

elif opcao == "Ver Relatório":
    st.header("Relatório de Manutenções (Google Sheets)")
    
    df = carregar_dados()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        colunas_valor = [col for col in df.columns if any(k in str(col).lower() for k in ["valor", "preco", "custo", "r$"])]
        if colunas_valor:
            col_nome = colunas_valor[0]
            valores_limpos = pd.to_numeric(
                df[col_nome].astype(str).str.replace("R$", "", regex=False).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).str.strip(),
                errors="coerce"
            ).fillna(0)
            total_gasto = valores_limpos.sum()
            st.metric("Total Gasto", f"R$ {total_gasto:,.2f}")
    else:
        st.info("Nenhuma manutenção encontrada na planilha ou a planilha está vazia.")
       
            


