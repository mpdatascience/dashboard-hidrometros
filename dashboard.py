# Cálculos para 2024
if ano_selecionado == "2024":
    # Somar o consumo de todos os meses de 2024
    consumo_total_2024 = df[df["Mês"].str.contains("2024")]["Consumo"].sum()
    # Calcular a média diária de consumo (considerando 365 dias no ano)
    media_diaria_2024 = consumo_total_2024 / 365 if consumo_total_2024 else "Sem Dados"
    
    # Calcular o mês de maior e menor consumo
    mes_maior_consumo = df[df["Consumo"] == maior_consumo]["Mês"].values[0] if not df[df["Consumo"] == maior_consumo].empty else "Sem dados"
    mes_menor_consumo = df[df["Consumo"] == menor_consumo]["Mês"].values[0] if not df[df["Consumo"] == menor_consumo].empty else "Sem dados"
    
    ultima_leitura = consumo_total_2024
    data_ultima_leitura = f"{media_diaria_2024:.2f} m³" if isinstance(media_diaria_2024, (int, float)) else "Sem Dados"
else:
    ultima_leitura = df.iloc[-1]["Leitura"] if not df.empty else "Sem Dados"
    data_ultima_leitura = (df.iloc[-1]["Data"] + timedelta(days=1)).strftime('%d/%m/%Y') if not df.empty else "Sem Dados"
    
    # Para 2025, a média diária de consumo é calculada pela média de todos os consumos até agora
    total_consumo_2025 = df["Consumo"].sum()  # Somando o total de consumo
    dias_registrados_2025 = len(df)  # Número de registros de consumo
    media_diaria_2025 = total_consumo_2025 / dias_registrados_2025 if dias_registrados_2025 > 0 else "Sem Dados"

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
        st.metric("Consumo do Ano", f"{consumo_total_2024} m³")
    else:
        st.metric("Última Leitura", f"{ultima_leitura} m³")
with col2:
    if ano_selecionado == "2024":
        st.metric("Média Diária de Consumo", f"{media_diaria_2024:.2f} m³")
    else:
        st.metric("Média Diária de Consumo", f"{media_diaria_2025:.2f} m³")
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
