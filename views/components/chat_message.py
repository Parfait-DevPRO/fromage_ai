from __future__ import annotations
import streamlit as st
from views.brand_icon import icon_html
from views.components.analysis_card import render_analysis


def render_message(message: dict) -> None:
    # L'alignement reste explicite quel que soit le thème Streamlit.
    is_user = message["role"] == "user"
    left, right = st.columns((2, 5) if is_user else (5, 2))
    column = right if is_user else left

    # Seuls les messages envoyés ont une carte : Fromazy_AI reste léger.
    container = column.container(border=is_user)
    with container:
        if is_user:
            st.caption("Vous")
        else:
            st.markdown(f'<div style="font-size:.8rem;color:#2563eb;font-weight:600">{icon_html(18)}&nbsp; Fromazy_AI</div>', unsafe_allow_html=True)
        if message.get("image"):
            st.image(message["image"], width=260)
        if message.get("content"):
            st.markdown(message["content"])
        if message.get("analysis"):
            render_analysis(message["analysis"])
        elif message.get("has_image"):
            st.caption("Image jointe à ce message (l’image elle-même n’est pas archivée).")
