import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="TeoDoro's Salgados - Calculadora e Precificação",
    page_icon="🥟",
    layout="wide",
)

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

# Menu principal de navegação / Modos
menu = st.sidebar.radio("📂 Navegação do Sistema", [
    "🥟 Receita Padrão (Mini Coxinha TeoDoro's)", 
    "⭐ Área Premium: Criador de Receitas Personalizadas"
])

if menu == "🥟 Receita Padrão (Mini Coxinha TeoDoro's)":
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

    # Cálculos
    cost_tempero_total = (3 * cabbage_price) + (3 * garlic_price) + (1 * oil_price) + (0.1 * herbs_price) + (3 * salt_price)
    cost_tempero_per_kg = cost_tempero_total / 10.1

    cost_massa_total = (0.2 * cost_tempero_per_kg) + (4 * flour_price)
    cost_massa_per_kg = cost_massa_total / 5.9

    mass_ratio = 100 / 130
    chicken_ratio = 30 / 130
    cost_product_per_kg = (mass_ratio * cost_massa_per_kg) + (chicken_ratio * chicken_price)
    packaging_cost_per_kg = 1.50
    total_cost_per_kg = cost_product_per_kg + packaging_cost_per_kg

    total_units_per_kg = 1000 / coxinha_weight
    cost_per_unit = total_cost_per_kg / total_units_per_kg

    tax_percent = 5
    total_deductions = profit_margin + opex_percent + tax_percent
    divisor = max(0.1, (100 - total_deductions) / 100)
    suggested_price_per_kg = total_cost_per_kg / divisor
    suggested_price_per_unit = suggested_price_per_kg / total_units_per_kg
    profit_per_kg = suggested_price_per_kg - total_cost_per_kg

    contribution_margin = suggested_price_per_kg - total_cost_per_kg
    break_even_kg = fixed_costs / contribution_margin if contribution_margin > 0 else 0
    break_even_units = break_even_kg * total_units_per_kg

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Ficha Técnica & Custos", "💰 Precificação e Markup", "📈 Ponto de Equilíbrio", "🏷️ Rótulo ANVISA"])

    with tab1:
        st.header("Resumo Estequiométrico da Ficha Técnica (1 kg)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Custo do Tempero Caseiro", f"R$ {cost_tempero_per_kg:.2f} /kg")
        col2.metric("Custo da Massa Pronta", f"R$ {cost_massa_per_kg:.2f} /kg")
        col3.metric("Custo Total de Produção", f"R$ {total_cost_per_kg:.2f} /kg")

        st.markdown("---")
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
        st.info(f"Rendimento estimado: **~{int(total_units_per_kg)} unidades** de {coxinha_weight}g por pacote de 1 kg. Custo por unidade: **R$ {cost_per_unit:.2f}**.")

    with tab2:
        st.header("Formação de Preço de Venda (Markup)")
        col1, col2 = st.columns(2)
        col1.metric("Preço Sugerido por Pacote (1 kg)", f"R$ {suggested_price_per_kg:.2f}", delta=f"Lucro: R$ {profit_per_kg:.2f}/kg")
        col2.metric(f"Preço Sugerido por Unidade ({coxinha_weight}g)", f"R$ {suggested_price_per_unit:.2f}")

    with tab3:
        st.header("Análise do Ponto de Equilíbrio (Break-Even)")
        col1, col2 = st.columns(2)
        col1.metric("Ponto de Equilíbrio (Quantidade)", f"{break_even_kg:.1f} pacotes / mês")
        col2.metric("Ponto de Equilíbrio (Unidades)", f"{int(break_even_units):,} unidades / mês".replace(",", "."))

    with tab4:
        st.header("Visualização do Rótulo Padrão ANVISA (100x150mm)")
        st.markdown(f"""
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
                <div style="font-size: 9px;">Porção: 40 g (2 unidades de {coxinha_weight} g)</div>
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
            </div>
            <br>
            <div style="font-size: 10px;">
                <b>INGREDIENTES:</b> Água, farinha de trigo, filé de peito de frango, tempero caseiro e óleo vegetal.<br>
                <b>ALÉRGICOS:</b> CONTÉM DERIVADOS DE TRIGO. CONTÉM GLÚTEN.
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # --- ÁREA PREMIUM: CRIADOR DE RECEITAS PERSONALIZADAS ---
    st.header("⭐ Área Premium: Construtor de Receitas Personalizadas")
    st.markdown("Cadastre seus próprios ingredientes, defina as quantidades por lote e calcule automaticamente os custos e o preço de venda de qualquer salgado (ex: Esfiha, Quibe, Risole).")

    with st.form("form_receita"):
        nome_receita = st.text_input("Nome do Novo Salgado", value="Esfiha de Carne Recheada")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        peso_unitario = col_p1.number_input("Peso de cada salgado (g)", value=30, step=5)
        rendimento_lote = col_p2.number_input("Rendimento total do lote (unidades)", value=100, step=10)
        margem_lucro_custom = col_p3.slider("Margem de Lucro Desejada (%)", 10, 60, 30)

        st.subheader("Ingredientes do Lote")
        st.markdown("Informe os ingredientes utilizados em todo o lote de produção:")

        # Tabela dinâmica simples simulada com inputs
        ingredientes_data = []
        
        # Vamos permitir adicionar 5 ingredientes dinâmicos
        col_i1, col_i2, col_i3 = st.columns([3, 2, 2])
        col_i1.markdown("**Nome do Ingrediente**")
        col_i2.markdown("**Qtd. Usada no Lote**")
        col_i3.markdown("**Preço por kg/L (R$)**")

        # Linhas de ingredientes
        ingredientes_input = []
        for i in range(6):
            c1, c2, c3 = st.columns([3, 2, 2])
            ing_nome = c1.text_input(f"Ingrediente {i+1}", value=["Farinha de Trigo", "Carne Moída", "Cebola", "Óleo", "Sal", "Tempero"][i] if i < 6 else "")
            ing_qtd = c2.number_input(f"Qtd {i+1} (kg ou L)", value=[2.0, 1.5, 0.5, 0.2, 0.1, 0.05][i] if i < 6 else 0.0, step=0.1, format="%.3f")
            ing_preco = c3.number_input(f"Preço {i+1} (R$)", value=[5.0, 25.0, 4.5, 9.0, 3.5, 15.0][i] if i < 6 else 0.0, step=0.5)
            if ing_nome and ing_qtd > 0:
                ingredientes_input.append({"nome": ing_nome, "qtd": ing_qtd, "preco": ing_preco, "total": ing_qtd * ing_preco})

        submitted = st.form_submit_button("🧮 Calcular Custos e Precificação da Receita")

    if submitted:
        st.markdown("---")
        st.subheader(f"📊 Relatório de Custos: {nome_receita}")

        df_custom = pd.DataFrame(ingredientes_input)
        if not df_custom.empty:
            custo_ingredientes_total = df_custom["total"].sum()
            custo_embalagem = 2.00 # custo fixo estimado de embalagem por lote
            custo_total_lote = custo_ingredientes_total + custo_embalagem
            custo_unitario = custo_total_lote / rendimento_lote
            
            # Preço sugerido com markup de 30% lucro + 20% opex
            divisor_custom = (100 - (margem_lucro_custom + 20 + 5)) / 100
            preco_venda_lote = custo_total_lote / max(0.1, divisor_custom)
            preco_venda_unitario = preco_venda_lote / rendimento_lote

            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("Custo Total do Lote", f"R$ {custo_total_lote:.2f}")
            col_r2.metric("Custo por Unidade", f"R$ {custo_unitario:.2f}")
            col_r3.metric("Preço de Venda Sugerido (Un.)", f"R$ {preco_venda_unitario:.2f}", delta=f"Lucro: R$ {(preco_venda_unitario - custo_unitario):.2f}/un")

            st.markdown("### Detalhamento dos Ingredientes")
            st.table(df_custom.rename(columns={"nome": "Ingrediente", "qtd": "Quantidade (kg/L)", "preco": "Preço Unitário (R$)", "total": "Custo Total (R$)"}))
            
            st.success("Receita personalizada calculada com sucesso! Você pode alterar os valores acima para simular diferentes cenários de custos.")
        else:
            st.error("Por favor, preencha pelo menos um ingrediente com quantidade válida.")
