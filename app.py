import streamlit as st
import streamlit.components.v1 as components
import json, re, time, base64, random
from datetime import date, timedelta
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
    padding: 7rem 1.5rem 6rem 1.5rem !important;
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
    padding: 0.75rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    box-sizing: border-box;
    z-index: 8000;
    display: flex;
    justify-content: center;
    align-items: center;
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
@keyframes green-flash{0%{background:#22c55e;transform:scale(1);}50%{background:#16a34a;transform:scale(1.04);}100%{background:#22c55e;transform:scale(1);}}

/* Square exercise videos — native controls hidden; button is the only control */
.stVideo, [data-testid="stVideo"] {
    width: 60% !important;
    margin: 0 auto !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    border: 1px solid #4a4a4a !important;
}
.stVideo video, [data-testid="stVideo"] video {
    width: 100% !important;
    aspect-ratio: 1 / 1 !important;
    object-fit: cover !important;
    border-radius: 16px !important;
    display: block !important;
    pointer-events: none !important;       /* disable click-on-video */
}
/* Hide the browser's built-in video control bar */
.stVideo video::-webkit-media-controls,
[data-testid="stVideo"] video::-webkit-media-controls {
    display: none !important;
}
.stVideo video::-webkit-media-controls-enclosure,
[data-testid="stVideo"] video::-webkit-media-controls-enclosure {
    display: none !important;
}

/* Chat Input Bar */
.stChatInput {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    z-index: 5000 !important;
    background: #FFFFFF !important;
    padding: 10px 14px 60px 14px !important;
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

/* Voice Controls */
.voice-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 8px;
    margin-left: auto; 
    align-self: center !important;
}

.voice-btn {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    background: transparent;
    color: #B4BACF;
    border: 1px solid #E0E2E7;
    flex-shrink: 0 !important;
}

.voice-btn:hover {
    background: #F0F2F7;
    color: #2B5CD9;
}

.voice-btn.active {
    background: #2B5CD9;
    color: #FFFFFF;
    border-color: #2B5CD9;
    animation: pulse-ring 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}

#movy-mic-btn {
    background: #5A6480 !important;
    color: #FFFFFF !important;
    border: none !important;
    transform: rotate(-90deg) !important; /* Points left */
}

#movy-speaker-btn {
    transform: none !important; /* Remove rotation from speaker */
}

.voice-btn.speaker-on {
    color: #2B5CD9;
    background: #EBF0FF;
    border-color: #2B5CD9;
}

.splash-video-container {
    width: 280px;
    height: 280px;
    margin: 0 auto 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.splash-video {
    width: 280px;
    height: auto;
    transform: rotate(90deg); /* Rotate 90deg right */
}

/* Bubble Speaker Button */
.bubble.movy {
    position: relative;
    padding-right: 2.2rem !important; /* Space for speaker icon */
}

.bubble-speaker-btn {
    position: absolute;
    right: 8px;
    bottom: 8px;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    z-index: 10;
}

.bubble-speaker-btn:hover {
    color: #FFFFFF;
    background: rgba(255, 255, 255, 0.15);
}

.bubble-speaker-btn svg {
    width: 16px;
    height: 16px;
}

.listening-indicator {
    position: absolute;
    top: -32px;
    left: 50%;
    transform: translateX(-50%);
    background: #1a1d27;
    color: #FFFFFF;
    border: 1px solid #000000;
    padding: 4px 14px;
    border-radius: 14px;
    font-size: 0.75rem;
    font-weight: 600;
    display: none;
    white-space: nowrap;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
  border-radius:24px;font-family:'Inter',sans-serif;font-size:1rem;font-weight:600;
  padding:0.8rem 2.2rem 0.8rem 2rem;cursor:pointer;transition:all 0.2s;
  white-space: nowrap !important;
  box-shadow: 0 4px 12px rgba(43, 92, 217, 0.2);}
.stButton>button:hover{background: #1e4bb3 !important; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(43, 92, 217, 0.3);}
/* Ensure splash button is on top */
div.stButton {
    position: relative;
    z-index: 10000 !important;
}
/* No secondary buttons - all CTAs should be blue/white */


.splash-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #FAF6F2;
    z-index: 9000;
}

.splash-v-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 15vh;
    z-index: 9999 !important; /* Extremely high to be on top of bg */
    position: relative;
}

.splash-v-center h2 {
    color: #2B5CD9;
    font-size: 2.6rem;
    font-weight: 600;
    margin: 0.5rem 0 0.2rem 0 !important;
}

.splash-v-center p {
    color: #5A6480;
    font-size: 1.3rem;
    margin-bottom: 2rem !important;
}

/* Appointment Summary Cards */
.appointment-summary-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem 0;
    width: 100%;
}
.summary-header-card {
    text-align: center;
    margin-bottom: 1.5rem;
}
.summary-header-img {
    width: 200px;
    height: auto;
    margin-bottom: 1rem;
}

.param-item {
    font-size: 0.88rem;
    color: #5A6480;
    margin-bottom: 1.25rem;
    line-height: 1.4;
}

/* Redesigned Summary Pills */
.pill-row {
    display: flex;
    gap: 0.75rem;
    margin-top: 0.3rem;
    width: 100%;
}
.pill-container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    flex: 1;
}
.pill-label {
    font-size: 0.72rem;
    color: #8E98B0;
    margin-bottom: 0.2rem;
    margin-left: 0.4rem;
}
.param-pill {
    width: 100%;
    border: none;
    padding: 0.45rem 0;
    text-align: left;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a1d27;
    background: transparent;
    white-space: nowrap;
}
.exercise-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1d27;
    margin-bottom: 0.1rem;
}

.circle-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border: none;
    font-weight: 600;
    color: #1a1d27;
}

.date-pill {
    display: flex;
    align-items: center;
    border: none;
    padding: 0.5rem 0;
    width: 100%;
    gap: 0.75rem;
    font-weight: 600;
    color: #1a1d27;
    white-space: nowrap;
}

.clinical-label {
    font-size: 0.85rem;
    color: #8E98B0;
    margin-bottom: 0.8rem;
    margin-top: 1rem;
    border-bottom: 1px solid #EAECEF;
    padding-bottom: 0.4rem;
}

.summary-row {
    display: flex;
    gap: 2rem;
    align-items: stretch; /* Force same height */
    width: 100%;
}
.summary-param-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 2.25rem;
    flex: 1;
    display: flex;
    flex-direction: column;
    border: 1px solid #EAECEF;
}

/* Premium Video Modal Overlay */
.video-overlay {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: rgba(255,255,255,0.7);
    z-index: 500;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(12px);
}
.video-modal-content {
    background: white;
    width: 90%;
    max-width: 450px;
    height: auto;
    border-radius: 32px;
    padding: 2rem;
    box-shadow: 0 30px 60px rgba(0,0,0,0.12);
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 501;
}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.close-btn-in-header {
    margin-bottom: 0 !important;
}
.close-btn-in-header button {
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    padding: 0 !important;
    border: 1px solid #E0E2E7 !important;
    background-color: white !important;
    color: #1a1d27 !important;
    line-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.video-modal-params {
    display: flex;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.splash-v-center {
    margin-top: -30vh !important;
    text-align: center;
    width: 100%;
}
.splash-video-container {
    margin-bottom: 0.5rem;
}
.splash-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #FAF6F2;
    z-index: 4000;
}
.video-modal-params div {
    color: #8E98B0;
    font-size: 0.95rem;
}
.param-divider {
    width: 1px;
    background: #EAECEF;
    height: 20px;
}
.video-container-inner {
    width: 100%;
    border-radius: 20px;
    overflow: hidden;
    background: #f8f9fa;
    position: relative; /* For overlay positioning */
}
.video-start-overlay {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
}
.start-cta-container {
    margin-bottom: 0 !important;
}
.start-cta-container button {
    background: #FFFFFF !important;
    color: #1a1d27 !important;
    border-radius: 24px !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 600 !important;
    border: none !important;
}
.mark-complete-container {
    margin-top: 1.5rem;
    text-align: center;
}
.mark-complete-container button {
    width: 100% !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
}
.btn-completed button {
    background-color: #22c55e !important;
    color: white !important;
    border: none !important;
}
.video-container-inner video {
    width: 100%;
    display: block;
}

.splash-native-btn {
    background: #2B5CD9 !important;
    color: #FFFFFF !important;
    border: none;
    border-radius: 24px;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    padding: 0.8rem 2.2rem;
    cursor: pointer;
    transition: all 0.2s;
    margin-top: 1.5rem;
    box-shadow: 0 4px 12px rgba(43, 92, 217, 0.25);
}

.splash-native-btn:hover {
    background: #1e4bb3 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(43, 92, 217, 0.35);
}

/* Ensure the streamlit button for splash is centered and visible */
.splash-btn-container {
    display: flex;
    justify-content: center;
    width: 100%;
    margin-top: 2rem;
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
Collect the following information in a conversational manner. Ask ONE question at a time and acknowledge each answer:
- preferred name
- injury description
- injury timeline
- work pattern
- activity level
- preferred days for sessions
- preferred time of day for sessions (CRITICAL: Always ask this immediately AFTER asking about preferred days)
- days unavailable
- the patient’s personal recovery goal (ask in natural language, never say “goal anchor”)

🔵 NEW — After all onboarding fields are collected:
Compute next_appointment_date as follows:
- Start from TODAY'S DATE shown at the top of this prompt.
- Add exactly 1 calendar month.
- If the resulting date falls on a Saturday or Sunday, shift forward to the next Monday.
- Assign a random time between 09:00 and 18:00, choosing only full or half hours
  (e.g., 09:00, 09:30, 10:00, 10:30, …).
Store next_appointment_date.

Then, do NOT speak further. Immediately emit:
<MOVY_SIGNAL>{{"action":"onboarding_complete","next_appointment":"[next_appointment_date]"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 3 — IN-SESSION
══════════════════════════════════════
Movy is PROACTIVE. Once the session starts, immediately introduce Exercise 1.

Step A: Introduce Exercise 1 warmly and encouragingly.
Say:
"Let's start with your exercise. Follow the video and take your time — I'm right here if you need anything."

Then emit:
<MOVY_SIGNAL>{{"action":"introduce_exercise","exercise":1}}</MOVY_SIGNAL>

UI behaviour:
- Play “Exercise 1” video.
- Wait until the user presses the "Start Check-In" button.

Step B: When the user presses the "Start Check-In" button:
The UI will send the hidden trigger: "I am ready for the check-in."
Congratulate the user on finishing the session. Say something like: "That's your session done, [preferred_name]. Great work — you're on track. Let's do a quick check-in. A few quick questions and you're done."
Then ask the first check-in question straight away.

Then emit:
<MOVY_SIGNAL>{{"action":"session_complete"}}</MOVY_SIGNAL>

══════════════════════════════════════
PHASE 4 — POST-SESSION CHECK-IN
══════════════════════════════════════
You have just asked the first question. Wait for the user to reply, and collect the following in order.
CRITICAL RULE: NEVER mention the internal question numbers (like "Q1", "Q3", "Q5") to the patient. Just ask the questions naturally.

Collect in order:
1. Pain level (Ask if they have any pain right now. If yes, ask for a rating 1-10. If ≥8, apply the pain threshold rule below before moving on).
2. Adherence (all / partial / none). If none → skip questions 3 and 4.
3. Confidence (low / medium / high)
4. Difficulty (manageable / about right / struggled)
5. Overall experience (adapt based on mid-session memory)
6. Reflection (open text)

🔵 NEW — Pain threshold rule:
If user reports pain ≥ 8/10 at any point:
- classify as severe
- advise stop+rest immediately with high empathy
- add a pain flag to summary
- reassure them their physiotherapist will review it

Safety: if user reports worsening pain, dizziness, or numbness → advise stop+rest,
mention physio will review.

CRITICAL RULE: Once the patient has answered the final question (Reflection), you MUST immediately generate the summary and emit the following signal in your response:
<MOVY_SIGNAL>{{"action":"generate_summary","summary":{{"adherence":"","confidence":"","difficulty":"","pain_score":0,"fatigue":"","emotional_tone":"","mid_session_memory":"","overall_experience":"","reflection":"","flags":[]}}}}</MOVY_SIGNAL>

Replace all values with actual collected data. flags is a list of clinical concerns.

══════════════════════════════════════
PHASE 4 CONCLUSION
══════════════════════════════════════
Immediately after emitting generate_summary, say warmly to the patient:
"All done. Your physiotherapist will have a full summary ready for your next appointment. Well done today, [preferred_name]!"

CRITICAL RULE: Do NOT write any clinical snapshot, summary paragraph, or snapshot text inside the chat message. Only write the warm message directly to the patient.

This completes the Movy experience.

══════════════════════════════════════
BEHAVIOUR RULES
══════════════════════════════════════
- Always adapt based on memory across the full journey.
- Use preferred_name once per new topic, then drop it.
- Keep responses short, warm, conversational.
- Never show internal reasoning, JSON, or clinical summaries to the patient.
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
        # TRIGGER SPLASH IMMEDIATELY
        st.session_state.show_splash = True
        st.session_state.splash_target_phase = "programme_selection"
        st.session_state.phase = "programme_selection"
    elif a == "exercises_selected":
        st.session_state.patient_data["exercise_1"] = sig.get("exercise_1", "Exercise 1")
        st.session_state.patient_data["exercise_2"] = sig.get("exercise_2", "Exercise 2")
        st.session_state.phase = "in_session"
        st.session_state.in_session_step = "intro"
    elif a == "introduce_exercise":
        n = sig.get("exercise", 1)
        st.session_state.in_session_step = f"ex{n}_ready"
    elif a == "checkin_pain_followup":
        # LLM detected pain in check-in reply and has asked for a rating.
        # Keep the button hidden until we know the rating is safe.
        st.session_state.in_session_step = "ex1_pain_rating_pending"
    elif a == "checkin_resolved":
        # LLM has fully processed the check-in (or pain rating).
        if sig.get("proceed", True):
            # Pain < 8 or non-pain response — show the Continue button.
            st.session_state.in_session_step = "ex1_checkin_answered"
        else:
            # Pain ≥ 8 — block progression entirely.
            st.session_state.in_session_step = "ex1_pain_stopped"
    elif a == "session_complete":
        st.session_state.phase = "post_checkin"
        st.session_state.in_session_step = "done"
        if "session_end_time" not in st.session_state:
            st.session_state.session_end_time = time.time()
    elif a == "generate_summary":
        st.session_state.patient_data["summary"] = sig.get("summary", {})
    elif a == "show_splash":
        p = sig.get("phase", "onboarding")
        if p != "pt_summary":
            st.session_state.show_splash = True
            st.session_state.splash_target_phase = p


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
    "ex_vid_01.mp4",
    "ex_vid_02.mp4",
    "ex_vid_03.mp4",
    "ex_vid_04.mp4",
    "ex_vid_05.mp4",
    "ex_vid_06.mp4",
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
    # Inject current state context to prevent the LLM from regressing to earlier phases
    current_phase = st.session_state.get("phase", "unknown")
    current_step = st.session_state.get("in_session_step", "unknown")
    
    state_injection = {
        "role": "system", 
        "content": f"CRITICAL STATE NOTIFICATION: You are currently in Phase '{current_phase}' (step: '{current_step}'). You must strictly follow the instructions for THIS phase. Do NOT regress to Phase 1 (Onboarding) or ask for the patient's name if you are in a later phase. Respond directly to the user's latest input according to your current phase rules."
    }
    
    # Prepend the state injection right after the main system prompt
    if len(history) > 0 and history[0]["role"] == "system":
        _v1 = st.session_state.get("selected_videos", ["Ex1"])[0]
        history[0]["content"] = (
            MOVY_UNIFIED_PROMPT
            + f"\n\n[SESSION VIDEO]\nVideo: {_v1}\n"
            + "This is the internal filename — NEVER speak or emit it.\n"
            + "Refer to it only as 'your exercise' or 'Exercise 1' in all messages and signals."
        )
        llm_history = [history[0], state_injection] + history[1:]
    else:
        llm_history = [state_injection] + history
        
    r = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=llm_history,
        temperature=temp,
    )
    return r.choices[0].message.content

# ── Session init ──────────────────────────────────────────────────────────────
if "show_splash" not in st.session_state:
    st.session_state.show_splash = True
if "phase" not in st.session_state:
    st.session_state.phase = "onboarding"
if "onboarding_completed" not in st.session_state:
    st.session_state.onboarding_completed = False
if "patient_data" not in st.session_state:
    st.session_state.patient_data = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
# Pick 2 random exercise videos for this session (done once at session start)
if "selected_videos" not in st.session_state:
    st.session_state.selected_videos = random.sample(VIDEO_FILES, 2)

if "full_history" not in st.session_state:
    _v1 = st.session_state.selected_videos[0]
    _session_prompt = (
        MOVY_UNIFIED_PROMPT
        + f"\n\n[SESSION VIDEO]\nVideo: {_v1}\n"
        + "This is the internal filename — NEVER speak or emit it.\n"
        + "Refer to it only as 'your exercise' or 'Exercise 1' in all messages and signals."
    )
    st.session_state.full_history = [{"role": "system", "content": _session_prompt}]
if "in_session_step" not in st.session_state:
    st.session_state.in_session_step = "intro"
if "ex_state" not in st.session_state:
    st.session_state.ex_state = {1: "idle", 2: "idle"}
if "show_video_overlay" not in st.session_state:
    st.session_state.show_video_overlay = False
if "current_video" not in st.session_state:
    st.session_state.current_video = None

# ── Proactive opening ─────────────────────────────────────────────────────────
if not st.session_state.messages and not st.session_state.show_splash and st.session_state.phase not in ["appointment_summary", "programme_selection"]:
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
PHASES = ["onboarding", "programme_selection", "in_session", "post_checkin"]
PHASE_LABELS = ["Onboarding", "Appointment", "Exercise Session", "Check-In"]

def render_header():
    st.markdown('<div class="nav-marker"></div>', unsafe_allow_html=True)
    cols = st.columns(len(PHASES))
    
    # Mark onboarding completed if the user has transitioned to any subsequent phase
    if st.session_state.phase != "onboarding":
        st.session_state.onboarding_completed = True
    onboarding_completed = st.session_state.get("onboarding_completed", False)
    
    for i, (p_id, p_label) in enumerate(zip(PHASES, PHASE_LABELS)):
        with cols[i]:
            btn_type = "primary" if st.session_state.phase == p_id else "secondary"
            is_disabled = (p_id != "onboarding") and not onboarding_completed
            
            if st.button(p_label, key=f"nav_{p_id}", use_container_width=True, type=btn_type, disabled=is_disabled):
                st.session_state.phase = p_id
                st.session_state.show_splash = False
                st.rerun()

    st.markdown("""
    <style>
    .nav-marker { display: none; }
    
    /* Target the columns container immediately following the marker */
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div {
        position: sticky;
        top: 0;
        z-index: 9500;
        background: #FAF6F2; /* matches app background */
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }
    
    /* Header buttons overrides */
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div button {
        border-radius: 20px !important;
        white-space: nowrap !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        height: auto !important;
        min-height: unset !important;
        transition: all 0.2s ease !important;
    }
    
    /* Primary / Selected */
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div button[kind="primary"] {
        background-color: #2B5CD9 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(43, 92, 217, 0.2) !important;
    }
    
    /* Secondary / Unlocked but inactive */
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2B5CD9 !important;
        border: 1px solid rgba(43, 92, 217, 0.3) !important;
        box-shadow: none !important;
    }
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div button[kind="secondary"]:hover {
        background-color: rgba(43, 92, 217, 0.05) !important;
        border-color: #2B5CD9 !important;
    }

    /* Disabled / Locked */
    div[data-testid="stVerticalBlock"] > div:has(.nav-marker) + div button:disabled {
        background-color: #E6E4E2 !important;
        color: #A39E9A !important;
        border: 1px solid #D1CFCB !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        opacity: 0.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.divider()

# \u2500\u2500 Video widget \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
def render_video_widget(n: int):
    """Render the exercise video player for exercise n (1 or 2).
    States: idle (auto-playing) -> completing (green flash) -> complete.
    Only a single Mark Complete button is shown.
    """
    name = st.session_state.patient_data.get(f"exercise_{n}", f"Exercise {n}")
    state = st.session_state.ex_state.get(n, "idle")
    vid_path = _video_path(name)

    def _show_video():
        if vid_path.exists():
            st.video(str(vid_path), muted=True)
        else:
            st.warning(f"Video not found: {vid_path}")

    def _mark_complete():
        """Call LLM and advance state after the green flash."""
        st.session_state.ex_state[n] = "complete"
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
        # After Exercise 1 is marked complete the LLM asks the mid-session
        # check-in question and must wait for the user to reply before
        # introducing Exercise 2.  Gate the flow here so the Ex2 widget
        # cannot appear until the user has actually answered.
        if n == 1 and st.session_state.in_session_step != "ex2_ready":
            st.session_state.in_session_step = "ex1_checkin_pending"

        # After Exercise 2 is marked complete, proactively start Phase 4
        # with a silent trigger — Movy announces the check-in and asks Q1
        # without waiting for the user to type anything.
        # Defensive: if the LLM forgot the session_complete signal, force the
        # phase forward now so the trigger fires unconditionally.
        if n == 2:
            if st.session_state.phase != "post_checkin":
                st.session_state.phase = "post_checkin"
                st.session_state.in_session_step = "done"
                if "session_end_time" not in st.session_state:
                    st.session_state.session_end_time = time.time()
            typing_ph2 = st.empty()
            typing_ph2.markdown(
                '<div class="chat-row movy"><div class="typing-indicator">'
                '<span></span><span></span><span></span></div></div>',
                unsafe_allow_html=True,
            )
            _checkin_trigger = "Please start the post-session check-in now."
            _h2 = [*st.session_state.full_history,
                   {"role": "user", "content": _checkin_trigger}]
            reply2 = call_llm(_h2)
            typing_ph2.empty()
            clean2, sig2 = parse_signal(reply2)
            # Add trigger + reply to history for context continuity
            st.session_state.full_history.append({"role": "user", "content": _checkin_trigger})
            st.session_state.full_history.append({"role": "assistant", "content": clean2})
            if clean2.strip():
                st.session_state.messages.append({"role": "assistant", "content": clean2})
            process_signal(sig2)

        st.rerun()

    if state == "idle":
        # Video auto-plays via JS. Show only the Mark Complete button.
        _show_video()
        if st.button("\u2713 Mark Complete", key=f"done_{n}"):
            st.session_state.ex_state[n] = "completing"
            st.rerun()

    elif state == "completing":
        # One render cycle: show a green flash pill, then immediately mark done.
        _show_video()
        st.markdown(
            '<div style="display:flex;justify-content:center;margin:0.5rem 0;">'
            '<div style="background:#22c55e;color:#fff;padding:0.5rem 1.6rem;'
            'border-radius:8px;font-weight:600;font-size:0.95rem;'
            'animation:green-flash 0.45s ease-out;">'
            '\u2713 Marked Complete!</div></div>',
            unsafe_allow_html=True,
        )
        _mark_complete()  # sets state to "complete" and reruns

    elif state == "complete":
        pass  # Completion shown as a user chat bubble; no widget needed here


def render_appointment_summary():
    # Temporarily widen the container for the summary view
    st.markdown("""
        <style>
        .block-container { max-width: 850px !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="appointment-summary-container">', unsafe_allow_html=True)
    
    # Character Header
    try:
        with open("assets/images/movy.png", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div class="summary-header-card">
                    <img src="data:image/png;base64,{b64}" class="summary-header-img">
                    <h2 style="font-size:1.6rem; color:#1a1d27;">You finished your appointment and Dr Smith has completed the program configuration. I have created your exercise program.</h2>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown('<h2 style="text-align:center;">You finished your appointment and Dr Smith has completed the program configuration. I have created your exercise program.</h2>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    # Center the button under the two cards
    _, b_col, _ = st.columns([1, 2, 1])
    with b_col:
        if st.button("Start Session  →", use_container_width=True):
            st.session_state.phase = "in_session"
            st.session_state.in_session_step = "ex1_ready"
            st.session_state.show_video_overlay = True
            st.session_state.current_video = st.session_state.selected_videos[0]
            st.session_state.video_started = False
            st.session_state.video_completed = False
            # Pass data for the overlay
            st.session_state.overlay_data = {
                "title": "Exercise 1",
                "reps": 5, "sets": 3, "hold": 5
            }
            st.rerun()

def render_video_overlay(video_name, data):
    video_path = Path("assets/video") / video_name
    
    # Inject CSS to style the entire block-container as a premium white card
    st.markdown("""
        <style>
        .block-container {
            background-color: #FFFFFF !important;
            border-radius: 20px !important;
            padding: 1.5rem 2.5rem 1.5rem 2.5rem !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.06) !important;
            border: 1px solid rgba(0,0,0,0.04) !important;
            margin-top: 1rem !important;
            margin-bottom: 1rem !important;
        }
        .block-container hr {
            margin: 1rem 0 !important;
        }
        .block-container [data-testid="stMetric"] {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            text-align: center !important;
        }
        .block-container [data-testid="stMetricValue"] {
            color: #1a1d27 !important;
            font-size: 1.6rem !important;
        }
        .block-container [data-testid="stMetricLabel"] {
            color: #5A6480 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"<h2 style='margin-top:0; margin-bottom:1rem; text-align:center;'>{data['title']}</h2>", unsafe_allow_html=True)
        
        # Clinical Parameters (Centered block)
        _, c1, c2, c3, _ = st.columns([1, 0.8, 0.8, 0.8, 1])
        c1.metric("Reps", data['reps'])
        c2.metric("Sets", data['sets'])
        c3.metric("Hold", f"{data['hold']}s")
        
        st.divider()
        
        if not video_path.exists():
            st.error(f"Video {video_name} not found.")
            if st.button("Close"):
                st.session_state.show_video_overlay = False
                st.rerun()
            return
    
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        # Native Video Player
        st.video(video_bytes, format="video/mp4", autoplay=st.session_state.get("video_started", False), loop=True, muted=True)
        
        # Action Bar
        st.divider()
        _, col_center, _ = st.columns([1, 2, 1])
        with col_center:
            if not st.session_state.get("video_started", False):
                if st.button("Start ➔", type="primary", use_container_width=True):
                    st.session_state.video_started = True
                    st.rerun()
            else:
                if st.button("Start Check-In ➔", type="primary", use_container_width=True):
                    st.session_state.video_completed = True
                    st.session_state.show_video_overlay = False
                    
                    # User bubble trigger
                    _trigger = "I am ready for the check-in."
                    st.session_state.full_history.append({"role": "user", "content": _trigger})
                    st.session_state.messages.append({"role": "user", "content": _trigger})
                    
                    # Force the LLM to reply automatically to this trigger
                    st.session_state.force_llm_reply = True
                    
                    st.session_state.phase = "post_checkin"
                    st.session_state.in_session_step = "done"
                    st.rerun()


# ── Main rendering logic ─────────────────────────────────────────────────────
if st.session_state.get("show_video_overlay") and st.session_state.get("current_video"):
    render_video_overlay(st.session_state.current_video, st.session_state.get("overlay_data", {"title":"Exercise", "reps":0, "sets":0, "hold":0}))
    st.stop()

# ── Render sticky progress header globally except for the first splash ──────
_target = st.session_state.get("splash_target_phase", "onboarding")
_is_first_splash = st.session_state.show_splash and _target == "onboarding"

if not _is_first_splash:
    render_header()

# ── Splash screen ────────────────────────────────────────────────────────────
if st.session_state.show_splash:
    target = st.session_state.get("splash_target_phase", "onboarding")
    
    # Concluding / Introducing messages
    messages = {
        "onboarding": ("Welcome!", "Let's get to know you better."),
        "programme_selection": ("Thanks for telling me a bit about you.", 
                               f"Your appointment is confirmed for {st.session_state.patient_data.get('next_appointment', '[date]')}"),
        "in_session": ("Ready to start?", "Let's begin your physiotherapy session."),
        "post_session": ("Session complete!", "Time for a quick check-in on how you feel."),
        "pt_summary": ("All done!", "Here is the clinical summary for your physiotherapist.")
    }
    conclude, introduce = messages.get(target, ("Moving forward...", "Let's continue."))
    
    # Media logic for splash screen
    media_html = ""
    if target == "onboarding":
        import base64
        p_svg = Path("assets/images/movy_logo1.svg")
        if p_svg.exists():
            svg_b64 = base64.b64encode(p_svg.read_bytes()).decode()
            media_html = f'<img src="data:image/svg+xml;base64,{svg_b64}" style="width:280px; height:auto; display:block; margin:0 auto;" alt="Movy Logo" />'
        else:
            p_png = Path("assets/images/movy_logo1.png")
            if p_png.exists():
                png_b64 = base64.b64encode(p_png.read_bytes()).decode()
                media_html = f'<img src="data:image/png;base64,{png_b64}" style="width:280px; height:auto; display:block; margin:0 auto;" alt="Movy Logo" />'
    else:
        import base64
        if target == "programme_selection":
            try:
                with open("assets/images/movy.png", "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                    media_html = f'<img src="data:image/png;base64,{img_b64}" style="width:280px; height:auto; display:block; margin:0 auto;" alt="Movy" />'
            except:
                media_html = '<img src="https://via.placeholder.com/280?text=Movy+Idle" style="width:280px; height:auto; display:block; margin:0 auto;" />'
        else:
            video_path = "assets/video/Ilde.mp4"
            try:
                with open(video_path, "rb") as f:
                    v_b64 = base64.b64encode(f.read()).decode()
                    # Ensure rotation and scaling for the mp4 assets
                    media_html = f'<video class="splash-video" autoplay loop muted playsinline style="transform: rotate(90deg); width:280px; height:auto;"><source src="data:video/mp4;base64,{v_b64}" type="video/mp4"></video>'
            except:
                media_html = '<img src="https://via.placeholder.com/280?text=Movy+Idle" class="splash-video" />'

    # Use a background overlay and standard columns for reliable button rendering
    st.markdown('<div class="splash-bg"></div>', unsafe_allow_html=True)
    
    _, col, _ = st.columns([1, 4, 1])
    with col:
        st.markdown(f"""
        <div class="splash-v-center">
            <div class="splash-video-container" style="margin-bottom: 0;">
                {media_html}
            </div>
            <h2>{conclude}</h2>
            <p>{introduce}</p>
        </div>
        """, unsafe_allow_html=True)
        
        btn_labels = {
            "onboarding": "Start Onboarding  →",
            "programme_selection": "Appointment  →",
            "in_session": "Begin Session  →",
            "post_session": "Start Check-In  →"
        }
        lbl = btn_labels.get(target, "Continue  →")
        
        # This button is now in the natural Streamlit flow, making it 100% reliable
        if st.button(lbl, use_container_width=True, key="splash_cta"):
            st.session_state.show_splash = False
            st.session_state.messages = []
            if target == "programme_selection":
                st.session_state.phase = "appointment_summary"
            else:
                st.session_state.phase = target
            st.rerun()
    
    st.stop()

elif st.session_state.phase == "appointment_summary":
    render_appointment_summary()
else:
    pass
    # \u2500\u2500 Render chat history \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
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
            _msg_content = msg["content"]
            # Small speaker icon SVG
            _speaker_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4V5z"></path><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>'
            st.markdown(
                f'<div class="chat-row movy">{_avatar_html}'
                f'<div class="bubble movy">'
                f'<div class="bubble-text">{_msg_content}</div>'
                f'<button class="bubble-speaker-btn" onclick="window.parent.__movy_speak_bubble(this)" title="Read aloud">'
                f'{_speaker_svg}</button></div></div>',
                unsafe_allow_html=True,
            )


# ── Start Session button (shown after onboarding, before session begins) ──────
if st.session_state.phase == "programme_selection":
    st.markdown("<div style='margin-top:1.5rem;text-align:center;'>", unsafe_allow_html=True)
    if st.button("▶  Start Session", key="start_session"):
        msg = "I'm ready to start my session now."
        st.session_state.messages.append({"role": "user", "content": msg})
        st.session_state.full_history.append({"role": "user", "content": msg})
        
        # Step 1: Exercises Selection
        typing_ph = st.empty()
        typing_ph.markdown('<div class="chat-row movy"><div class="typing-indicator"><span></span><span></span><span></span></div></div>', unsafe_allow_html=True)
        reply = call_llm(st.session_state.full_history)
        typing_ph.empty()
        clean, sig = parse_signal(reply)
        st.session_state.full_history.append({"role": "assistant", "content": clean})
        st.session_state.messages.append({"role": "assistant", "content": clean})
        process_signal(sig)

        # Step 2: Proactive Intro (if LLM didn't already intro)
        if st.session_state.phase == "in_session" and st.session_state.in_session_step == "intro":
            typing_ph2 = st.empty()
            typing_ph2.markdown('<div class="chat-row movy"><div class="typing-indicator"><span></span><span></span><span></span></div></div>', unsafe_allow_html=True)
            _trigger = "Please introduce the first exercise now."
            # Call LLM with the trigger context
            _h2 = [*st.session_state.full_history, {"role": "user", "content": _trigger}]
            reply2 = call_llm(_h2)
            typing_ph2.empty()
            clean2, sig2 = parse_signal(reply2)
            
            st.session_state.full_history.append({"role": "user", "content": _trigger})
            st.session_state.full_history.append({"role": "assistant", "content": clean2})
            if clean2.strip():
                st.session_state.messages.append({"role": "assistant", "content": clean2})
            
            process_signal(sig2)
            # HARD FALLBACK: Ensure the video appears even if the signal was missing
            st.session_state.in_session_step = "ex1_ready"

        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# Show video widget when in-session
if st.session_state.phase == "in_session":
    step = st.session_state.in_session_step
    ex1_s = st.session_state.ex_state.get(1, "idle")
    ex2_s = st.session_state.ex_state.get(2, "idle")

    # Legacy widgets disabled in favor of the new premium modal overlay
    # if (step in ("ex1_ready", "ex1_checkin_pending") or ex1_s in ("playing", "complete")) and not (ex1_s == "complete" and ex2_active):
    #     render_video_widget(1)

    # if step == "ex2_ready" or ex2_s in ("playing", "paused", "complete"):
    #     render_video_widget(2)

# ── End session button in Check-In phase when complete ────────────────────────
if st.session_state.phase == "post_checkin" and "summary" in st.session_state.patient_data:
    st.markdown("<br>", unsafe_allow_html=True)
    _, end_col, _ = st.columns([1, 2, 1])
    with end_col:
        if st.button("End current session", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ── JS helpers: placeholder colour + scroll + video play/pause control ─────────
_is_splash  = "true"  if st.session_state.show_splash else "false"
_ex1_state  = st.session_state.ex_state.get(1, "idle")
_ex2_state  = st.session_state.ex_state.get(2, "idle")
components.html(f"""
<script>
(function(){{
    var IS_SPLASH  = {_is_splash};
    var EX_STATES  = ['{_ex1_state}', '{_ex2_state}'];
    var doc        = window.parent.document;
    var storage    = window.parent.sessionStorage;

    if (!doc.getElementById('movy-placeholder-style')) {{
        var s = doc.createElement('style');
        s.id = 'movy-placeholder-style';
        s.textContent = '.stChatInput textarea::placeholder {{ color: #B4BACF !important; opacity: 1 !important; }}';
        doc.head.appendChild(s);
    }}

    if (!IS_SPLASH) window.parent.scrollTo({{ top: doc.body.scrollHeight, behavior: 'smooth' }});

    function controlVideo(vid, state, key) {{
        var shouldPlay = (state === 'idle' || state === 'completing');
        if (shouldPlay) {{
            var saved = parseFloat(storage.getItem(key) || '0');
            function doPlay() {{
                if (saved > 0 && isFinite(saved)) vid.currentTime = saved;
                vid.play().catch(function(){{}});
                vid.ontimeupdate = function() {{ storage.setItem(key, vid.currentTime); }};
            }}
            if (vid.readyState >= 1) {{ doPlay(); }}
            else {{ vid.addEventListener('loadedmetadata', doPlay, {{once: true}}); }}
        }} else {{
            vid.pause();
            storage.removeItem(key);
        }}
    }}

    function applyVideoStates() {{
        var vids = doc.querySelectorAll('[data-testid="stVideo"] video');
        vids.forEach(function(v, i) {{
            if (i < EX_STATES.length) controlVideo(v, EX_STATES[i], 'movy_vid_' + i);
        }});
    }}

    var vS = window.parent.__movy_voice = window.parent.__movy_voice || {{
        recognition: null,
        ttsEnabled: storage.getItem('movy_tts_enabled') !== 'false', // Default true
        lastRead: storage.getItem('movy_last_read') || ''
    }};
    var SpeechRecognition = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
    var synth             = window.parent.speechSynthesis;

    if (IS_SPLASH) {{
        vS.ttsEnabled = false;
        storage.setItem('movy_tts_enabled', 'false');
    }}

    window.parent.__movy_initVoice = function() {{
        if (!SpeechRecognition) return;
        if (vS.recognition) try {{ vS.recognition.abort(); }} catch(e) {{}}
        
        var rec = new SpeechRecognition();
        rec.continuous = false; rec.interimResults = false; rec.lang = 'en-US';

        rec.onstart = function() {{
            var mic = doc.getElementById('movy-mic-btn');
            if (mic) mic.classList.add('active');
            var ind = doc.getElementById('movy-listening-indicator');
            if (ind) ind.style.display = 'block';
        }};

        rec.onresult = function(event) {{
            var text = event.results[0][0].transcript;
            var textarea = doc.querySelector('.stChatInput textarea');
            if (!textarea) return;
            var ns = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
            ns.call(textarea, text);
            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
            setTimeout(function() {{
                var btn = doc.querySelector('.stChatInput button[data-testid="stChatInputSubmitButton"]') || 
                          doc.querySelector('.stChatInput button');
                if (btn) btn.click();
            }}, 150);
        }};

        rec.onend = rec.onerror = function() {{
            if (vS.recognition) vS.recognition.active = false;
            var mic = doc.getElementById('movy-mic-btn');
            if (mic) mic.classList.remove('active');
            var ind = doc.getElementById('movy-listening-indicator');
            if (ind) ind.style.display = 'none';
        }};
        vS.recognition = rec;
    }};

    // GESTURE PROXY: Bypasses iframe restrictions for sound on Windows/Chrome
    if (!window.parent.__movy_gesture_bound) {{
        window.parent.document.addEventListener('click', function(e) {{
            if (window.parent.__movy_pending_text) {{
                window.parent.__movy_speak(window.parent.__movy_pending_text, true);
                window.parent.__movy_pending_text = null;
            }}
        }}, true);
        window.parent.__movy_gesture_bound = true;
    }}

    window.parent.__movy_speak = function(text, force) {{
        if ((!vS.ttsEnabled && !force) || !synth) return;
        
        var voices = synth.getVoices();
        if (voices.length === 0 && !window.parent.__movy_voice_warming) {{
            window.parent.__movy_voice_warming = true;
            synth.onvoiceschanged = function() {{ 
                window.parent.__movy_speak(text, force); 
            }};
            return;
        }}

        try {{
            synth.cancel(); 
            var ut = new window.parent.SpeechSynthesisUtterance(text);
            var pref = ['Google UK English Female', 'Google US English Female', 'Microsoft Zira', 'Samantha', 'Victoria', 'Fiona'];
            var v = null;
            for (var i = 0; i < pref.length; i++) {{
                v = voices.find(vx => vx.name.includes(pref[i]));
                if (v) break;
            }}
            if (!v) v = voices.find(vx => vx.name.toLowerCase().includes('female'));
            if (!v) v = voices[0];
            if (v) ut.voice = v;
            ut.pitch = 1.05; ut.rate = 0.95;
            if (synth.paused) synth.resume();
            synth.speak(ut);
        }} catch(e) {{}}
    }};

    window.parent.__movy_speak_bubble = function(btn) {{
        var bubble = btn.closest('.bubble.movy');
        var bubbleText = bubble ? bubble.querySelector('.bubble-text') : null;
        if (bubbleText) {{
            // Set pending text so the gesture proxy picks it up on this same click
            window.parent.__movy_pending_text = bubbleText.innerText;
        }}
    }};

    function injectVoiceUI() {{
        // Target the actual interactive area of the chat input bar
        var inputArea = doc.querySelector('[data-testid="stChatInput"] div[data-baseweb="base-input"]');
        var container = inputArea ? inputArea.parentElement : doc.querySelector('.stChatInput > div');
        if (!container) return;

        // Force horizontal layout to prevent stacking
        container.style.display = 'flex';
        container.style.flexDirection = 'row';
        container.style.alignItems = 'center';
        container.style.flexWrap = 'nowrap';

        var ctrls = doc.getElementById('movy-voice-ctrls');
        if (!ctrls) {{
            ctrls = doc.createElement('div');
            ctrls.id = 'movy-voice-ctrls';
            ctrls.className = 'voice-controls';
            ctrls.innerHTML = `
                <div id="movy-listening-indicator" class="listening-indicator">Listening...</div>
                <button id="movy-mic-btn" class="voice-btn" title="Speak Answer">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </button>
            `;
            ctrls.style.flex = '0 0 auto';
            var submitBtn = container.querySelector('button[data-testid="stChatInputSubmitButton"]') || container.querySelector('button');
            if (submitBtn) {{
                submitBtn.style.flex = '0 0 auto';
                container.insertBefore(ctrls, submitBtn);
            }} else {{
                container.appendChild(ctrls);
            }}
        }} else if (!container.contains(ctrls)) {{
            ctrls.style.flex = '0 0 auto';
            var submitBtn = container.querySelector('button[data-testid="stChatInputSubmitButton"]') || container.querySelector('button');
            if (submitBtn) {{
                submitBtn.style.flex = '0 0 auto';
                container.insertBefore(ctrls, submitBtn);
            }} else {{
                container.appendChild(ctrls);
            }}
        }}

        // CRITICAL: Always re-bind handlers because the iframe functions are replaced every rerun
        var mic = doc.getElementById('movy-mic-btn');
        var speaker = doc.getElementById('movy-speaker-btn');
        
        if (mic) {{
            mic.classList.toggle('active', vS.recognition && vS.recognition.active);
            mic.onclick = function(e) {{
                e.preventDefault(); e.stopPropagation();
                if (this.classList.contains('active')) {{
                    if (vS.recognition) vS.recognition.stop();
                }} else {{
                    window.parent.__movy_initVoice();
                    try {{ vS.recognition.start(); vS.recognition.active = true; }} catch(err) {{}}
                }}
            }};
        }}

        if (speaker) {{
            speaker.classList.toggle('speaker-on', vS.ttsEnabled);
            speaker.onclick = function(e) {{
                e.preventDefault(); e.stopPropagation();
                vS.ttsEnabled = !vS.ttsEnabled;
                storage.setItem('movy_tts_enabled', vS.ttsEnabled);
                this.classList.toggle('speaker-on', vS.ttsEnabled);
                if (vS.ttsEnabled) window.parent.__movy_speak("Voice output enabled.");
                else synth.cancel();
            }};
        }}
    }}

    window.parent.__movy_readNewMessages = function() {{
        var bubbles = doc.querySelectorAll('.bubble.movy');
        if (bubbles.length === 0) return;
        var text = bubbles[bubbles.length - 1].innerText;
        if (text !== vS.lastRead) {{
            vS.lastRead = text;
            storage.setItem('movy_last_read', text);
            window.parent.__movy_speak(text);
        }}
    }};

    applyVideoStates();
    injectVoiceUI();
    if (window.parent.__movy_obs) window.parent.__movy_obs.disconnect();
    window.parent.__movy_obs = new MutationObserver(function() {{
        applyVideoStates();
        injectVoiceUI();
        if (window.parent.__movy_readNewMessages) window.parent.__movy_readNewMessages();
    }});
    window.parent.__movy_obs.observe(doc.body, {{childList: true, subtree: true}});
    
    setInterval(injectVoiceUI, 1000);
}})();
</script>
""", height=0)

# ── Chat input (hidden during splash) ───────────────────────────────────────
if not st.session_state.get("show_splash", True):
    user_input = st.chat_input("Type your message…")
else:
    user_input = None

trigger_llm = False

if user_input and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.full_history.append({"role": "user", "content": user_input})
    st.markdown(f'<div class="chat-row user"><div class="bubble user">{user_input}</div></div>',
                unsafe_allow_html=True)
    trigger_llm = True

if st.session_state.get("force_llm_reply"):
    trigger_llm = True
    st.session_state.force_llm_reply = False

if trigger_llm:
    ph = st.empty()
    ph.markdown('<div class="chat-row movy"><div class="typing-indicator"><span></span><span></span><span></span></div></div>',
                unsafe_allow_html=True)

    reply = call_llm(st.session_state.full_history)
    ph.empty()

    clean, sig = parse_signal(reply)
    st.session_state.full_history.append({"role": "assistant", "content": clean})
    st.session_state.messages.append({"role": "assistant", "content": clean})
    process_signal(sig)

    # Defensive fallbacks: if the LLM responded but forgot to emit a signal,
    # advance the state manually so the flow never gets stuck.
    _step = st.session_state.get("in_session_step")
    if _step == "ex1_completed":
        # The LLM just generated the check-in question. Now we wait for user reply.
        st.session_state.in_session_step = "ex1_checkin_pending"
    elif _step == "ex1_checkin_pending":
        # Detect whether the LLM is asking for a pain rating (forgot the
        # checkin_pain_followup signal) rather than giving a closing reply.
        _pain_rating_keywords = [
            "rate", "scale", "out of 10", "1 to 10", "1-10", "/10",
            "how bad", "how much pain", "pain level", "score",
        ]
        _asking_for_rating = any(kw in clean.lower() for kw in _pain_rating_keywords)
        if _asking_for_rating:
            # Still waiting for the pain number — keep the button hidden.
            st.session_state.in_session_step = "ex1_pain_rating_pending"
        else:
            # LLM gave a full closing response — safe to show the button.
            st.session_state.in_session_step = "ex1_checkin_answered"
    elif _step == "ex1_pain_rating_pending":
        # LLM responded to the pain rating without emitting checkin_resolved.
        # Since it acknowledged and moved on, assume pain < 8 and show button.
        st.session_state.in_session_step = "ex1_checkin_answered"

    if clean.strip():
        ph.markdown(f'<div class="chat-row movy"><div class="bubble movy">{clean}</div></div>',
                    unsafe_allow_html=True)
    else:
        ph.empty()
    st.rerun()

# ── "Continue to Exercise 2" button ─────────────────────────────────────────
# Shown after Movy has responded to the mid-session check-in and the user is
# ready (but has not yet tapped Continue). Hidden for pain ≥8 cases because
# the LLM will not set this state when it advises a stop.
if (
    st.session_state.phase == "in_session"
    and st.session_state.get("in_session_step") == "ex1_checkin_answered"
):
    st.markdown("<div style='margin-top:1.5rem;text-align:center;'>", unsafe_allow_html=True)
    if st.button("▶  Continue to Exercise 2", key="continue_ex2"):
        _trigger = "I am ready to continue to Exercise 2."
        # Show the trigger as a user bubble
        st.session_state.messages.append({"role": "user", "content": _trigger})
        st.session_state.full_history.append({"role": "user", "content": _trigger})
        typing_ph = st.empty()
        typing_ph.markdown(
            '<div class="chat-row movy"><div class="typing-indicator">'
            '<span></span><span></span><span></span></div></div>',
            unsafe_allow_html=True,
        )
        _reply = call_llm(st.session_state.full_history)
        typing_ph.empty()
        _clean, _sig = parse_signal(_reply)
        st.session_state.full_history.append({"role": "assistant", "content": _clean})
        st.session_state.messages.append({"role": "assistant", "content": _clean})
        process_signal(_sig)
        # Defensive: if the LLM didn't emit the signal, force state forward
        if st.session_state.get("in_session_step") == "ex1_checkin_answered":
            st.session_state.in_session_step = "ex2_ready"
            
        st.session_state.show_video_overlay = True
        st.session_state.current_video = st.session_state.selected_videos[1]
        st.session_state.video_started = False
        st.session_state.video_completed = False
        st.session_state.overlay_data = {
            "title": "Exercise 2",
            "reps": 5, "sets": 3, "hold": 5
        }
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
