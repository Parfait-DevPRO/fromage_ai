from __future__ import annotations
import streamlit as st
from views.components.chat_message import render_message
from views.brand_icon import icon_html


def render_chat(messages: list[dict]) -> None:
    if not messages:
        st.markdown("""
        <div style="text-align: center; padding: 2.2rem 1rem 1.2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 62px; height: 62px; border-radius: 20px; background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%); box-shadow: 0 10px 25px rgba(37,99,235,0.25); margin-bottom: 1.1rem;">
                <span style="font-size: 30px;">🧀</span>
            </div>
            <h2 style="font-size: 1.85rem; font-weight: 750; color: #0F172A; margin: 0 0 0.4rem; letter-spacing: -0.02em;">
                Bonjour ! Comment puis-je vous aider ?
            </h2>
            <p style="color: #64748B; font-size: 0.95rem; max-width: 540px; margin: 0 auto 1.8rem; line-height: 1.5;">
                Fromazy_AI combine la vision par ordinateur et l'IA pour reconnaître, évaluer la qualité et répondre à toutes vos questions fromagères.
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02); margin-bottom: 0.75rem; border-left: 3px solid #2563EB;">
                <div style="font-weight: 650; color: #1E293B; font-size: 0.9rem; margin-bottom: 0.2rem;">📷 Analyse visuelle par photo</div>
                <div style="font-size: 0.82rem; color: #64748B; line-height: 1.4;">Joignez une image ci-dessous pour analyser son aspect : sain, desséché, fissuré ou moisissure.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02); border-left: 3px solid #3B82F6;">
                <div style="font-weight: 650; color: #1E293B; font-size: 0.9rem; margin-bottom: 0.2rem;">🍷 Accords mets & vins</div>
                <div style="font-size: 0.82rem; color: #64748B; line-height: 1.4;">Demandez les meilleurs vins, pains ou fruits pour sublimer votre plateau de fromages.</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02); margin-bottom: 0.75rem; border-left: 3px solid #2563EB;">
                <div style="font-weight: 650; color: #1E293B; font-size: 0.9rem; margin-bottom: 0.2rem;">❄️ Conservation & Hygiène</div>
                <div style="font-size: 0.82rem; color: #64748B; line-height: 1.4;">Apprenez à bien conserver vos fromages au réfrigérateur et à repérer les altérations.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02); border-left: 3px solid #3B82F6;">
                <div style="font-weight: 650; color: #1E293B; font-size: 0.9rem; margin-bottom: 0.2rem;">🧀 Histoire & Fabrication</div>
                <div style="font-size: 0.82rem; color: #64748B; line-height: 1.4;">Découvrez l'origine, le terroir et les étapes d'affinage de vos fromages préférés.</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:.65rem;font-size:1.45rem;font-weight:700;line-height:1.2;margin:.2rem 0 .75rem">{icon_html(30)}<span>Fromazy_AI</span></div>',
            unsafe_allow_html=True,
        )
        for message in messages:
            render_message(message)
