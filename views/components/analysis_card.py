from __future__ import annotations
import streamlit as st
from views.brand_icon import icon_html


def render_analysis(analysis: dict) -> None:
    if not analysis.get("is_cheese"):
        st.warning(analysis.get("message", "Cette image ne peut pas être analysée comme fromage."))
        return
    label = analysis["predicted_class"].replace("_", " ").title()
    confidence = analysis.get("confidence_text") or str(float(analysis["confidence"]))
    st.markdown(f'{icon_html(22)}&nbsp; **Analyse du modèle**\n\n**Résultat principal : {label}**  \nScore du modèle : **{confidence} %**', unsafe_allow_html=True)
    for name, score in sorted(analysis["probabilities"].items(), key=lambda item: item[1], reverse=True):
        display = analysis.get("probabilities_text", {}).get(name, str(float(score)))
        st.progress(min(max(score / 100, 0.0), 1.0), text=f"{name.replace('_', ' ').title()} : {display} %")
    st.caption("Ces scores sont des probabilités visuelles du modèle et non une certitude sanitaire.")
