import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir caminho do arquivo
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Lista de planilhas
planilhas = ["Jan - 2025", "Fev - 2025"]

# Identificar o mês atual
mes_atual = datetime.now().strftime("%b - %Y")
mes_atual = next((m for m in planilhas if mes_atual in m), None)

# Carregar os dados
df_list = []
for sheet in planilhas:
    temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
    temp_df["Mês"] = sheet  # Adiciona a coluna do mês
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
df.dropna(inplace=True)

# Converter tipos
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Calcular indicadores
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()
media_consumo = df["Consumo"].mean()

ultima_leitura = df.iloc[-1]["Leitura"]
data_ultima_leitura = df.iloc[-1]["Data"] + pd.Timedelta(days=1)
consumo_ultima_leitura = df.iloc[-1]["Consumo"]

data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].values[0]

# Calcular a data do menor consumo ignorando domingos
df_menor_consumo = df[(df["Consumo"] == menor_consumo) & (df["Data"].dt.weekday != 6)]
data_menor_consumo = df_menor_consumo["Data"].values[0] if not df_menor_consumo.empty else "Sem dados"

# Calcular consumo do mês corretamente
if mes_atual:
    df_mes_atual = df[df["Mês"] == mes_atual]
    consumo_mes_atual = df_mes_atual[df_mes_atual["Consumo"] > 0]["Consumo"].sum()
else:
    consumo_mes_atual = 0

# Criar layout
st.title("Consumo de Água - Simões Filho")
st.subheader("Indicadores", divider="blue")

# Criar três quadrados azuis para os principais indicadores
st.markdown("""
    <div style="display: flex; justify-content: center; gap: 20px;">
        <div style="background-color:#007bff; padding: 15px; border-radius:10px; text-align:center; color: white; font-weight: bold;">
            Última Leitura:<br> {} m³
        </div>
        <div style="background-color:#007bff; padding: 15px; border-radius:10px; text-align:center; color: white; font-weight: bold;">
            Data da Última Leitura:<br> {}
        </div>
        <div style="background-color:#007bff; padding: 15px; border-radius:10px; text-align:center; color: white; font-weight: bold;">
            Consumo Atual:<br> {} m³
        </div>
    </div>
    """.format(ultima_leitura, data_ultima_leitura.strftime('%d/%m/%Y'), consumo_ultima_leitura), unsafe_allow_html=True)

# Consumo do mês
st.markdown("### Consumo do Mês Atual")
st.markdown(
    f"""
    <div style="background-color:#4CAF50; padding:20px; border-radius:10px; text-align:center; color:white; font-size:18px;">
        {mes_atual}: {consumo_mes_atual} m³
    </div>
    """, unsafe_allow_html=True
)

# Exibir indicadores adicionais
st.subheader("Outros Indicadores", divider="blue")
col1, col2, col3 = st.columns(3)
col1.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
col1.metric("Dias com Consumo Zero", dias_consumo_zero)
col1.metric("Menor Consumo", f"{menor_consumo} m³")
col1.metric("Data do Menor Consumo", pd.to_datetime(data_menor_consumo).strftime('%d/%m/%Y') if data_menor_consumo != "Sem dados" else "Sem dados")

col2.metric("Maior Consumo", f"{maior_consumo} m³")
col2.metric("Data do Maior Consumo", pd.to_datetime(data_maior_consumo).strftime('%d/%m/%Y'))

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
st.plotly_chart(fig)
