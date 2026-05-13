import streamlit as st
import json, re, time, base64
from pathlib import Path
from openai import OpenAI

st.set_page_config(page_title="Movy", page_icon="🏃", layout="centered",
                   initial_sidebar_state="collapsed")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp {
    background: #d8d1ca; /* Outside the phone */
    color: #1a1d27;
}
#MainMenu,footer,header{visibility:hidden;}

/* The Phone Screen */
.block-container {
    background: #FAF6F2 !important;
    max-width: 410px !important;
    height: 880px !important;
    margin: 40px auto !important;
    padding: 60px 20px 0 20px !important;   /* bottom padding handled by input bar */
    border: 12px solid #2d2d2d; /* Titanium frame */
    border-radius: 60px;
    box-shadow: 0 50px 100px rgba(0,0,0,0.3);
    position: relative;
    overflow-y: auto !important;
    scrollbar-width: none;
    display: flex !important;
    flex-direction: column !important;
}
.block-container::-webkit-scrollbar { display: none; }

section[data-testid="stSidebar"]{display:none;}

/* Dynamic Island */
.stApp::before {
    content: "";
    position: fixed;
    top: 55px; /* Adjust based on margin */
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 35px;
    background: #000;
    border-radius: 20px;
    z-index: 9999;
}

/* Home Indicator */
.stApp::after {
    content: "";
    position: fixed;
    bottom: 55px; /* Adjust based on margin */
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 5px;
    background: #000;
    border-radius: 10px;
    opacity: 0.2;
    z-index: 9999;
}


/* Header */
.movy-header{text-align:center;padding:1rem 0 0.5rem;}

.movy-header .logo{font-size:2.4rem;letter-spacing:-1px;font-weight:600;
  background:linear-gradient(135deg,#7c6af7 0%,#a78bfa 50%,#60a5fa 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.movy-header .tagline {
    font-size: 0.82rem;
    color: #8b837a;
    margin-top: 0.25rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* Phase progress */
.phase-bar{display:flex;align-items:center;justify-content:center;gap:0;margin:1rem 0 1.5rem;}
.phase-dot{width:10px;height:10px;border-radius:50%;background:#d8d1ca;transition:all 0.4s;}
.phase-dot.done{background:#C4603A;}
.phase-dot.active{background:#C4603A;box-shadow:0 0 8px rgba(196,96,58,0.3);transform:scale(1.25);}
.phase-line{width:40px;height:2px;background:#d8d1ca;}
.phase-line.done{background:#C4603A;}
.phase-label{font-size:0.65rem;color:#8b837a;text-align:center;margin-top:0.3rem;
  letter-spacing:0.05em;text-transform:uppercase;}
.phase-step{display:flex;flex-direction:column;align-items:center;gap:0.2rem;}

/* Chat bubbles */
.chat-row{display:flex;margin-bottom:1rem;animation:fadeSlide 0.25s ease-out;}
@keyframes fadeSlide{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.chat-row.user{justify-content:flex-end;}
.chat-row.movy{justify-content:flex-start;}
.bubble{max-width:72%;padding:0.75rem 1.1rem;border-radius:18px;font-size:0.93rem;line-height:1.55;}
.bubble.user {
    background: #FFFFFF;
    color: #2B5CD9;
    border: 1px solid #2B5CD9;
    border-bottom-right-radius: 4px;
}
.bubble.movy {
    background: #C4603A;
    color: #FFFFFF;
    border: 1px solid #C4603A;
    border-bottom-left-radius: 4px;
}

/* Typing */
.typing-indicator{display:flex;align-items:center;gap:5px;padding:0.6rem 1rem;
  background:#C4603A;border:1px solid #C4603A;border-radius:18px;
  border-bottom-left-radius:4px;width:fit-content;}
.typing-indicator span{width:7px;height:7px;background:#FFFFFF;border-radius:50%;
  animation:bounce 1.2s infinite;}
.typing-indicator span:nth-child(2){animation-delay:0.2s;}
.typing-indicator span:nth-child(3){animation-delay:0.4s;}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:0.4;}40%{transform:translateY(-6px);opacity:1;}}

/* ── Chat Input Bar (inside the phone frame) ────────────────────────── */
.stChatInput {
    position: sticky !important;
    bottom: 0 !important;
    left: 0 !important;
    transform: none !important;
    width: 100% !important;
    z-index: 10000;
    /* White bar that spans the full phone width */
    background: #FFFFFF !important;
    padding: 10px 16px 28px 16px !important;  /* 28px bottom = home-indicator clearance */
    margin-left: -20px !important;            /* bleed to phone edges */
    margin-right: -20px !important;
    box-shadow: 0 -1px 0 #e8e2dc;
}
/* The pill-shaped row Streamlit renders */
.stChatInput > div {
    background: #F0F2F7 !important;
    border: none !important;
    border-radius: 24px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 6px 0 14px !important;
    transition: box-shadow 0.2s;
}
.stChatInput > div:focus-within {
    box-shadow: 0 0 0 2px rgba(43,92,217,0.25) !important;
}
/* The textarea itself */
.stChatInput textarea {
    background: transparent !important;
    color: #1a1d27 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.93rem !important;
    border: none !important;
    outline: none !important;
    resize: none !important;
}
.stChatInput textarea::placeholder { color: #8b837a !important; }
/* Send button — blue circle with white arrow */
.stChatInput button {
    background: #2B5CD9 !important;
    border: none !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    min-width: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    flex-shrink: 0 !important;
    transition: background 0.2s, transform 0.15s !important;
    box-shadow: 0 2px 8px rgba(43,92,217,0.35) !important;
    padding: 0 !important;
}
.stChatInput button:hover {
    background: #1e4bb3 !important;
    transform: scale(1.07) !important;
}
/* Replace whatever SVG Streamlit puts inside with a white arrow via CSS */
.stChatInput button svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    width: 18px !important;
    height: 18px !important;
}


/* Bottom Home Indicator */
.home-indicator {
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 120px;
    height: 5px;
    background: #000;
    border-radius: 10px;
    opacity: 0.2;
    z-index: 1000;
}

::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:#2a2d3a;border-radius:10px;}

/* Video placeholder */
.video-wrap{width:100%;border-radius:16px;overflow:hidden;margin:1rem 0;
  border:1px solid #d8d1ca;background:#FFFFFF;}
.video-screen{width:100%;aspect-ratio:16/9;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:1rem;position:relative;overflow:hidden;}
.video-screen.idle{background:linear-gradient(135deg,#fcfaf8,#f4f0ec,#fcfaf8);}
.video-screen.playing{animation:vidPulse 3s ease-in-out infinite;
  background:linear-gradient(135deg,#fff2ed,#ffe8df,#fff2ed);}
.video-screen.complete{background:#fcfaf8;}
@keyframes vidPulse{0%,100%{background:linear-gradient(135deg,#fff2ed,#ffe8df,#fff2ed);}
  50%{background:linear-gradient(135deg,#ffe8df,#ffd9cd,#ffe8df);}}
.vid-icon{font-size:2.5rem;opacity:0.6;}
.vid-label{font-size:0.9rem;font-weight:500;color:#C4603A;letter-spacing:0.04em;}
.vid-sublabel{font-size:0.75rem;color:#8b837a;}
.vid-badge{font-size:0.75rem;font-weight:600;color:#34d399;background:rgba(52,211,153,0.1);
  border:1px solid rgba(52,211,153,0.3);border-radius:999px;padding:0.2rem 0.75rem;}
.video-controls{padding:0.75rem 1rem;display:flex;gap:0.75rem;justify-content:center;
  border-top:1px solid #d8d1ca;}

/* Summary card */
.summary-card{background:#FFFFFF;border:1px solid #C4603A30;border-radius:16px;
  padding:1.25rem 1.5rem;margin:1rem 0;}
.summary-card h4{color:#C4603A;font-size:0.8rem;font-weight:600;letter-spacing:0.08em;
  text-transform:uppercase;margin:0 0 0.75rem;}
.summary-card .snapshot{font-size:0.88rem;line-height:1.6;color:#1a1d27;margin-bottom:1.25rem;
  padding-bottom:1rem;border-bottom:1px solid #f0edea;}
.summary-field{display:flex;justify-content:space-between;align-items:center;
  padding:0.35rem 0;border-bottom:1px solid #f0edea;font-size:0.82rem;}
.summary-field:last-child{border-bottom:none;}
.summary-key{color:#8b837a;font-weight:500;}
.summary-val{color:#1a1d27;font-weight:400;text-align:right;max-width:60%;}
.flag-pill{display:inline-block;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
  color:#ef4444;border-radius:999px;font-size:0.7rem;font-weight:600;padding:0.15rem 0.6rem;margin:0.1rem;}

/* Streamlit button overrides */
.stButton>button{background: #2B5CD9 !important; color:#FFFFFF !important; border:none;
  border-radius:24px;font-family:'Inter',sans-serif;font-size:0.9rem;font-weight:600;
  padding:0.6rem 1.5rem;cursor:pointer;transition:all 0.2s;
  box-shadow: 0 4px 12px rgba(43, 92, 217, 0.2);}
.stButton>button:hover{background: #1e4bb3 !important; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(43, 92, 217, 0.3);}
/* No secondary buttons - all CTAs should be blue/white */


/* Splash Screen */
.splash-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    gap: 2rem;
    padding-bottom: 4rem;
}
.splash-logo {
    width: 180px;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Exercise library ──────────────────────────────────────────────────────────
EXERCISE_LIBRARY = [
    "Seated Knee Extension", "Straight Leg Raise", "Calf Raises",
    "Hip Abduction", "Glute Bridge", "Wall Squat",
    "Shoulder External Rotation", "Cervical Retraction",
    "Ankle Circles", "Quad Sets",
]

# ── Unified system prompt ─────────────────────────────────────────────────────
MOVY_UNIFIED_PROMPT = f"""
You are Movy, an agentic physiotherapy assistant guiding a patient through a complete journey:
1. Onboarding
2. Programme Selection
3. In-Session Exercise Experience
4. Post-Session Check-In
5. Physiotherapist Summary

You behave as a single continuous agent. Detect the current phase automatically from stored state.
Always speak with warmth, clarity, and encouragement.
Never give medical diagnoses. Stay within physiotherapy-appropriate guidance.

══════════════════════════════════════
PHASE 1 — ONBOARDING
══════════════════════════════════════
Collect: preferred name, injury description, injury timeline, work pattern,
activity level, preferred days, preferred time, days unavailable, goal anchor
(verbatim — never paraphrase), notification preference.

Ask ONE question at a time. Acknowledge each answer.
When all data is collected say exactly:
"Great, I have everything I need. Let me prepare your session."
Then emit: <MOVY_SIGNAL>{{"action":"onboarding_complete"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 2 — PROGRAMME SELECTION
══════════════════════════════════════
Use the injury to select 2 exercises from this library:
{EXERCISE_LIBRARY}

If injury is unclear, pick any 2. Store exercise_1_name and exercise_2_name.
Say: "Perfect, I've prepared two exercises for you. Let's begin."
Then emit: <MOVY_SIGNAL>{{"action":"exercises_selected","exercise_1":"[NAME]","exercise_2":"[NAME]"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 3 — IN-SESSION
══════════════════════════════════════
Step A: Introduce Exercise 1 warmly.
Then emit: <MOVY_SIGNAL>{{"action":"introduce_exercise","exercise":1}}</MOVY_SIGNAL>
(UI will show the video player. Wait for user to report completion.)

Step B: When user says they completed Exercise 1, do the mid-session check-in.
Ask: "How is it going?"
Classify response as: energetic / tired / pain / unsure / positive / no_response.
Store: mid_session_energy_level, mid_session_pain, mid_session_confusion.
Respond appropriately:
- energetic: encourage
- tired: slow pace, reassure
- pain: ask location → description → persistence; advise stop+rest if serious
- unsure: clarify
- positive: encourage
- no_response: repeat once, then continue gently

Step C: Introduce Exercise 2 warmly.
Then emit: <MOVY_SIGNAL>{{"action":"introduce_exercise","exercise":2}}</MOVY_SIGNAL>

Step D: When user says they completed Exercise 2, say:
"That's your session done, [preferred_name]. Great work — you're on track."
Then emit: <MOVY_SIGNAL>{{"action":"session_complete"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 4 — POST-SESSION CHECK-IN
══════════════════════════════════════
Ask: "Whenever you're ready, [preferred_name], we can do a quick check-in."

If 15+ minutes have passed before the user responds, adapt tone:
"Welcome back. Since some time has passed, let's do a quick check-in."

Collect in order:
Q1 — Adherence (all / partial / none). If none → skip Q2+Q3.
Q2 — Confidence (low / medium / high)
Q3 — Difficulty (manageable / about right / struggled)
Q4 — Overall experience. Adapt based on mid-session memory:
  - tired earlier → ask if fatigue changed
  - pain earlier → ask if pain changed
  - energetic earlier → reinforce
  - unsure earlier → ask if clarity improved
Q5 — Reflection (open text)

Safety: if user reports worsening pain, dizziness, or numbness → advise stop+rest,
mention physio will review.

After all check-in data is collected, generate the summary and emit:
<MOVY_SIGNAL>{{"action":"generate_summary","summary":{{"adherence":"","confidence":"","difficulty":"","pain_score":0,"fatigue":"","emotional_tone":"","mid_session_memory":"","overall_experience":"","reflection":"","flags":[]}}}}</MOVY_SIGNAL>

Replace all values with actual collected data. flags is a list of clinical concerns.

══════════════════════════════════════
PHASE 5 — PT SUMMARY
══════════════════════════════════════
Immediately after emitting generate_summary, write a clinical snapshot paragraph
for the physiotherapist (third person, under 30 seconds to read), covering:
injury, exercises performed, mid-session responses, post-session check-in,
pain flags, adherence, difficulty, confidence, overall experience.
Then say warmly to the patient: "All done. Your physiotherapist will have a full
summary ready for your next appointment. Well done today, [preferred_name]."

══════════════════════════════════════
BEHAVIOUR RULES
══════════════════════════════════════
- Always adapt based on memory across the full journey.
- Use preferred_name once per new topic, then drop it.
- Keep responses short, warm, conversational.
- Never show internal reasoning or JSON to the patient (except the PT snapshot).
- Never diagnose. Never contradict physiotherapy safety.
- One <MOVY_SIGNAL> per response, only at the exact moments described above.
- Never emit a signal at any other moment.
"""

# ── Client ────────────────────────────────────────────────────────────────────
client = OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"],
                base_url="https://openrouter.ai/api/v1")

# ── Signal parser ─────────────────────────────────────────────────────────────
_SIG_RE = re.compile(r'<MOVY_SIGNAL>(.*?)</MOVY_SIGNAL>', re.DOTALL)

def parse_signal(text: str):
    m = _SIG_RE.search(text)
    if not m:
        return text, None
    clean = _SIG_RE.sub('', text).strip()
    try:
        sig = json.loads(m.group(1).strip())
    except Exception:
        sig = None
    return clean, sig

def process_signal(sig: dict):
    if not sig:
        return
    a = sig.get("action", "")
    if a == "onboarding_complete":
        st.session_state.phase = "programme_selection"
    elif a == "exercises_selected":
        st.session_state.patient_data["exercise_1"] = sig.get("exercise_1", "Exercise 1")
        st.session_state.patient_data["exercise_2"] = sig.get("exercise_2", "Exercise 2")
        st.session_state.phase = "in_session"
        st.session_state.in_session_step = "intro"
    elif a == "introduce_exercise":
        n = sig.get("exercise", 1)
        st.session_state.in_session_step = f"ex{n}_ready"
    elif a == "session_complete":
        st.session_state.phase = "post_checkin"
        st.session_state.in_session_step = "done"
        st.session_state.music_playing = False
        if "session_end_time" not in st.session_state:
            st.session_state.session_end_time = time.time()
    elif a == "generate_summary":
        st.session_state.phase = "pt_summary"
        st.session_state.patient_data["summary"] = sig.get("summary", {})

# ── Audio loader ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_audio_b64() -> str | None:
    p = Path("assets/audio/ambient.mp3")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# ── Video loader ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_video_b64(n: int) -> str | None:
    """Load Ex0n.mp4 from assets/video/ and return as base64 string."""
    p = Path(f"assets/video/Ex0{n}.mp4")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# ── LLM call ─────────────────────────────────────────────────────────────────
def call_llm(history: list, temp: float = 0.7) -> str:
    r = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=history,
        temperature=temp,
    )
    return r.choices[0].message.content

# ── Session init ──────────────────────────────────────────────────────────────
if "show_splash" not in st.session_state:
    st.session_state.show_splash = True
if "phase" not in st.session_state:

    st.session_state.phase = "onboarding"
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "full_history" not in st.session_state:
    st.session_state.full_history = [{"role": "system", "content": MOVY_UNIFIED_PROMPT}]
if "in_session_step" not in st.session_state:
    st.session_state.in_session_step = "intro"
if "music_playing" not in st.session_state:
    st.session_state.music_playing = False
if "ex_state" not in st.session_state:
    st.session_state.ex_state = {1: "idle", 2: "idle"}

# ── Proactive opening ─────────────────────────────────────────────────────────
if not st.session_state.messages and not st.session_state.show_splash:
    _h = [*st.session_state.full_history,
          {"role": "user", "content": "Please begin the conversation now."}]
    _reply = call_llm(_h)
    _clean, _sig = parse_signal(_reply)
    st.session_state.full_history.append({"role": "user", "content": "Please begin the conversation now."})
    st.session_state.full_history.append({"role": "assistant", "content": _clean})
    st.session_state.messages.append({"role": "assistant", "content": _clean})
    process_signal(_sig)
    st.rerun()


# ── Phase progress indicator ──────────────────────────────────────────────────
PHASES = ["onboarding", "programme_selection", "in_session", "post_checkin", "pt_summary"]
PHASE_LABELS = ["Onboarding", "Programme", "Session", "Check-In", "Summary"]

def render_header():
    cur = PHASES.index(st.session_state.phase) if st.session_state.phase in PHASES else 0
    dots_html = ""
    for i, label in enumerate(PHASE_LABELS):
        cls = "active" if i == cur else ("done" if i < cur else "")
        dots_html += f'<div class="phase-step"><div class="phase-dot {cls}"></div><div class="phase-label">{label}</div></div>'
        if i < len(PHASE_LABELS) - 1:
            line_cls = "done" if i < cur else ""
            dots_html += f'<div class="phase-line {line_cls}" style="margin-bottom:1rem"></div>'
    st.markdown(f"""
    <div class="movy-header">
      <div class="logo">Movy</div>
      <div class="tagline">Your physiotherapy companion</div>
    </div>
    <div class="phase-bar">{dots_html}</div>
    """, unsafe_allow_html=True)

# The header and other elements will render inside the styled block-container
if st.session_state.show_splash:
    st.markdown('<div class="splash-container">', unsafe_allow_html=True)
    st.image("assets/images/movy_logo1.png", width=220)
    if st.button("Start Onboarding  →"):
        st.session_state.show_splash = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    render_header()
    # ── Render chat history ───────────────────────────────────────────────────────
    for msg in st.session_state.messages:
        rc = "user" if msg["role"] == "user" else "movy"
        st.markdown(f'<div class="chat-row {rc}"><div class="bubble {rc}">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)


# ── Ambient music ─────────────────────────────────────────────────────────────
if st.session_state.music_playing:
    audio_b64 = load_audio_b64()
    if audio_b64:
        st.markdown(f'<audio autoplay loop style="display:none"><source src="data:audio/mpeg;base64,{audio_b64}" type="audio/mpeg"></audio>',
                    unsafe_allow_html=True)

# ── Video widget ─────────────────────────────────────────────────────────────
def render_video_widget(n: int):
    """Render the exercise video player for exercise n (1 or 2)."""
    name = st.session_state.patient_data.get(f"exercise_{n}", f"Exercise {n}")
    state = st.session_state.ex_state.get(n, "idle")
    video_b64 = load_video_b64(n)

    def _embed_video(autoplay: bool = False) -> None:
        """Inject an HTML5 <video> element. Falls back to placeholder if file missing."""
        if video_b64:
            autoplay_attr = "autoplay" if autoplay else ""
            st.markdown(
                f"""
                <div class="video-wrap">
                  <video
                    {autoplay_attr}
                    controls
                    loop
                    playsinline
                    style="width:100%;border-radius:16px;display:block;"
                  >
                    <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                    Your browser does not support HTML5 video.
                  </video>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Fallback placeholder if video file is not found
            icon = "🏃" if autoplay else "▶️"
            sublabel = "Exercise in progress…" if autoplay else "Ready to begin"
            css_state = "playing" if autoplay else "idle"
            st.markdown(
                f"""
                <div class="video-wrap">
                  <div class="video-screen {css_state}">
                    <div class="vid-icon">{icon}</div>
                    <div class="vid-label">{name}</div>
                    <div class="vid-sublabel">{sublabel}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if state == "idle":
        # Show video paused, ready to start
        st.markdown(
            f'<div class="vid-label" style="font-size:0.9rem;font-weight:600;'
            f'color:#C4603A;margin-bottom:0.4rem;">{name}</div>',
            unsafe_allow_html=True,
        )
        _embed_video(autoplay=False)
        if st.button(f"▶ Start Exercise {n}", key=f"start_{n}"):
            st.session_state.ex_state[n] = "playing"
            st.session_state.music_playing = True
            st.rerun()

    elif state == "playing":
        # Video autoplays while in progress
        st.markdown(
            f'<div class="vid-label" style="font-size:0.9rem;font-weight:600;'
            f'color:#C4603A;margin-bottom:0.4rem;">{name} — in progress 🏃</div>',
            unsafe_allow_html=True,
        )
        _embed_video(autoplay=True)
        if st.button(f"✓ Mark Exercise {n} Complete", key=f"done_{n}"):
            st.session_state.ex_state[n] = "complete"
            st.session_state.music_playing = False
            msg = f"I've completed {name}."
            st.session_state.messages.append({"role": "user", "content": msg})
            st.session_state.full_history.append({"role": "user", "content": msg})
            typing_ph = st.empty()
            typing_ph.markdown(
                '<div class="chat-row movy"><div class="typing-indicator">'
                '<span></span><span></span><span></span></div></div>',
                unsafe_allow_html=True,
            )
            reply = call_llm(st.session_state.full_history)
            typing_ph.empty()
            clean, sig = parse_signal(reply)
            st.session_state.full_history.append({"role": "assistant", "content": clean})
            st.session_state.messages.append({"role": "assistant", "content": clean})
            process_signal(sig)
            st.rerun()

    elif state == "complete":
        st.markdown(
            f"""
            <div class="video-wrap">
              <div class="video-screen complete">
                <div class="vid-badge">✓ Completed</div>
                <div class="vid-label" style="color:#6b7280">{name}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Show video widget when in-session
if st.session_state.phase == "in_session":
    step = st.session_state.in_session_step
    ex1_s = st.session_state.ex_state.get(1, "idle")
    ex2_s = st.session_state.ex_state.get(2, "idle")
    # Always show ex1 widget once it has been introduced
    if step in ("ex1_ready",) or ex1_s in ("playing", "complete"):
        render_video_widget(1)
    # Show ex2 widget once it has been introduced
    if step in ("ex2_ready",) or ex2_s in ("playing", "complete"):
        render_video_widget(2)

# ── PT Summary card ───────────────────────────────────────────────────────────
if st.session_state.phase == "pt_summary":
    summary = st.session_state.patient_data.get("summary", {})
    if summary:
        flags = summary.get("flags", [])
        flag_html = "".join(f'<span class="flag-pill">⚠ {f}</span>' for f in flags) if flags else '<span style="color:#6b7280">None</span>'
        fields = [
            ("Adherence", summary.get("adherence", "—")),
            ("Confidence", summary.get("confidence", "—")),
            ("Difficulty", summary.get("difficulty", "—")),
            ("Pain score", summary.get("pain_score", "—")),
            ("Fatigue", summary.get("fatigue", "—")),
            ("Emotional tone", summary.get("emotional_tone", "—")),
            ("Overall experience", summary.get("overall_experience", "—")),
            ("Reflection", summary.get("reflection", "—")),
        ]
        rows = "".join(f'<div class="summary-field"><span class="summary-key">{k}</span><span class="summary-val">{v}</span></div>' for k, v in fields)
        st.markdown(f"""
        <div class="summary-card">
          <h4>📋 PT Summary</h4>
          <div class="summary-field">
            <span class="summary-key">Mid-session</span>
            <span class="summary-val">{summary.get("mid_session_memory","—")}</span>
          </div>
          {rows}
          <div class="summary-field">
            <span class="summary-key">Clinical flags</span>
            <span class="summary-val">{flag_html}</span>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type your message…")

if user_input and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.full_history.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="chat-row user"><div class="bubble user">{user_input}</div></div>',
                unsafe_allow_html=True)

    ph = st.empty()
    ph.markdown('<div class="chat-row movy"><div class="typing-indicator"><span></span><span></span><span></span></div></div>',
                unsafe_allow_html=True)

    reply = call_llm(st.session_state.full_history)
    ph.empty()

    clean, sig = parse_signal(reply)
    st.session_state.full_history.append({"role": "assistant", "content": clean})
    st.session_state.messages.append({"role": "assistant", "content": clean})
    process_signal(sig)

    ph.markdown(f'<div class="chat-row movy"><div class="bubble movy">{clean}</div></div>',
                unsafe_allow_html=True)
    st.rerun()
