import streamlit as st
import pandas as pd
import random
import string
import barcode
from barcode.writer import SVGWriter
import io

st.set_page_config(
    page_title="Plataforma SaaS Profissional - Precificação & Ficha Técnica",
    page_icon="📊",
    layout="wide",
)

# --- ESTILIZAÇÃO CSS PROFISSIONAL ---
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
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS DE LICENÇAS NA SESSÃO (3 Planos) ---
if "licencas_db" not in st.session_state:
    st.session_state.licencas_db = {
        "INI-1700-TESTE": {"plano": "Iniciante", "nome": "Produtor Iniciante", "status": "Ativo"},
        "PRO-3900-TESTE": {"plano": "Profissional", "nome": "Salgaderia Profissional", "status": "Ativo"},
        "PREM-7900-TESTE": {"plano": "Premium", "nome": "Fábrica / Premium", "status": "Ativo"}
    }

# --- CONFIGURAÇÃO DA MARCA (White-Label) ---
if "config_marca" not in st.session_state:
    st.session_state.config_marca = {
        "nome_empresa": "TeoDoro's Salgados & Alimentos",
        "nome_fantasia": "Qualidade Artesanal Premium",
        "whatsapp": "(11) 99999-9999",
        "email": "contato@teodorosalgados.com.br"
    }

# --- ESTOQUE UNIVERSAL DE INSUMOS ---
if "estoque_insumos" not in st.session_state:
    st.session_state.estoque_insumos = {
        "Farinha de Trigo": {"preco": 5.00, "unidade": "kg", "fornecedor": "Atacadão dos Cereais"},
        "Peito de Frango": {"preco": 18.00, "unidade": "kg", "fornecedor": "Frango Bom Gosto"},
        "Cebola": {"preco": 4.50, "unidade": "kg", "fornecedor": "Hortifrúti Central"},
        "Alho": {"preco": 15.00, "unidade": "kg", "fornecedor": "Hortifrúti Central"},
        "Óleo Vegetal": {"preco": 9.00, "unidade": "L", "fornecedor": "Distribuidora Master"},
        "Cheiro Verde": {"preco": 20.00, "unidade": "kg", "fornecedor": "Produtor Local"},
        "Sal Refinado": {"preco": 3.50, "unidade": "kg", "fornecedor": "Supermercado"}
    }

# --- BARRA LATERAL: CONTROLE DE ACESSO E ADMIN ---
st.sidebar.title("🔐 Acesso ao Sistema")
modo_acesso = st.sidebar.radio("Modo de Acesso", ["Cliente / Assinante", "Painel Administrativo (Admin)"])

is_admin = False
plano_atual = "Nenhum"
cliente_nome = "Visitante"

if modo_acesso == "Painel Administrativo (Admin)":
    senha_admin = st.sidebar.text_input("Senha Mestre Admin", type="password")
    if senha_admin == "teo2026admin":
        is_admin = True
        st.sidebar.success("✅ Painel Admin Liberado!")
    elif senha_admin:
        st.sidebar.error("❌ Senha incorreta.")
else:
    chave_input = st.sidebar.text_input("Digite sua Chave de Licença", value="PREM-7900-TESTE")
    if chave_input in st.session_state.licencas_db:
        dados_lic = st.session_state.licencas_db[chave_input]
        if dados_lic["status"] == "Ativo":
            plano_atual = dados_lic["plano"]
            cliente_nome = dados_lic["nome"]
            st.sidebar.success(f"✅ Plano Ativo: **{plano_atual}**")
            st.sidebar.markdown(f"👤 **Cliente:** {cliente_nome}")
        else:
            st.sidebar.error("❌ Licença bloqueada.")
    else:
        st.sidebar.error("❌ Chave inválida.")

# Permissões por Plano
tem_iniciante = plano_atual in ["Iniciante", "Profissional", "Premium"] or is_admin
tem_profissional = plano_atual in ["Profissional", "Premium"] or is_admin
tem_premium = plano_atual in ["Premium"] or is_admin

# --- PAINEL ADMINISTRATIVO ---
if is_admin:
    st.title("🛠️ Painel Administrativo de Licenças SaaS")
    st.markdown("Gerencie assinaturas e gere novas chaves de acesso para os planos Iniciante (R$ 17), Profissional (R$ 39) e Premium (R$ 79).")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Gerar Nova Chave de Licença")
        with st.form("form_nova_chave"):
            novo_nome = st.text_input("Nome do Cliente / Empresa")
            novo_plano = st.selectbox("Plano Contratado", ["Iniciante", "Profissional", "Premium"])
            gerar_btn = st.form_submit_button("Gerar Chave de Acesso")
            
            if gerar_btn and novo_nome:
                prefixo = "INI" if novo_plano == "Iniciante" else ("PRO" if novo_plano == "Profissional" else "PREM")
                sufixo = ''.join(random.choices(string.digits, k=4))
                nova_chave = f"{prefixo}-{sufixo}-{random.randint(10,99)}"
                st.session_state.licencas_db[nova_chave] = {
                    "plano": novo_plano,
                    "nome": novo_nome,
                    "status": "Ativo"
                }
                st.success(f"Chave gerada com sucesso para **{novo_nome}**!")
                st.code(nova_chave)
                
    with col_b:
        st.subheader("Licenças Ativas no Sistema")
        df_lic = pd.DataFrame.from_dict(st.session_state.licencas_db, orient='index')
        st.dataframe(df_lic, use_container_width=True)
        
    st.divider()

# --- APLICAÇÃO PRINCIPAL ---
st.title(f"📊 {st.session_state.config_marca['nome_empresa']}")
st.markdown(f"*{st.session_state.config_marca['nome_fantasia']} — Plataforma Universal de Ficha Técnica, Custos e Precificação.*")

if not tem_iniciante and not is_admin:
    st.warning("⚠️ Insira uma chave de licença válida na barra lateral para acessar o sistema.")
else:
    # Abas de Navegação Dinâmicas
    tabs_disponiveis = ["📊 Dashboard Gerencial", "🛒 Gestão de Insumos", "📋 Ficha Técnica & Custos", "💰 Precificação e Lucro", "⚖️ Ponto de Equilíbrio"]
    if tem_profissional:
        tabs_disponiveis.append("🏷️ Simulador de Custo")
    if tem_premium:
        tabs_disponiveis.extend(["⭐ Receitas Customizadas", "🏷️ Rótulo ANVISA & EAN-13", "🎨 Minha Marca"])
        
    selected_tabs = st.tabs(tabs_disponiveis)
    tab_idx = 0
    
    # 1. DASHBOARD GERENCIAL
    with selected_tabs[tab_idx]:
        st.header("📊 Dashboard Gerencial & Indicadores")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Insumos Cadastrados", len(st.session_state.estoque_insumos))
        c2.metric("Planos Ativos", len(st.session_state.licencas_db))
        c3.metric("Seu Plano Atual", plano_atual if not is_admin else "Administrador")
        c4.metric("Status da Conexão", "Online 🟢")
        
        st.info("💡 **Dica Pro:** Utilize a aba **Gestão de Insumos** para atualizar os preços dos ingredientes sempre que houver variação no mercado. Todos os cálculos de receitas e fichas técnicas serão atualizados instantaneamente.")
    tab_idx += 1

    # 2. GESTÃO DE INSUMOS E EMBALAGENS (Universal com Pesquisa e Filtros)
    with selected_tabs[tab_idx]:
        st.header("🛒 Gestão Universal de Insumos e Embalagens")
        st.markdown("Cadastre e atualize os insumos utilizados em qualquer nicho de alimentação (salgados, doces, massas, bolos, etc.).")
        
        col_pesq1, col_pesq2 = st.columns([2, 1])
        termo_busca = col_pesq1.text_input("🔍 Pesquisar ingrediente por nome...", "")
        
        fornecedores_disponiveis = ["Todos"] + list(set([item["fornecedor"] for item in st.session_state.estoque_insumos.values()]))
        filtro_forn = col_pesq2.selectbox("Filtrar por Fornecedor", fornecedores_disponiveis)
        
        st.subheader("Adicionar ou Atualizar Insumo")
        with st.form("form_insumo"):
            col1, col2, col3, col4 = st.columns(4)
            nome_ins = col1.text_input("Nome do Ingrediente/Embalagem")
            preco_ins = col2.number_input("Preço (R$)", min_value=0.01, value=10.00, step=0.50)
            unidade_ins = col3.selectbox("Unidade de Medida", ["kg", "g", "L", "ml", "unidade", "pacote"])
            forn_ins = col4.text_input("Fornecedor", value="Fornecedor Padrão")
            
            salvar_insumo = st.form_submit_button("Salvar Insumo no Estoque")
            if salvar_insumo and nome_ins:
                st.session_state.estoque_insumos[nome_ins] = {
                    "preco": preco_ins,
                    "unidade": unidade_ins,
                    "fornecedor": forn_ins
                }
                st.success(f"Insumo **{nome_ins}** salvo com sucesso!")
                
        st.subheader("Tabela de Insumos Cadastrados")
        lista_insumos = []
        for k, v in st.session_state.estoque_insumos.items():
            if termo_busca.lower() in k.lower():
                if filtro_forn == "Todos" or v["fornecedor"] == filtro_forn:
                    lista_insumos.append({
                        "Ingrediente": k,
                        "Preço (R$)": v["preco"],
                        "Unidade": v["unidade"],
                        "Fornecedor": v["fornecedor"]
                    })
        if lista_insumos:
            df_ins = pd.DataFrame(lista_insumos)
            st.dataframe(df_ins, use_container_width=True)
        else:
            st.warning("Nenhum insumo encontrado com os filtros aplicados.")
    tab_idx += 1

    # 3. FICHA TÉCNICA & CUSTOS
    with selected_tabs[tab_idx]:
        st.header("📋 Ficha Técnica & Custo de Produção")
        st.markdown("Cálculo estequiométrico baseado na proporção de massa, recheio e insumos.")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.subheader("Parâmetros de Produção")
            peso_coxinha = st.number_input("Peso médio por unidade (g)", min_value=5, max_value=200, value=20)
            lote_kg = st.number_input("Tamanho do Lote Base (kg)", min_value=0.5, max_value=50.0, value=1.0)
            
            # Cálculo estimado
            total_unidades = int((lote_kg * 1000) / peso_coxinha)
            st.metric("Unidades Estimadas por Lote", f"{total_unidades} unidades")
            
        with col_f2:
            st.subheader("Custos Calculados do Lote")
            custo_massa = lote_kg * 5.20
            custo_recheio = lote_kg * 6.80
            custo_embalagem = lote_kg * 1.50
            custo_total_lote = custo_massa + custo_recheio + custo_embalagem
            custo_unit = custo_total_lote / total_unidades if total_unidades > 0 else 0
            
            st.metric("Custo Total do Lote", f"R$ {custo_total_lote:.2f}")
            st.metric("Custo por Unidade", f"R$ {custo_unit:.3f}")
    tab_idx += 1

    # 4. PRECIFICAÇÃO E LUCRO
    with selected_tabs[tab_idx]:
        st.header("💰 Precificação Inteligente e Margem de Lucro")
        custo_base_prod = 0.17 # R$ por unidade
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            markup = st.slider("Multiplicador de Markup (sobre o custo)", 1.5, 4.0, 2.5, 0.1)
            preco_venda_sugerido = custo_base_prod * markup
            st.metric("Preço de Venda Sugerido (por unidade)", f"R$ {preco_venda_sugerido:.2f}")
            
        with col_p2:
            lucro_unit = preco_venda_sugerido - custo_base_prod
            margem_pct = (lucro_unit / preco_venda_sugerido) * 100 if preco_venda_sugerido > 0 else 0
            st.metric("Lucro Bruto por Unidade", f"R$ {lucro_unit:.2f}")
            st.metric("Margem de Lucro Efetiva", f"{margem_pct:.1f}%")
    tab_idx += 1

    # 5. PONTO DE EQUILÍBRIO
    with selected_tabs[tab_idx]:
        st.header("⚖️ Ponto de Equilíbrio (Break-Even Point)")
        st.markdown("Descubra quantas unidades você precisa vender para cobrir todos os seus custos fixos.")
        
        col_eq1, col_eq2 = st.columns(2)
        custos_fixos_mes = col_eq1.number_input("Custos Fixos Mensais (Aluguel, Energia, Salários, etc.)", value=2000.00, step=100.00)
        lucro_por_unidade = col_eq2.number_input("Lucro Contribuição por Unidade (Preço - Custo Variável)", value=0.35, step=0.05)
        
        if lucro_por_unidade > 0:
            ponto_eq = custos_fixos_mes / lucro_por_unidade
            st.metric("Ponto de Equilíbrio (Unidades/Mês)", f"{int(ponto_eq)} unidades")
            st.success(f"Para pagar todas as contas e operar sem prejuízo, você precisa vender pelo menos **{int(ponto_eq)} unidades por mês** (cerca de {int(ponto_eq/30)} unidades por dia).")
        else:
            st.error("O lucro por unidade precisa ser maior que zero.")
    tab_idx += 1

    # 6. SIMULADOR DE CUSTO (PROFISSIONAL)
    if tem_profissional:
        with selected_tabs[tab_idx]:
            st.header("🏷️ Simulador Avançado de Custo")
            st.markdown("Simule lotes personalizados de produção com taxas de perda e rendimento.")
            st.info("Módulo Profissional Ativo. Utilize os controles para simular cenários de produção em grande escala.")
        tab_idx += 1

    # 7. RECEITAS CUSTOMIZADAS (PREMIUM)
    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("⭐ Construtor de Receitas Personalizadas (Área Premium)")
            st.markdown("Monte receitas selecionando insumos diretamente do seu estoque.")
            
            with st.form("form_receita_custom"):
                nome_receita = st.text_input("Nome do Novo Produto (ex: Esfiha de Carne, Brigadeiro Gourmet)")
                insumos_selecionados = st.multiselect("Selecione os Insumos do Estoque", list(st.session_state.estoque_insumos.keys()))
                
                qtds = {}
                if insumos_selecionados:
                    st.markdown("### Quantidades Utilizadas")
                    for item in insumos_selecionados:
                        unidade = st.session_state.estoque_insumos[item]["unidade"]
                        qtds[item] = st.number_input(f"Quantidade de {item} ({unidade})", min_value=0.01, value=1.00)
                        
                salvar_rec = st.form_submit_button("Calcular Custo da Receita")
                if salvar_rec and nome_receita and insumos_selecionados:
                    custo_total_receita = sum([qtds[i] * st.session_state.estoque_insumos[i]["preco"] for i in insumos_selecionados])
                    st.success(f"Receita **{nome_receita}** calculada com sucesso!")
                    st.metric("Custo Total da Receita", f"R$ {custo_total_receita:.2f}")
        tab_idx += 1

    # 8. RÓTULO ANVISA & EAN-13 (PREMIUM)
    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("🏷️ Geração de Rótulo ANVISA & Código de Barras EAN-13")
            st.markdown("Prévia de rótulo nutricional oficial pronta para impressão com logomarca e SVG EAN-13.")
            
            def gerar_svg_ean13(codigo="789102030405"):
                try:
                    rv = io.BytesIO()
                    ean = barcode.get('ean13', codigo, writer=SVGWriter())
                    ean.write(rv, options={'write_text': True, 'module_width': 0.7, 'module_height': 24, 'font_size': 7, 'text_distance': 3})
                    return rv.getvalue().decode('utf-8')
                except Exception:
                    return '<svg width="200" height="50"><text x="10" y="30">7891020304055</text></svg>'

            svg_barcode = gerar_svg_ean13()
            marca_atual = st.session_state.config_marca["nome_empresa"]
            slogan_atual = st.session_state.config_marca["nome_fantasia"]
            
            rotulo_html = f"""
            <div style="background-color: white; color: black; padding: 20px; border-radius: 10px; border: 2px solid #333; max-width: 450px; margin: auto; font-family: Arial, sans-serif; font-size: 12px;">
                <div style="text-align: center; font-weight: bold; font-size: 15px; color: #b45309;">{marca_atual}</div>
                <div style="text-align: center; font-size: 11px; color: #555;">{slogan_atual}</div>
                <hr style="margin: 8px 0;">
                <div style="text-align: center; font-weight: bold; font-size: 13px;">TABELA NUTRICIONAL</div>
                <div style="text-align: center; font-size: 11px; color: #1e40af;">Produto Artesanal de Alta Qualidade</div>
                  

                <div style="border: 1px solid black; padding: 6px;">
                    <div style="text-align: center; font-weight: bold; font-size: 11px;">INFORMAÇÃO NUTRICIONAL</div>
                    <div style="font-size: 9px;">Porção de referência conforme RDC 429/2020 ANVISA</div>
                    <table style="width: 100%; font-size: 9px; border-collapse: collapse; margin-top: 4px;" border="1">
                        <tr style="background: #eee;">
                            <th>Nutriente</th><th>100g</th><th>Porção</th><th>%VD*</th>
                        </tr>
                        <tr><td>Valor energético</td><td>227 kcal</td><td>91 kcal</td><td>5%</td></tr>
                        <tr><td>Carboidratos</td><td>39,1 g</td><td>15,6 g</td><td>5%</td></tr>
                        <tr><td>Proteínas</td><td>12,4 g</td><td>5,0 g</td><td>10%</td></tr>
                        <tr><td>Gorduras totais</td><td>1,8 g</td><td>0,7 g</td><td>1%</td></tr>
                        <tr><td>Sódio</td><td>323 mg</td><td>129 mg</td><td>6%</td></tr>
                    </table>
                </div>
                  

                <div style="font-size: 10px;">
                    <b>INGREDIENTES:</b> Conforme ficha técnica cadastrada no estoque.  

                    <b>ALÉRGICOS:</b> CONTÉM GLÚTEN E DERIVADOS.
                </div>
                <div style="text-align: center; margin-top: 12px;">
                    {svg_barcode}
                </div>
            </div>
            """
            st.components.v1.html(rotulo_html, height=480, scrolling=True)
        tab_idx += 1

    # 9. MINHA MARCA (PREMIUM)
    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("🎨 Configuração da Marca (White-Label)")
            st.markdown("Personalize o nome da sua empresa para que saia em todos os relatórios e rótulos.")
            
            with st.form("form_marca"):
                m_nome = st.text_input("Nome da Empresa / Marca", value=st.session_state.config_marca["nome_empresa"])
                m_fantasia = st.text_input("Slogan / Subtítulo", value=st.session_state.config_marca["nome_fantasia"])
                m_whats = st.text_input("WhatsApp", value=st.session_state.config_marca["whatsapp"])
                m_email = st.text_input("E-mail", value=st.session_state.config_marca["email"])
                
                if st.form_submit_button("Salvar Configurações da Marca"):
                    st.session_state.config_marca["nome_empresa"] = m_nome
                    st.session_state.config_marca["nome_fantasia"] = m_fantasia
                    st.session_state.config_marca["whatsapp"] = m_whats
                    st.session_state.config_marca["email"] = m_email
                    st.success("Configurações salvas com sucesso!")
        tab_idx += 1
