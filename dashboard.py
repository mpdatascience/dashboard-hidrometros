import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta

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

# Consumo total do ano de 2024 e média diária
if ano_selecionado == "2024":
    try:
        df_cd34 = pd.read_excel(caminho_arquivo, sheet_name="Atual", header=None)
        consumo_total_2024 = df_cd34.iloc[1, 1] if not df_cd34.empty else "Sem Dados"
        media_diaria_2024 = consumo_total_2024 / 12 if isinstance(consumo_total_2024, (int, float)) else "Sem Dados"
    except Exception as e:
        consumo_total_2024 = "Sem Dados"
        media_diaria_2024 = "Sem Dados"

    # Calcular o mês com menor consumo
    mes_maior_consumo = df[df["Consumo"] == maior_consumo]["Mês"].values[0] if not df[df["Consumo"] == maior_consumo].empty else "Sem dados"
    mes_menor_consumo = df[df["Consumo"] == menor_consumo]["Mês"].values[0] if not df[df["Consumo"] == menor_consumo].empty else "Sem dados"
    
    ultima_leitura = consumo_total_2024
    data_ultima_leitura = f"{media_diaria_2024:.2f} m³" if isinstance(media_diaria_2024, (int, float)) else "Sem Dados"
else:
    ultima_leitura = df.iloc[-1]["Leitura"] if not df.empty else "Sem Dados"
    data_ultima_leitura = (df.iloc[-1]["Data"] + timedelta(days=1)).strftime('%d/%m/%Y') if not df.empty else "Sem Dados"

consumo_atual = df.iloc[-1]["Consumo"] if not df.empty else "Sem Dados"
media_consumo = df["Consumo"].mean()

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
    if ano_selecionado == "2024":
        st.metric("Consumo do Ano", f"{ultima_leitura} m³")
    else:
        st.metric("Última Leitura", f"{ultima_leitura} m³")
with col2:
    if ano_selecionado == "2024":
        st.metric("Média Diária de Consumo", f"{media_diaria_2024:.2f} m³")
    else:
        st.metric("Data da Última Leitura", data_ultima_leitura)
with col3:
    st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")

st.markdown("---")

# Exibir indicadores adicionais
st.subheader("Outros Indicadores")
col1, col2 = st.columns(2)
with col1:
    st.metric("Dias com Consumo Zero", dias_consumo_zero)
    if ano_selecionado == "2024":
        st.metric(f"Menor Consumo ({mes_menor_consumo})", f"{menor_consumo} m³")
    else:
        st.metric(f"Último Consumo", f"{consumo_atual} m³")

with col2:
    if ano_selecionado == "2024":
        st.metric(f"Maior Consumo ({mes_maior_consumo})", f"{maior_consumo} m³")
    else:
        st.metric(f"Média de Consumo Diário", f"{media_consumo:.2f} m³")

st.markdown("---")

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#004B8D", "#008CBA", "#00A5CF", "#4CAF50"])
st.plotly_chart(fig)
