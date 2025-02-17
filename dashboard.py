import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Definir caminho do arquivo
caminho_arquivo = os.path.join(os.path.dirname(__file__), "LEITURA DE HIDROMETROS.xlsx")

# Gerar a lista de meses do ano
anos = [str(datetime.now().year)]  # Você pode modificar para incluir vários anos
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

# Ler o consumo total do mês da guia "Atual" célula A1
try:
    xls = pd.ExcelFile(caminho_arquivo)
    if "Atual" in xls.sheet_names:
        df_atual = pd.read_excel(caminho_arquivo, sheet_name="Atual", usecols="A", nrows=1)
        consumo_mes_atual = df_atual.iloc[0, 0] if not df_atual.empty and pd.notna(df_atual.iloc[0, 0]) else "Dados indisponíveis"
    else:
        consumo_mes_atual = "Planilha 'Atual' não encontrada"
except Exception as e:
    consumo_mes_atual = "Erro ao carregar"
    print(f"Erro ao ler consumo do mês: {e}")

# Criar layout
st.set_page_config(page_title="Dashboard Hidrometros", layout="wide")
st.image("natura_logo.png", width=200)
st.title("Consumo de Água - Simões Filho")

st.markdown("---")

# Criar uma linha com o logo e as métricas
col1, col2, col3, col4 = st.columns([1, 1, 1, 2])  # Aumentar o número de colunas
with col1:
    st.metric("Última Leitura", f"{consumo_ultima_leitura if consumo_ultima_leitura is not None else 'Sem Dados'} m³")
with col2:
    st.metric("Data da Última Leitura", f"{data_ultima_leitura.strftime('%d/%m/%Y') if data_ultima_leitura else 'Sem Dados'}")
with col3:
    st.metric("Consumo Atual", f"{consumo_ultima_leitura if consumo_ultima_leitura is not None else 'Sem Dados'} m³")
with col4:
    st.markdown("### Consumo do Mês Atual", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="background-color:#004B8D; padding:10px; border-radius:10px; text-align:center; color:white; font-size:16px; width:200px; margin:auto;">
            {mes_atual}: {consumo_mes_atual if consumo_mes_atual is not None else 'Dados indisponíveis'} m³
        </div>
        """, unsafe_allow_html=True
    )

st.markdown("---")

# Exibir indicadores adicionais
st.subheader("Outros Indicadores")
col1, col2 = st.columns(2)
with col1:
    st.metric("Média de Consumo Diário", f"{media_consumo:.2f} m³")
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
