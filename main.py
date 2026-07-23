import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit_authenticator as stauth
import database as db
import bcrypt

# ==========================================
# 1. INICIALIZAÇÃO DO BANCO & CONFIGURAÇÃO
# ==========================================
st.set_page_config(
    page_title="Apply Jobs - Gestão Inteligente de Vagas",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializa as tabelas no Supabase/Postgres
try:
    db.init_db()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")

# Injeção de CSS
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f172a !important;
        font-family: 'Inter', sans-serif;
        color: #f8fafc !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label { font-size: 13px; color: #94a3b8; }
    .kanban-col-header {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 15px; font-weight: 700; padding: 10px;
        border-radius: 8px; margin-bottom: 12px; text-align: center;
    }
    .kanban-card {
        background-color: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #38bdf8;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important; border: none !important; border-radius: 8px !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Modal para visualização e edição detalhada de candidatura
@st.dialog("✏️ Editar Candidatura")
def modal_editar_vaga(vaga):
    status_opcoes = ["Aplicado", "Triagem", "Entrevista", "Proposta", "Rejeitado"]
    idx_status = status_opcoes.index(vaga['status']) if vaga['status'] in status_opcoes else 0
    
    with st.form(key=f"form_edit_modal_{vaga['id']}"):
        empresa = st.text_input("Empresa", value=vaga['empresa'])
        cargo = st.text_input("Cargo", value=vaga['cargo'])
        status = st.selectbox("Status", options=status_opcoes, index=idx_status)
        link = st.text_input("Link da Vaga", value=str(vaga.get('link') or vaga.get('link_vaga') or ''))
        anotacoes = st.text_area("Anotações / Tags", value=str(vaga.get('tags') or vaga.get('anotacoes') or ''))

        if st.form_submit_button("Salvar Alterações"):
            db.atualizar_vaga(vaga['id'], empresa, cargo, status, link, anotacoes)
            st.toast("✅ Candidatura atualizada com sucesso!")
            st.rerun()

# ==========================================
# 2. SISTEMA DE LOGIN E CADASTRO
# ==========================================
if "user_info" not in st.session_state:
    st.session_state.user_info = None

def login_page():
    st.markdown('<div style="text-align: center; padding: 20px;"><div class="badge-pill">💼 APPLY JOBS</div><h1>Acesse sua Conta</h1></div>', unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
    
    with tab_login:
        with st.form("form_login"):
            username_input = st.text_input("Usuário").strip()
            password_input = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar")
            
            if btn_login:
                user = db.buscar_usuario_por_username(username_input)
                if user and bcrypt.checkpw(password_input.encode('utf-8'), user["password_hash"].encode('utf-8')):
                    st.session_state.user_info = user
                    st.success(f"Bem-vindo(a), {user['nome']}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

    with tab_register:
        with st.form("form_register"):
            new_nome = st.text_input("Nome Completo")
            new_email = st.text_input("E-mail")
            new_user = st.text_input("Nome de Usuário (Username)")
            new_pass = st.text_input("Senha", type="password")
            new_pass_confirm = st.text_input("Confirme a Senha", type="password")
            btn_register = st.form_submit_button("Criar Conta")
            
            if btn_register:
                if not new_nome or not new_email or not new_user or not new_pass:
                    st.warning("Preencha todos os campos obrigatórios.")
                elif new_pass != new_pass_confirm:
                    st.error("As senhas não coincidem.")
                else:
                    pass_hash = stauth.Hasher.hash(new_pass)
                    sucesso, msg = db.cadastrar_usuario(new_user, new_email, new_nome, pass_hash)
                    if sucesso:
                        st.success("Conta criada com sucesso! Faça login na aba ao lado.")
                    else:
                        st.error(f"Erro ao cadastrar: {msg}")

if not st.session_state.user_info:
    login_page()
    st.stop()

# ==========================================
# 3. INTERFACE PRINCIPAL (USUÁRIO LOGADO)
# ==========================================
current_user = st.session_state.user_info

with st.sidebar:
    st.markdown('<div class="badge-pill">⚡ Multi-Tenant Active</div>', unsafe_allow_html=True)
    st.title("Apply Jobs")
    st.write(f"👤 **{current_user['nome']}**")
    st.caption(f"@{current_user['username']}")
    st.markdown("---")

    menu = st.radio(
        "Navegação",
        ["📊 Dashboard", "📋 Quadro Kanban", "➕ Nova Candidatura", "✨ Otimizador ATS"],
        index=0
    )

    st.markdown("---")
    if st.button("🚪 Sair (Logout)"):
        st.session_state.user_info = None
        st.rerun()

termo_busca = st.sidebar.text_input("🔍 Busca Rápida de Vagas", placeholder="Cargo ou Empresa...")

vagas_raw = db.listar_vagas_usuario(current_user["id"], busca=termo_busca)
df_vagas = pd.DataFrame(vagas_raw) if vagas_raw else pd.DataFrame(columns=["id", "empresa", "cargo", "salario", "status", "tags", "data_aplicacao", "link"])

# ==========================================
# 4. PAINÉIS / PÁGINAS
# ==========================================
if menu == "📊 Dashboard":
    st.markdown("<h1 style='font-family: Plus Jakarta Sans;'>Dashboard Executivo</h1>", unsafe_allow_html=True)
    st.write("Acompanhe o desempenho do seu funil de contratação.")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df_vagas)}</div><div class="metric-label">Total de Aplicações</div></div>', unsafe_allow_html=True)
    with col2:
        andamento = len(df_vagas[df_vagas['status'].isin(['Aplicado', 'Triagem', 'Entrevista'])]) if not df_vagas.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{andamento}</div><div class="metric-label">Em Andamento</div></div>', unsafe_allow_html=True)
    with col3:
        entrevistas = len(df_vagas[df_vagas['status'] == 'Entrevista']) if not df_vagas.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{entrevistas}</div><div class="metric-label">Entrevistas</div></div>', unsafe_allow_html=True)
    with col4:
        propostas = len(df_vagas[df_vagas['status'] == 'Proposta']) if not df_vagas.empty else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{propostas}</div><div class="metric-label">Propostas</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if not df_vagas.empty:
        g1, g2 = st.columns([1.2, 1])
        with g1:
            st.subheader("Funil por Estágio")
            fase_counts = df_vagas['status'].value_counts().reset_index()
            fase_counts.columns = ['Status', 'Quantidade']
            fig_bar = px.bar(fase_counts, x='Status', y='Quantidade', color='Status')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8'))
            st.plotly_chart(fig_bar, use_container_width=True)
        with g2:
            st.subheader("Distribuição")
            fig_pie = px.pie(fase_counts, names='Status', values='Quantidade', hole=0.5)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc'))
            st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "📋 Quadro Kanban":
    st.markdown("<h1 style='font-family: Plus Jakarta Sans;'>Pipeline de Vagas</h1>", unsafe_allow_html=True)
    
    if termo_busca:
        st.info(f"Filtrando por: **{termo_busca}** ({len(df_vagas)} resultados)")

    fases = [
        {"nome": "Aplicado", "cor": "#38bdf8", "bg": "rgba(56, 189, 248, 0.15)"},
        {"nome": "Triagem", "cor": "#818cf8", "bg": "rgba(129, 140, 248, 0.15)"},
        {"nome": "Entrevista", "cor": "#f59e0b", "bg": "rgba(245, 158, 11, 0.15)"},
        {"nome": "Proposta", "cor": "#10b981", "bg": "rgba(16, 185, 129, 0.15)"}
    ]
    cols = st.columns(len(fases))
    status_opcoes = ["Aplicado", "Triagem", "Entrevista", "Proposta", "Rejeitado"]

    for idx, fase in enumerate(fases):
        with cols[idx]:
            st.markdown(f'<div class="kanban-col-header" style="background-color: {fase["bg"]}; color: {fase["cor"]};">{fase["nome"]}</div>', unsafe_allow_html=True)
            if not df_vagas.empty:
                vagas_fase = df_vagas[df_vagas['status'] == fase['nome']]
                for _, job in vagas_fase.iterrows():
                    link_url = job.get('link') or job.get('link_vaga') or ''
                    link_icon = f' <a href="{link_url}" target="_blank" title="Acessar anúncio" style="text-decoration:none; font-size:14px;">🔗</a>' if link_url else ''

                    st.markdown(f'''
                        <div class="kanban-card" style="border-left-color: {fase['cor']};">
                            <h4 style="margin:0;">{job['empresa']}{link_icon}</h4>
                            <p style="margin:4px 0; color:#94a3b8;">🏢 <b>{job['cargo']}</b></p>
                            <p style="font-size:12px; color:#64748b;">📅 {job.get('data_aplicacao', 'N/A')}</p>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    c_sel, c_edit = st.columns([3, 1])
                    with c_sel:
                        novo_st = st.selectbox(
                            "Mover",
                            status_opcoes,
                            index=status_opcoes.index(job['status']) if job['status'] in status_opcoes else 0,
                            key=f"k_sel_{job['id']}",
                            label_visibility="collapsed"
                        )
                        if novo_st != job['status']:
                            db.atualizar_vaga(
                                vaga_id=job['id'],
                                empresa=str(job['empresa']),
                                cargo=str(job['cargo']),
                                status=novo_st,
                                link=str(job.get('link') or job.get('link_vaga') or ''),
                                anotacoes=str(job.get('tags') or job.get('anotacoes') or '')
                            )
                            st.toast(f"Movido para {novo_st}!")
                            st.rerun()

                    with c_edit:
                        if st.button("✏️", key=f"btn_edit_card_{job['id']}", help="Editar ou ver detalhes"):
                            modal_editar_vaga(job.to_dict())

elif menu == "➕ Nova Candidatura":
    st.markdown("<h1 style='font-family: Plus Jakarta Sans;'>Cadastrar Nova Vaga</h1>", unsafe_allow_html=True)
    with st.form("form_nova_vaga", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            empresa = st.text_input("Empresa *")
            cargo = st.text_input("Cargo *")
            salario = st.text_input("Faixa Salarial")
        with c2:
            status = st.selectbox("Status Inicial", ["Aplicado", "Triagem", "Entrevista", "Proposta"])
            data_app = st.date_input("Data de Aplicação", value=datetime.now())
            link = st.text_input("Link da Vaga")
            tags = st.text_input("Tags (ex: Python, Remote)")
        
        btn_salvar = st.form_submit_button("Salvar Vaga")
        if btn_salvar:
            if not empresa or not cargo:
                st.warning("Preencha os campos obrigatórios (Empresa e Cargo).")
            else:
                duplicado = db.verificar_duplicado(current_user["id"], empresa, cargo)
                if duplicado:
                    st.error(f"⚠️ **Atenção:** Você já cadastrou a vaga de '{cargo}' na '{empresa}' em {duplicado[1]}. Status atual: **{duplicado[0]}**.")
                else:
                    db.inserir_vaga(current_user["id"], empresa, cargo, salario, link, status, tags, data_app)
                    st.success(f"Vaga de **{cargo}** na **{empresa}** cadastrada com sucesso!")

elif menu == "✨ Otimizador ATS":
    st.markdown("<h1 style='font-family: Plus Jakarta Sans;'>Otimizador ATS</h1>", unsafe_allow_html=True)
    st.info("Em breve: Integração nativa com LLM para comparação do seu CV com os requisitos da vaga.")
