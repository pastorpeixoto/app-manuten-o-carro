[10:43, 18/08/2026] José Carlos Peixoto: import streamlit as st
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
[10:48, 18/08/2026] José Carlos Peixoto: import streamlit as st
import datetime
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Manutenção de Carro", page_icon="🚗", layout="wide")

# Título Principal
st.title("🚗 App Manutenção de Carro")
st.write("Cadastre as informações do veículo e acompanhe o histórico de revisões.")

# Inicializa o histórico na memória da sessão se ainda não existir
if "historico" not in st.session_state:
    st.session_state.historico = []

st.divider()

# --- FORMULÁRIO DE CADASTRO ---
with st.form("form_manutencao", clear_on_submit=True):
    st.subheader("📋 Novo Registro de Manutenção")
    
    col1, col2 = st.columns(2)
    with col1:
        modelo = st.text_input("Modelo do Carro", placeholder="Ex: Gol 1.0, Civic, Onix...")
    with col2:
        placa = st.text_input("Placa do Carro", placeholder="Ex: ABC-1234").upper()

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

    observacoes = st.text_area("Observações ou Detalhes do Serviço", placeholder="Ex: Próxima troca em 10.000 KM...")

    # Botão de Envio do Formulário
    submetido = st.form_submit_button("💾 Salvar Manutenção", type="primary")

    if submetido:
        if modelo and placa:
            # Cria o novo registro
            novo_registro = {
                "Data": data_servico.strftime('%d/%m/%Y'),
                "Modelo": modelo,
                "Placa": placa,
                "Serviço": tipo_servico,
                "Quilometragem": f"{km_atual:,} km",
                "Observações": observacoes if observacoes else "-"
            }
            # Adiciona ao histórico na sessão
            st.session_state.historico.append(novo_registro)
            st.success(f"Manutenção do *{modelo}* ({placa}) salva no histórico!")
        else:
            st.error("Por favor, preencha pelo menos o *Modelo* e a *Placa* do veículo.")

st.divider()

# --- EXIBIÇÃO DO HISTÓRICO EM TABELA ---
st.subheader("📊 Histórico de Manutenções Realizadas")

if len(st.session_state.historico) > 0:
    # Converte o histórico para uma Tabela (DataFrame)
    df = pd.DataFrame(st.session_state.historico)
    
    # Exibe a tabela interativa na tela
    st.dataframe(df, use_container_width=True)

    # Prepara o arquivo CSV para download
    csv = df.to_csv(index=False).encode('utf-8')
    
    col_download, col_limpar = st.columns([1, 1])
    with col_download:
        st.download_button(
            label="📥 Baixar Histórico em Excel / CSV",
            data=csv,
            file_name=f"historico_manutencao_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    with col_limpar:
        if st.button("🗑️ Limpar Histórico Atual"):
            st.session_state.historico = []
            st.rerun()
else:
    st.info("Nenhuma manutenção registrada até o momento. Preencha o formulário acima para adicionar o primeiro registro.")
