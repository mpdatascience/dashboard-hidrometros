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

# Concatenar todos os dataframes em um único
df = pd.concat(df_list, ignore_index=True)
df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
df.dropna(inplace=True)

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")

# Corrigir valores negativos no consumo
df["Consumo"] = df["Consumo"].apply(lambda x: max(x, 0))

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

# Ler o consumo total do mês diretamente da célula D34 e corrigir possíveis valores negativos
if mes_atual:
    consumo_mes_atual = pd.read_excel(caminho_arquivo, sheet_name=mes_atual, usecols="D", skiprows=33, nrows=1).iloc[0, 0]
    consumo_mes_atual = max(consumo_mes_atual, 0)
else:
    consumo_mes_atual = 0

# Criar layout do dashboard
st.title("Consumo de Água - Simões Filho", anchor="center")
st.subheader("Indicadores", divider="blue")

# Exibir informações principais em três quadrados pequenos AZUIS
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
    </style>
    """, unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between;">
        <div class="small-box">Última Leitura: {ultima_leitura} m³</div>
        <div class="small-box">Data da Última Leitura: {data_ultima_leitura.strftime('%d/%m/%Y')}</div>
        <div class="small-box">Consumo Atual: {consumo_ultima_leitura} m³</div>
    </div>
    """, unsafe_allow_html=True
)

# Exibir outras métricas
col1, col2 = st.columns(2)
col1.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
col1.metric("Dias com Consumo Zero", dias_consumo_zero)
col1.metric("Menor Consumo", f"{menor_consumo} m³")

col2.metric("Maior Consumo", f"{maior_consumo} m³")
col2.metric("Data do Maior Consumo", pd.to_datetime(data_maior_consumo).strftime('%d/%m/%Y'))

# Adicionar um card azul de destaque para o consumo do mês atual
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
              color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])  # Exemplo de cores
st.plotly_chart(fig)

# Rodar o Streamlit
# No terminal, execute: streamlit run nome_do_arquivo.py
