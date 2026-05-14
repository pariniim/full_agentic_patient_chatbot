import streamlit as st
import streamlit.components.v1 as components
import json, re, time, base64, random
from datetime import date
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
    background: #FAF6F2;
    color: #1a1d27;
}
#MainMenu,footer,header{visibility:hidden;}

/* Main content area — clean, no phone frame */
.block-container {
    background: #FAF6F2 !important;
    max-width: 680px !important;
    margin: 0 auto !important;
    padding: 6rem 1.5rem 6rem 1.5rem !important;
    border: none !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"]{display:none;}


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

/* Sticky header — fixed to the top of the viewport */
.sticky-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background: #FAF6F2;
    padding: 10px 20px 0.75rem 20px;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    box-sizing: border-box;
    z-index: 8000;
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
.chat-row{display:flex;margin-bottom:1rem;animation:fadeSlide 0.25s ease-out;align-items:flex-end;}
@keyframes fadeSlide{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.chat-row.user{justify-content:flex-end;}
.chat-row.movy{justify-content:flex-start;gap:8px;}
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
/* Movy avatar icon */
.movy-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
    align-self: flex-end;
    margin-bottom: 2px;
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

/* Square exercise videos (st.video renders these) */
.stVideo, [data-testid="stVideo"] {
    width: 100% !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}
.stVideo video, [data-testid="stVideo"] video {
    width: 100% !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
    border-radius: 16px !important;
    display: block !important;
}

/* Chat Input Bar */
.stChatInput {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    z-index: 5000 !important;
    background: #FFFFFF !important;
    padding: 10px 14px 24px 14px !important;
    box-shadow: 0 -1px 0 rgba(0,0,0,0.06) !important;
}
/* Every wrapper div Streamlit nests inside the bar → all #F0F2F7 */
.stChatInput div,
.stChatInput > div,
.stChatInput [data-testid="stChatInputTextArea"],
.stChatInput [data-baseweb="textarea"],
.stChatInput [data-baseweb="base-input"] {
    background: #F0F2F7 !important;
    background-color: #F0F2F7 !important;
    border: none !important;
    border-radius: 24px !important;
}
.stChatInput > div {
    display: flex !important;
    align-items: center !important;
    padding: 0 6px 0 14px !important;
    transition: box-shadow 0.2s;
}
.stChatInput > div:focus-within {
    box-shadow: 0 0 0 2px rgba(43,92,217,0.25) !important;
}
/* Textarea itself — explicit background, NOT transparent */
.stChatInput textarea {
    background: #F0F2F7 !important;
    background-color: #F0F2F7 !important;
    color: #1a1d27 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.93rem !important;
    border: none !important;
    outline: none !important;
    resize: none !important;
    box-shadow: none !important;
    -webkit-text-fill-color: #1a1d27 !important;
}
.stChatInput textarea::placeholder {
    color: #B4BACF !important;
    opacity: 1 !important;
}
.stChatInput textarea:focus {
    background: #F0F2F7 !important;
    background-color: #F0F2F7 !important;
    outline: none !important;
    box-shadow: none !important;
}
/* #2B5CD9 round send button */
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
/* White arrow SVG — rotated 90° so it points RIGHT */
.stChatInput button svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    width: 18px !important;
    height: 18px !important;
    transform: rotate(90deg) !important;
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
    text-align: center;
    gap: 2rem;
    padding: 4rem 1rem;
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

MOVY_UNIFIED_PROMPT = f"""
TODAY'S DATE: {date.today().strftime("%A, %d %B %Y")}
Always use this date as "today" for any date calculations.

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

🔵 NEW — After all onboarding fields are collected:
Compute next_appointment_date as follows:
- Start from TODAY'S DATE shown at the top of this prompt.
- Add exactly 1 calendar month.
- If the resulting date falls on a Saturday or Sunday, shift forward to the next Monday.
- Assign a random time between 09:00 and 18:00, choosing only full or half hours
  (e.g., 09:00, 09:30, 10:00, 10:30, …).
Store next_appointment_date.

Then say:
"Great, I have everything I need. Your next appointment is scheduled for [next_appointment_date]. 
When you're ready, you can start your exercise session by tapping the button below."

After saying this, proactively invite the user:
"Would you like to begin your session now?"

Then emit:
<MOVY_SIGNAL>{{"action":"onboarding_complete","next_appointment":"[next_appointment_date]"}}</MOVY_SIGNAL>

The UI will show a 'Start Session' button. Movy should encourage the user to tap it,
but must wait for the user to press the button before moving to Programme Selection.

══════════════════════════════════════
PHASE 2 — PROGRAMME SELECTION
══════════════════════════════════════
Two exercise videos have been selected for this session.

They must always be referred to as:
- “Exercise 1”
- “Exercise 2”

Never mention filenames (e.g., Ex01.mp4). Never show filenames in the user bubble.

Randomly choose the sequence order each time:
Option A: Exercise 1 → Exercise 2
Option B: Exercise 2 → Exercise 1

Store exercise_1_name = "Exercise 1"
Store exercise_2_name = "Exercise 2"
(Only the labels are stored; filenames are never spoken.)

Say:
"Perfect, I've prepared two exercises for you. Let's begin."

Then emit:
<MOVY_SIGNAL>{{"action":"exercises_selected","exercise_1":"Exercise 1","exercise_2":"Exercise 2"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 3 — IN-SESSION
══════════════════════════════════════
Step A: Introduce Exercise 1 warmly.
Say:
"Let's start with your first exercise. Follow the video and take your time."

Then emit:
<MOVY_SIGNAL>{{"action":"introduce_exercise","exercise":1}}</MOVY_SIGNAL>

UI behaviour:
- Play “Exercise 1” video.
- Automatically start ambient music (assets/audio/ambient.mp3).
- Show a “Mark Exercise as Complete” button.
Wait until the user presses the completion button.

Step B: When the user marks Exercise 1 as complete:
Ask the mid-session check-in question:
"How is it going?"

Classify response as: energetic / tired / pain / unsure / positive / no_response.
Store: mid_session_energy_level, mid_session_pain, mid_session_confusion.

Pain threshold rule:
If pain ≥ 8/10 → treat as severe:
- advise immediate stop
- recommend rest
- reassure physiotherapist will review
- do NOT continue unless user insists

Step C: Introduce Exercise 2 warmly.
Say:
"Great. Let's move on to your second exercise."

Then emit:
<MOVY_SIGNAL>{{"action":"introduce_exercise","exercise":2}}</MOVY_SIGNAL>

UI behaviour:
- Play “Exercise 2” video.
- Automatically start ambient music (assets/audio/ambient.mp3).
- Show a “Mark Exercise as Complete” button.
Wait until the user presses the completion button.

Step D: When the user marks Exercise 2 as complete:
Say:
"That's your session done, [preferred_name]. Great work — you're on track."

Then emit:
<MOVY_SIGNAL>{{"action":"session_complete"}}</MOVY_SIGNAL>


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
Q4 — Overall experience (adapt based on mid-session memory)
Q5 — Reflection (open text)

🔵 NEW — Pain threshold rule:
If user reports pain ≥ 8/10 at any point:
- classify as severe
- advise stop+rest
- add a pain flag to summary
- reassure physiotherapist will review

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
pain flags, adherence, difficulty, confidence, overall experience,
🔵 NEW — include next_appointment_date.

Then say warmly to the patient:
"All done. Your physiotherapist will have a full summary ready for your next appointment. Well done today, [preferred_name]."

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
        # Save the appointment date the LLM computed
        if sig.get("next_appointment"):
            st.session_state.patient_data["next_appointment"] = sig["next_appointment"]
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

# ── Logo loader (PNG avatar for chat bubbles) ────────────────────────────────
@st.cache_data(show_spinner=False)
def load_logo_b64() -> str | None:
    p = Path("assets/images/LogoCircle1.png")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# ── Splash logo loader (SVG — stays vector, no rasterisation) ────────────────
@st.cache_data(show_spinner=False)
def load_splash_svg() -> str | None:
    """Return a base64-encoded data URI for the SVG splash logo."""
    p = Path("assets/images/movy_logo1.svg")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    # Fallback to PNG if SVG not found
    p2 = Path("assets/images/movy_logo1.png")
    if p2.exists():
        return None  # caller will use st.image for PNG
    return None

# ── Video loader ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_video_b64(n: int) -> str | None:
    """Load Ex0n.mp4 from assets/video/ and return as base64 string."""
    p = Path(f"assets/video/Ex0{n}.mp4")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# All available exercise video files
VIDEO_FILES = [
    "Ex01_square.mp4",
    "Ex02_square.mp4",
    "Ex03_square.mp4",
    "Ex04_square.mp4",
]

def _video_path(exercise_name: str) -> Path:
    """Resolve the Path to the video file for the given exercise label.

    The LLM uses 'Exercise 1' / 'Exercise 2' as labels.
    We map these to the session-selected video files.
    """
    selected = st.session_state.get('selected_videos', VIDEO_FILES[:2])
    nm = exercise_name.lower().strip()
    if nm in ('exercise 2', 'ex2', 'exercise2'):
        return Path(f'assets/video/{selected[1]}')
    if nm in ('exercise 1', 'ex1', 'exercise1'):
        return Path(f'assets/video/{selected[0]}')
    # Fallback: try matching against known filenames
    for vf in selected:
        if vf.lower().replace('_square.mp4', '') in nm or vf.lower() in nm:
            return Path(f'assets/video/{vf}')
    return Path(f'assets/video/{selected[0]}')

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
# Pick 2 random exercise videos for this session (done once at session start)
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = random.sample(VIDEO_FILES, 2)

if "full_history" not in st.session_state:
    _v1, _v2 = st.session_state.selected_videos
    _session_prompt = (
        MOVY_UNIFIED_PROMPT
        + f"\n\n[SESSION VIDEOS]\nVideo A: {_v1}\nVideo B: {_v2}\n"
        + "These are the internal filenames — NEVER speak or emit them.\n"
        + "Refer to them only as 'Exercise 1' and 'Exercise 2' in all messages and signals."
    )
    st.session_state.full_history = [{"role": "system", "content": _session_prompt}]
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
    <div class="sticky-header">
      <div class="movy-header">
        <div class="logo">Movy</div>
        <div class="tagline">Your physiotherapy companion</div>
      </div>
      <div class="phase-bar">{dots_html}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Splash screen ──────────────────────────────────────────────────────────────────────
if st.session_state.show_splash:
    # Add vertical space to push content towards the centre
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    # Centre with columns: narrow | content | narrow
    _, col, _ = st.columns([1, 3, 1])
    with col:
        _svg_b64 = load_splash_svg()
        if _svg_b64:
            # Inline SVG via data URI — stays vector, renders crisp at any DPI
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{_svg_b64}" '
                f'style="width:460px;max-width:100%;display:block;margin:0 auto 1rem auto;" '
                f'alt="Movy logo" />',
                unsafe_allow_html=True,
            )
        else:
            st.image("assets/images/movy_logo1.png", width=320)
        st.write("")
        if st.button("Start Onboarding  →", use_container_width=True):
            st.session_state.show_splash = False
            st.rerun()
else:
    render_header()
    # ── Render chat history ───────────────────────────────────────────────────────
    _logo_b64 = load_logo_b64()
    _avatar_html = (
        f'<img src="data:image/png;base64,{_logo_b64}" class="movy-avatar" alt="Movy">'
        if _logo_b64 else ''
    )
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-row user"><div class="bubble user">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="chat-row movy">{_avatar_html}<div class="bubble movy">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )


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
    vid_path = _video_path(name)

    def _show_video():
        if vid_path.exists():
            st.video(str(vid_path))
        else:
            st.warning(f"Video not found: {vid_path}")

    if state == "idle":
        st.markdown(
            f'<div class="vid-label" style="font-size:0.9rem;font-weight:600;'
            f'color:#C4603A;margin-bottom:0.4rem;">{name}</div>',
            unsafe_allow_html=True,
        )
        _show_video()
        if st.button(f"▶ Start Exercise {n}", key=f"start_{n}"):
            st.session_state.ex_state[n] = "playing"
            st.session_state.music_playing = True
            st.rerun()

    elif state == "playing":
        st.markdown(
            f'<div class="vid-label" style="font-size:0.9rem;font-weight:600;'
            f'color:#C4603A;margin-bottom:0.4rem;">{name} — in progress 🏃</div>',
            unsafe_allow_html=True,
        )
        _show_video()
        if st.button(f"✓ Mark Exercise {n} Complete", key=f"done_{n}"):
            st.session_state.ex_state[n] = "complete"
            st.session_state.music_playing = False
            msg = f"I have completed {name}."
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
            f'<div class="video-wrap"><div class="video-screen complete">'
            f'<div class="vid-badge">✓ Completed</div>'
            f'<div class="vid-label" style="color:#6b7280">{name}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# Show video widget when in-session
if st.session_state.phase == "in_session":
    step = st.session_state.in_session_step
    ex1_s = st.session_state.ex_state.get(1, "idle")
    ex2_s = st.session_state.ex_state.get(2, "idle")

    # Show ex1 widget while it hasn't been replaced by ex2 starting
    ex2_active = ex2_s in ("playing", "complete") or step == "ex2_ready"
    if (step in ("ex1_ready",) or ex1_s in ("playing", "complete")) and not (ex1_s == "complete" and ex2_active):
        render_video_widget(1)

    # Show ex2 widget as soon as ex1 is complete OR ex2 has been introduced
    if ex2_active or ex1_s == "complete":
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

# ── Inject placeholder colour (components.html actually executes JS) ──────────
components.html("""
<script>
(function(){
    var doc = window.parent.document;
    if (doc.getElementById('movy-placeholder-style')) return;
    var s = doc.createElement('style');
    s.id = 'movy-placeholder-style';
    s.textContent = [
        '.stChatInput textarea::placeholder { color: #B4BACF !important; opacity: 1 !important; }',
        '.stChatInput textarea::-webkit-input-placeholder { color: #B4BACF !important; opacity: 1 !important; }',
        '.stChatInput textarea:-ms-input-placeholder { color: #B4BACF !important; opacity: 1 !important; }',
    ].join('');
    doc.head.appendChild(s);
})();
</script>
""", height=0)

# ── Chat input (hidden during splash) ───────────────────────────────────────
if not st.session_state.get("show_splash", True):
    user_input = st.chat_input("Type your message…")
else:
    user_input = None

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
