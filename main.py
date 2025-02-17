import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dados
caminho_arquivo = "LEITURA DE HIDROMETROS AVON SIMÕES FILHO 2024.xlsx"
df = pd.read_excel(caminho_arquivo, sheet_name="Jan-2024", header=1)
df.columns = ["Data", "Leitura", "Consumo", "Status"]
df.dropna(inplace=True)

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Calcular indicadores
media_consumo = df["Consumo"].mean()
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df["Consumo"].min()

# Criar layout do dashboard
st.title("Dashboard de Consumo de Água")
st.subheader("Indicadores")
st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
st.metric("Dias com Consumo Zero", dias_consumo_zero)
st.metric("Maior Consumo", f"{maior_consumo} m³")
st.metric("Menor Consumo", f"{menor_consumo} m³")

# Criar gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", title="Consumo Diário de Água", markers=True)
st.plotly_chart(fig)

# Rodar o Streamlit
# No terminal, execute: streamlit run nome_do_arquivo.py