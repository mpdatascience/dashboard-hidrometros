import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir caminho do arquivo (no mesmo diretório do script)
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Lista de planilhas a serem lidas
planilhas = ["Jan - 2025", "Fev - 2025"]

# Lendo todas as planilhas e combinando os dados
df_list = []
for sheet in planilhas:
    temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
    temp_df["Mês"] = sheet  # Adicionar uma coluna para identificar o mês
    df_list.append(temp_df)

# Concatenar todos os dataframes em um único
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

# Filtro para somar o consumo do mês atual
mes_atual = datetime.now().strftime("%b - %Y")  # Exemplo: "Fev - 2025"
consumo_mes_atual = df[df["Mês"] == mes_atual]["Consumo"].sum()

# Criar layout do dashboard
st.title("Dashboard de Consumo de Água", anchor="center")
st.subheader("Indicadores", divider="blue")

# Exibir informações principais
st.markdown("### Informação Diária")
col4, col5, col6 = st.columns(3)
col4.metric("Última Leitura", f"{ultima_leitura} m³")
col5.metric("Data da Última Leitura", data_ultima_leitura.strftime('%d/%m/%Y'))
col6.metric("Consumo Atual", f"{consumo_ultima_leitura} m³")

col1, col2, col3 = st.columns(3)
col1.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
col1.metric("Dias com Consumo Zero", dias_consumo_zero)
col1.metric("Menor Consumo", f"{menor_consumo} m³")

col2.metric("Maior Consumo", f"{maior_consumo} m³")
col2.metric("Data do Maior Consumo", pd.to_datetime(data_maior_consumo).strftime('%d/%m/%Y'))

# Novo quadro com consumo do mês atual
st.markdown("### Consumo do Mês Atual")
st.metric(f"Consumo acumulado em {mes_atual}", f"{consumo_mes_atual} m³")

# Criar gráfico de consumo diário com nova paleta de cores
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])  # Exemplo de cores
st.plotly_chart(fig)

# Rodar o Streamlit
# No terminal, execute: streamlit run nome_do_arquivo.py
