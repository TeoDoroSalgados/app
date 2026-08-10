import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="TeoDoro's Salgados - Sistema de Custos",
    page_icon="🥟",
    layout="wide",
)

# --- SISTEMA DE LICENÇAS E PLANOS ---
# Em um cenário real, estas chaves podem vir de um arquivo ou banco simples.
# Prefixo ou tipo define o plano: 'INI' (Iniciante), 'PRO' (Profissional), 'PREM' (Premium)
LICENCAS = {
    "INI-1020-TESTE": {"plano": "Iniciante", "nome": "Cliente Iniciante"},
    "PRO-3040-TESTE": {"plano": "Profissional", "nome": "Salgaderia Pro"},
    "PREM-5060-TESTE": {"plano": "Premium", "nome": "Fábrica Premium"}
}

st.sidebar.header("🔐 Acesso à Assinatura")

# Estado da sessão para manter o usuário logado
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False
    st.session_state.plano_atual = "Gratuito (Visitante)"
    st.session_state.nome_cliente = ""

# Se não estiver logado, exibe tela de ativação de licença
if not st.session_state.usuario_logado:
    st.sidebar.markdown("Digite sua **Chave de Licença** enviada após a assinatura:")
    chave_input = st.sidebar.text_input("Chave de Licença", type="password")
    
    if st.sidebar.button("Ativar Acesso"):
        if chave_input in LICENCAS:
            st.session_state.usuario_logado = True
            st.session_state.plano_atual = LICENCAS[chave_input]["plano"]
            st.session_state.nome_cliente = LICENCAS[chave_input]["nome"]
            st.sidebar.success(f"Bem-vindo(a), {st.session_state.nome_cliente}!")
            st.rerun()
        else:
            st.sidebar.error("❌ Chave inválida. Verifique com o suporte.")
    
    st.sidebar.info("💡 **Não tem uma chave?**\nEscolha seu plano:\n- **Iniciante:** R$ 17/mês\n- **Profissional:** R$ 39/mês\n- **Premium:** R$ 79/mês")
    plano_ativo = "Gratuito"
else:
    st.sidebar.success(f"Plano Ativo: **{st.session_state.plano_atual}**")
    if st.sidebar.button("Sair / Trocar Chave"):
        st.session_state.usuario_logado = False
        st.session_state.plano_atual = "Gratuito"
        st.rerun()
    plano_ativo = st.session_state.plano_atual

# --- CONTEÚDO PRINCIPAL DO APLICATIVO COM BASE NO PLANO ---
st.title("🥟 TeoDoro's Salgados - Sistema de Custos & Precificação")

if plano_ativo == "Gratuito":
    st.warning("⚠️ Você está visualizando o modo de demonstração. Insira uma chave de licença válida na barra lateral para liberar os recursos do seu plano.")

# Definindo o que cada plano pode acessar
permite_profissional = plano_ativo in ["Profissional", "Premium"]
permite_premium = plano_ativo == "Premium"

# Abas do Sistema
tabs = ["📊 Ficha Técnica Básica"]
if permite_profissional:
    tabs.append("💰 Precificação, Markup & Ponto de Equilíbrio")
if permite_premium:
    tabs.append("⭐ Construtor de Receitas Personalizadas (Área Premium)")
    tabs.append("🏷️ Rótulo ANVISA Completo (PDF)")

selected_tab = st.tabs(tabs)

# --- ABA 1: FICHA TÉCNICA BÁSICA (Disponível para todos, inclusive Iniciante) ---
with selected_tab[0]:
    st.header("Ficha Técnica - Mini Coxinha Padrão")
    st.markdown("Cálculo básico de insumos por quilo e unidade.")
    
    chicken_price = st.number_input("Preço do Peito de Frango (kg)", value=18.00)
    flour_price = st.number_input("Preço da Farinha de Trigo (kg)", value=5.00)
    
    total_custo_basico = chicken_price * 0.3 + flour_price * 4.0
    st.metric("Custo Estimado dos Ingredientes Principais", f"R$ {total_custo_basico:.2f}")

    if plano_ativo == "Iniciante":
        st.info("🔒 **Faça um upgrade para o Plano Profissional (R$ 39/mês)** para desbloquear o cálculo completo de Markup, Lucro e Ponto de Equilíbrio!")

# --- ABA 2: PROFISSIONAL (Markup e Break-Even) ---
if permite_profissional:
    with selected_tab[1]:
        st.header("Módulo Profissional: Precificação & Ponto de Equilíbrio")
        fixed_costs = st.number_input("Custos Fixos Mensais (Aluguel, Energia, etc.)", value=1500.00)
        profit_margin = st.slider("Margem de Lucro Desejada (%)", 10, 50, 30)
        st.success("✅ Módulo Profissional Ativo! Seus cálculos avançados estão liberados.")

# --- ABA 3: PREMIUM (Receitas Personalizadas e Rótulos) ---
if permite_premium:
    with selected_tab[2]:
        st.header("⭐ Construtor de Receitas Personalizadas (Área Premium)")
        st.markdown("Cadastre seus próprios ingredientes, pesos e rendimentos livremente.")
        nome_novo_salgado = st.text_input("Nome do Salgado (ex: Esfiha, Quibe)", value="Esfiha Especial")
        st.button("Salvar e Calcular Nova Receita")

    with selected_tab[3]:
        st.header("🏷️ Geração de Rótulo ANVISA Oficial")
        st.markdown("Prévia do rótulo 100x150mm com logomarca e código de barras EAN-13 pronto para impressão.")
        st.success("✅ Geração de etiquetas profissionais liberada para o plano Premium.")

