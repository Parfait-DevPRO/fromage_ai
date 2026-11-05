from __future__ import annotations

import streamlit as st

from controllers.auth_controller import AuthController
from views.brand_icon import icon_html


def _login_style() -> None:
    st.markdown("""
    <style>
    .stApp {
        min-height: 100vh;
        background:
            radial-gradient(ellipse at 12% 8%, rgba(147, 197, 253, .28), transparent 34%),
            radial-gradient(ellipse at 90% 92%, rgba(191, 219, 254, .36), transparent 35%),
            #f5f8ff !important;
    }
    [data-testid="stAppViewContainer"] { background: transparent !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    .main .block-container {
        max-width: 1080px !important;
        min-height: 100vh;
        padding: 5vh 1.5rem !important;
        display: flex;
        align-items: center;
    }
    .st-key-auth_shell {
        box-sizing: border-box;
        width: 100%;
        padding: .65rem;
        overflow: hidden;
        background: rgba(255,255,255,.82);
        border: 1px solid rgba(219, 230, 247, .9);
        border-radius: 30px;
        box-shadow: 0 28px 80px rgba(37, 75, 135, .13);
        backdrop-filter: blur(16px);
    }
    .st-key-auth_shell [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
        gap: 0 !important;
    }
    .st-key-auth_shell [data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    .auth-hero {
        box-sizing: border-box;
        position: relative;
        display: flex;
        min-height: 570px;
        height: 100%;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
        padding: 2.45rem;
        color: #fff;
        background: linear-gradient(148deg, #1d5ed0 0%, #1746a2 54%, #123777 100%);
        border-radius: 23px;
    }
    .auth-hero:before, .auth-hero:after {
        position: absolute;
        content: "";
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 50%;
        pointer-events: none;
    }
    .auth-hero:before { width: 360px; height: 360px; right: -155px; top: -150px; }
    .auth-hero:after { width: 290px; height: 290px; right: -120px; top: -115px; }
    .hero-brand, .hero-copy, .hero-note { position: relative; z-index: 1; }
    .hero-brand { display: flex; align-items: center; gap: .75rem; }
    .hero-brand img {
        padding: .45rem;
        background: rgba(255,255,255,.16);
        border: 1px solid rgba(255,255,255,.24);
        border-radius: 15px;
    }
    .hero-brand strong { font-size: 1.13rem; letter-spacing: -.035em; }
    .hero-brand span {
        display: block;
        margin-top: .13rem;
        color: #dbeafe;
        font-size: .72rem;
        letter-spacing: .12em;
        text-transform: uppercase;
    }
    .hero-kicker {
        margin: 0 0 .85rem;
        color: #bfdbfe;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .hero-copy h1 {
        max-width: 390px;
        margin: 0 0 1rem;
        color: white;
        font-size: clamp(2.15rem, 3.5vw, 3.25rem);
        line-height: 1.08;
        letter-spacing: -.055em;
    }
    .hero-copy > p {
        max-width: 370px;
        margin: 0;
        color: #e0ecff;
        font-size: 1rem;
        line-height: 1.7;
    }
    .hero-points {
        display: grid;
        gap: .85rem;
        margin-top: 2rem;
    }
    .hero-point { display: flex; align-items: center; gap: .75rem; color: #f3f7ff; font-size: .9rem; }
    .hero-point i {
        display: grid;
        width: 1.6rem;
        height: 1.6rem;
        place-items: center;
        color: #dbeafe;
        background: rgba(255,255,255,.13);
        border: 1px solid rgba(255,255,255,.17);
        border-radius: 50%;
        font-size: .72rem;
        font-style: normal;
        font-weight: 700;
    }
    .hero-note {
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255,255,255,.18);
        color: #dbeafe;
        font-size: .78rem;
    }
    .st-key-auth_card {
        box-sizing: border-box;
        display: flex;
        min-height: 570px;
        flex-direction: column;
        justify-content: center;
        padding: 2.7rem clamp(1.7rem, 4vw, 3.5rem);
    }
    .st-key-auth_card .auth-eyebrow {
        margin: 0 0 .55rem;
        color: #2563eb;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .13em;
        text-transform: uppercase;
    }
    .st-key-auth_card h2 {
        margin: 0 0 .45rem;
        color: #15233b;
        font-size: 2rem;
        line-height: 1.18;
        letter-spacing: -.045em;
    }
    .st-key-auth_card .auth-subtitle {
        margin: 0 0 1.55rem;
        color: #6b7890;
        font-size: .93rem;
        line-height: 1.55;
    }
    .st-key-auth_card [data-testid="stTextInput"] { margin-bottom: .72rem; }
    .st-key-auth_card [data-testid="stTextInput"] label {
        display: block;
        margin-bottom: .35rem;
        color: #34445f !important;
        font-size: .83rem;
        font-weight: 600;
    }
    .st-key-auth_card input {
        min-height: 3.05rem;
        color: #172033 !important;
        background: #f8faff !important;
        border: 1px solid #dce5f2 !important;
        border-radius: 12px !important;
        padding: 0 .9rem !important;
        transition: border-color .16s ease, box-shadow .16s ease;
    }
    .st-key-auth_card input:focus {
        background: white !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,.13) !important;
    }
    .st-key-auth_card [data-testid="stForm"] {
        background: transparent !important;
        border: 0 !important;
        padding: 0 !important;
    }
    .st-key-auth_card [data-testid="stFormSubmitButton"] button {
        width: 100%;
        min-height: 3.05rem;
        margin-top: .45rem;
        color: #fff !important;
        background: linear-gradient(110deg, #2872e8, #1746a2) !important;
        border: 0 !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 18px rgba(37,99,235,.2);
        font-size: .94rem !important;
        font-weight: 700 !important;
        transition: transform .16s ease, box-shadow .16s ease;
    }
    .st-key-auth_card [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 11px 22px rgba(37,99,235,.27);
    }
    .st-key-auth_card [data-testid="stButton"] button {
        width: 100%;
        min-height: 2.9rem;
        color: #2457a7 !important;
        background: #fff !important;
        border: 1px solid #dbe6f5 !important;
        border-radius: 12px !important;
        font-size: .88rem !important;
        font-weight: 650 !important;
        transition: background .16s ease, border-color .16s ease;
    }
    .st-key-auth_card [data-testid="stButton"] button:hover {
        background: #f2f7ff !important;
        border-color: #a9c8f4 !important;
    }
    .st-key-auth_card [data-testid="stCaptionContainer"] p {
        margin: .4rem 0 .75rem;
        color: #78869d !important;
        font-size: .77rem;
        line-height: 1.5;
    }
    .auth-switch-note {
        margin: 1rem 0 .55rem;
        color: #8490a3;
        text-align: center;
        font-size: .78rem;
    }
    @media (max-width: 760px) {
        .main .block-container { min-height: auto; padding: 1.25rem .75rem !important; }
        .st-key-auth_shell { padding: .4rem; border-radius: 22px; }
        .auth-hero { display: none; }
        .st-key-auth_card { min-height: auto; padding: 2.2rem 1.25rem; }
        .st-key-auth_card h2 { font-size: 1.75rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        .st-key-auth_card button, .st-key-auth_card input { transition: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)


def render_login() -> bool:
    _login_style()
    auth = AuthController()
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    with st.container(key="auth_shell"):
        hero, form_column = st.columns((.94, 1.06), gap="small")
        with hero:
            st.markdown(
                f"""
                <section class="auth-hero">
                    <div class="hero-brand">
                        {icon_html(48)}
                        <div><strong>Fromazy_AI</strong><span>Votre compagnon gourmand</span></div>
                    </div>
                    <div class="hero-copy">
                        <p class="hero-kicker">Le fromage, autrement</p>
                        <h1>Chaque fromage a son histoire.</h1>
                        <p>Identifiez vos découvertes, comprenez leurs particularités et trouvez l'inspiration pour les savourer.</p>
                        <div class="hero-points">
                            <div class="hero-point"><i>01</i> Des réponses adaptées à vos fromages</div>
                            <div class="hero-point"><i>02</i> Une analyse simple, à partir d'une photo</div>
                            <div class="hero-point"><i>03</i> Vos échanges réunis au même endroit</div>
                        </div>
                    </div>
                    <div class="hero-note">Curieux de fromage ? Vous êtes au bon endroit.</div>
                </section>
                """,
                unsafe_allow_html=True,
            )

        with form_column:
            with st.container(key="auth_card"):
                if st.session_state.auth_mode != "signup":
                    st.markdown(
                        '<p class="auth-eyebrow">Bienvenue chez Fromazy_AI</p>'
                        '<h2>Ravi de vous revoir.</h2>'
                        '<p class="auth-subtitle">Connectez-vous pour retrouver vos conversations et continuer vos découvertes.</p>',
                        unsafe_allow_html=True,
                    )
                    with st.form("login_form"):
                        st.text_input("Nom d’utilisateur", placeholder="Votre nom d’utilisateur", key="login_username")
                        st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe", key="login_password")
                        submitted = st.form_submit_button("Se connecter", use_container_width=True)
                    if submitted:
                        try:
                            st.session_state.user = auth.sign_in(
                                st.session_state.login_username,
                                st.session_state.login_password,
                            )
                            return True
                        except (ValueError, RuntimeError) as exc:
                            st.error(str(exc))
                    st.markdown('<p class="auth-switch-note">Nouveau sur Fromazy_AI ?</p>', unsafe_allow_html=True)
                    if st.button("Créer mon compte", key="show_signup", use_container_width=True):
                        st.session_state.auth_mode = "signup"
                        st.rerun()
                else:
                    st.markdown(
                        '<p class="auth-eyebrow">Un compte, de belles découvertes</p>'
                        '<h2>Créez votre espace.</h2>'
                        '<p class="auth-subtitle">Quelques secondes suffisent pour commencer votre aventure fromagère.</p>',
                        unsafe_allow_html=True,
                    )
                    with st.form("signup_form"):
                        st.text_input("Nom d’utilisateur", placeholder="Choisissez un nom d’utilisateur", key="signup_username")
                        st.text_input("Mot de passe", type="password", placeholder="6 caractères minimum", key="signup_password")
                        st.text_input("Confirmer le mot de passe", type="password", placeholder="Répétez le mot de passe", key="signup_confirmation")
                        st.caption("3 à 30 caractères pour le nom (lettres, chiffres, _, . ou -) ; 6 caractères minimum pour le mot de passe.")
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
                    st.markdown('<p class="auth-switch-note">Vous avez déjà un compte ?</p>', unsafe_allow_html=True)
                    if st.button("Me connecter", key="show_login", use_container_width=True):
                        st.session_state.auth_mode = "login"
                        st.rerun()
    return False
