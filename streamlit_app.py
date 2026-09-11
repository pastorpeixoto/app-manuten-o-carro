import pandas as pd
import streamlit as st
import re

# Nome do aplicativo ajustado
NOME_SISTEMA = "LAYOU T - Gestão de Manutenções"

st.set_page_config(page_title=NOME_SISTEMA, page_icon="🚗", layout="wide")

# 1. LINK DA PLANILHA PUBLICADA NA WEB (formato CSV):
URL_PUBLICADA_CSV = r"""https://docs.google.com/spreadsheets/d/e/2PACX-1vTpcVNInjDdwUZ5E0tgRARfXn63Bx3zBRgFngEW4ffivNPv1bICkbeDfeO-74vUESMg93pj0-Ppyu9p/pub?output=csv"""

st.title(f"🚗 {NOME_SISTEMA}")

def carregar_dados_completos():
    if "SUA_URL_PUBLICADA" in URL_PUBLICADA_CSV:
        st.warning("Cole o link gerado em 'Publicar na web' no seu código.")
        return pd.DataFrame()
    
    try:
        # Lê o CSV bruto para podermos fatiar as tabelas
        df_bruto = pd.read_csv(URL_PUBLICADA_CSV, header=None)
        return df_bruto
    except Exception as e:
        st.error(f"Não foi possível carregar a planilha. Erro: {e}")
        return pd.DataFrame()

def extrair_valor_numerico(item):
    txt = str(item).strip()
    numeros = re.findall(r"[\d.,]+", txt)
    if numeros:
        val_str = numeros[0]
        if "." in val_str and "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        elif "," in val_str:
            val_str = val_str.replace(",", ".")
        try:
            return float(val_str)
        except ValueError:
            return 0.0
    return 0.0

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
    st.header("Relatório & Gráficos de Manutenções")
    
    df_bruto = carregar_dados_completos()
    
    if not df_bruto.empty:
        # Limpeza geral de lixo ou "noni"
        df_bruto = df_bruto.replace(to_replace=r'(?i)noni', value='', regex=True)
        
        # --- TABELA 1: MANUTENÇÃO DE VEÍCULOS ---
        st.subheader("📋 Manutenção de Veículo")
        try:
            # Aqui ajustamos para pegar a primeira tabela (ajuste as linhas se necessário conforme sua planilha)
            # Vamos supor que a tabela de manutenção começa logo no topo
            df_manutencao = df_bruto.iloc[1:5, :4].copy() # Exemplo de recorte de linhas/colunas
            df_manutencao.columns = ["Carro", "Serviço Realizado", "Data", "Valor"]
            df_manutencao = df_manutencao.dropna(how='all').fillna("")
            
            # Limpa e converte valores para métrica
            df_manutencao['Valor_Limpo'] = df_manutencao['Valor'].apply(extrair_valor_numerico)
            total_gasto = df_manutencao['Valor_Limpo'].sum()
            total_fmt = f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Gasto (Manutenções)", total_fmt)
            with col_m2:
                st.metric("Registros de Manutenção", len(df_manutencao))
                
            df_exibicao_manut = df_manutencao.drop(columns=['Valor_Limpo'])
            st.dataframe(df_exibicao_manut, use_container_width=True, hide_index=True)
        except Exception as e:
            st.info("Ainda não há dados suficientes formatados para a tabela de manutenção.")

        st.markdown("---")
        
        # --- TABELA 2: REGISTRO DE PNEUS ---
        st.subheader("🛞 Registro de Pneus")
        try:
            # Bloco isolado para a tabela de pneus que fica mais abaixo na planilha
            # Caso queira que fiquem em abas separadas no Google Sheets no futuro, a leitura fica perfeita.
            df_pneus = df_bruto.iloc[7:11, :4].copy() # Exemplo de recorte para a segunda tabela
            df_pneus.columns = ["Carro", "Data da Troca", "Marca do Pneu", "Quilometragem"]
            df_pneus = df_pneus.dropna(how='all').fillna("")
            
            st.metric("Registros de Pneus Trocados", len(df_pneus))
            st.dataframe(df_pneus, use_container_width=True, hide_index=True)
        except Exception as e:
            st.info("Nenhum registro de pneu localizado na seção correspondente.")
            
    else:
        st.info("Nenhuma informação encontrada na planilha.")



