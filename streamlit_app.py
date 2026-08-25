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
        st.warning("Cole o link gerado em 'Publicar na web' na linha 11 do seu código no GitHub.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(URL_PUBLICADA_CSV)
        return df
    except Exception as e:
        st.error("Não foi possível carregar a planilha. Verifique se o link publicado na web foi copiado corretamente.")
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
        # Coluna D (índice 3) para os valores numéricos
        col_valor = df.columns[3] if len(df.columns) >= 4 else df.columns[-1]
        
        # Converte valores da Coluna D em números
        df['Valor_Limpo'] = df[col_valor].apply(extrair_valor_numerico)
        
        col_veiculo = df.columns[1] if len(df.columns) >= 2 else df.columns[0]
        col_servico = df.columns[2] if len(df.columns) >= 3 else df.columns[0]
        
        # --- FILTRO POR VEÍCULO NA BARRA LATERAL ---
        st.sidebar.markdown("---")
        st.sidebar.header("Filtros")
        
        # Pega a lista única de veículos cadastrados
        veiculos_unicos = df[col_veiculo].dropna().astype(str).unique()
        lista_veiculos = ["Todos os Veículos"] + sorted(list(veiculos_unicos))
        
        veiculo_selecionado = st.sidebar.selectbox("Filtrar por Veículo:", lista_veiculos)
        
        if veiculo_selecionado != "Todos os Veículos":
            df_filtrado = df[df[col_veiculo].astype(str) == veiculo_selecionado]
        else:
            df_filtrado = df
        
        # Métricas no topo
        total_gasto = df_filtrado['Valor_Limpo'].sum()
        total_fmt = f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total Gasto Somado", total_fmt)
        with col_m2:
            st.metric("Quantidade de Registros", len(df_filtrado))
            
        st.markdown("---")
        
        # Seção de Gráficos e Resumos
        st.subheader("📊 Análise Visual de Custos")
        
        col_g1, col_g2 = st.columns(2)
        
        # Agrupamento por Serviço
        g_servico = df_filtrado.groupby(df_filtrado[col_servico].astype(str))['Valor_Limpo'].sum().reset_index()
        g_servico.columns = ['Serviço', 'Valor (R$)']
        
        # Agrupamento por Veículo
        g_veiculo = df_filtrado.groupby(df_filtrado[col_veiculo].astype(str))['Valor_Limpo'].sum().reset_index()
        g_veiculo.columns = ['Veículo', 'Valor (R$)']
        
        with col_g1:
            st.markdown("*Gasto Total por Serviço (R$)*")
            st.bar_chart(data=g_servico, x='Serviço', y='Valor (R$)')
            st.dataframe(g_servico, use_container_width=True, hide_index=True)
            
        with col_g2:
            st.markdown("*Gasto Total por Veículo (R$)*")
            st.bar_chart(data=g_veiculo, x='Veículo', y='Valor (R$)')
            st.dataframe(g_veiculo, use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.subheader("📋 Tabela Detalhada de Registros")
        
        df_display = df_filtrado.drop(columns=['Valor_Limpo'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
            
    else:
        st.info("Nenhuma manutenção encontrada na planilha ou a planilha está vazia.")
            



