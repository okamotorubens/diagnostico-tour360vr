# ==========================================
# CÁLCULO DE DESLOCAMENTO E COMBUSTÍVEL
# ==========================================
st.subheader("🚗 Custos de Deslocamento e Logística")

with st.expander("Configurar Deslocamento (Distância e Combustível)", expanded=False):
    col_log1, col_log2, col_log3 = st.columns(3)
    
    with col_log1:
        distancia_ida_volta = st.number_input("Distância Total (Ida e Volta em km)", min_value=0.0, value=0.0, step=5.0)
    with col_log2:
        consumo_medio = st.number_input("Consumo Médio (km/L)", min_value=1.0, value=11.0, step=0.5) # Ex: média esperada para SUV
    with col_log3:
        preco_combustivel = st.number_input("Preço do Litro (R$)", min_value=0.0, value=5.89, step=0.10)
        
    pedagio_total = st.number_input("Valor Total de Pedágios (Ida e Volta R$)", min_value=0.0, value=0.0, step=5.0)

# Cálculo do custo de combustível
litros_gastos = distancia_ida_volta / consumo_medio if consumo_medio > 0 else 0
custo_combustivel = litros_gastos * preco_combustivel
custo_logistica_total = custo_combustivel + pedagio_total

if distancia_ida_volta > 0:
    st.info((f"**Resumo do Deslocamento:** Consumo estimado de {litros_gastos:.1f} litros "
             f"(R$ {custo_combustivel:.2f} de combustível) + R$ {pedagio_total:.2f} de pedágios. "
             f"**Total de Logística: R$ {custo_logistica_total:.2f}**"))
