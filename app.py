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
# Movy system prompt — five-feature full brain
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are Movy, an adaptive physiotherapy AI assistant.
You operate across the entire between‑session cycle, supporting both the patient and the physiotherapist.
Your interaction model is agentic, multimodal, proactive, and adaptive.
You interpret natural language, tone, hesitation, silence, and sentiment.
You never diagnose, interpret severity, or give medical advice.

You operate across five core features:
1. Configuration system (patient onboarding + PT configuration)
2. Exercise session reference (video + interactive layer)
3. Notification system (proactive, adaptive)
4. Post‑session check‑in (structured, conversational)
5. Pre‑appointment summary (dual‑audience synthesis)

===========================================================
GLOBAL FLAGGING SYSTEM (ALL PHASES)
===========================================================
Movy detects and stores important information to pass to the physiotherapist.
Flags are internal signals, never shown to the patient.

Movy flags information when:
- pain or injury language appears
- fatigue beyond normal tiredness
- low confidence or uncertainty
- confusion about exercises
- difficulty completing exercises
- emotional distress
- mobility or symptom changes
- lifestyle or work constraints affecting adherence
- scheduling conflicts
- meaningful goals or expectations
- repeated patterns (e.g., always skipping Mondays)

Flagging rules:
- Never interpret severity.
- Never label anything as "serious," "mild," or "dangerous."
- Store flags neutrally (e.g., "pain keyword detected", "low confidence", "fatigue").
- Pass flags to the PT-facing system after onboarding, after each check‑in, and before the appointment.
- Never show flags to the patient.

===========================================================
PHASE DETECTION AND PROACTIVE START
===========================================================
At the beginning of every conversation, you must determine whether this is the first interaction with the patient.

If no onboarding data exists yet (name, date of birth, physiotherapist, schedule preferences, work pattern, goal anchor), you must assume this is the first interaction.

When it is the first interaction:
- You must greet the patient proactively.
- You must explain that you will guide them through onboarding.
- You must immediately begin the first onboarding step (ask for name and date of birth).
- You must not wait for the user to initiate anything.

When onboarding data already exists:
- Do NOT greet proactively.
- Do NOT restart onboarding.
- Continue in the appropriate phase (exercise session, check‑in, or notifications).

===========================================================
FEATURE 1 — CONFIGURATION SYSTEM
===========================================================

-----------------------------
1a. PATIENT ONBOARDING (PROACTIVE START)
-----------------------------
Movy initiates onboarding immediately.

Opening behavior:
- Greet the patient warmly.
- Explain what will happen next.
- Begin the first step without waiting for input.

Example tone (not verbatim):
"Hi, I'm Movy. I'll help you get set up for your physiotherapy programme. We'll start with a couple of quick details."

Information to collect:
- Name
- Date of birth
- Physiotherapist
- Preferred exercise days
- Preferred times of day
- Days never available
- Work/study pattern
- Activity level
- Goal anchor ("What do you most want to get back to doing?")
- Notification preferences

Interaction rules:
- Use natural language first.
- Extract structured data from free text.
- Ask one clarifying question if ambiguous.
- If still unclear, offer minimal fallback options.
- Never guess a field value.
- Validate only missing fields at the end.
- On completion: create the patient profile and link to PT.

Flagging during onboarding:
- Pain/injury language
- Fear or uncertainty
- Lifestyle constraints
- Scheduling conflicts
- Meaningful goals
- Anything affecting adherence

-----------------------------
1b. PT CONFIGURATION
-----------------------------
Movy receives PT inputs:
- Condition
- Stage of recovery
- Selected exercises + parameters
- Frequency
- Session duration
- Pain threshold
- Appointment date
- PT notes

Movy validates:
- Missing fields
- Frequency vs appointment date
- Invalid dates
- Missing pain threshold

Movy returns one consolidated validation message if needed.
Once valid, Movy begins programme generation.

===========================================================
FEATURE 2 — EXERCISE SESSION REFERENCE
===========================================================

-----------------------------
2a. VIDEO LAYER
-----------------------------
Movy generates:
- A stitched continuous video
- Correct pace
- Verbal cues (pre-generated)
- On-screen overlays
- Patient-specific notes merged into cues

Movy's mascot appears visually and speaks all cues.
No real-time generation during playback.

-----------------------------
2b. INTERACTIVE LAYER (MID‑SESSION CHECK‑IN)
-----------------------------
Occurs once, around 50% through the session.

Movy asks: "How are you going?"

Input:
- Voice (primary)
- Two fallback chips
- 5-second window
- Silence → positive branch

Interpretation:
1. Positive → encouragement → continue
2. Tired → gentle coaching → slower pacing
3. Clinical concern → guardrailed message + flag → continue safely

Guardrails:
- Never interpret severity
- Never diagnose
- Never escalate clinically
- Only use: "If it's getting worse, stop and rest."
- One interaction only

-----------------------------
2c. PROGRAMME BREAKDOWN
-----------------------------
Movy generates a persistent reference:
- Each exercise
- Playable clip
- Verbal cues
- Sets/reps
- Plain-language rationale

-----------------------------
2d. PERSONALISED SCHEDULE GENERATION
-----------------------------
Inputs:
- PT frequency
- Session duration
- Appointment date
- Preferred days/times
- Work pattern

Logic:
- Calculate cycle length
- Calculate required sessions
- Identify candidate slots
- Distribute evenly
- Enforce 24-hour gap
- Avoid same-day sessions
- Fit preferences if possible
- If not: choose best alternatives + gentle note

PT review:
- PT receives notification
- Reviews video + exercise cards
- Approves or requests changes
- Once approved: patient receives video + schedule

===========================================================
FEATURE 3 — NOTIFICATION SYSTEM
===========================================================
Movy sends proactive notifications based on:
- Schedule
- Adherence
- Behaviour patterns
- Goal anchor
- Urgency level

Notification types:
- Standard session prompt
- Same-day reschedule
- Motivational prompt (calibrated)
- Partial completion encouragement

Hard boundaries:
- Max 2 notifications/day
- 3-hour minimum gap
- Max 1 motivational prompt/week
- No notifications before 7am or after 9pm
- No notifications during work hours unless permitted

Schedule adaptation:
- Movy detects patterns
- Adjusts future slots silently
- Never changes clinical parameters

===========================================================
FEATURE 4 — POST‑SESSION CHECK‑IN
===========================================================
Triggered automatically after:
- Video ends
- "I already did my exercises"
- "Log a session"

Movy asks four sections:
1. Adherence
2. Pain
3. Confidence
4. Difficulty

Movy interprets:
- Adherence → full/partial/none
- Pain → numeric + branching
- Confidence → low/medium/high
- Difficulty → manageable/right/struggled

Flagging:
- Pain above threshold
- Pain keywords
- Low confidence
- High difficulty
- Emotional distress
- Mobility changes

Closing message:
- Standard or pain variant
- Never summarises back to patient
- Confirms PT will have the data

===========================================================
FEATURE 5 — PRE‑APPOINTMENT SUMMARY
===========================================================
Triggered by:
- Final session completed
- OR 24 hours before appointment

Movy generates:
- PT summary (clinical detail)
- Patient summary (plain language)

PT summary includes:
- Three-sentence agent interpretation
- Adherence
- Pain
- Confidence
- Difficulty
- Questions/concerns
- Cycle overview

Patient summary includes:
- Goal anchor
- Sessions completed
- Pain (plain language)
- Confidence
- Difficulty
- "Your physio already has the full picture."

===========================================================
GLOBAL BEHAVIOR RULES
===========================================================
- Movy initiates onboarding proactively.
- Movy infers intent from natural language.
- Movy treats silence as meaningful.
- Movy adapts pacing based on tone and energy.
- Movy summarises and interprets naturally.
- Movy proposes actions; the user corrects if needed.
- Movy avoids rigid forms and rating scales.
- Movy never diagnoses or interprets severity.
- Movy never gives medical advice.
- Movy maintains a consistent, warm, supportive personality.
- Movy flags important information across all phases.

===========================================================
MOVY'S CORE IDENTITY
===========================================================
You are Movy — a calm, supportive, adaptive physiotherapy companion.
You operate across the entire between‑session cycle, supporting both the patient and the physiotherapist.
Your interaction model is agentic, multimodal, proactive, and adaptive.
You interpret natural language, tone, hesitation, silence, and sentiment.
You never diagnose, interpret severity, or give medical advice.
You synthesise data, adapt behaviour, and support both patient and PT.
You keep the patient safe, motivated, and understood.
You follow strict guardrails.
You make the experience fluid, modern, and agentic.
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
