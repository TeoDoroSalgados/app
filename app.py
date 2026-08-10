import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="TeoDoro's Salgados - Calculadora e Precificação",
    page_icon="🥟",
    layout="wide",
)

# Estilo visual moderno com tema escuro elegante
st.markdown("""
    <style>
    .main {
        background-color: #090d16;
        color: #f8fafc;
    }
    .stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #1f2937;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥟 TeoDoro's Salgados - Sistema de Custos & Precificação")
st.markdown("Ferramenta profissional para cálculo de fichas técnicas, custos estequiométricos, ponto de equilíbrio e rótulos ANVISA.")

# Sidebar para Insumos e Parâmetros
st.sidebar.header("🛠️ Parâmetros & Insumos")

st.sidebar.subheader("Preços dos Ingredientes (R$)")
chicken_price = st.sidebar.number_input("Filé de Peito de Frango (kg)", value=18.00, step=0.50)
flour_price = st.sidebar.number_input("Farinha de Trigo (kg)", value=5.00, step=0.50)
cabbage_price = st.sidebar.number_input("Cebola (kg)", value=4.50, step=0.50)
garlic_price = st.sidebar.number_input("Alho (kg)", value=15.00, step=0.50)
oil_price = st.sidebar.number_input("Óleo Vegetal (L)", value=9.00, step=0.50)
herbs_price = st.sidebar.number_input("Cheiro Verde (kg)", value=20.00, step=0.50)
salt_price = st.sidebar.number_input("Sal Refinado (kg)", value=3.50, step=0.50)

st.sidebar.subheader("Configuração da Produção")
coxinha_weight = st.sidebar.slider("Peso médio por coxinha (g)", min_value=10, max_value=50, value=20, step=5)
fixed_costs = st.sidebar.number_input("Custos Fixos Mensais (R$)", value=1500.00, step=100.00)
profit_margin = st.sidebar.slider("Margem de Lucro Desejada (%)", min_value=10, max_value=60, value=30, step=5)
opex_percent = st.sidebar.slider("Despesas Operacionais / Vendas (%)", min_value=5, max_value=30, value=20, step=5)

# --- CÁLCULOS ESTEQUIOMÉTRICOS ---
# Tempero (Base 3kg sal: 3kg cebola, 3kg alho, 1L óleo, 100g cheiro verde, 3kg sal = 10.1 kg)
cost_tempero_total = (3 * cabbage_price) + (3 * garlic_price) + (1 * oil_price) + (0.1 * herbs_price) + (3 * salt_price)
cost_tempero_per_kg = cost_tempero_total / 10.1

# Massa (200g tempero + 4kg farinha + 1.7kg água = 5.9 kg)
cost_massa_total = (0.2 * cost_tempero_per_kg) + (4 * flour_price)
cost_massa_per_kg = cost_massa_total / 5.9

# Produto Final (100g massa + 30g frango = 130g)
mass_ratio = 100 / 130
chicken_ratio = 30 / 130
cost_product_per_kg = (mass_ratio * cost_massa_per_kg) + (chicken_ratio * chicken_price)
packaging_cost_per_kg = 1.50 # embalagem + etiqueta
total_cost_per_kg = cost_product_per_kg + packaging_cost_per_kg

total_units_per_kg = 1000 / coxinha_weight
cost_per_unit = total_cost_per_kg / total_units_per_kg

# Precificação (Markup)
tax_percent = 5
total_deductions = profit_margin + opex_percent + tax_percent
divisor = max(0.1, (100 - total_deductions) / 100)
suggested_price_per_kg = total_cost_per_kg / divisor
suggested_price_per_unit = suggested_price_per_kg / total_units_per_kg
profit_per_kg = suggested_price_per_kg - total_cost_per_kg

# Ponto de Equilíbrio
contribution_margin = suggested_price_per_kg - total_cost_per_kg
break_even_kg = fixed_costs / contribution_margin if contribution_margin > 0 else 0
break_even_units = break_even_kg * total_units_per_kg

# --- ABAS DA APLICAÇÃO ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Ficha Técnica & Custos", "💰 Precificação e Markup", "📈 Ponto de Equilíbrio", "🏷️ Rótulo ANVISA"])

with tab1:
    st.header("Resumo Estequiométrico da Ficha Técnica (1 kg)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Custo do Tempero Caseiro", f"R$ {cost_tempero_per_kg:.2f} /kg")
    col2.metric("Custo da Massa Pronta", f"R$ {cost_massa_per_kg:.2f} /kg")
    col3.metric("Custo Total de Produção", f"R$ {total_cost_per_kg:.2f} /kg")

    st.markdown("---")
    st.subheader("Detalhamento de Custos")
    
    df_costs = pd.DataFrame({
        "Componente": ["Tempero Caseiro (utilizado)", "Farinha de Trigo", "Filé de Peito de Frango", "Embalagem + Etiqueta"],
        "Proporção no Lote": ["200 g", "4,0 kg", "300 g", "1 pacote (1 kg)"],
        "Custo Total (R$)": [
            f"R$ {(0.2 * cost_tempero_per_kg):.2f}",
            f"R$ {(4 * flour_price):.2f}",
            f"R$ {(0.3 * chicken_price):.2f}",
            f"R$ {packaging_cost_per_kg:.2f}"
        ]
    })
    st.table(df_costs)
    st.info(f"Rendimento estimado: **~{int(total_units_per_kg)} unidades** de {coxinhaWeight}g por pacote de 1 kg. Custo por unidade: **R$ {cost_per_unit:.2f}**.")

with tab2:
    st.header("Formação de Preço de Venda (Markup)")
    
    col1, col2 = st.columns(2)
    col1.metric("Preço Sugerido por Pacote (1 kg)", f"R$ {suggested_price_per_kg:.2f}", delta=f"Lucro: R$ {profit_per_kg:.2f}/kg")
    col2.metric(f"Preço Sugerido por Unidade ({coxinhaweight}g)", f"R$ {suggested_price_per_unit:.2f}")

    st.markdown("---")
    st.write(f"**Markup Aplicado:** `{1/divisor:.2f}x`")
    st.write(f"O preço de venda foi calculado considerando **{profit_margin}% de lucro líquido**, **{opex_percent}% de despesas operacionais** e **5% de impostos/taxas**.")

with tab3:
    st.header("Análise do Ponto de Equilíbrio (Break-Even)")
    
    col1, col2 = st.columns(2)
    col1.metric("Ponto de Equilíbrio (Quantidade)", f"{break_even_kg:.1f} pacotes / mês")
    col2.metric("Ponto de Equilíbrio (Unidades)", f"{int(break_even_units):,} unidades / mês".replace(",", "."))

    st.markdown("---")
    st.write(f"Para pagar todos os seus custos fixos mensais de **R$ {fixed_costs:,.2f}**, a **TeoDoro's Salgados** precisa vender pelo menos `{break_even_kg:.1f} kg` de salgados por mês. A partir disso, cada pacote vendido gera lucro puro!")

with tab4:
    st.header("Visualização do Rótulo Padrão ANVISA (100x150mm)")
    
    st.markdown("""
    <div style="background-color: white; color: black; padding: 20px; border-radius: 10px; border: 2px solid #ccc; max-width: 450px; margin: auto; font-family: Arial, sans-serif; font-size: 12px;">
        <div style="text-align: center; font-weight: bold; font-size: 14px; color: #b45309;">TeoDoro's Salgados</div>
        <div style="text-align: center; font-size: 11px; color: #555;">Artesanais & Congelados</div>
        <hr style="margin: 8px 0;">
        <div style="text-align: center; font-weight: bold; font-size: 13px;">MINI COXINHAS DE FRANGO</div>
        <div style="text-align: center; font-size: 11px; color: #1e40af;">Peso Líquido: 1 kg</div>
        <br>
        <div style="border: 1px solid black; padding: 6px;">
            <div style="text-align: center; font-weight: bold; font-size: 11px;">INFORMAÇÃO NUTRICIONAL</div>
            <div style="font-size: 9px;">Porções por embalagem: Cerca de 25 porções (aprox. 50 unidades)</div>
            <div style="font-size: 9px;">Porção: 40 g (2 unidades)</div>
            <table style="width: 100%; font-size: 9px; border-collapse: collapse; margin-top: 4px;" border="1">
                <tr style="background: #eee;">
                    <th></th><th>100g</th><th>Porção</th><th>%VD*</th>
                </tr>
                <tr><td>Valor energético</td><td>227 kcal</td><td>91 kcal</td><td>5%</td></tr>
                <tr><td>Carboidratos</td><td>39,1 g</td><td>15,6 g</td><td>5%</td></tr>
                <tr><td>Proteínas</td><td>12,4 g</td><td>5,0 g</td><td>10%</td></tr>
                <tr><td>Gorduras totais</td><td>1,8 g</td><td>0,7 g</td><td>1%</td></tr>
                <tr><td>Sódio</td><td>323 mg</td><td>129 mg</td><td>6%</td></tr>
            </table>
            <div style="font-size: 8px; margin-top: 2px;">* Percentual de valores diários fornecidos pela porção.</div>
        </div>
        <br>
        <div style="font-size: 10px;">
            <b>INGREDIENTES:</b> Água, farinha de trigo enriquecida com ferro e ácido fólico, filé de peito de frango, tempero caseiro (sal, cebola, alho, óleo vegetal e cheiro verde) e óleo vegetal.<br><br>
            <b>ALÉRGICOS:</b> CONTÉM DERIVADOS DE TRIGO. PODE CONTER SOJA, LEITE E OVO. <b>CONTÉM GLÚTEN.</b>
        </div>
        <br>
        <div style="border: 1px solid black; padding: 4px; font-size: 9px; background: #f9f9f9;">
            <b>CONSERVAÇÃO:</b> Manter congelado a -18°C.<br>
            <b>MODO DE PREPARO:</b> Fritar em óleo quente (180°C) por 3 min ou assar a 200°C por 12 min.<br>
            <b>FABRICAÇÃO:</b> __/__/____ | <b>VALIDADE:</b> __/__/____
        </div>
        <div style="text-align: center; margin-top: 10px; font-family: monospace; font-size: 11px;">
            ||| ||||| |||| ||||| <br>7891020304055
        </div>
    </div>
    """, unsafe_allow_html=True)
