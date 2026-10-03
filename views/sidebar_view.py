from __future__ import annotations
import streamlit as st
from views.brand_icon import icon_html


def render_sidebar(conversations: list[dict], active_id: str):
    with st.sidebar:
        st.markdown(f'<div style="font-size:1.25rem;font-weight:700">{icon_html(28)}&nbsp; Fromazy_AI</div>', unsafe_allow_html=True)
        st.caption("ESPACE DE TRAVAIL")
        new = st.button("＋  Nouvelle conversation", type="primary", use_container_width=True)
        st.caption("RÉCENT")
        selected = active_id
        for conversation in conversations:
            label = ("●  " if conversation["id"] == active_id else "◦  ") + conversation["title"]
            if st.button(label, key="conv_" + conversation["id"], use_container_width=True):
                selected = conversation["id"]
        st.divider()
        st.caption("À PROPOS")
        st.caption("Assistant de découverte et d’analyse des fromages.")
        st.caption("Les analyses sont indicatives : vérifiez toujours l’état réel de l’aliment.")
        st.divider()
        user = st.session_state.get("user")
        if user:
            st.caption(f"Connecté : {getattr(user, 'username', 'utilisateur')}")
        logout = st.button("Se déconnecter", key="logout", use_container_width=True)
        return new, selected, logout
