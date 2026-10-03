from __future__ import annotations

import streamlit as st

from controllers.auth_controller import AuthController
from views.brand_icon import icon_html


def _login_style() -> None:
    st.markdown("""
    <style>
    .stApp { min-height:100vh; background:linear-gradient(135deg,#f4f7fc 0%,#e8eff9 100%) !important; }
    [data-testid="stAppViewContainer"] { background:transparent !important; }
    .main .block-container { max-width:390px !important; padding:4vh 1rem 2rem !important; }
    [data-testid="stHorizontalBlock"] { align-items:center !important; gap:0 !important; }
    [data-testid="stVerticalBlockBorderWrapper"] { background:transparent !important; border:0 !important; box-shadow:none !important; padding:0 !important; }
    .st-key-auth_card { box-sizing:border-box; width:100%; padding:1.35rem 1.35rem 1.2rem; background:rgba(255,255,255,.96); border:1px solid #e1e8f2; border-radius:22px; box-shadow:0 18px 48px rgba(35,60,100,.13); }
    .st-key-auth_card .brand-lockup { display:flex; flex-direction:row; align-items:center; justify-content:center; gap:.55rem; margin:0 0 .3rem; }
    .st-key-auth_card .brand-lockup span { color:#1746a2; font-size:1.45rem; font-weight:800; letter-spacing:-.05em; }
    .st-key-auth_card .brand-tagline { color:#64748b; text-align:center; font-size:.82rem; line-height:1.4; margin:0 0 1rem; }
    .st-key-auth_card h2 { color:#172033; font-size:1.3rem; margin:0 0 .65rem; text-align:center; }
    .st-key-auth_card .auth-subtitle { color:#64748b; text-align:center; margin:0 0 .8rem; font-size:.85rem; }
    .st-key-auth_card [data-testid="stTextInput"] label { display:none; }
    .st-key-auth_card input { min-height:3rem; background:#f8faff !important; border:1px solid #d9e2f0 !important; border-radius:11px !important; color:#1c1e21 !important; padding:0 .85rem !important; }
    .st-key-auth_card input:focus { border-color:#1877f2 !important; box-shadow:0 0 0 2px #e7f3ff !important; }
    .st-key-auth_card [data-testid="stForm"] { background:transparent !important; border:0 !important; padding:0 !important; }
    .st-key-auth_card [data-testid="stFormSubmitButton"] button { width:100%; min-height:2.85rem; background:linear-gradient(135deg,#2563eb,#1746a2) !important; border:0 !important; border-radius:11px !important; color:#fff !important; font-size:.98rem !important; font-weight:700 !important; box-shadow:0 5px 14px rgba(37,99,235,.2); }
    .st-key-auth_card [data-testid="stFormSubmitButton"] button:hover { background:#fff !important; color:#1877f2 !important; }
    .st-key-auth_card [data-testid="stButton"] button { min-height:2.65rem; background:#fff !important; border:1px solid #d5e1f2 !important; border-radius:11px !important; color:#1746a2 !important; font-weight:700 !important; }
    .st-key-auth_card [data-testid="stButton"] button:hover { background:#eaf3ff !important; }
    .st-key-auth_card [data-testid="stCaptionContainer"] p { color:#606770 !important; text-align:center; }
    .auth-divider { border-top:1px solid #dadde1; margin:.7rem 0 1rem; }
    @media(max-width:760px) { .main .block-container { max-width:390px !important; padding:2rem 1rem !important; } .st-key-auth_card { padding:1.25rem 1.1rem 1rem; } }
    </style>
    """, unsafe_allow_html=True)


def render_login() -> bool:
    _login_style()
    auth = AuthController()
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    _, center, _ = st.columns((1, 2, 1))
    with center:
        with st.container(key="auth_card"):
            st.markdown(
                f'<div class="brand-lockup">{icon_html(58)}<span>Fromazy_AI</span></div>'
                '<p class="brand-tagline">Comprenez vos fromages et recevez des conseils.</p>',
                unsafe_allow_html=True,
            )
            if st.session_state.auth_mode != "signup":
                st.markdown("<h2>Connexion</h2>", unsafe_allow_html=True)
                with st.form("login_form"):
                    st.text_input("Nom d’utilisateur", placeholder="Nom d’utilisateur", key="login_username")
                    st.text_input("Mot de passe", type="password", placeholder="Mot de passe", key="login_password")
                    submitted = st.form_submit_button("Se connecter", use_container_width=True)
                if submitted:
                    try:
                        st.session_state.user = auth.sign_in(st.session_state.login_username, st.session_state.login_password)
                        return True
                    except (ValueError, RuntimeError) as exc:
                        st.error(str(exc))
                st.caption("Mot de passe oublié ?")
                st.markdown('<div class="auth-divider"></div>', unsafe_allow_html=True)
                if st.button("Créer un compte", key="show_signup", use_container_width=True):
                    st.session_state.auth_mode = "signup"
                    st.rerun()
            else:
                st.markdown('<h2>Créer un compte</h2><p class="auth-subtitle">Rejoignez Fromazy_AI</p>', unsafe_allow_html=True)
                with st.form("signup_form"):
                    st.text_input("Nom d’utilisateur", placeholder="Choisissez un nom d’utilisateur", key="signup_username")
                    st.text_input("Mot de passe", type="password", placeholder="8 caractères minimum", key="signup_password")
                    st.text_input("Confirmer le mot de passe", type="password", placeholder="Répétez le mot de passe", key="signup_confirmation")
                    st.caption("Lettres, chiffres, _, . et - sont acceptés.")
                    submitted = st.form_submit_button("Créer mon compte", use_container_width=True)
                if submitted:
                    username = st.session_state.signup_username
                    password = st.session_state.signup_password
                    confirmation = st.session_state.signup_confirmation
                    if password != confirmation:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        try:
                            st.session_state.user = auth.sign_up(username, password)
                            return True
                        except (ValueError, RuntimeError) as exc:
                            st.error(str(exc))
                if st.button("J’ai déjà un compte : me connecter", key="show_login", use_container_width=True):
                    st.session_state.auth_mode = "login"
                    st.rerun()
    return False
