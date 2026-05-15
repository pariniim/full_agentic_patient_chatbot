import streamlit as st

st.set_page_config(layout="wide")

if "started" not in st.session_state:
    st.session_state.started = False

# --- 1. Global Invisible Signal Receivers ---
# We put these in an empty container so they don't affect layout
with st.container():
    st.write("<style>.hidden-signal-btns { display: none; }</style>", unsafe_allow_html=True)
    st.write('<div class="hidden-signal-btns">', unsafe_allow_html=True)
    if st.button("SIG_CLOSE"):
        st.warning("Successfully received CLOSE signal!")
    if st.button("SIG_START"):
        st.session_state.started = True
        st.success("Successfully received START signal!")
    if st.button("SIG_COMPLETE"):
        st.success("Successfully received COMPLETE signal!")
    st.write('</div>', unsafe_allow_html=True)

# --- 2. Ultra-Resilient JS Bridge ---
st.markdown("""
<script>
function sendSignal(signalName) {
    console.log("Attempting to send signal: " + signalName);
    
    // Function to search a specific document context
    const clickButtonInContext = (doc) => {
        const buttons = Array.from(doc.querySelectorAll('button'));
        const target = buttons.find(b => b.textContent.includes(signalName));
        if (target) {
            console.log("Found target in context, clicking...");
            target.click();
            return true;
        }
        return false;
    };

    // Try current document, then parent document (if in iframe)
    if (clickButtonInContext(document)) return;
    if (window.parent && window.parent.document && clickButtonInContext(window.parent.document)) return;
    
    console.error("Failed to find signal button: " + signalName);
}
</script>
""", unsafe_allow_html=True)

# --- 3. Modal HTML with Embedded Buttons ---
start_overlay = ""
if not st.session_state.started:
    start_overlay = """
    <div style="position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:10; display:flex; align-items:center; justify-content:center;">
        <button onclick="sendSignal('SIG_START')" style="background:#2B5CD9; color:white; border:none; border-radius:32px; padding:1rem 3.5rem; font-weight:600; font-size:1.1rem; cursor:pointer; box-shadow:0 10px 25px rgba(43,92,217,0.4);">
            Start →
        </button>
    </div>
    """

st.markdown(f"""
<style>
.video-overlay {{
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(255,255,255,0.7); z-index: 500;
    display: flex; align-items: center; justify-content: center;
    backdrop-filter: blur(12px);
}}
.video-modal-content {{
    background: white; width: 90%; max-width: 450px; height: auto;
    border-radius: 32px; padding: 2rem; box-shadow: 0 30px 60px rgba(0,0,0,0.12);
    display: flex; flex-direction: column; position: relative; z-index: 501;
}}
.close-btn {{
    position: absolute; top: 20px; right: 20px;
    border-radius: 50%; width: 42px; height: 42px;
    border: 1px solid #EAECEF; background: white; color: black;
    font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05); z-index: 100;
}}
.complete-btn {{
    background: #4CAF50; color: white; border: none; border-radius: 24px;
    padding: 0.8rem 2.5rem; font-weight: bold; cursor: pointer;
    align-self: center; margin-top: 1rem;
}}
</style>

<div class="video-overlay">
    <div class="video-modal-content">
        <button class="close-btn" onclick="sendSignal('SIG_CLOSE')">X</button>
        <div style="font-size:1.5rem; font-weight:bold; margin-bottom:1rem;">Exercise 1</div>
        <div style="height:480px; position:relative; border-radius:24px; overflow:hidden; background:#ddd; display:flex; align-items:center; justify-content:center;">
            {start_overlay}
            <p>[Video Player]</p>
        </div>
        <button class="complete-btn" onclick="sendSignal('SIG_COMPLETE')">Mark as complete</button>
    </div>
</div>
""", unsafe_allow_html=True)
