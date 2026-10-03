from __future__ import annotations
import streamlit as st
from views.components.chat_message import render_message
from views.brand_icon import icon_html


def render_chat(messages: list[dict]) -> None:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:.65rem;font-size:2rem;font-weight:700;line-height:1.2;margin:.3rem 0 1rem">{icon_html(42)}<span>Fromazy_AI</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Décrivez votre fromage ou envoyez une photo pour obtenir une explication claire.")
    for message in messages:
        render_message(message)
