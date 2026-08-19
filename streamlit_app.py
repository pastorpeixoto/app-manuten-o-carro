import streamlit as st
import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuracao da pagina
st.set_page_config(page_title="Manutencao de Carro", page_icon="🚗", layout="wide")

# Titulo Principal
st.title("🚗 App Manutenção de Carro")
st.write("Cadastre as informações do veículo e acompanhe o histórico salvo permanentemente na nuvem.")

# Conexao com o Google Sheets via Streamlit Connections
conn = st.connection("gsheets", type=GSheetsConnection)

# Funcao para carregar dados do Google Sheets
def carregar_dados():
    try:
        df = conn.read(ttl=0) # ttl=0 garante leitura sem cache antigo
        return df
    except Exception as e:
        # Retorna DataFrame vazio em caso de erro na conexao inicial ou planilha vazia
        return pd.DataFrame(columns=["Data", "Modelo", "Placa", "Serviço", "KM", "Obs"])

st.divider()

# --- FORMULARIO DE CADASTRO ---
st.subheader("📋 Novo Registro de Manutenção")

col1, col2 = st.columns(2)
with col1:
    modelo = st.text_input("Modelo do Carro", placeholder="Ex: Gol, Civic, Onix...")
with col2:
    placa = st.text_input("Placa do Carro", placeholder="Ex: ABC-1234").upper()

tipo_servico = st.selectbox(
    "Tipo de Serviço",
    [
        "Troca de Óleo e Filtro",
        "Sistema de Freios",
        "Troca de Pneus",
        "Alinhamento e Balanceamento",
        "Revisão Geral",
        "Outro"
    ]
)

col3, col4 = st.columns(2)
with col3:
    km_atual = st.number_input("Quilometragem Atual (KM)", min_value=0, step=500)
with col4:
    data_servico = st.date_input("Data da Manutenção", datetime.date.today())

observacoes = st.text_area("Observações", placeholder="Ex: Troca feita na oficina X...")

st.write("")

# --- BOTAO DE SALVAR NO GOOGLE SHEETS ---
if st.button("💾 Salvar no Google Sheets", type="primary", use_container_width=True):
    if modelo and placa:
        with st.spinner("Salvando registro na planilha..."):
            # 1. Carrega o estado atual da planilha
            df_atual = carregar_dados()
            
            # 2. Prepara a nova linha
            novo_registro = pd.DataFrame([{
                "Data": data_servico.strftime("%d/%m/%Y"),
                "Modelo": modelo,
                "Placa": placa,
                "Serviço": tipo_servico,
                "KM": f"{km_atual} km",
                "Obs": observacoes if observacoes else "-"
            }])
            
            # 3. Adiciona a nova linha mantendo os dados antigos
            df_atualizado = pd.concat([df_atual, novo_registro], ignore_index=True)
            
            # 4. Grava de volta no Google Sheets
            conn.update(data=df_atualizado)
            
            st.success("Manutenção gravada permanentemente no Google Sheets com sucesso!")
            st.rerun()
    else:
        st.error("Por favor, preencha pelo menos o Modelo e a Placa do veículo.")

st.divider()

# --- TABELA DE HISTORICO EM TEMPO REAL ---
st.subheader("📊 Histórico de Manutenções (Google Sheets)")

df_historico = carregar_dados()

if not df_historico.empty:
    st.dataframe(df_historico, use_container_width=True)
else:
    st.info("Nenhuma manutenção encontrada na planilha. Cadastre o primeiro registro acima!")
