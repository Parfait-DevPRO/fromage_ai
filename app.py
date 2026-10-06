from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta, timezone
from config.settings import secret
from services.api_usage_service import today_count

from controllers.analysis_controller import AnalysisController
from controllers.chat_controller import ChatController
from services.conversation_service import ConversationService
from views.chat_view import render_chat
from views.login_view import render_login
from views.sidebar_view import render_sidebar
from views.styles import inject_custom_styles

st.set_page_config(page_title="Fromazy_AI", page_icon="assets/cheese_icon.svg", layout="wide")


def init_state(user_id: str) -> None:
    owner_changed = st.session_state.get("conversation_owner") != user_id
    last_cleanup = st.session_state.get("conversation_cleanup_at")
    cleanup_due = owner_changed or not last_cleanup or datetime.now(timezone.utc) - last_cleanup >= timedelta(hours=1)
    if cleanup_due:
        ConversationService.purge_expired(user_id, retention_days=3)
        st.session_state.conversation_cleanup_at = datetime.now(timezone.utc)
    if cleanup_due:
        conversations = ConversationService.load_for_user(user_id)
        st.session_state.conversations = conversations
        st.session_state.active_id = conversations[0]["id"]
        st.session_state.conversation_owner = user_id


def current() -> dict:
    return next(c for c in st.session_state.conversations if c["id"] == st.session_state.active_id)


if not st.session_state.get("user"):
    if render_login():
        st.rerun()
    st.stop()

try:
    init_state(st.session_state.user.id)
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

inject_custom_styles()

new, selected, logout, delete_id = render_sidebar(st.session_state.conversations, st.session_state.active_id)
if logout:
    st.session_state.pop("user", None)
    st.session_state.pop("conversation_owner", None)
    st.rerun()
if delete_id:
    try:
        ConversationService.delete(st.session_state.user.id, delete_id)
        st.session_state.conversations = [c for c in st.session_state.conversations if c["id"] != delete_id]
        if not st.session_state.conversations:
            st.session_state.conversations = [ConversationService.new_conversation(st.session_state.user.id)]
        if st.session_state.active_id == delete_id:
            st.session_state.active_id = st.session_state.conversations[0]["id"]
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    st.rerun()
if new:
    try:
        conversation = ConversationService.new_conversation(st.session_state.user.id)
        st.session_state.conversations.insert(0, conversation)
        st.session_state.active_id = conversation["id"]
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    st.rerun()
if selected != st.session_state.active_id:
    st.session_state.active_id = selected
    st.rerun()

conversation = current()
daily_limit = int(secret("GEMINI_DAILY_LIMIT", "1500"))
remaining = max(daily_limit - today_count(), 0)
st.markdown(
    f"<div style='text-align:right;color:#6b7280;font-size:.85rem'>Messages restants aujourd'hui : <b>{remaining}</b> / {daily_limit}</div>",
    unsafe_allow_html=True,
)
render_chat(conversation["messages"])

# Le composant natif regroupe le texte, le bouton d'image et l'envoi dans un
# seul champ, épinglé au bas de la discussion comme dans ChatGPT.
submission = st.chat_input(
    "Posez une question sur votre fromage…",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if submission:
    prompt = submission.text
    uploaded = submission.files[0] if submission.files else None
    if not prompt.strip() and uploaded is None:
        st.warning("Écrivez un message ou joignez une image avant d'envoyer.")
        st.stop()

    text = prompt.strip() or "Pouvez-vous analyser les caractéristiques visibles de ce fromage ?"
    analysis, image = None, None
    if uploaded:
        try:
            analysis_obj, image = AnalysisController().analyze_upload(uploaded)
            analysis = analysis_obj.to_dict()
        except (ValueError, FileNotFoundError, RuntimeError) as exc:
            st.error(str(exc))
            st.stop()

    user_message = {"role": "user", "content": text, "image": image, "analysis": analysis}
    try:
        user_message["id"] = ConversationService.save_message(
            conversation["id"], "user", text, image=image, analysis=analysis
        )
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    conversation["messages"].append(user_message)
    if conversation["title"] == "Nouvelle conversation":
        conversation["title"] = ConversationService.title_from(text)
        try:
            ConversationService.rename(conversation["id"], conversation["title"])
        except RuntimeError as exc:
            st.error(str(exc))
            st.stop()

    history = [{"role": m["role"], "content": m["content"]} for m in conversation["messages"]]
    with st.status("Fromazy_AI réfléchit…", expanded=False) as thinking:
        answer = ChatController().reply(text, analysis, image, history)
        thinking.update(label="Réponse prête", state="complete", expanded=False)

    # Keras scores are passed privately to Gemini but never rendered in the chat.
    try:
        assistant_id = ConversationService.save_message(conversation["id"], "assistant", answer)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    conversation["messages"].append({"id": assistant_id, "role": "assistant", "content": answer})
    st.session_state.conversations.remove(conversation)
    st.session_state.conversations.insert(0, conversation)
    # L'historique est rendu avant le formulaire, de l'ancien au plus récent.
    st.rerun()
