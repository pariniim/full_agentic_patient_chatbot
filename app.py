import streamlit as st
from openai import OpenAI  # OpenRouter uses the same OpenAI-compatible client

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Movy",
    page_icon="🏃",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS — dark, premium, minimal
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 6rem;
    max-width: 780px;
}

/* ── Header ── */
.movy-header {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.movy-header .logo {
    font-size: 2.6rem;
    letter-spacing: -1px;
    font-weight: 600;
    background: linear-gradient(135deg, #7c6af7 0%, #a78bfa 50%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.movy-header .tagline {
    font-size: 0.85rem;
    color: #6b7280;
    margin-top: 0.3rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Chat messages ── */
.chat-row {
    display: flex;
    margin-bottom: 1.1rem;
    animation: fadeSlide 0.25s ease-out;
}
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.chat-row.user  { justify-content: flex-end; }
.chat-row.movy  { justify-content: flex-start; }

.bubble {
    max-width: 72%;
    padding: 0.75rem 1.1rem;
    border-radius: 18px;
    font-size: 0.93rem;
    line-height: 1.55;
}
.bubble.user {
    background: linear-gradient(135deg, #7c6af7, #60a5fa);
    color: #fff;
    border-bottom-right-radius: 4px;
}
.bubble.movy {
    background: #1a1d27;
    color: #dde1ef;
    border: 1px solid #2a2d3a;
    border-bottom-left-radius: 4px;
}

/* ── Typing indicator ── */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 0.6rem 1rem;
    background: #1a1d27;
    border: 1px solid #2a2d3a;
    border-radius: 18px;
    border-bottom-left-radius: 4px;
    width: fit-content;
}
.typing-indicator span {
    width: 7px; height: 7px;
    background: #7c6af7;
    border-radius: 50%;
    animation: bounce 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40%           { transform: translateY(-6px); opacity: 1; }
}

/* ── Input box ── */
.stChatInput > div {
    background: #1a1d27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 14px !important;
    transition: border-color 0.2s;
}
.stChatInput > div:focus-within {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124, 106, 247, 0.15) !important;
}
.stChatInput textarea {
    color: #e8eaf0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.93rem !important;
}
.stChatInput textarea::placeholder { color: #4b5563 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Context-specific system prompts
# ─────────────────────────────────────────────

# ── Prompt for Patient Onboarding context ──
# Replace the placeholder below with your full onboarding system prompt.
ONBOARDING_PROMPT = """\
[PATIENT ONBOARDING SYSTEM PROMPT — PASTE HERE]
"""

# ── Prompt for Patient Check-In context ──
# Replace the placeholder below with your full check-in system prompt.
CHECKIN_PROMPT = """\
[PATIENT CHECK-IN SYSTEM PROMPT — PASTE HERE]
"""

# Map context labels → prompts
CONTEXT_PROMPTS = {
    "🚀  Patient Onboarding": ONBOARDING_PROMPT,
    "✅  Patient Check-In":   CHECKIN_PROMPT,
}

# ─────────────────────────────────────────────
# OpenRouter client  (OpenAI-compatible)
# ─────────────────────────────────────────────
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

# ─────────────────────────────────────────────
# Sidebar — context switcher
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: #13151f;
        border-right: 1px solid #2a2d3a;
    }
    section[data-testid="stSidebar"] * { color: #dde1ef !important; }
    .sidebar-title {
        font-size: 0.78rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6b7280 !important;
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    </style>
    <p class="sidebar-title">Testing Context</p>
    """, unsafe_allow_html=True)

    selected_context = st.radio(
        label="context",
        options=list(CONTEXT_PROMPTS.keys()),
        label_visibility="collapsed",
        key="context_radio",
    )

    st.markdown("---")
    if st.button("🔄  Reset conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.full_history = [
            {"role": "system", "content": CONTEXT_PROMPTS[selected_context]}
        ]
        st.rerun()

# ─────────────────────────────────────────────
# Session state — init or reset on context switch
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_history" not in st.session_state:
    st.session_state.full_history = [
        {"role": "system", "content": CONTEXT_PROMPTS[selected_context]}
    ]
if "active_context" not in st.session_state:
    st.session_state.active_context = selected_context

# If user switched context, reset the conversation automatically
if st.session_state.active_context != selected_context:
    st.session_state.active_context = selected_context
    st.session_state.messages = []
    st.session_state.full_history = [
        {"role": "system", "content": CONTEXT_PROMPTS[selected_context]}
    ]
    st.rerun()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
# Derive a short badge label from the selected context
_badge_label = selected_context.split("  ", 1)[-1]   # strip the emoji prefix
st.markdown(f"""
<style>
.context-badge {{
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    background: rgba(124, 106, 247, 0.15);
    border: 1px solid rgba(124, 106, 247, 0.4);
    color: #a78bfa;
    margin-top: 0.5rem;
}}
</style>
<div class="movy-header">
    <div class="logo">Movy</div>
    <div class="tagline">Your physiotherapy companion</div>
    <div class="context-badge">{_badge_label}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Render chat history
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "movy"
    bubble_class = "user" if msg["role"] == "user" else "movy"
    st.markdown(f"""
    <div class="chat-row {role_class}">
        <div class="bubble {bubble_class}">{msg["content"]}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Chat input
# ─────────────────────────────────────────────
user_input = st.chat_input("Type your message…")

if user_input and user_input.strip():
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.full_history.append({"role": "user", "content": user_input})

    # Show user bubble immediately
    st.markdown(f"""
    <div class="chat-row user">
        <div class="bubble user">{user_input}</div>
    </div>
    """, unsafe_allow_html=True)

    # Typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="chat-row movy">
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Call via OpenRouter
    response = client.chat.completions.create(
        model="openai/gpt-4o",          # change to any OpenRouter model id
        messages=st.session_state.full_history,
        temperature=0.7,
    )
    assistant_reply = response.choices[0].message.content

    # Store assistant reply
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.session_state.full_history.append({"role": "assistant", "content": assistant_reply})

    # Replace typing indicator with reply
    typing_placeholder.markdown(f"""
    <div class="chat-row movy">
        <div class="bubble movy">{assistant_reply}</div>
    </div>
    """, unsafe_allow_html=True)
