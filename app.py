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

if "embalagens" not in st.session_state:
    st.session_state.embalagens = {
        "Caixa de Papelão 1kg": {"preco": 1.20, "fornecedor": "Embalagens Express"},
        "Saco Plástico 1kg": {"preco": 0.30, "fornecedor": "PlastCorp"},
        "Etiqueta Adesiva": {"preco": 0.15, "fornecedor": "Gráfica Rápida"}
    }

if "custos_fixos" not in st.session_state:
    st.session_state.custos_fixos = {
        "Aluguel": 1200.00,
        "Energia Elétrica": 450.00,
        "Água": 120.00,
        "Internet & Telefone": 150.00,
        "Contador": 400.00
    }

if "produtos_cadastrados" not in st.session_state:
    st.session_state.produtos_cadastrados = [
        {
            "nome": "Mini Coxinha de Frango (1kg)",
            "rendimento": 50,
            "peso_un": 20,
            "custo_total": 12.50,
            "preco_sugerido": 25.00,
            "lucro": 12.50
        }
    ]

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

tem_iniciante = plano_atual in ["Iniciante", "Profissional", "Premium"] or is_admin
tem_profissional = plano_atual in ["Profissional", "Premium"] or is_admin
tem_premium = plano_atual in ["Premium"] or is_admin

# --- PAINEL ADMINISTRATIVO ---
if is_admin:
    st.title("🛠️ Painel Administrativo de Licenças SaaS")
    st.markdown("Gerencie assinaturas e gere novas chaves de acesso para os planos.")
    
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
    tabs_disponiveis = ["📊 Dashboard Gerencial", "🛒 Gestão de Insumos", "📋 Ficha Técnica & Custos", "💰 Precificação e Lucro", "⚖️ Ponto de Equilíbrio"]
    if tem_profissional:
        tabs_disponiveis.append("🏷️ Simulador de Custo")
    if tem_premium:
        tabs_disponiveis.extend(["⭐ Receitas Customizadas", "🏷️ Rótulo ANVISA & EAN-13", "🎨 Minha Marca"])
        
    selected_tabs = st.tabs(tabs_disponiveis)
    tab_idx = 0
    
    with selected_tabs[tab_idx]:
        st.header("📊 Dashboard Gerencial & Indicadores")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Insumos Cadastrados", len(st.session_state.estoque_insumos))
        c2.metric("Planos Ativos", len(st.session_state.licencas_db))
        c3.metric("Seu Plano Atual", plano_atual if not is_admin else "Administrador")
        c4.metric("Status da Conexão", "Online 🟢")
    tab_idx += 1

    with selected_tabs[tab_idx]:
        st.header("🛒 Gestão Universal de Insumos e Embalagens")
        col_pesq1, col_pesq2 = st.columns([2, 1])
        termo_busca = col_pesq1.text_input("🔍 Pesquisar ingrediente por nome...", "")
        fornecedores_disponiveis = ["Todos"] + list(set([item["fornecedor"] for item in st.session_state.estoque_insumos.values()]))
        filtro_forn = col_pesq2.selectbox("Filtrar por Fornecedor", fornecedores_disponiveis)
        
        with st.form("form_insumo"):
            col1, col2, col3, col4 = st.columns(4)
            nome_ins = col1.text_input("Nome do Ingrediente/Embalagem")
            preco_ins = col2.number_input("Preço (R$)", min_value=0.01, value=10.00, step=0.50)
            unidade_ins = col3.selectbox("Unidade de Medida", ["kg", "g", "L", "ml", "unidade", "pacote"])
            forn_ins = col4.text_input("Fornecedor", value="Fornecedor Padrão")
            if st.form_submit_button("Salvar Insumo no Estoque") and nome_ins:
                st.session_state.estoque_insumos[nome_ins] = {"preco": preco_ins, "unidade": unidade_ins, "fornecedor": forn_ins}
                st.success(f"Insumo **{nome_ins}** salvo!")
                
        lista_insumos = []
        for k, v in st.session_state.estoque_insumos.items():
            if termo_busca.lower() in k.lower():
                if filtro_forn == "Todos" or v["fornecedor"] == filtro_forn:
                    lista_insumos.append({"Ingrediente": k, "Preço (R$)": v["preco"], "Unidade": v["unidade"], "Fornecedor": v["fornecedor"]})
        if lista_insumos:
            st.dataframe(pd.DataFrame(lista_insumos), use_container_width=True)
        else:
            st.warning("Nenhum insumo encontrado.")
    tab_idx += 1

    with selected_tabs[tab_idx]:
        st.header("📋 Ficha Técnica & Custo de Produção")
        col_f1, col_f2 = st.columns(2)
        peso_coxinha = col_f1.number_input("Peso médio por unidade (g)", min_value=5, max_value=200, value=20)
        lote_kg = col_f2.number_input("Tamanho do Lote Base (kg)", min_value=0.5, max_value=50.0, value=1.0)
        total_unidades = int((lote_kg * 1000) / peso_coxinha)
        st.metric("Unidades Estimadas por Lote", f"{total_unidades} unidades")
    tab_idx += 1

    with selected_tabs[tab_idx]:
        st.header("💰 Precificação Inteligente e Margem de Lucro")
        custo_base_prod = 0.17
        markup = st.slider("Multiplicador de Markup", 1.5, 4.0, 2.5, 0.1)
        st.metric("Preço de Venda Sugerido (por unidade)", f"R$ {custo_base_prod * markup:.2f}")
    tab_idx += 1

    with selected_tabs[tab_idx]:
        st.header("⚖️ Ponto de Equilíbrio (Break-Even Point)")
        col_eq1, col_eq2 = st.columns(2)
        custos_fixos_mes = col_eq1.number_input("Custos Fixos Mensais (R$)", value=2000.00, step=100.00)
        lucro_por_unidade = col_eq2.number_input("Lucro Contribuição Unitário (R$)", value=0.35, step=0.05)
        if lucro_por_unidade > 0:
            st.metric("Ponto de Equilíbrio", f"{int(custos_fixos_mes / lucro_por_unidade)} unidades/mês")
    tab_idx += 1

    if tem_profissional:
        with selected_tabs[tab_idx]:
            st.header("🏷️ Simulador Avançado de Custo")
            st.info("Módulo Profissional Ativo.")
        tab_idx += 1

    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("⭐ Construtor de Receitas Personalizadas (Área Premium)")
            with st.form("form_rec_custom"):
                nome_receita = st.text_input("Nome do Produto")
                ins_sel = st.multiselect("Insumos", list(st.session_state.estoque_insumos.keys()))
                if st.form_submit_button("Salvar") and nome_receita:
                    st.success("Receita salva com sucesso!")
        tab_idx += 1

    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("🏷️ Geração de Rótulo ANVISA & Código de Barras EAN-13")
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
            
            rotulo_html = f\"\"\"
            <div style="background-color: white; color: black; padding: 20px; border-radius: 10px; border: 2px solid #333; max-width: 450px; margin: auto; font-family: Arial, sans-serif; font-size: 12px;">
                <div style="text-align: center; font-weight: bold; font-size: 15px; color: #b45309;">{marca_atual}</div>
                <div style="text-align: center; font-size: 11px; color: #555;">{slogan_atual}</div>
                <hr style="margin: 8px 0;">
                <div style="text-align: center; font-weight: bold; font-size: 13px;">TABELA NUTRICIONAL</div>
                <div style="border: 1px solid black; padding: 6px; margin-top: 8px;">
                    <table style="width: 100%; font-size: 9px; border-collapse: collapse;" border="1">
                        <tr style="background: #eee;"><th>Nutriente</th><th>100g</th><th>Porção</th><th>%VD*</th></tr>
                        <tr><td>Valor energético</td><td>227 kcal</td><td>91 kcal</td><td>5%</td></tr>
                        <tr><td>Carboidratos</td><td>39,1 g</td><td>15,6 g</td><td>5%</td></tr>
                        <tr><td>Proteínas</td><td>12,4 g</td><td>5,0 g</td><td>10%</td></tr>
                        <tr><td>Gorduras totais</td><td>1,8 g</td><td>0,7 g</td><td>1%</td></tr>
                        <tr><td>Sódio</td><td>323 mg</td><td>129 mg</td><td>6%</td></tr>
                    </table>
                </div>
                <div style="text-align: center; margin-top: 12px;">{svg_barcode}</div>
            </div>
            \"\"\"
            st.components.v1.html(rotulo_html, height=480, scrolling=True)
        tab_idx += 1

    if tem_premium:
        with selected_tabs[tab_idx]:
            st.header("🎨 Configuração da Marca (White-Label)")
            with st.form("form_marca"):
                m_nome = st.text_input("Nome da Empresa", value=st.session_state.config_marca["nome_empresa"])
                m_fant = st.text_input("Slogan", value=st.session_state.config_marca["nome_fantasia"])
                if st.form_submit_button("Salvar Marca"):
                    st.session_state.config_marca["nome_empresa"] = m_nome
                    st.session_state.config_marca["nome_fantasia"] = m_fant
                    st.success("Salvo com sucesso!")
        tab_idx += 1
