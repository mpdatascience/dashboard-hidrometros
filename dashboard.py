import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

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

# Calcular indicadores
dias_consumo_zero = (df["Consumo"] == 0).sum()
maior_consumo = df["Consumo"].max()
menor_consumo = df[df["Consumo"] > 0]["Consumo"].min()
media_consumo = df["Consumo"].mean()

if ano_selecionado == "2025":
    ultima_leitura = df.iloc[-1]["Leitura"]
    data_ultima_leitura = df.iloc[-1]["Data"] + pd.Timedelta(days=1)
    consumo_ultima_leitura = df.iloc[-1]["Consumo"]
else:
    consumo_ultima_leitura = df["Consumo"].sum()
    data_ultima_leitura = "Total 2024"
    media_consumo = df["Consumo"].mean()

data_maior_consumo = df[df["Consumo"] == maior_consumo]["Data"].values[0]

df_menor_consumo = df[(df["Consumo"] == menor_consumo) & (df["Data"].dt.weekday != 6)]
data_menor_consumo = df_menor_consumo["Data"].values[0] if not df_menor_consumo.empty else "Sem dados"

# Criar layout
st.image("natura_logo.png", width=200)
st.title("Consumo de Água - Simões Filho")

st.markdown("---")

# Criar uma linha com o logo e as métricas
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.metric("Consumo Total" if ano_selecionado == "2024" else "Última Leitura", f"{consumo_ultima_leitura if consumo_ultima_leitura is not None else 'Sem Dados'} m³")
with col2:
    st.metric("Ano de Referência" if ano_selecionado == "2024" else "Data da Última Leitura", 
              data_ultima_leitura.strftime('%Y-%m-%d %H:%M:%S') if isinstance(data_ultima_leitura, pd.Timestamp) else str(data_ultima_leitura))
with col3:
    st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")

st.markdown("---")

# Exibir indicadores adicionais
st.subheader("Outros Indicadores")
col1, col2 = st.columns(2)
with col1:
    st.metric("Dias com Consumo Zero", dias_consumo_zero)
    st.metric("Menor Consumo", f"{menor_consumo} m³")
    st.metric("Data do Menor Consumo", pd.to_datetime(data_menor_consumo).strftime('%d/%m/%Y') if data_menor_consumo != "Sem dados" else "Sem dados")

with col2:
    st.metric("Maior Consumo", f"{maior_consumo} m³")
    st.metric("Data do Maior Consumo", pd.to_datetime(data_maior_consumo).strftime('%d/%m/%Y'))

st.markdown("---")

# Gráfico de consumo diário
fig = px.line(df, x="Data", y="Consumo", color="Mês", title="Consumo Diário de Água", markers=True,
              color_discrete_sequence=["#004B8D", "#008CBA", "#00A5CF", "#4CAF50"])
st.plotly_chart(fig)
