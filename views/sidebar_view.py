from __future__ import annotations
import streamlit as st
from views.brand_icon import icon_html


def render_sidebar(conversations: list[dict], active_id: str):
    with st.sidebar:
        st.markdown(
            f'<div style="font-size:1.25rem;font-weight:700;display:flex;align-items:center;gap:0.5rem;margin-bottom:0.8rem;">{icon_html(28)}<span>Fromazy_AI</span></div>',
            unsafe_allow_html=True,
        )
        new = st.button("＋  Nouvelle conversation", type="primary", use_container_width=True)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        st.caption("DISCUSSIONS RÉCENTES")
        selected = active_id
        delete_id = None
        for conversation in conversations:
            label = ("●  " if conversation["id"] == active_id else "◦  ") + conversation["title"]
            title_col, delete_col = st.columns([0.84, 0.16], vertical_alignment="center")
            with title_col:
                if st.button(label, key="conv_" + conversation["id"], use_container_width=True):
                    selected = conversation["id"]
            with delete_col:
                if st.button("×", key="delete_" + conversation["id"], help="Supprimer cette conversation"):
                    delete_id = conversation["id"]

        st.divider()
        st.caption("À PROPOS")
        st.caption("Assistant intelligent de découverte et d’analyse des fromages.")
        st.caption("Les analyses visuelles sont indicatives et basées sur l'apprentissage automatique.")
        st.divider()

        user = st.session_state.get("user")
        if user:
            username = getattr(user, "username", "utilisateur")
            initial = (username[0] if username else "U").upper()
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.65rem; padding: 0.55rem 0.7rem; background: #F8FAFC; border-radius: 12px; margin-bottom: 0.75rem; border: 1px solid #E2E8F0;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; box-shadow: 0 2px 6px rgba(37,99,235,0.25);">
                    {initial}
                </div>
                <div style="overflow: hidden; flex: 1;">
                    <div style="font-weight: 650; font-size: 0.86rem; color: #0F172A; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{username}</div>
                    <div style="font-size: 0.72rem; color: #16A34A; font-weight: 600; display: flex; align-items: center; gap: 0.3rem;">
                        <span style="font-size: 8px;">●</span> Supabase Cloud
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        logout = st.button("Se déconnecter", key="logout", use_container_width=True)
        return new, selected, logout, delete_id
