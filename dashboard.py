import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir caminho do arquivo
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Lista de planilhas
planilhas = ["Jan - 2025", "Fev - 2025"]

# Nome do mês atual
mes_atual = datetime.now().strftime("%b - %Y")
mes_atual = next((m for m in planilhas if mes_atual in m), None)

# Lendo as planilhas e combinando os dados
df_list = []
for sheet in planilhas:
    temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
    temp_df["Mês"] = sheet
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
df.dropna(inplace=True)

# Conversões de tipos
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Calcular indicadores gerais
media_consumo = df["Consumo"].mean()
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()

data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].values[0]

# Última leitura registrada
ultima_leitura = df.iloc[-1]["Leitura"]
data_ultima_leitura = df.iloc[-1]["Data"].strftime('%d/%m/%Y')
consumo_ultima_leitura = df.iloc[-1]["Consumo"]

# Calcular consumo do mês atual considerando apenas valores positivos
if mes_atual:
    temp_mes_df = pd.read_excel(caminho_arquivo, sheet_name=mes_atual, usecols="C", skiprows=2, nrows=31)
    consumo_mes_atual = temp_mes_df[temp_mes_df["Consumo"] >= 0]["Consumo"].sum()
else:
    consumo_mes_atual = 0

# Criar layout do dashboard
st.title("Consumo de Água - Simões Filho", anchor="center")
st.subheader("Indicadores", divider="blue")

# Exibir métricas principais
col1, col2, col3 = st.columns(3)
col1.markdown(
    f"""
    <div style="background-color:#007BFF; padding:15px; border-radius:10px; text-align:center; color:white;">
        <strong>Última Leitura:</strong><br> {ultima_leitura} m³
    </div>
    """, unsafe_allow_html=True)
col2.markdown(
    f"""
    <div style="background-color:#007BFF; padding:15px; border-radius:10px; text-align:center; color:white;">
        <strong>Data da Última Leitura:</strong><br> {data_ultima_leitura}
    </div>
    """, unsafe_allow_html=True)
col3.markdown(
    f"""
    <div style="background-color:#007BFF; padding:15px; border-radius:10px; text-align:center; color:white;">
        <strong>Consumo Atual:</strong><br> {consumo_ultima_leitura} m³
    </div>
    """, unsafe_allow_html=True)

# Indicadores gerais
st.markdown("### Indicadores Gerais")
col4, col5, col6 = st.columns(3)
col4.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
col5.metric("Dias com Consumo Zero", dias_consumo_zero)
col6.metric("Menor Consumo", f"{menor_consumo} m³")

col7, col8 = st.columns(2)
col7.metric("Maior Consumo", f"{maior_consumo} m³")
col8.metric("Data do Maior Consumo", pd.to_datetime(data_maior_consumo).strftime('%d/%m/%Y'))

# Consumo do Mês Atual com destaque
st.markdown("### Consumo do Mês Atual")
st.markdown(
    f"""
    <div style="background-color:#4CAF50; padding:20px; border-radius:10px; text-align:center;">
        <h2 style="color:white;">{mes_atual}: {consumo_mes_atual:.2f} m³</h2>
    </div>
    """, unsafe_allow_html=True
)

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
st.plotly_chart(fig)
