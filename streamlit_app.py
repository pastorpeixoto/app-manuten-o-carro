import pandas as pd
import streamlit as st
import sqlite3
import os

# Configuração da página
st.set_page_config(page_title="Manutenção de Veículos", page_icon="🏋️", layout="centered")

st.title("🚗 Controle de Manutenção de Veículos")

# Conexão com o banco de dados local (SQLite)
DB_FILE = "manutencoes.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(""" 
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT,
            placa TEXT,
            servico TEXT,
            km INTEGER,
            data TEXT,
            observacoes TEXT
        )
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
    conn = sqlite3.connect('salvcar.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manutencoes (data, veiculo, servico, valor, observacoes)
        VALUES (?, ?, ?, ?, ?)
    """, (data, veiculo, servico, valor, observacoes))
    conn.commit()
    conn.close()
# Inicializa o banco de dados
init_db()

# Formulário de Cadastro
st.header("📋 Cadastrar Nova Manutenção")

with st.form("form_manutencao", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        modelo = st.text_input("Modelo do Carro")
        placa = st.text_input("Placa do Carro")
        servico = st.selectbox("Tipo de Serviço", [
            "Troca de Óleo", 
            "Alinhamento e Balanceamento", 
            "Troca de Pastilhas de Freio", 
            "Revisão Geral", 
            "Troca de Pneus",
            "Outro"
        ])
    
    with col2:
        km = st.number_input("Quilometragem Atual (KM)", min_value=0, step=1000)
        data = st.date_input("Data da Manutenção")
        obs = st.text_area("Observações", placeholder="Ex: Marcas do filtro trocado, valor, etc.")
    
    submitted = st.form_submit_button("Salvar Manutenção")
    
    if submitted:
        if not modelo or not placa:
            st.warning("Por favor, preencha pelo menos o Modelo e a Placa.")
        else:
            salvar_dados(modelo, placa, servico, km, data, obs)
            st.success("Manutenção cadastrada com sucesso!")

st.divider()

# Exibição dos Dados e Download
st.header("📊 Historico de Manutenções")

df = carregar_dados()

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Botão para baixar em CSV / Excel
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório em Excel (CSV)",
        data=csv,
        file_name="manutencoes_veiculos.csv",
        mime="text/csv"
    )
else:
    st.info("Nenhuma manutenção cadastrada ainda.")
conn.close()
