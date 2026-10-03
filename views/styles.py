"""Modern Blue & White CSS design system for Fromazy AI."""
import streamlit as st


def inject_custom_styles() -> None:
    st.markdown("""
    <style>
    /* ==========================================================================
       MODERN BLUE & WHITE DESIGN SYSTEM - FROMAZY AI
       ========================================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Background with subtle modern blue mesh */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.04) 0px, transparent 50%) !important;
        color: #0F172A !important;
    }

    /* Main container padding */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 980px !important;
    }

    /* ==========================================================================
       SIDEBAR STYLING
       ========================================================================== */
    section[data-testid="stSidebar"] {
        background-color: #1746A2 !important;
        border-right: 1px solid #123A89 !important;
        box-shadow: 4px 0 20px -5px rgba(15, 23, 42, 0.18) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Sidebar workspace buttons */
    section[data-testid="stSidebar"] button {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 10px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.75rem !important;
        margin-bottom: 0.35rem !important;
        transition: all 0.15s ease-in-out !important;
    }

    section[data-testid="stSidebar"] button,
    section[data-testid="stSidebar"] button p,
    section[data-testid="stSidebar"] button span,
    section[data-testid="stSidebar"] button div {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: #EAF1FF !important;
        border-color: #D5E3FF !important;
        color: #111827 !important;
        transform: translateX(2px) !important;
    }

    /* Keep all interactive controls in the same blue palette. */
    button[kind="secondary"], [data-testid="stFormSubmitButton"] button {
        border-radius: 10px !important;
        transition: all .18s ease !important;
    }
    button[kind="secondary"]:hover { border-color: #93C5FD !important; color: #1D4ED8 !important; }

    /* Active conversation button */
    .active-conversation button {
        background-color: #FFFFFF !important;
        border-left: 3px solid #111827 !important;
        border-color: #FFFFFF !important;
        color: #111827 !important;
        font-weight: 600 !important;
    }

    /* Primary buttons (New chat, Submit, etc.) */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.28) !important;
        transition: all 0.2s ease !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.38) !important;
        transform: translateY(-1px) !important;
    }

    button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    /* ==========================================================================
       TABS STYLING (Modern Pills)
       ========================================================================== */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        background-color: #F1F5F9 !important;
        padding: 0.35rem !important;
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
    }

    [data-testid="stTabs"] button[role="tab"] {
        border-radius: 10px !important;
        padding: 0.45rem 1.25rem !important;
        background-color: transparent !important;
        color: #64748B !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1D4ED8 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }

    /* ==========================================================================
       INPUTS & FORMS
       ========================================================================== */
    div[data-baseweb="input"] {
        border-radius: 12px !important;
        border-color: #E2E8F0 !important;
        background-color: #FFFFFF !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* Chat input pinned at bottom */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.16) !important;
    }
    [data-testid="stChatInput"] button {
        background: #2563EB !important;
        color: #fff !important;
        border-radius: 11px !important;
    }
    [data-testid="stChatInput"] button:hover { background: #1D4ED8 !important; }

    /* Compact, app-like authentication screen. */
    .auth-shell { max-width: 470px; margin: 5vh auto 0 auto; }
    .auth-brand { text-align: center; margin-bottom: 1.25rem; }
    .auth-brand-mark { font-size: 2rem; }
    .auth-brand-title { color: #0F172A; font-weight: 800; font-size: 1.8rem; letter-spacing: -.04em; }
    .auth-brand-subtitle { color: #64748B; margin-top: .2rem; }
    [data-testid="stForm"] { border: 0 !important; padding: 0 !important; }

    /* ==========================================================================
       HERO & AI PLATFORM CARDS
       ========================================================================== */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 2rem 1rem;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.08);
        margin-bottom: 2rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.85rem;
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 9999px;
        color: #1D4ED8;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }

    .hero-title span {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-desc {
        color: #64748B;
        font-size: 1rem;
        max-width: 580px;
        margin: 0 auto 1.5rem auto;
        line-height: 1.5;
    }

    /* Suggestion Prompt Cards */
    .prompt-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.85rem;
        margin-top: 1rem;
    }

    .prompt-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1rem;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .prompt-card:hover {
        background: #EFF6FF;
        border-color: #93C5FD;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }

    .prompt-card-icon {
        font-size: 1.3rem;
        margin-bottom: 0.4rem;
    }

    .prompt-card-title {
        font-weight: 600;
        font-size: 0.9rem;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }

    .prompt-card-sub {
        font-size: 0.78rem;
        color: #64748B;
        line-height: 1.3;
    }

    /* ==========================================================================
       CHAT MESSAGES
       ========================================================================== */
    .msg-user-box {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.25rem;
        color: #1E3A8A;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.05);
        margin-bottom: 0.5rem;
    }

    .msg-assistant-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px 18px 18px 4px;
        padding: 1.25rem 1.5rem;
        color: #1E293B;
        font-size: 0.95rem;
        line-height: 1.65;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.04);
        margin-bottom: 0.5rem;
    }

    .msg-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }

    .msg-header-assistant {
        color: #2563EB;
    }

    .msg-header-user {
        color: #1D4ED8;
    }

    /* ==========================================================================
       AI ANALYSIS CARD
       ========================================================================== */
    .analysis-container {
        background: #FFFFFF;
        border: 1px solid #BFDBFE;
        border-radius: 16px;
        padding: 1.25rem;
        margin: 0.75rem 0 1rem 0;
        box-shadow: 0 8px 24px -4px rgba(37, 99, 235, 0.1);
        border-left: 4px solid #2563EB;
    }

    .analysis-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.85rem;
    }

    .badge-sain {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .badge-warning {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    .badge-danger {
        background-color: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FCA5A5;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
    }

    /* User Profile in sidebar */
    .user-profile-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin-top: 1rem;
    }

    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2563EB, #60A5FA);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }

    /* Status Pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .status-connected {
        background-color: #DCFCE7;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }

    .status-local {
        background-color: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
    }

    .status-warning {
        background-color: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    /* Glassmorphism auth container */
    .auth-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 2.25rem;
        box-shadow: 0 15px 35px -5px rgba(37, 99, 235, 0.09);
        margin: 2rem auto;
        max-width: 480px;
    }

    .auth-logo-circle {
        width: 64px;
        height: 64px;
        margin: 0 auto 1rem auto;
        border-radius: 20px;
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        box-shadow: 0 8px 20px -3px rgba(37, 99, 235, 0.35);
    }
    </style>
    """, unsafe_allow_html=True)
