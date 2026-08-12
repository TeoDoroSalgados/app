Aqui está o código completo e atualizado do arquivo **`app_streamlit.py`** (já com a Gestão de Estoque, Construtor Inteligente de Receitas para qualquer nicho de alimentação, os 3 planos e o Painel Administrativo).

Basta copiar todo o código abaixo, colar no seu arquivo `app.py` lá no GitHub e clicar em **Commit changes**:

```python
import streamlit as st
import pandas as pd
import random
import string

st.set_page_config(
    page_title="TeoDoro's - Sistema de Custos & Precificação",
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

# --- BANCO DE DADOS DE LICENÇAS NA SESSÃO ---
if "licencas_db" not in st.session_state:
    st.session_state.licencas_db = {
        "INI-1700-TESTE": {"plano": "Iniciante", "nome": "Produtor Iniciante", "status": "Ativo"},
        "PRO-3900-TESTE": {"plano": "Profissional", "nome": "Salgaderia Profissional", "status": "Ativo"},
        "PREM-7900-TESTE": {"plano": "Premium", "nome": "Fábrica / Premium", "status": "Ativo"}
    }

# --- ESTOQUE DE INSUMOS DO CLIENTE (Sessão) ---
if "estoque_insumos" not in st.session_state:
    st.session_state.estoque_insumos = {
        "Farinha de Trigo": {"preco": 5.00, "unidade": "kg"},
        "Peito de Frango": {"preco": 18.00, "unidade": "kg"},
        "Açúcar Cristal": {"preco": 4.80, "unidade": "kg"},
        "Leite Condensado": {"preco": 6.50, "unidade": "un"},
        "Chocolate em Pó": {"preco": 25.00, "unidade": "kg"},
        "Cebola": {"preco": 4.50, "unidade": "kg"},
        "Alho": {"preco": 15.00, "unidade": "kg"},
        "Óleo Vegetal": {"preco": 9.00, "unidade": "L"},
        "Sal": {"preco": 3.50, "unidade": "kg"},
    }

st.sidebar.header("🔐 Acesso & Licenciamento")
modo_acesso = st.sidebar.radio("Modo de Acesso", ["Cliente / Assinante", "Painel Administrativo (Admin)"])

if modo_acesso == "Painel Administrativo (Admin)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Login do Administrador")
    senha_admin = st.sidebar.text_input("Senha Mestre", type="password")
    SENHA_MESTRE_ADMIN = "teo2026admin"
    
    if senha_admin == SENHA_MESTRE_ADMIN:
        st.sidebar.success("✅ Painel Admin Liberado!")
        st.session_state.is_admin = True
    else:
        if senha_admin:
            st.sidebar.error("❌ Senha incorreta.")
        st.session_state.is_admin = False
    plano_ativo = "Admin"
else:
    st.session_state.is_admin = False
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = False
        st.session_state.plano_atual = "Gratuito (Visitante)"
        st.session_state.nome_cliente = ""

    if not st.session_state.usuario_logado:
        st.sidebar.markdown("Digite sua **Chave de Licença**:")
        chave_input = st.sidebar.text_input("Chave de Licença", type="password")
        
        if st.sidebar.button("Ativar Acesso"):
            if chave_input in st.session_state.licencas_db and st.session_state.licencas_db[chave_input]["status"] == "Ativo":
                st.session_state.usuario_logado = True
                st.session_state.plano_atual = st.session_state.licencas_db[chave_input]["plano"]
                st.session_state.nome_cliente = st.session_state.licencas_db[chave_input]["nome"]
                st.sidebar.success(f"Acesso liberado: {st.session_state.nome_cliente}!")
                st.rerun()
            else:
                st.sidebar.error("❌ Chave inválida.")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏷️ Nossos Planos:")
        st.sidebar.markdown("- **Iniciante (R$ 17/mês):** Ficha básica.")
        st.sidebar.markdown("- **Profissional (R$ 39/mês):** Custos + Markup + Break-Even.")
        st.sidebar.markdown("- **Premium (R$ 79/mês):** Estoque + Receitas Customizadas + ANVISA.")
        plano_ativo = "Gratuito"
    else:
        st.sidebar.success(f"Plano Ativo: **{st.session_state.plano_atual}**")
        if st.sidebar.button("Sair / Trocar Chave"):
            st.session_state.usuario_logado = False
            st.session_state.plano_atual = "Gratuito"
            st.rerun()
        plano_ativo = st.session_state.plano_atual

# --- PAINEL ADMIN ---
if st.session_state.get("is_admin", False):
    st.title("🛠️ Painel Administrativo - Gestão de Licenças")
    st.markdown("Gerencie as chaves de licença dos clientes dos 3 planos.")
    
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        st.subheader("➕ Gerar Nova Chave")
        with st.form("form_nova_chave"):
            nome_cliente_novo = st.text_input("Nome do Cliente", value="Ex: Confeitaria Doce Mel")
            plano_escolhido = st.selectbox("Plano Contratado", ["Iniciante", "Profissional", "Premium"])
            gerar_btn = st.form_submit_button("Gerar Chave de Acesso")
            
            if gerar_btn:
                prefixo = "INI" if plano_escolhido == "Iniciante" else ("PRO" if plano_escolhido == "Profissional" else "PREM")
                sufixo = ''.join(random.choices(string.digits, k=4))
                nova_chave = f"{prefixo}-{sufixo}-{random.randint(10,99)}"
                st.session_state.licencas_db[nova_chave] = {"plano": plano_escolhido, "nome": nome_cliente_novo, "status": "Ativo"}
                st.success("Chave gerada com sucesso!")
                st.code(nova_chave)

    with col_adm2:
        st.subheader("📋 Chaves Ativas")
        df_licencas = pd.DataFrame([
            {"Chave": k, "Plano": v["plano"], "Cliente": v["nome"], "Status": v["status"]}
            for k, v in st.session_state.licencas_db.items()
        ])
        st.dataframe(df_licencas, use_container_width=True)

else:
    # --- APP DO CLIENTE ---
    st.title("🥟 Sistema Universal de Custos, Fichas Técnicas & Precificação")
    st.markdown("Atende a todos os nichos de alimentação: **Salgados, Doces, Confeitaria, Massas e Marmitas**.")

    tem_profissional = plano_ativo in ["Profissional", "Premium"]
    tem_premium = plano_ativo == "Premium"

    if plano_ativo == "Gratuito":
        st.warning("⚠️ Modo de demonstração (Visitante). Insira uma chave de licença válida na barra lateral para liberar as funcionalidades do seu plano.")

    tabs = ["📊 Ficha Técnica Básica"]
    if tem_profissional:
        tabs.append("💰 Precificação & Ponto de Equilíbrio")
    if tem_premium:
        tabs.append("📦 Gestão de Insumos (Estoque)")
        tabs.append("⭐ Construtor Inteligente de Receitas")
        tabs.append("🏷️ Rotulagem ANVISA Oficial")

    selected_tabs = st.tabs(tabs)

    # ABA 1: Iniciante
    with selected_tabs[0]:
        st.header("📊 Ficha Técnica & Custo Base")
        peso_un = st.slider("Peso médio de cada unidade (g)", 10, 50, 20, 5)
        
        f_trigo = st.session_state.estoque_insumos.get("Farinha de Trigo", {}).get("preco", 5.0)
        p_frango = st.session_state.estoque_insumos.get("Peito de Frango", {}).get("preco", 18.0)
        
        total_cost_per_kg = (0.3 * p_frango) + (4.0 * f_trigo) / 5.9 + 1.50
        total_units = 1000 / peso_un
        cost_per_unit = total_cost_per_kg / total_units
        
        col_b1, col_b2 = st.columns(2)
        col_b1.metric("Custo Total por kg", f"R$ {total_cost_per_kg:.2f}")
        col_b2.metric(f"Custo Unitário ({peso_un}g)", f"R$ {cost_per_unit:.2f}")
        
        if plano_ativo == "Gratuito":
            st.info("💡 Faça o upgrade para o **Plano Profissional (R$ 39/mês)** para calcular margens de lucro, markup automático e o ponto de equilíbrio!")

    # ABA 2: Profissional
    if tem_profissional:
        with selected_tabs[1]:
            st.header("💰 Módulo Profissional: Precificação Avançada & Break-Even")
            col_p1, col_p2 = st.columns(2)
            fixed_costs = col_p1.number_input("Custos Fixos Mensais (R$)", value=1500.00, step=100.00)
            profit_margin = col_p2.slider("Margem de Lucro Desejada (%)", 10, 60, 30, 5)
            
            opex_percent = 20
            tax_percent = 5
            total_deductions = profit_margin + opex_percent + tax_percent
            divisor = max(0.1, (100 - total_deductions) / 100)
            
            suggested_price = total_cost_per_kg / divisor
            unit_price = suggested_price / total_units
            profit_kg = suggested_price - total_cost_per_kg
            
            contribution_margin = suggested_price - total_cost_per_kg
            break_even_kg = fixed_costs / contribution_margin if contribution_margin > 0 else 0
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Preço de Venda Sugerido (1 kg)", f"R$ {suggested_price:.2f}", delta=f"Lucro: R$ {profit_kg:.2f}/kg")
            col_m2.metric(f"Preço Sugerido por Unidade ({peso_un}g)", f"R$ {unit_price:.2f}")
            
            st.markdown("---")
            st.subheader("📈 Ponto de Equilíbrio (Break-Even)")
            st.metric("Volume Mínimo de Vendas para Cobrir Custos", f"{break_even_kg:.1f} kg / mês")

    # ABA 3: Gestão de Insumos (Estoque) - Premium
    tab_index = 2
    if tem_premium:
        with selected_tabs[tab_index]:
            st.header("📦 Gestão de Insumos & Preços (Estoque Universal)")
            st.markdown("Cadastre ingredientes para qualquer nicho (salgados, doces, confeitarias) e atualize preços sempre que precisar.")
            
            with st.form("form_add_insumo"):
                st.subheader("Adicionar ou Atualizar Ingrediente")
                col_in1, col_in2, col_in3 = st.columns(3)
                novo_nome = col_in1.text_input("Nome do Insumo (ex: Leite Condensado, Chocolate)", value="")
                novo_preco = col_in2.number_input("Preço Unitário (R$)", value=10.0, step=0.50)
                nova_unidade = col_in3.selectbox("Unidade de Medida", ["kg", "L", "un", "g", "ml", "pct"])
                
                salvar_insumo = st.form_submit_button("Salvar no Estoque")
                if salvar_insumo and novo_nome:
                    st.session_state.estoque_insumos[novo_nome] = {"preco": novo_preco, "unidade": nova_unidade}
                    st.success(f"Insumo **{novo_nome}** salvo/atualizado com sucesso!")
            
            st.markdown("---")
            st.subheader("Seus Insumos Cadastrados no Sistema")
            insumos_list = [{"Ingrediente": k, "Preço (R$)": v["preco"], "Unidade": v["unidade"]} for k, v in st.session_state.estoque_insumos.items()]
            st.dataframe(pd.DataFrame(insumos_list), use_container_width=True)
            st.info("💡 Estes ingredientes aparecem automaticamente no **Construtor Inteligente de Receitas**.")
        
        tab_index += 1

        # ABA 4: Construtor Inteligente de Receitas - Premium
        with selected_tabs[tab_index]:
            st.header("⭐ Construtor Inteligente de Receitas (Multi-Nicho)")
            st.markdown("Selecione os ingredientes do estoque, informe a quantidade usada e o sistema calcula tudo instantaneamente.")
            
            with st.form("form_receita_inteligente"):
                nome_receita_custom = st.text_input("Nome do Produto (ex: Brigadeiro Gourmet, Esfiha, Bolo de Pote)", value="Brigadeiro Gourmet")
                rendimento_lote_custom = st.number_input("Rendimento do Lote (unidades ou porções)", value=50, step=5)
                
                st.markdown("### Selecione os Ingredientes para o Lote:")
                ingredientes_disponiveis = list(st.session_state.estoque_insumos.keys())
                ingredientes_selecionados = []
                
                for idx in range(6):
                    col_s1, col_s2 = st.columns([3, 2])
                    ing_escolhido = col_s1.selectbox(f"Ingrediente {idx+1}", ["-- Nenhum --"] + ingredientes_disponiveis, key=f"ing_esc_{idx}")
                    qtd_usada = col_s2.number_input(f"Qtd usada no lote ({idx+1})", value=0.0, step=0.1, format="%.3f", key=f"qtd_usada_{idx}")
                    
                    if ing_escolhido != "-- Nenhum --" and qtd_usada > 0:
                        preco_unit = st.session_state.estoque_insumos[ing_escolhido]["preco"]
                        unidade_medida = st.session_state.estoque_insumos[ing_escolhido]["unidade"]
                        custo_parcial = qtd_usada * preco_unit
                        ingredientes_selecionados.append({
                            "Ingrediente": ing_escolhido,
                            "Quantidade": f"{qtd_usada} {unidade_medida}",
                            "Preço Unit.": f"R$ {preco_unit:.2f}",
                            "Custo Total": custo_parcial
                        })
                
                custo_embalagem_lote = st.number_input("Custo de Embalagem / Embalagem para o Lote (R$)", value=5.00, step=0.50)
                calcular_receita_btn = st.form_submit_button("🧮 Calcular Custos e Precificação")
                
            if calcular_receita_btn:
                if ingredientes_selecionados:
                    df_rec_result = pd.DataFrame(ingredientes_selecionados)
                    custo_ingredientes_soma = df_rec_result["Custo Total"].sum()
                    custo_total_lote_final = custo_ingredientes_soma + custo_embalagem_lote
                    custo_unitario_final = custo_total_lote_final / rendimento_lote_custom
                    
                    div_custom = (100 - (30 + 20 + 5)) / 100
                    preco_venda_lote_sug = custo_total_lote_final / max(0.1, div_custom)
                    preco_venda_unit_sug = preco_venda_lote_sug / rendimento_lote_custom
                    
                    st.markdown("---")
                    st.subheader(f"📊 Relatório de Custos: {nome_receita_custom}")
                    
                    col_c1, col_c2, col_c3 = st.columns(3)
                    col_c1.metric("Custo Total do Lote", f"R$ {custo_total_lote_final:.2f}")
                    col_c2.metric("Custo por Unidade", f"R$ {custo_unitario_final:.2f}")
                    col_c3.metric("Preço de Venda Sugerido (Un.)", f"R$ {preco_venda_unit_sug:.2f}", delta=f"Lucro: R$ {(preco_venda_unit_sug - custo_unitario_final):.2f}/un")
                    
                    st.markdown("### Detalhamento dos Custos")
                    st.table(df_rec_result)
                    st.success("Receita calculada com sucesso!")
                else:
                    st.warning("⚠️ Selecione pelo menos um ingrediente e informe a quantidade.")

        tab_index += 1

        # ABA 5: Rotulagem ANVISA - Premium
        with selected_tabs[tab_index]:
            st.header("🏷️ Geração de Rótulo ANVISA Oficial (100x150mm)")
            st.markdown("Prévia oficial pronta para impressão com logomarca e código de barras.")
            
            st.markdown("""
            <div style="background-color: white; color: black; padding: 20px; border-radius: 10px; border: 2px solid #ccc; max-width: 450px; margin: auto; font-family: Arial, sans-serif; font-size: 12px;">
                <div style="text-align: center; font-weight: bold; font-size: 14px; color: #b45309;">TeoDoro's Salgados & Doces</div>
                <div style="text-align: center; font-size: 11px; color: #555;">Artesanais & Congelados</div>
                <hr style="margin: 8px 0;">
                <div style="text-align: center; font-weight: bold; font-size: 13px;">PRODUTO ARTESANAL</div>
                <div style="text-align: center; font-size: 11px; color: #1e40af;">Peso Líquido: 1 kg</div>
                <br>
                <div style="border: 1px solid black; padding: 6px;">
                    <div style="text-align: center; font-weight: bold; font-size: 11px;">INFORMAÇÃO NUTRICIONAL</div>
                    <div style="font-size: 9px;">Porções por embalagem: Cerca de 25 porções</div>
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
                    <b>INGREDIENTES:</b> Ingredientes cadastrados no sistema.<br>
                    <b>ALÉRGICOS:</b> CONTÉM DERIVADOS DE TRIGO E LEITE. CONTÉM GLÚTEN.
                </div>
                <div style="text-align: center; margin-top: 10px; font-family: monospace; font-size: 11px;">
                    ||| ||||| |||| ||||| <br>7891020304055
                </div>
            </div>
            """, unsafe_allow_html=True)
```
