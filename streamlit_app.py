mport streamlit as st
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

st.write("") # Espaço em branco

# --- BOTÃO DE SALVAR (BEM VISÍVEL) ---
if st.button("💾 Salvar Manutenção", type="primary", use_container_width=True):
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
        # Adiciona ao histórico
        st.session_state.historico.append(novo_registro)
        st.success(f"Manutenção do *{modelo}* ({placa}) salva no histórico com sucesso!")
    else:
        st.error("Por favor, preencha pelo menos o *Modelo* e a *Placa* do veículo antes de salvar.")

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
    
    col_download, col_limpar = st.columns(2)
    with col_download:
        st.download_button(
            label="📥 Baixar Histórico em Excel / CSV",
            data=csv,
            file_name=f"historico_manutencao_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_limpar:
        if st.button("🗑️ Limpar Histórico Atual", use_container_width=True):
            st.session_state.historico = []
            st.rerun()
else:
    st.info("Nenhuma manutenção registrada até o momento. Preencha os campos acima e clique em 'Salvar Manutenção'.")
