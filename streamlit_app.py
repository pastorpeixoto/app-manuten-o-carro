import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Salvcar - Gestão de Manutenções", page_icon="🚗", layout="wide")

# COLE O LINK DA SUA PLANILHA ENTRE AS ASPAS ABAIXO:
URL_PLANILHA = r"""https://docs.google.com/spreadsheets/d/https://docs.google.com/spreadsheets/d/https://docs.google.com/spreadsheets/d/1F3d_IMSvhn9k9vHJeu2LLQRwPdkvT98ycRhlXJmoe8w/edit?gid=1366024982#gid=1366024982/edit"""

st.title("🚗 Salvcar - Controle de Manutenções")

def carregar_dados():
    conn = st.connection("gsheets", type=GSheetsConnection) 
    df = conn.read(spreadsheet=URL_PLANILHA, ttl="0s")
    return conn, df

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
                try:
                    conn, df = carregar_dados()
                    novo_registro = pd.DataFrame([{
                        "Carro": veiculo,
                        "Serviço Realizado": servico,
                        "Data": str(data),
                        "Valor (R$)": valor
                    }])
                    df_atualizado = pd.concat([df, novo_registro], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILHA, data=df_atualizado)
                    st.success("Manutenção cadastrada com sucesso na nuvem!")
                except Exception as e:
                    st.error(f"Erro ao salvar na planilha: {e}")
            else:
                st.error("Por favor, preencha os campos obrigatórios (Veículo e Serviço).")

elif opcao == "Ver Relatório":
    st.header("Relatório de Manutenções")
    
    try:
        conn, df = carregar_dados()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            df["Valor (R$)"] = pd.to_numeric(df["Valor (R$)"], errors="coerce").fillna(0)
            total_gasto = df["Valor (R$)"].sum()
            st.metric("Total Gasto com Manutenções", f"R$ {total_gasto:,.2f}")
        else:
            st.info("Nenhuma manutenção cadastrada até o momento.")
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
