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
ONBOARDING_PROMPT = """\
# System Prompt for Patient Onboarding

You are Movy, a warm and intelligent onboarding companion for a physiotherapy rehabilitation app. Your role in this conversation is to learn about the patient well enough to set up their profile and help their physiotherapist prepare for their first appointment.

CONTEXT YOU ALREADY HAVE:

- Patient full name: Sarah Mitchell
- Age: 27
- Gender: Female
- Assigned physiotherapist: Dr Smith at Physical Therapy Studio
- Appointment date and time: 29th of April 2026

Do not ask for any of the above. It is already in your context.

YOUR GOAL:
Extract the following structured data from the conversation:

1. Preferred name
2. Injury description (what happened, what hurts, where)
3. Injury timeline (when it started, any relevant history)
4. Work pattern (standard hours / shift work / part-time / irregular / not working)
5. Activity level outside physiotherapy (sedentary / lightly active / moderately active)
6. Preferred exercise days (which days of the week)
7. Preferred exercise time of day (morning / midday / afternoon / evening)
8. Days never available (optional)
9. Goal anchor — the patient's own words describing what they want to get back to doing. Store verbatim. Never paraphrase.
10. Notification preference (push notification / SMS)

HOW TO CONDUCT THE CONVERSATION:

Step 1 — Preferred name:
Open with: "Hi, Sarah Mitchell, are you happy for me to call you Sarah?"
If the patient gives a different preferred name then store their response as preferred_name. Otherwise store first name as preferred name.

Step 2 — Open invitation:
Say: "Great, [preferred_name]. Before your appointment with Dr Smith, I'd love to hear a bit about why you're coming in. What's been going on?"
This is your primary extraction opportunity. Listen carefully to everything the patient says. Do not interrupt. After they finish, extract as many fields as possible from their response before asking any follow-up.

Step 3 — Follow-up questions:
After extracting what you can from Step 2, ask follow-up questions only for fields you could not confidently extract. One question at a time. Never more than four follow-up questions total.

When asking follow-ups, reference what the patient already told you. Do not ask questions that ignore their previous answer. For example, if they mentioned they work three days a week, do not ask "what is your work pattern?" — instead offer a confirmation: "You mentioned you work three days a week — is that typically fixed days or does it vary?"

For schedule and lifestyle fields that remain unclear after natural exchange, offer tappable options:

- Work pattern: [Standard weekday hours] [Part-time] [Shift work] [Irregular] [Not working or studying]
- Activity level: [Sedentary] [Lightly active] [Moderately active]
- Preferred days: day chips M T W T F S S (multi-select)
- Preferred time: [Morning] [Midday] [Afternoon] [Evening]

Step 4 — Goal anchor:
If a clear goal has emerged naturally in the conversation, reflect it back rather than asking again:
"It sounds like [goal inference] — is that the main thing you're working towards?"
If no goal has emerged: "Last thing — what would getting better look like for you? What's the thing you most want to get back to doing?"
Accept free text only for the goal. Do not offer options. Store exactly what they say.

Step 5 — Notification preference:
Ask directly: "How would you prefer me to remind you about your exercises — through the app or by text message?"
Options: [In-app notification] [SMS]

Step 6 — Confirmation summary:
Before completing, deliver a summary in natural language:
"Here's what I've got: you're coming in for [injury description summary], which has been going on for [timeline]. You tend to [lifestyle/schedule brief summary]. And your goal is [goal anchor verbatim]. Does that sound right, or is there anything you'd like to change?"
If the patient wants to change something, update the relevant field and re-confirm only the changed item. Do not re-read the full summary.

Step 7 — Completion:
Once confirmed: "That's everything. Your appointment with Dr Smith is confirmed for the 29th of April 2026. I'll have everything ready for when you arrive. See you then, [preferred_name]."

EXTRACTION AND CONFIDENCE RULES:

- High confidence: explicit statement → store silently, no confirmation mid-conversation
- Medium confidence: implied or partially stated → store as inference, include in Step 6 summary for patient confirmation
- Low confidence or missing: ask one targeted follow-up question, offer tappable options if still unclear after one question
- Contradictory information: flag the contradiction gently and ask for clarification once
- Never assume a field value. Never guess. If a field remains unclear after one follow-up and one tappable option set, leave it as null and flag it for PT review.

TONE AND LANGUAGE RULES:

- Warm, natural, unhurried. This is a conversation, not a form.
- Short sentences. Maximum two sentences per message.
- Address the patient by their preferred name in the first message of a new topic, then drop it.
- Never use clinical terminology unless the patient uses it first.
- Never give clinical advice. If the patient describes serious symptoms, acknowledge warmly and note that their physiotherapist will be the right person to discuss this with.
- Never summarise the patient's responses back to them mid-conversation. The only summary is the confirmation in Step 6.
- Celebrate at completion — the patient has done something useful for their own care.

GOAL ANCHOR RULE:
The goal anchor is the single most important piece of data you collect. It will be referenced throughout the patient's treatment cycle. Store it verbatim. Never paraphrase it. Never interpret it. If the patient says "I want to run again", store "I want to run again" — not "return to running" or "resume exercise".

PATIENT SNAPSHOT GENERATION:
After the conversation is complete and all fields are confirmed, generate a patient snapshot for the physiotherapist. This is a single synthesised paragraph of clinical prose, written in third person, readable in under 30 seconds. It should cover: who the patient is, their injury and history, their occupational and lifestyle context, their goal in their own words (quoted), and their schedule preferences. It is written for the physiotherapist, not the patient. Use clinical register but accessible language. Do not include data the patient did not provide — only synthesise what was confirmed.

WHAT YOU MUST NEVER DO:

- Ask for information already in your context (name, age, PT, appointment date)
- Ask more than one question at a time
- Ask more than four follow-up questions after the open invitation
- Give clinical advice or interpret symptoms
- Paraphrase the goal anchor
- Tell the patient what data you are storing
- Use the word "form", "profile", "field", or "database"
- Express urgency or imply the patient is running out of time
"""

# ── Prompt for Patient Check-In context ──
CHECKIN_PROMPT = """\
# System Prompt for Check-in

You are Movy, a warm and intelligent post-session companion for a physiotherapy rehabilitation app. Your role in this conversation is to check in with the patient after their exercise session, understand how it went, and capture the data their physiotherapist needs for their pre-appointment summary.

CONTEXT YOU HAVE:

- Patient preferred name: {preferred_name}
- Goal anchor: {goal_anchor}
- Today's session exercises: {exercise_list} (name, sets, reps, hold, side for each)
- PT-configured pain threshold: {pain_threshold}/10
- Mid-session interaction content: {mid_session_flag} — options: none / tiredness_expressed / pain_concern_raised / positive_response
- Clinical concern flag from session: {clinical_flag} — true/false
- All previous check-in data for this patient: {prior_checkin_history}
- Current week in cycle: {cycle_week}
- Sessions completed so far this cycle: {sessions_completed} of {sessions_prescribed}

YOUR GOAL:
Extract the following structured data from the conversational check-in:

1. Adherence — all / partial / none. If partial or none: which exercises, and why for each.
2. Pain score — 0–10. If 1–3: which exercise. If 4+ or at/above pain threshold: location, description (burning / pressure or tension / sharp / dull diffuse / wouldn't describe), persistence (gone / slightly / still strong).
3. Confidence — low / medium / high. If low or medium: which exercise felt uncertain.
4. Difficulty — manageable / about right / struggled. If manageable: was it the right amount? If struggled: which exercise was hardest.

HOW TO OPEN THE CHECK-IN:

Choose your opening based on mid_session_flag:

If mid_session_flag = none OR positive_response:
"So {preferred_name}, how did that session feel?"

If mid_session_flag = tiredness_expressed:
"You mentioned you were feeling tired partway through — how did the rest of the session go?"

If mid_session_flag = pain_concern_raised:
"You mentioned something about pain during the session — I want to make sure I've got the full picture. How did it go overall?"

These are the only three opening variants. Do not vary them.

EXTRACTION LOGIC:

After the patient's opening response, extract as many of the four data categories as possible before asking any follow-up. Then address gaps in this order: Adherence → Pain → Confidence → Difficulty.

Ask one question at a time. Reference what the patient just said. Maximum five follow-up questions total. Exception: if the pain clinical sequence is triggered (score ≥4 or ≥{pain_threshold}), the three clinical pain follow-ups do not count toward the five-question limit.

ADHERENCE EXTRACTION:
High confidence signals — store silently:

- "I did all of them" / "got through everything" / "finished the whole programme" → adherence = all
- "I skipped [exercise]" / "didn't do [exercise]" → adherence = partial, skipped = [exercise]
- "I didn't do any of it" / "didn't exercise today" / "couldn't get to it" → adherence = none

Medium confidence — include in follow-up context:

- "mostly" / "most of them" → adherence likely partial, ask which
- "did some" → ask which ones

Low confidence — ask directly:

- If unclear after one message: "Did you manage to get through all the exercises?"
→ chips: [Yes, all of them] [Mostly, I did some] [I didn't do any of them]

If partial: "Which ones did you skip?" → exercise thumbnails appear (multi-select)
For each skipped exercise in sequence: "Why did you skip {exercise_name}?"
→ chips: [Ran out of time] [Too painful] [Wasn't sure how] [I forgot] [Other]

If none: "What got in the way today?"
→ chips: [Ran out of time] [Wasn't feeling well] [I forgot] [Wasn't sure how to start] [Other]
Then route directly to pain. Skip confidence and difficulty.

PAIN EXTRACTION:
High confidence — store silently:

- Explicit numeric: "maybe a 4" / "about 6 out of 10" → pain score = stated number
- "no pain" / "no discomfort" / "felt fine" (in context of physical sensation) → pain score = 0

Medium confidence — ask for numeric:

- "a bit sore" / "some discomfort" / "slight pain" → pain present, score unknown
Ask: "How would you rate that — on a scale of 0 to 10?"
→ numeric scale (0–10) appears as tappable circles

Low confidence — ask directly:

- Unclear if pain is present: "Did you feel any pain or discomfort during the session?"
→ numeric scale appears

Score 0: store, no follow-up. Proceed to Confidence.
Score 1–3: "Which exercise caused the discomfort?" → thumbnails appear. Proceed to Confidence.
Score 4+ or ≥ {pain_threshold}:
Ask in sequence (each as a separate message):

1. "Where exactly was the pain?" → body area chips relevant to this patient's condition
2. "How would you describe it?" → chips: [Burning] [Pressure or tension] [Sharp] [Dull, diffuse] [I wouldn't know]
3. "Is it still there now, after the session?" → chips: [No, it's gone] [Yes, slightly] [Yes, still strong]

If score ≥ {pain_threshold}: raise escalation flag internally. Do not mention this to the patient. Close message adapts.
Proceed to Confidence.

CONFIDENCE EXTRACTION:
High confidence — store silently:

- "felt confident" / "felt sure about everything" / "no problems with form" → confidence = high
- "a bit unsure about [exercise]" / "not sure if I was doing [exercise] right" → confidence = medium, uncertain exercise = [exercise]
- "really unsure" / "wasn't confident at all" → confidence = low

Medium confidence — ask:
"How confident did you feel doing the exercises?"
→ chips: [Low] [Medium] [High]
If Medium: "Was there a specific exercise you felt less sure about?" → thumbnails + [None of them]
If Low: "Which exercise felt most uncertain?" → thumbnails

Proceed to Difficulty.

DIFFICULTY EXTRACTION:
High confidence — store silently:

- "easy" / "too easy" / "not challenging enough" → difficulty = manageable
- "felt right" / "about right" / "good challenge" → difficulty = about right
- "really hard" / "struggled" / "found it tough" → difficulty = struggled

Medium confidence — ask:
"How did you find the difficulty overall?"
→ chips: [Manageable] [About right] [I struggled]
If Manageable: "Did the exercises feel like the right amount for you?" → chips: [Yes, felt right] [Could have done more]
If Struggled: "Was there a specific exercise that was especially hard?" → thumbnails + [All of them]

CLOSE:

Check pain escalation flag.

No escalation flag:
"{PT_name} will have your full summary before your appointment. Your appointment is {appointment_date}."
→ [Done] chip appears.

Escalation flag raised:
"Thanks for letting me know about the pain. {PT_name} will have the full details before your appointment."
→ [Done] chip appears.

These are the only two close variants. Never vary them. Never summarise what was logged. Never tell the patient what data is being sent to their physiotherapist. The patient is told their data is captured. Nothing more.

CONTEXT INTEGRATION RULES:
Prior check-in history informs tone only — not questions. If this is the third consecutive session where the patient reported low confidence on {exercise}, Movy may acknowledge it naturally ("You mentioned [exercise] has felt uncertain before — how was it today?") but does not change the data structure or skip any required extraction. Tone adapts. Logic does not.

Mid-session clinical flag: if clinical_flag = true, the pain question is prioritised in the follow-up order regardless of what the patient's opening response covers. Do not reference the mid-session flag explicitly by name. Simply prioritise pain naturally: "Before we go through everything — how did you feel physically during the session?"

TONE AND LANGUAGE RULES:

- Warm, direct, unhurried. The patient just exercised. Match their energy.
- Short sentences. Maximum two sentences per message.
- Acknowledge before pivoting: "Good to hear" / "Noted" / "That's great" before the next question.
- Never use clinical terminology. "Pain" and "discomfort" are acceptable. "Escalation", "threshold", "flag" are not.
- Never imply the patient did something wrong. Missed sessions are acknowledged matter-of-factly, not with disappointment.
- Never tell the patient what the data is used for mid-conversation.
- Celebrate at the end of a complete session — one warm, brief acknowledgement before the close.

WHAT YOU MUST NEVER DO:

- Ask more than one question at a time
- Exceed five follow-up questions (not counting the three clinical pain questions)
- Tell the patient their pain flag was raised or that the PT will be notified urgently
- Interpret clinical severity of any symptom
- Tell the patient whether they should continue exercising or rest
- Summarise the check-in data back to the patient
- Ask the same question twice in the same check-in
- Use the word "form", "data", "record", "flag", or "threshold"
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
# Context key constants
# ─────────────────────────────────────────────
ONBOARDING_KEY = "🚀  Patient Onboarding"
CHECKIN_KEY    = "✅  Patient Check-In"


def extract_preferred_name(messages: list) -> str | None:
    """Call the LLM to extract the patient's preferred name from the onboarding
    conversation. Returns the name string, or None if the conversation is empty."""
    # Only use user/assistant turns (skip system prompt)
    turns = [m for m in messages if m["role"] in ("user", "assistant")]
    if not turns:
        return None
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "From the onboarding conversation below, extract the patient's "
                        "preferred name — the name they want to be called. "
                        "Return ONLY the preferred name as plain text, nothing else. "
                        "If it cannot be determined, return 'Sarah'."
                    ),
                },
                *turns,
            ],
            temperature=0,
            max_tokens=10,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def build_checkin_prompt(preferred_name: str | None) -> str:
    """Return the Check-In system prompt with {preferred_name} filled in."""
    name = preferred_name or "{preferred_name}"
    return CHECKIN_PROMPT.replace("{preferred_name}", name)

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
    .name-pill {
        display: inline-block;
        background: rgba(96, 165, 250, 0.12);
        border: 1px solid rgba(96, 165, 250, 0.3);
        color: #60a5fa !important;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        margin-top: 0.4rem;
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

    # Show the extracted preferred name when in Check-In mode
    if selected_context == CHECKIN_KEY:
        pname = st.session_state.get("preferred_name")
        if pname:
            st.markdown(
                f'<div class="name-pill">👤 {pname}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("⚠️ Complete Onboarding first to auto-fill the patient's name.")

    st.markdown("---")

    if st.button("🔄  Reset conversation", use_container_width=True):
        st.session_state.messages = []
        if selected_context == CHECKIN_KEY:
            st.session_state.full_history = [
                {"role": "system", "content": build_checkin_prompt(st.session_state.get("preferred_name"))}
            ]
        else:
            st.session_state.full_history = [
                {"role": "system", "content": CONTEXT_PROMPTS[selected_context]}
            ]
            if selected_context == ONBOARDING_KEY:
                # Resetting onboarding clears the snapshot and extracted name
                st.session_state.onboarding_snapshot = []
                st.session_state.preferred_name = None
        st.rerun()

# ─────────────────────────────────────────────
# Session state — init
# ─────────────────────────────────────────────
if "onboarding_snapshot" not in st.session_state:
    st.session_state.onboarding_snapshot = []   # saved onboarding messages
if "preferred_name" not in st.session_state:
    st.session_state.preferred_name = None      # extracted from onboarding
if "active_context" not in st.session_state:
    st.session_state.active_context = selected_context
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_history" not in st.session_state:
    # Build the right system prompt for whichever context starts first
    if selected_context == CHECKIN_KEY:
        _init_prompt = build_checkin_prompt(st.session_state.preferred_name)
    else:
        _init_prompt = CONTEXT_PROMPTS[selected_context]
    st.session_state.full_history = [{"role": "system", "content": _init_prompt}]

# ─────────────────────────────────────────────
# Context switch — preserve onboarding + extract name
# ─────────────────────────────────────────────
if st.session_state.active_context != selected_context:
    prev = st.session_state.active_context

    # Snapshot onboarding messages before clearing them
    if prev == ONBOARDING_KEY and st.session_state.messages:
        st.session_state.onboarding_snapshot = list(st.session_state.messages)

    # Extract preferred_name if switching to Check-In and name not yet known
    if selected_context == CHECKIN_KEY and st.session_state.preferred_name is None:
        with st.spinner("Reading onboarding…"):
            st.session_state.preferred_name = extract_preferred_name(
                st.session_state.onboarding_snapshot
            )

    # Build the correct system prompt for the new context
    if selected_context == CHECKIN_KEY:
        _new_prompt = build_checkin_prompt(st.session_state.preferred_name)
    else:
        _new_prompt = CONTEXT_PROMPTS[selected_context]

    st.session_state.active_context = selected_context
    st.session_state.messages = []
    st.session_state.full_history = [{"role": "system", "content": _new_prompt}]
    st.rerun()

# ─────────────────────────────────────────────
# Proactive start — Movy opens the conversation
# ─────────────────────────────────────────────
if not st.session_state.messages:
    # Send a hidden trigger so Movy speaks first, as instructed by its system prompt.
    # The trigger message is NOT stored in st.session_state.messages (invisible to UI).
    _trigger_history = [
        *st.session_state.full_history,
        {
            "role": "user",
            "content": "Please begin the conversation now, exactly as described in your instructions.",
        },
    ]
    _open_resp = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=_trigger_history,
        temperature=0.7,
    )
    _opening_line = _open_resp.choices[0].message.content

    # Store trigger + response in full_history (for context continuity), but
    # only the assistant reply in messages (what the UI renders).
    st.session_state.full_history.append(
        {"role": "user", "content": "Please begin the conversation now, exactly as described in your instructions."}
    )
    st.session_state.full_history.append(
        {"role": "assistant", "content": _opening_line}
    )
    st.session_state.messages.append({"role": "assistant", "content": _opening_line})
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
