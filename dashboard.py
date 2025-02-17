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
mes_atual = datetime.now().strftime("%b - %Y")  # Exemplo: "Fev - 2025"
mes_atual = next((m for m in planilhas if mes_atual in m), None)  # Verifica se o mês existe na planilha

# Lendo todas as planilhas e combinando os dados
df_list = []
for sheet in planilhas:
    temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
    temp_df["Mês"] = sheet  # Adicionar uma coluna para identificar o mês corretamente
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
df.dropna(inplace=True)

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Calcular indicadores gerais
media_consumo = df["Consumo"].mean()
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()  # Menor consumo diferente de zero

# Última leitura registrada
ultima_leitura = df.iloc[-1]["Leitura"]
data_ultima_leitura = df.iloc[-1]["Data"] + pd.Timedelta(days=1)
consumo_ultima_leitura = df.iloc[-1]["Consumo"]

# Data do maior consumo
data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].values[0]

# Calcular o consumo do mês atual somando apenas valores positivos
if mes_atual:
    df_mes = pd.read_excel(caminho_arquivo, sheet_name=mes_atual, usecols="C", skiprows=2, nrows=31)
    df_mes.columns = ["Consumo"]
    consumo_mes_atual = df_mes[df_mes["Consumo"] >= 0]["Consumo"].sum()
else:
    consumo_mes_atual = 0

# Criar layout do dashboard
st.title("Consumo de Água - Simões Filho", anchor="center")
st.subheader("Indicadores", divider="blue")

# Exibir informações principais com caixas azuis centralizadas
st.markdown("""
    <style>
        .metric-box {
            background-color: #007BFF;
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
col4.markdown(f'<div class="metric-box">Última Leitura:<br> {ultima_leitura} m³</div>', unsafe_allow_html=True)
col5.markdown(f'<div class="metric-box">Data da Última Leitura:<br> {data_ultima_leitura.strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
col6.markdown(f'<div class="metric-box">Consumo Atual:<br> {consumo_ultima_leitura} m³</div>', unsafe_allow_html=True)

st.markdown("### Consumo do Mês Atual")
st.markdown(
    f"""
    <div style="background-color:#4CAF50; padding:20px; border-radius:10px; text-align:center;">
        <h2 style="color:white;">{mes_atual}: {consumo_mes_atual} m³</h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Criar gráfico de consumo diário com nova paleta de cores
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
st.plotly_chart(fig)
