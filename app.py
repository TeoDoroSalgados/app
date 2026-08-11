
import streamlit as st
import pandas as pd
import random
import string

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

# --- BANCO DE DADOS DE LICENÇAS NA SESSÃO (Para persistir durante os testes no Streamlit) ---
if "licencas_db" not in st.session_state:
    st.session_state.licencas_db = {
        "INI-1700-TESTE": {"plano": "Iniciante", "nome": "Produtor Iniciante", "status": "Ativo"},
        "PRO-3900-TESTE": {"plano": "Profissional", "nome": "Salgaderia Profissional", "status": "Ativo"},
        "PREM-7900-TESTE": {"plano": "Premium", "nome": "Fábrica / Premium", "status": "Ativo"}
    }

st.sidebar.header("🔐 Acesso & Licenciamento")

# Modo Admin ou Cliente na Barra Lateral
modo_acesso = st.sidebar.radio("Modo de Acesso", ["Cliente / Assinante", "Painel Administrativo (Admin)"])

if modo_acesso == "Painel Administrativo (Admin)":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 Login do Administrador")
    senha_admin = st.sidebar.text_input("Senha Mestre", type="password")
    
    # Senha mestre padrão do admin (pode alterar aqui)
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
        st.sidebar.markdown("Digite sua **Chave de Licença** do plano adquirido:")
        chave_input = st.sidebar.text_input("Chave de Licença", type="password")
        
        if st.sidebar.button("Ativar Acesso"):
            if chave_input in st.session_state.licencas_db and st.session_state.licencas_db[chave_input]["status"] == "Ativo":
                st.session_state.usuario_logado = True
                st.session_state.plano_atual = st.session_state.licencas_db[chave_input]["plano"]
                st.session_state.nome_cliente = st.session_state.licencas_db[chave_input]["nome"]
                st.sidebar.success(f"Acesso liberado: {st.session_state.nome_cliente}!")
                st.rerun()
            else:
                st.sidebar.error("❌ Chave inválida ou desativada.")
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🏷️ Nossos Planos:")
        st.sidebar.markdown("- **Iniciante (R$ 17/mês)**")
        st.sidebar.markdown("- **Profissional (R$ 39/mês)**")
        st.sidebar.markdown("- **Premium (R$ 79/mês)**")
        
        plano_ativo = "Gratuito"
    else:
        st.sidebar.success(f"Plano Ativo: **{st.session_state.plano_atual}**")
        if st.sidebar.button("Sair / Trocar Chave"):
            st.session_state.usuario_logado = False
            st.session_state.plano_atual = "Gratuito"
            st.rerun()
        plano_ativo = st.session_state.plano_atual

# --- TELA DO PAINEL ADMINISTRATIVO ---
if st.session_state.get("is_admin", False):
    st.title("🛠️ Painel Administrativo - TeoDoro's Salgados")
    st.markdown("Gerencie as chaves de licença dos clientes, crie novos acessos e monitore assinaturas ativas.")
    
    col_adm1, col_adm2 = st.columns(2)
    
    with col_adm1:
        st.subheader("➕ Gerar Nova Chave de Licença")
        with st.form("form_nova_chave"):
            nome_cliente_novo = st.text_input("Nome do Cliente / Empresa", value="Ex: Buffet do Carlos")
            plano_escolhido = st.selectbox("Plano Contratado", ["Iniciante", "Profissional", "Premium"])
            
            gerar_btn = st.form_submit_button("Gerar Chave de Acesso")
            
            if gerar_btn:
                # Prefixo baseado no plano
                prefixo = "INI" if plano_escolhido == "Iniciante" else ("PRO" if plano_escolhido == "Profissional" else "PREM")
                sufixo = ''.join(random.choices(string.digits, k=4))
                nova_chave = f"{prefixo}-{sufixo}-{random.randint(10,99)}"
                
                st.session_state.licencas_db[nova_chave] = {
                    "plano": plano_escolhido,
                    "nome": nome_cliente_novo,
                    "status": "Ativo"
                }
                st.success(f"Chave gerada com sucesso para **{nome_cliente_novo}**!")
                st.code(nova_chave)

    with col_adm2:
        st.subheader("📋 Lista de Chaves Ativas no Sistema")
        df_licencas = pd.DataFrame([
            {"Chave": k, "Plano": v["plano"], "Cliente": v["nome"], "Status": v["status"]}
            for k, v in st.session_state.licencas_db.items()
        ])
        st.dataframe(df_licencas, use_container_width=True)
        
        st.info("💡 **Dica:** Você pode copiar a chave gerada e enviá-la diretamente para o cliente via WhatsApp após a confirmação do pagamento via Pix.")

else:
    # --- APLICATIVO NORMAL PARA O CLIENTE ---
    st.title("🥟 TeoDoro's Salgados - Sistema de Custos & Precificação")

    tem_profissional = plano_ativo in ["Profissional", "Premium"]
    tem_premium = plano_ativo == "Premium"

    if plano_ativo == "Gratuito":
        st.warning("⚠️ Modo de demonstração (Visitante). Insira uma chave de licença na barra lateral para liberar as funcionalidades do seu plano.")

    tabs = ["📊 Ficha Técnica Básica (Iniciante)"]
    if tem_profissional:
        tabs.append("💰 Precificação & Ponto de Equilíbrio (Profissional)")
    if tem_premium:
        tabs.append("⭐ Construtor de Receitas Customizadas (Premium)")
        tabs.append("🏷️ Rotulagem ANVISA Oficial (Premium)")

    selected_tabs = st.tabs(tabs)

    with selected_tabs[0]:
        st.header("📊 Ficha Técnica & Custo Base (Mini Coxinha TeoDoro's)")
        
        col_i1, col_i2 = st.columns(2)
        chicken_price = col_i1.number_input("Preço do Peito de Frango (kg)", value=18.00, step=0.50)
        flour_price = col_i2.number_input("Preço da Farinha de Trigo (kg)", value=5.00, step=0.50)
        coxinha_weight = st.slider("Peso médio da coxinha (g)", 10, 50, 20, 5)
        
        total_cost_per_kg = (0.3 * chicken_price) + (4.0 * flour_price) / 5.9 + 1.50
        total_units = 1000 / coxinha_weight
        cost_per_unit = total_cost_per_kg / total_units
        
        st.metric("Custo Total de Produção por Pacote (1 kg)", f"R$ {total_cost_per_kg:.2f}")
        st.metric(f"Custo Unitário por Coxinha ({coxinha_weight}g)", f"R$ {cost_per_unit:.2f}")
        
        if plano_ativo == "Gratuito":
            st.info("💡 **Dica:** Faça o upgrade para o **Plano Profissional (R$ 39/mês)** para calcular margens de lucro, markup automático e o ponto de equilíbrio!")

    if tem_profissional:
        with selected_tabs[1]:
            st.header("💰 Módulo Profissional: Precificação Avançada & Break-Even")
            col_p1, col_p2 = st.columns(2)
            fixed_costs = col_p1.number_input("Custos Fixos Mensais (Aluguel, Energia, etc.)", value=1500.00, step=100.00)
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
            col_m2.metric(f"Preço Sugerido por Unidade ({coxinha_weight}g)", f"R$ {unit_price:.2f}")
            
            st.markdown("---")
            st.subheader("📈 Ponto de Equilíbrio (Break-Even)")
            st.metric("Volume Mínimo de Vendas para Cobrir Custos", f"{break_even_kg:.1f} pacotes / mês")

    if tem_premium:
        with selected_tabs[2]:
            st.header("⭐ Construtor de Receitas Personalizadas (Área Premium)")
            st.markdown("Cadastre os ingredientes e quantidades dos seus próprios salgados.")
            with st.form("custom_recipe"):
                recipe_name = st.text_input("Nome do Salgado", value="Esfiha de Carne")
                batch_yield = st.number_input("Rendimento do lote (unidades)", value=100, step=10)
                
                c1, c2, c3 = st.columns(3)
                ing1_nome = c1.text_input("Ingrediente 1", value="Farinha de Trigo")
                ing1_qtd = c2.number_input("Qtd 1 (kg)", value=2.0)
                ing1_preco = c3.number_input("Preço 1 (R$/kg)", value=5.0)
                
                submitted = st.form_submit_button("🧮 Calcular Receita Personalizada")
                
            if submitted:
                custo_lote = (ing1_qtd * ing1_preco) + 5.00
                custo_un = custo_lote / batch_yield
                st.success(f"Receita **{recipe_name}** calculada com sucesso!")
                st.metric("Custo Total do Lote", f"R$ {custo_lote:.2f}")
                st.metric("Custo por Unidade", f"R$ {custo_un:.2f}")

        with selected_tabs[3]:
            st.header("🏷️ Geração de Rótulo ANVISA Oficial (100x150mm)")
            st.markdown("Prévia oficial pronta para impressão com logomarca e código de barras.")
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
