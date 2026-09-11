import pandas as pd
import streamlit as st
import re

# Nome do aplicativo ajustado
NOME_SISTEMA = "LAYOU T - Gestão de Manutenções"

st.set_page_config(page_title=NOME_SISTEMA, page_icon="🚗", layout="wide")

# 1. LINK DA PLANILHA PUBLICADA NA WEB (formato CSV):
URL_PUBLICADA_CSV = r"""https://docs.google.com/spreadsheets/d/e/2PACX-1vTpcVNInjDdwUZ5E0tgRARfXn63Bx3zBRgFngEW4ffivNPv1bICkbeDfeO-74vUESMg93pj0-Ppyu9p/pub?output=csv"""

st.title(f"🚗 {NOME_SISTEMA}")

def carregar_dados():
    if "SUA_URL_PUBLICADA" in URL_PUBLICADA_CSV:
        st.warning("Cole o link gerado em 'Publicar na web' no seu código.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(URL_PUBLICADA_CSV, header=1)
        df = df.dropna(how='all')
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
    
    df = carregar_dados()
    
    if not df.empty:
        # Limpeza de dados indesejados e termos corrompidos
        df = df.replace(to_replace=r'(?i)noni', value='', regex=True)
        
        # Identifica colunas dinamicamente
        colunas_disponiveis = [str(c).strip().lower() for c in df.columns]
        
        col_valor = next((df.columns[i] for i, c in enumerate(colunas_disponiveis) if 'valor' in c), df.columns[-1])
        df['Valor_Limpo'] = df[col_valor].apply(extrair_valor_numerico)
        
        col_veiculo = next((df.columns[i] for i, c in enumerate(colunas_disponiveis) if 'carro' in c or 'veículo' in c or 'veiculo' in c), df.columns[0])
        col_servico = next((df.columns[i] for i, c in enumerate(colunas_disponiveis) if 'serviço' in c or 'servico' in c), df.columns[1] if len(df.columns) > 1 else df.columns[0])
        
        # FILTRA LINHAS INCOMPATÍVEIS (Remove linhas que são títulos de outras tabelas, como "Registro de troca de pneus")
        mask_valida = ~df[col_servico].astype(str).str.contains(r'pneus|troca de pneus|registro', case=False, na=False)
        df_manutencao = df[mask_valida].copy()
        
        # --- FILTRO POR VEÍCULO NA BARRA LATERAL ---
        st.sidebar.markdown("---")
        st.sidebar.header("Filtros")
        
        veiculos_unicos = df_manutencao[col_veiculo].dropna().astype(str).unique()
        lista_veiculos = ["Todos os Veículos"] + sorted(list(veiculos_unicos))
        
        veiculo_selecionado = st.sidebar.selectbox("Filtrar por Veículo:", lista_veiculos)
        
        if veiculo_selecionado != "Todos os Veículos":
            df_filtrado = df_manutencao[df_manutencao[col_veiculo].astype(str) == veiculo_selecionado]
        else:
            df_filtrado = df_manutencao
        
        # Métricas no topo
        total_gasto = df_filtrado['Valor_Limpo'].sum()
        total_fmt = f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total Gasto Somado", total_fmt)
        with col_m2:
            st.metric("Quantidade de Registros", len(df_filtrado))
            
        st.markdown("---")
        
        # --- SEÇÃO DE GRÁFICOS ---
        st.subheader("📊 Análise Visual de Custos")
        
        col_g1, col_g2 = st.columns(2)
        
        g_servico = df_filtrado.groupby(df_filtrado[col_servico].astype(str))['Valor_Limpo'].sum().reset_index()
        g_servico.columns = ['Serviço', 'Valor (R$)']
        
        g_veiculo = df_filtrado.groupby(df_filtrado[col_veiculo].astype(str))['Valor_Limpo'].sum().reset_index()
        g_veiculo.columns = ['Veículo', 'Valor (R$)']
        
        with col_g1:
            st.markdown("Gasto Total por Serviço (R$)")
            if not g_servico.empty and g_servico['Valor (R$)'].sum() > 0:
                st.bar_chart(data=g_servico, x='Serviço', y='Valor (R$)')
            else:
                st.info("Sem dados suficientes para o gráfico de serviços.")
            
        with col_g2:
            st.markdown("Gasto Total por Veículo (R$)")
            if not g_veiculo.empty and g_veiculo['Valor (R$)'].sum() > 0:
                st.bar_chart(data=g_veiculo, x='Veículo', y='Valor (R$)')
            else:
                st.info("Sem dados suficientes para o gráfico de veículos.")
            
        st.markdown("---")
        
        # --- TABELA DETALHADA DE MANUTENÇÃO LIMPA ---
        st.subheader("📋 Tabela Detalhada de Manutenções")
        df_display = df_filtrado.drop(columns=['Valor_Limpo'], errors='ignore')
        df_display = df_display.fillna("")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # --- SEÇÃO DE PNEUS ISOLADA (Pegando as linhas que contêm dados de pneus) ---
        st.markdown("---")
        st.subheader("🛞 Registro de Troca de Pneus")
        
        df_pneus = df[df[col_servico].astype(str).str.contains(r'pneus|troca de pneus|registro', case=False, na=False)].copy()
        if not df_pneus.empty:
            df_pneus_display = df_pneus.drop(columns=['Valor_Limpo'], errors='ignore').fillna("")
            st.dataframe(df_pneus_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro específico de pneus separado na listagem atual.")
            
    else:
        st.info("Nenhuma manutenção encontrada na planilha ou a planilha está vazia.")


