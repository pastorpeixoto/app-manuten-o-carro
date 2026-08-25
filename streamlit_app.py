import pandas as pd
import streamlit as st
import re

st.set_page_config(page_title="Salvcar - Gestão de Manutenções", page_icon="🚗", layout="wide")

# 1. LINK DA PLANILHA PUBLICADA NA WEB (formato CSV):
URL_PUBLICADA_CSV = r"""https://docs.google.com/spreadsheets/d/e/2PACX-1vTpcVNInjDdwUZ5E0tgRARfXn63Bx3zBRgFngEW4ffivNPv1bICkbeDfeO-74vUESMg93pj0-Ppyu9p/pub?output=csv"""

st.title("🚗 Salvcar - Controle de Manutenções")

def carregar_dados():
    if "SUA_URL_PUBLICADA" in URL_PUBLICADA_CSV:
        st.warning("Cole o link gerado em 'Publicar na web' na linha 8 do seu código no GitHub.")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(URL_PUBLICADA_CSV)
        return df
    except Exception as e:
        st.error("Não foi possível carregar a planilha. Verifique se o link publicado na web foi copiado corretamente.")
        return pd.DataFrame()

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
    st.header("Relatório de Manutenções (Google Sheets)")
    
    df = carregar_dados()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        colunas_disponiveis = list(df.columns)
        
        # Tenta identificar automaticamente a coluna de valores
        coluna_valor_padrao = next(
            (col for col in colunas_disponiveis if any(k in str(col).lower() for k in ["valor", "preco", "preço", "custo", "r$", "total", "gasto"])), 
            colunas_disponiveis[-1]
        )
        
        st.markdown("---")
        col_selecionada = st.selectbox(
            "Selecione a coluna que contém os Valores (R$):", 
            colunas_disponiveis, 
            index=colunas_disponiveis.index(coluna_valor_padrao)
        )
        
        def limpar_valor_extremo(val):
            if pd.isna(val):
                return 0.0
            
            # Converte tudo para texto e remove letras/símbolos mantendo apenas digitos, pontos e virgulas
            s = str(val).strip()
            # Se for número puro (int ou float)
            if isinstance(val, (int, float)):
                return float(val)
                
            # Remove R$, espaços e caracteres não numéricos
            s = re.sub(r"[^\d.,]", "", s)
            
            if not s:
                return 0.0
            
            # Se tem ponto e vírgula (ex: 1.500,50) -> remove ponto, troca virgula por ponto
            if "." in s and "," in s:
                s = s.replace(".", "").replace(",", ".")
            # Se tem apenas vírgula (ex: 1500,50 ou 15,00)
            elif "," in s:
                s = s.replace(",", ".")
            # Se tem múltiplos pontos de milhar sem vírgula (ex: 1.500.000)
            elif s.count(".") > 1:
                s = s.replace(".", "")
                
            try:
                return float(s)
            except ValueError:
                return 0.0

        valores_convertidos = df[col_selecionada].apply(limpar_valor_extremo)
        total_gasto = valores_convertidos.sum()
        
        total_fmt = f"R$ {total_gasto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total Gasto Somado", total_fmt)
        with col_m2:
            st.metric("Quantidade de Registros", len(df))
            
    else:
        st.info("Nenhuma manutenção encontrada na planilha ou a planilha está vazia.")


