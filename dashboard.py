import streamlit as st
import io
import sqlite3
import pandas as pd
import plotly.express as px
import xlsxwriter
import os
from datetime import datetime, timedelta
from PIL import Image


#st.image("natura_logo.png", width=200)
# Definir caminho do arquivo
st.set_page_config(page_title="Dashboard Hidrometros", layout="wide")
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Gerar a lista de meses do ano
anos = ["2024", "2025"]
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
        temp_df["Mês"] = sheet
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

# Criar um seletor de mês baseado no ano escolhido
meses_disponiveis = [m.split(" - ")[0] for m in planilhas if ano_selecionado in m]
mes_selecionado = st.sidebar.selectbox("Selecione o Mês", meses_disponiveis)

# Filtrar os dados pelo mês selecionado
df = df[df["Mês"] == f"{mes_selecionado} - {ano_selecionado}"]

# Calcula o consumo total do mês ignorando valores negativos
consumo_total_atual = df.loc[df["Consumo"] > 0, "Consumo"].sum()

# Criar botão para baixar a planilha do mês
if not df.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Consumo", index=False)
    st.download_button(
        label="Baixar Planilha do Mês",
        data=output.getvalue(),
        file_name=f"Consumo_{mes_selecionado}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Criar botão para baixar a planilha geral
output_total = io.BytesIO()
with pd.ExcelWriter(output_total, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Geral", index=False)

st.download_button(
    label="Baixar Planilha Geral",
    data=output_total.getvalue(),
    file_name="Consumo_Geral.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Calcular indicadores
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()
media_consumo = df["Consumo"].mean()

data_ultima_leitura = (df.iloc[-1]["Data"] + timedelta(days=0)).strftime('%d/%m/%Y') if not df.empty else "Sem dados"
data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].min().strftime('%d/%m/%Y') if not df.empty else "Sem dados"
data_menor_consumo = df[df["Consumo"] == menor_consumo]["Data"].min().strftime('%d/%m/%Y') if not df.empty else "Sem dados"

if ano_selecionado == "2024":
    consumo_total_atual = df["Consumo"].sum()
    ultima_leitura_dezembro = df[df["Mês"] == "Dez - 2024"]
    if not ultima_leitura_dezembro.empty:
        data_ultima_leitura = (ultima_leitura_dezembro.iloc[-1]["Data"] + timedelta(days=0)).strftime('%d/%m/%Y')

# Criar layout
st.image("natura_logo.png", width=200)
st.markdown(
    """
    <div style='position: relative; text-align: center;'>
        <h1 style='color: #004B8D;'>Consumo de Água - Simões Filho</h1>
    </div>
    """, unsafe_allow_html=True
)

st.markdown("---")

# Criar uma linha com as métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Última Leitura", f"{df.iloc[-1]['Consumo']} m³" if not df.empty else "Sem dados")
with col2:
    st.metric("Data da Última Leitura", data_ultima_leitura)
with col3:
    st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
with col4:
    st.metric("Consumo Total Atual", f"{consumo_total_atual} m³")

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

# Criar gráfico de barras interativo
fig = px.bar(
    df, x="Data", y="Consumo", 
    title=f"Consumo Diário - {mes_selecionado}/{ano_selecionado}",
    labels={"Data": "Data", "Consumo": "Consumo de Água (m³)"},
    text_auto=True,  # Exibe os valores automaticamente
    color="Consumo",  # Deixa o gráfico colorido conforme os valores
    color_continuous_scale="Blues"  # Escolhe um gradiente de cores
)

# Melhorar interatividade e visual
fig.update_traces(
    textfont_size=12, textposition="outside",
    marker=dict(line=dict(width=0.5, color="black"))  # Bordas finas para destacar barras
)

fig.update_layout(
    xaxis_title="Data",
    yaxis_title="Consumo de Água (m³)",
    xaxis=dict(tickformat="%d/%m"),  # Formato de data simplificado
    hovermode="x unified",  # Tooltip dinâmica ao passar o mouse
    margin=dict(l=40, r=40, t=40, b=40),  # Ajuste de margens
    plot_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
    paper_bgcolor="rgba(0,0,0,0)",  # Fundo transparente
    coloraxis_showscale=False  # Oculta a barra de cores
)

# Exibir gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)
