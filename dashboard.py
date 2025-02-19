import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir configuração da página antes de qualquer outro comando Streamlit
st.set_page_config(page_title="Dashboard Hidrometros", layout="wide")

# Restante do código...


# Definir caminho do arquivo
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Gerar a lista de meses para os anos 2024 e 2025
anos = ["2024", "2025"]
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
planilhas = {ano: [f"{mes} - {ano}" for mes in meses] for ano in anos}

# Criar menu lateral para seleção de ano
st.sidebar.title("Menu")
ano_selecionado = st.sidebar.radio("Selecione o Ano", options=anos)

# Identificar o mês atual no ano selecionado
mes_atual = datetime.now().strftime("%b - %Y")
mes_atual = next((m for m in planilhas[ano_selecionado] if mes_atual in m), None)

# Carregar os dados
df_list = []
for sheet in planilhas[ano_selecionado]:
    try:
        temp_df = pd.read_excel(caminho_arquivo, sheet_name=sheet, header=1)
        temp_df["Mês"] = sheet  # Adiciona a coluna do mês
        df_list.append(temp_df)
    except ValueError:
        print(f"A planilha {sheet} não foi encontrada no arquivo.")

if df_list:
    df = pd.concat(df_list, ignore_index=True)
    df.columns = ["Data", "Leitura", "Consumo", "Status", "Mês"]
    df.dropna(inplace=True)

    # Converter tipos
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Leitura"] = pd.to_numeric(df["Leitura"], errors="coerce")
    df["Consumo"] = pd.to_numeric(df["Consumo"], errors="coerce")
    
    # Calcular indicadores
    consumo_mes_atual = df[df["Mês"] == mes_atual]["Consumo"].sum()
    media_consumo = df["Consumo"].mean()
    dias_consumo_zero = (df["Consumo"] == 0).sum()
    maior_consumo = df["Consumo"].max()
    menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()
else:
    st.error("Não há dados disponíveis para este ano.")
    st.stop()

# Criar layout
st.set_page_config(page_title="Dashboard Hidrometros", layout="wide")
st.image("natura_logo.png", width=200)
st.title(f"Consumo de Água - Simões Filho ({ano_selecionado})")
st.markdown("---")

# Exibir indicadores
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Consumo do Mês Atual", f"{consumo_mes_atual:.2f} m³")
    st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
with col2:
    st.metric("Dias com Consumo Zero", dias_consumo_zero)
    st.metric("Menor Consumo", f"{menor_consumo} m³")
with col3:
    st.metric("Maior Consumo", f"{maior_consumo} m³")

st.markdown("---")

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#004B8D", "#008CBA", "#00A5CF", "#4CAF50"])
st.plotly_chart(fig)
