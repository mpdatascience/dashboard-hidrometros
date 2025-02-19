import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Definir caminho do arquivo
st.set_page_config(page_title="Dashboard Hidrometros", layout="wide")
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Gerar a lista de meses do ano
anos = ["2024", "2025"]  # Incluir dados de 2024 e 2025
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
planilhas = [f"{mes} - {ano}" for ano in anos for mes in meses]

# Identificar o mês atual
mes_atual = datetime.now().strftime("%b - %Y")
mes_atual = next((m for m in planilhas if mes_atual in m), None)

# Carregar os dados
df_list = []
for sheet in planilhas:
    try:
        temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
        temp_df["Mês"] = sheet  # Adiciona a coluna do mês
        df_list.append(temp_df)
    except ValueError:
        print(f"A planilha {sheet} não foi encontrada no arquivo.")

df = pd.concat(df_list, ignore_index=True)
df.dropna(inplace=True)

# Renomear colunas
colunas_esperadas = ["Data", "Leitura", "Consumo", "Status", "Mês"]
if len(df.columns) == len(colunas_esperadas):
    df.columns = colunas_esperadas

# Converter tipos
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Criar um seletor de ano
ano_selecionado = st.sidebar.radio("Selecione o Ano", ["2024", "2025"])
df = df[df["Mês"].str.contains(ano_selecionado)]

# Criar um seletor de comparação de meses
st.sidebar.subheader("Comparação de Consumo")
mes1 = st.sidebar.selectbox("Selecione o primeiro mês", meses)
mes2 = st.sidebar.selectbox("Selecione o segundo mês", meses)

df_mes1 = df[df["Mês"].str.contains(mes1)]
df_mes2 = df[df["Mês"].str.contains(mes2)]

# Calcular indicadores
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()
media_consumo = df["Consumo"].mean()

ultima_leitura = df.iloc[-1]["Leitura"] if not df.empty else "Sem Dados"
consumo_atual = df.iloc[-1]["Consumo"] if not df.empty else "Sem Dados"

# Consumo total do mês selecionado a partir da guia "Atual"
try:
    df_atual = pd.read_excel(caminho_arquivo, sheet_name="Atual", header=None)
    consumo_total_mes = df_atual.iloc[0, 1] if not df_atual.empty else "Sem Dados"
except Exception as e:
    consumo_total_mes = "Sem Dados"

data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].values
if len(data_maior_consumo) > 0:
    data_maior_consumo = pd.to_datetime(data_maior_consumo[0]).strftime('%d/%m/%Y')
else:
    data_maior_consumo = "Sem dados"

df_menor_consumo = df[(df["Consumo"] == menor_consumo) & (df["Data"].dt.weekday != 6)]
data_menor_consumo = df_menor_consumo["Data"].values
if len(data_menor_consumo) > 0:
    data_menor_consumo = pd.to_datetime(data_menor_consumo[0]).strftime('%d/%m/%Y')
else:
    data_menor_consumo = "Sem dados"

# Criar layout
st.image("natura_logo.png", width=200)
st.markdown(
    f"""
    <div style='position: relative; text-align: center;'>
        <img src="Embasa.png" style="position: absolute; width: 100%; opacity: 0.2; z-index: -1;">
        <h1 style='color: #004B8D;'>Consumo de Água - Simões Filho</h1>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("---")

# Criar uma linha com o logo e as métricas
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("Última Leitura", f"{ultima_leitura} m³")
with col2:
    st.metric("Consumo Atual", f"{consumo_atual} m³")
with col3:
    st.metric("Consumo Total do Mês", f"{consumo_total_mes} m³")

st.markdown("---")

# Exibir indicadores adicionais
st.subheader("Outros Indicadores")
col1, col2 = st.columns(2)
with col1:
    st.metric("Dias com Consumo Zero", dias_consumo_zero)
    st.metric("Menor Consumo", f"{menor_consumo} m³")
    st.metric("Data do Menor Consumo", data_menor_consumo)

with col2:
    st.metric("Maior Consumo", f"{maior_consumo} m³")
    st.metric("Data do Maior Consumo", data_maior_consumo)

st.markdown("---")

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#004B8D", "#008CBA", "#00A5CF", "#4CAF50"])
st.plotly_chart(fig)
