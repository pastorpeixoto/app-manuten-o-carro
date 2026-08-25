import pandas as pd
import streamlit as st 

st.set_page_config(page_title="Salvcar - Gestão de Manutenções", page_icon="🚗", layout="wide")

# COLE O LINK DA SUA PLANILHA ENTRE AS ASPAS TRIPLAS ABAIXO:
URL_PLANILHA = r"""https://docs.google.com/spreadsheets/d/https://docs.google.com/spreadsheets/d/1F3d_IMSvhn9k9vHJeu2LLQRwPdkvT98ycRhlXJmoe8w/edit?gid=1366024982#gid=1366024982/edit"""

def extrair_id(url):
    try:
        if "/d/" in url:
            parts = url.split("/d/")
            return parts[1].split("/")[0]
        return ""
    except Exception:
        return ""

SHEET_ID = extrair_id(URL_PLANILHA)

st.title("🚗 Salvcar - Controle de Manutenções")

def carregar_dados():
    if not SHEET_ID or "SEU_LINK_AQUI" in URL_PLANILHA:
        return pd.DataFrame(columns=["Carro", "Serviço Realizado", "Data", "Valor (R$)"])
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(csv_url)
        return df
    except Exception:
        st.error("Certifique-se de que a planilha está compartilhada como 'Qualquer pessoa com o link'.")
        return pd.DataFrame(columns=["Carro", "Serviço Realizado", "Data", "Valor (R$)"])

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
        
        if "Valor (R$)" in df.columns:
            df["Valor (R$)"] = pd.to_numeric(
                df["Valor (R$)"].astype(str).str.replace("R$", "", regex=False).str.replace(",", ".", regex=False),
                errors="coerce"
            ).fillna(0)
            total_gasto = df["Valor (R$)"].sum()
            st.metric("Total Gasto com Manutenções", f"R$ {total_gasto:,.2f}")
    else:
        st.info("Nenhuma manutenção encontrada na planilha ou planilha vazia.") 
