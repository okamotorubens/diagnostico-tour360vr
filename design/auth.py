"""Login compartilhado (Supabase Auth) para Gestão e Radar."""
import streamlit as st
from supabase import create_client
from design.components import section_title, glass_container


def _cliente_auth():
    if "auth_client" not in st.session_state:
        st.session_state["auth_client"] = create_client(
            st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"]
        )
    return st.session_state["auth_client"]


def exigir_login(titulo: str = "Acesso restrito", chave: str = "usuario_logado"):
    """Chame após inject_theme(). Interrompe a página enquanto não houver login."""
    if chave in st.session_state:
        return st.session_state[chave]

    section_title(f"🔐 {titulo}")
    with glass_container():
        with st.form(f"form_login_{chave}"):
            email = st.text_input("E-mail")
            senha = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar")
    if entrar:
        try:
            res = _cliente_auth().auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state[chave] = res.user.email
            st.rerun()
        except Exception:
            st.error("E-mail ou senha inválidos.")
    st.stop()


def barra_usuario(chave: str = "usuario_logado"):
    """Mostra 'Conectado como ... [Sair]' no topo."""
    st.markdown(
        "<style>div[data-testid='stHorizontalBlock']:has(.gl-logout) button"
        "{min-height:30px !important;height:auto !important;padding:2px 14px !important;"
        "font-size:.78rem !important;width:auto !important;}</style>",
        unsafe_allow_html=True,
    )
    col_u, col_s = st.columns([9, 1.4])
    with col_u:
        st.markdown(
            f"<div class='gl-user'><span class='gl-logout'></span>Conectado como "
            f"<b>{st.session_state[chave]}</b></div>",
            unsafe_allow_html=True,
        )
    with col_s:
        if st.button("Sair", key=f"sair_{chave}"):
            try:
                _cliente_auth().auth.sign_out()
            except Exception:
                pass
            for k in [chave, "auth_client"]:
                st.session_state.pop(k, None)
            st.rerun()
