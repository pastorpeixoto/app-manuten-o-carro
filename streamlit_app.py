import streamlit as st
import datetime
import pandas as pd

# Configuracao da pagina
st.set_page_config(page_title="Manutencao de Carro", page_icon="🚗")

# Titulo Principal
st.title("🚗 App Manutenção de Carro")
st.write("Cadastre as informações do veículo e acompanhe o histórico.")

# Inicializa o historico na memoria
if "historico" not in st.session_state:
    st.session_state.historico = []

st.divider()

# --- FORMULARIO DE CADASTRO ---
st.subheader("📋 Novo Registro de Manutenção")

col1, col2 = st.columns(2)
with col1:
    modelo = st.text_input("Modelo do Carro", placeholder="Ex: Gol, Civic, Onix...")
with col2:
    placa = st.text_input("Placa do Carro", placeholder="Ex: ABC-1234")

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

# --- BOTAO DE SALVAR ---
if st.button("💾 Salvar Manutenção", type="primary"):
    if modelo and placa:
        novo_registro = {
            "Data": data_servico.strftime("%d/%m/%Y"),
            "Modelo": modelo,
            "Placa": placa.upper(),
            "Serviço": tipo_servico,
            "KM": f"{km_atual} km",
            "Obs": observacoes if observacoes else "-"
        }
        st.session_state.historico.append(novo_registro)
        st.success("Manutenção salva com sucesso!")
    else:
        st.error("Por favor, preencha o Modelo e a Placa do veículo.")

st.divider()

# --- TABELA DE HISTORICO ---
st.subheader("📊 Histórico de Manutenções")

if len(st.session_state.historico) > 0:
    df = pd.DataFrame(st.session_state.historico)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Limpar Histórico"):
        st.session_state.historico = []
        st.rerun()
else:
    st.info("Nenhuma manutenção registrada até o momento.")
