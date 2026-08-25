import pandas as pd
import streamlit as st
import sqlite3
import os

st.set_page_config(page_title="Salvcar - Gestão de Manutenções", page_icon="🚗", layout="wide")

def criar_tabela():
    conn = sqlite3.connect('salvcar.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            veiculo TEXT,
            servico TEXT,
            valor REAL,
            observacoes TEXT
        )
    """)
    conn.commit()
    conn.close()

criar_tabela()

def inserir_manutencao(data, veiculo, servico, valor, observacoes):
    conn = sqlite3.connect('salvcar.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manutencoes (data, veiculo, servico, valor, observacoes)
        VALUES (?, ?, ?, ?, ?)
    """, (data, veiculo, servico, valor, observacoes))
    conn.commit()
    conn.close()

def listar_manutencoes():
    conn = sqlite3.connect('salvcar.db')
    df = pd.read_sql_query("SELECT * FROM manutencoes", conn)
    conn.close()
    return df

st.title("🚗 Salvcar - Controle de Manutenções")

st.sidebar.header("Menu de Navegação")
opcao = st.sidebar.radio("Selecione uma opção:", ["Cadastrar Manutenção", "Ver Relatório"])

if opcao == "Cadastrar Manutenção":
    st.header("Cadastrar Nova Manutenção")
    
    with st.form("form_manutencao"):
        data = st.date_input("Data do Serviço")
        veiculo = st.text_input("Placa / Modelo do Veículo")
        servico = st.text_input("Descrição do Serviço")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        observacoes = st.text_area("Observações")
        
        submetido = st.form_submit_button("Salvar Manutenção")
        
        if submetido:
            if veiculo and servico:
                inserir_manutencao(str(data), veiculo, servico, valor, observacoes)
                st.success("Manutenção cadastrada com sucesso!")
            else:
                st.error("Por favor, preencha os campos obrigatórios (Veículo e Serviço).")

elif opcao == "Ver Relatório":
    st.header("Relatório de Manutenções")
    
    df = listar_manutencoes()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        total_gasto = df["valor"].sum()
        st.metric("Total Gasto com Manutenções", f"R$ {total_gasto:,.2f}")
    else:
        st.info("Nenhuma manutenção cadastrada até o momento.")
