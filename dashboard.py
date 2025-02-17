import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir caminho do arquivo (no mesmo diretório do script)
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Lista de planilhas a serem lidas
planilhas = ["Jan - 2025", "Fev - 2025"]

# Definir nome correto do mês atual com base nos dados disponíveis
mes_atual = datetime.now().strftime("%b - %Y")
mes_atual = next((m for m in planilhas if mes_atual in m), None)

# Lendo todas as planilhas e combinando os dados
df_list = []
for sheet in planilhas:
    temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
    temp_df["Mês"] = sheet
    df_list.append(temp_df)

# Concatenar todos os dataframes
df = pd.concat(df_list, ignore_index=True)
df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
df.dropna(inplace=True)

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Corrigir valores negativos no consumo
df["Consumo"] = df["Consumo"].apply(lambda x: max(x, 0))

# Última leitura registrada
ultima_leitura = df.iloc[-1]["Leitura"]
data_ultima_leitura = df.iloc[-1]["Data"] + pd.Timedelta(days=1)
consumo_ultima_leitura = df.iloc[-1]["Consumo"]

# Ler o consumo total do mês diretamente da célula D34
if mes_atual:
    consumo_mes_atual = pd.read_excel(caminho_arquivo, sheet_name=mes_atual, usecols="D", skiprows=33, nrows=1).iloc[0, 0]
    consumo_mes_atual = max(consumo_mes_atual, 0)
else:
    consumo_mes_atual = 0

# Criar layout do dashboard
st.title("Consumo de Água - Simões Filho", anchor="center")
st.subheader("Indicadores", divider="blue")

# Estilização para centralizar os textos
st.markdown(
    """
    <style>
    .small-box {
        display: inline-block;
        background-color: #007BFF;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-size: 18px;
        font-weight: bold;
        margin: 5px;
        width: 30%;
    }
    .box-title {
        font-size: 16px;
        font-weight: normal;
        display: block;
        margin-bottom: 5px;
    }
    .box-value {
        font-size: 22px;
        font-weight: bold;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True
)

# Criar os três quadrados pequenos azul com textos centralizados em duas linhas
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between;">
        <div class="small-box">
            <span class="box-title">Última Leitura:</span>
            <span class="box-value">{ultima_leitura} m³</span>
        </div>
        <div class="small-box">
            <span class="box-title">Data da Última Leitura:</span>
            <span class="box-value">{data_ultima_leitura.strftime('%d/%m/%Y')}</span>
        </div>
        <div class="small-box">
            <span class="box-title">Consumo Atual:</span>
            <span class="box-value">{consumo_ultima_leitura} m³</span>
        </div>
    </div>
    """, unsafe_allow_html=True
)

# Adicionar um card azul para o consumo do mês atual
st.markdown("### Consumo do Mês Atual")
st.markdown(
    f"""
    <div style="background-color:#007BFF; padding:20px; border-radius:10px; text-align:center;">
        <h2 style="color:white;">{mes_atual}: {consumo_mes_atual} m³</h2>
    </div>
    """, 
    unsafe_allow_html=True
)

# Criar gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
st.plotly_chart(fig)

# Rodar o Streamlit
# No terminal, execute: streamlit run nome_do_arquivo.py
