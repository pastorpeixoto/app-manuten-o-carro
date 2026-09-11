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
        
        # Converte todo o DataFrame para string para facilitar a busca de palavras-chave
        df_str = df_bruto.astype(str)
        
        # Encontra a linha onde começa a tabela de pneus (se houver)
        mask_pneus = df_str.apply(lambda row: row.str.contains('pneu|quilometragem', case=False, na=False).any(), axis=1)
        indices_pneus = df_str[mask_pneus].index.tolist()
        
        if indices_pneus:
            corte_idx = indices_pneus[0]
            df_manut_raw = df_bruto.iloc[:corte_idx]
            df_pneus_raw = df_bruto.iloc[corte_idx:]
        else:
            df_manut_raw = df_bruto
            df_pneus_raw = pd.DataFrame()

        # --- PROCESSAMENTO DA TABELA DE MANUTENÇÃO ---
        try:
            # Encontra a linha que contém os cabeçalhos reais (Carro, Serviço, Data, Valor)
            mask_head = df_manut_raw.apply(lambda row: row.str.contains('carro|serviço|servico', case=False, na=False).any(), axis=1)
            head_idx = df_manut_raw[mask_head].index[0] if not df_manut_raw[mask_head].empty else 1
            
            df_manut = df_manut_raw.iloc[head_idx + 1:].copy()
            cols_manut = df_manut_raw.iloc[head_idx].values
            
            # Ajusta colunas se tiverem o tamanho correto
            if len(cols_manut) >= 4:
                df_manut = df_manut.iloc[:, :4]
                df_manut.columns = ["Carro", "Serviço realizado", "Data", "Valor"]
            else:
                df_manut.columns = [f"Col_{i}" for i in range(df_manut.shape[1])]
                
            df_manut = df_manut.dropna(how='all').fillna("")
            
            # Remove linhas que contenham títulos ou textos indesejados
            filtro_lixo = df_manut["Carro"].str.contains("carro|manutenção|controle|registro", case=False, na=False) | \
                          df_manut["Serviço realizado"].str.contains("serviço|servico|registro", case=False, na=False)
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
        
        # Exibe a Tabela de Manutenções limpa
        st.subheader("📋 Tabela Detalhada: Manutenção de Veículo")
        if not df_manut.empty:
            df_manut_display = df_manut.drop(columns=['Valor_Limpo'], errors='ignore')
            st.dataframe(df_manut_display, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado na tabela de manutenções.")

        st.markdown("---")
        
        # --- PROCESSAMENTO DA TABELA DE PNEUS ---
        st.subheader("🛞 Tabela Detalhada: Registro de Troca de Pneus")
        try:
            if not df_pneus_raw.empty:
                # Pula a linha do título "Registro de troca de pneus" e pega o cabeçalho real
                df_pneus = df_pneus_raw.iloc[1:].copy()
                df_pneus = df_pneus.dropna(how='all').fillna("")
                
                if len(df_pneus) > 1:
                    # Define cabeçalho e limpa linhas vazias/títulos duplicados
                    df_pneus.columns = ["Carro", "Data da troca", "Marca do pneu", "Quilometragem"] if df_pneus.shape[1] >= 4 else [f"Col_{i}" for i in range(df_pneus.shape[1])]
                    df_pneus = df_pneus[~df_pneus.iloc[:, 0].astype(str).str.contains("Carro|Pneus|Registro", case=False, na=False)]
                    st.dataframe(df_pneus, use_container_width=True, hide_index=True)
                else:
                    st.info("Aguardando preenchimento dos dados de troca de pneus.")
            else:
                st.info("Nenhum registro de pneu cadastrado nesta seção.")
        except Exception as e:
            st.info("Aguardando preenchimento dos dados de troca de pneus.")
            
    else:
        st.info("A planilha está vazia ou não pôde ser lida.")
