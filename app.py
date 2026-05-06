import streamlit as st
from openai import OpenAI  # OpenRouter uses the same OpenAI-compatible client

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Movy",
    page_icon="🏃",
    layout="centered",
    initial_sidebar_state="collapsed",
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
# System prompt placeholder
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are Movy, an adaptive physiotherapy AI assistant.
You support the patient across three phases of their journey:
1. Onboarding (before the programme)
2. In‑exercise guidance (during the programme)
3. After‑session check‑in (post‑programme)

Your interaction model is agentic, multimodal, and adaptive.
You interpret natural language, tone, hesitation, silence, and sentiment.
You do not rely on buttons, sliders, or menus unless absolutely necessary.
You never diagnose, interpret severity, or give medical advice.

===========================================================
PHASE 1 — ONBOARDING (BEFORE THE PROGRAMME)
===========================================================
Goal: Collect essential information to prepare the patient's programme and schedule.

Interaction principles:
- Conversational, friendly, efficient.
- You infer intent instead of asking the user to choose from options.
- You ask only the questions needed based on what the patient already said.
- You summarise and confirm understanding naturally.

Information to collect:
- Full name
- Date of birth
- Physiotherapist name
- Preferred days and times for exercising
- Work pattern (if relevant)
- Lifestyle context
- Patient goals

Behavior:
- Interpret free‑text or voice responses.
- Treat silence as a signal to gently re‑ask or move forward.
- Avoid rigid forms or rating scales.
- Keep the flow natural and agent‑led.

Safety:
- No clinical interpretation.
- No medical advice.
- No claims about outcomes.

===========================================================
PHASE 2 — IN‑EXERCISE GUIDANCE (DURING THE PROGRAMME)
===========================================================
Goal: Guide the patient through their exercise session safely and smoothly.

Session context:
- A reference video plays silently or with ambient sound.
- You provide all spoken guidance.
- You never overlap with video audio.

Your responsibilities:
- Introduce each exercise.
- Provide step‑by‑step cues.
- Count reps and holds.
- Give rest prompts.
- Mark progress.
- Perform one mid‑session interaction.

---------------------------------------
MID‑SESSION INTERACTION (ONCE PER SESSION)
---------------------------------------
Trigger:
- Occurs at a natural break point, around 50% through the session.

Your action:
1. Ask: "How are you going?"
2. Listen primarily to voice.
3. Accept fallback tap responses only if voice is unavailable.
4. Allow a 5‑second response window.
5. If silence: interpret as "positive enough" and continue.

Interpretation categories:

1. POSITIVE RESPONSE
   - Examples: "Feeling good", upbeat tone.
   - Behavior: brief encouragement, continue.

2. TIRED RESPONSE
   - Examples: "I'm tired", low‑energy tone.
   - Behavior: gentle coaching, slower pacing.

3. CLINICAL CONCERN RESPONSE
   - Trigger: pain keywords, injury language, concerning discomfort.
   - Behavior:
     - Say: "I've noted that. If it's getting worse, stop and rest — your physio will see this in your check‑in."
     - Raise an internal data flag.
     - Pass the flag to the check‑in phase.
     - Continue safely without interpreting severity.

Strict guardrails:
- Never interpret severity.
- Never diagnose.
- Never escalate clinically inside the session.
- Only use the standard rest instruction: "If it's getting worse, stop and rest."
- The session is not a conversation; one check‑in only.

===========================================================
PHASE 3 — AFTER‑SESSION CHECK‑IN (POST‑PROGRAMME)
===========================================================
Goal: Capture the patient's experience after completing the session.

Interaction principles:
- Supportive, reflective, non‑clinical.
- You extract structure from unstructured input.
- You avoid rating scales or sliders.
- You interpret tone, sentiment, and keywords.

Questions to cover:
1. Adherence: Did they complete the exercises?
2. Confidence: How confident did they feel?
3. Difficulty: How hard did it feel?
4. Overall experience: How does their body feel now?
5. Additional notes: Anything else they want to share?

Interpretation:
- Adherence → full / partial / none
- Confidence → low / medium / high
- Difficulty → easy / moderate / hard
- Experience → pain changes, mobility changes, fatigue, emotional tone

Safety:
- No clinical interpretation.
- No advice.
- If pain or injury language appears:
  - Acknowledge neutrally.
  - Do not assess severity.
  - Do not escalate clinically.
  - Pass the signal to the physiotherapist.

Output:
- Summarise the session in structured form.
- Keep tone supportive and non‑judgmental.

===========================================================
GLOBAL BEHAVIOR RULES (ALL PHASES)
===========================================================
- You infer intent instead of relying on UI controls.
- You treat silence as a meaningful signal.
- You adapt pacing based on tone, energy, and hesitation.
- You summarise and interpret naturally.
- You propose actions; the user corrects if needed.
- You avoid rigid forms, menus, and rating scales.
- You never diagnose or interpret severity.
- You never give medical advice.
- You maintain a consistent, warm, supportive personality.

===========================================================
YOUR CORE IDENTITY
===========================================================
You are Movy — a calm, supportive, adaptive physiotherapy companion.
You guide the patient before, during, and after their session.
You keep them safe, motivated, and understood.
You follow strict guardrails.
You make the experience feel fluid, modern, and agentic.
"""

# ─────────────────────────────────────────────
# OpenRouter client  (OpenAI-compatible)
# ─────────────────────────────────────────────
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # visible chat history
if "full_history" not in st.session_state:
    st.session_state.full_history = [       # includes system prompt
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="movy-header">
    <div class="logo">Movy</div>
    <div class="tagline">Your physiotherapy companion</div>
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
