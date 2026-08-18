import streamlit as st
import datetime

# Configuração da página
st.set_page_config(page_title="Manutenção de Carro", page_icon="🚗")

# Título Principal
st.title("🚗 App Manutenção de Carro")
st.write("Cadastre as informações do veículo e o histórico de revisões.")

st.divider()

# --- SEÇÃO 1: DADOS DO VEÍCULO ---
st.subheader("📋 Dados do Veículo")

col1, col2 = st.columns(2)

with col1:
    modelo = st.text_input("Modelo do Carro", placeholder="Ex: Gol 1.0, Civic, Onix...")

with col2:
    placa = st.text_input("Placa do Carro", placeholder="Ex: ABC-1234").upper()


# --- SEÇÃO 2: DADOS DA MANUTENÇÃO ---
st.subheader("🔧 Registro de Manutenção")

tipo_servico = st.selectbox(
    "Tipo de Serviço",
    [
        "Troca de Óleo e Filtro",
        "Sistema de Freios",
        "Troca / Rotação de Pneus",
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

observacoes = st.text_area("Observações ou Detalhes do Serviço", placeholder="Ex: Marcado para trocar novamente daqui 10.000 KM...")

st.divider()

# --- BOTÃO DE REGISTRAR ---
if st.button("💾 Salvar Manutenção", type="primary"):
    if modelo and placa:
        st.success(f"Manutenção do *{modelo}* ({placa}) salva com sucesso!")
        
        # Exibe os dados confirmados logo abaixo
        st.write("---")
        st.write("*Resumo do Registro:*")
        st.write(f"- *Veículo:* {modelo} - Placa: {placa}")
        st.write(f"- *Serviço:* {tipo_servico}")
        st.write(f"- *KM:* {km_atual:,} km")
        st.write(f"- *Data:* {data_servico.strftime('%d/%m/%Y')}")
        if observacoes:
            st.write(f"- *Obs:* {observacoes}")
    else:
        st.error("Por favor, preencha pelo menos o *Modelo* e a *Placa* do veículo antes de salvar.")
