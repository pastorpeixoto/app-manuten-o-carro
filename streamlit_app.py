import pandas as pd
import streamlit as st
import re

# Nome do aplicativo ajustado
NOME_SISTEMA = "LAYOU T - Gestão de Manutenções"

st.set_page_config(page_title=NOME_SISTEMA, page_icon="🚗", layout="wide")

# 1. LINK DA PLANILHA PUBLICADA NA WEB (formato CSV):
URL_PUBLICADA_CSV = r"""https://docs.google.com/spreadsheets/d/e/2PACX-1vTpcVNInjDdwUZ5E0tgRARfXn63Bx3zBRgFngEW4ffivNPv1bICkbeDfeO-74vUESMg93pj0-Ppyu9p/pub?output=csv"""

st.title(f"🚗 {NOME_SISTEMA}")

def carregar_dados_brutos():
    if "SUA_URL_PUBLICADA" in URL_PUBLICADA_CSV:
        st.warning("Cole o link gerado em 'Publicar na web' no seu código.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(URL_PUBLICADA_CSV, header=None)
        return df
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
    
    df_bruto = carregar_dados_brutos()
    
    if not df_bruto.empty:
        # Limpeza geral de termos indesejados ("noni", etc.)
        df_bruto = df_bruto.replace(to_replace=r'(?i)noni', value='', regex=True)
        
        # --- PROCESSAMENTO DA TABELA 1: MANUTENÇÃO DE VEÍCULOS ---
        try:
            df_manut = df_bruto.iloc[2:6, 0:4].copy()
            df_manut.columns = ["Carro", "Serviço realizado", "Data", "Valor"]
            df_manut = df_manut.dropna(how='all').fillna("")
            
            # FILTRO CRUCIAL: Remove linhas que contenham palavras de cabeçalho ou da outra tabela (como "pneus")
            filtro_lixo = df_manut["Carro"].str.contains("Carro|Manutenção|Pneu|Registro", case=False, na=False) | \
                          df_manut["Serviço realizado"].str.contains("Pneu|Registro|Troca de pneus", case=False, na=False)
            df_manut = df_manut[~filtro_lixo]
            
            # Prepara valores para os gráficos
            df_manut['Valor_Limpo'] = df_manut["Valor"].apply(extrair_valor_numerico)
            
            # Métricas no topo
            total_gasto = df_manut['Valor_Limpo'].sum()
            total_fmt = f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Gasto (Manutenções)", total_fmt)
            with col_m2:
                st.metric("Registros de Manutenção", len(df_manut))
                
            st.markdown("---")
            
            # --- GRÁFICOS ---
            st.subheader("📊 Análise Visual de Custos (Manutenções)")
            col_g1, col_g2 = st.columns(2)
            
            g_servico = df_manut.groupby("Serviço realizado")['Valor_Limpo'].sum().reset_index()
            g_veiculo = df_manut.groupby("Carro")['Valor_Limpo'].sum().reset_index()
            
            with col_g1:
                st.markdown("Gasto por Serviço (R$)")
                if not g_servico.empty and g_servico['Valor_Limpo'].sum() > 0:
                    st.bar_chart(data=g_servico, x="Serviço realizado", y='Valor_Limpo')
                else:
                    st.info("Sem dados suficientes.")
                    
            with col_g2:
                st.markdown("Gasto por Veículo (R$)")
                if not g_veiculo.empty and g_veiculo['Valor_Limpo'].sum() > 0:
                    st.bar_chart(data=g_veiculo, x="Carro", y='Valor_Limpo')
                else:
                    st.info("Sem dados suficientes.")
                    
        except Exception as e:
            df_manut = pd.DataFrame()

        st.markdown("---")
        
        # Exibe a Tabela 1 limpa (Apenas os carros e serviços reais)
        st.subheader("📋 Tabela Detalhada: Manutenção de Veículo")
        if not df_manut.empty:
            df_manut_display = df_manut.drop(columns=['Valor_Limpo'], errors='ignore')
            st.dataframe(df_manut_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado na tabela de manutenções.")

        st.markdown("---")
        
        # --- PROCESSAMENTO DA TABELA 2: REGISTRO DE TROCA DE PNEUS ---
        st.subheader("🛞 Tabela Detalhada: Registro de Troca de Pneus")
        try:
            df_pneus = df_bruto.iloc[8:12, 0:4].copy()
            df_pneus.columns = ["Carro", "Data da troca", "Marca do pneu", "Quilometragem"]
            df_pneus = df_pneus.dropna(how='all').fillna("")
            
            # Remove linhas de cabeçalho duplicadas se houver
            df_pneus = df_pneus[~df_pneus["Carro"].str.contains("Carro|Pneus|Registro", case=False, na=False)]
            
            if not df_pneus.empty:
                st.dataframe(df_pneus, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum registro de pneu cadastrado nesta seção.")
        except Exception as e:
            st.info("Aguardando preenchimento dos dados de troca de pneus.")
            
    else:

