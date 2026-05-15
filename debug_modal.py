import streamlit as st

st.set_page_config(layout="wide")

# CSS to style and position the buttons using the "marker" sibling hack
st.markdown("""
<style>
body { background: #FAF6F2; }

/* The Modal Overlay */
.video-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(255,255,255,0.7); z-index: 500;
    display: flex; align-items: center; justify-content: center;
    backdrop-filter: blur(12px);
}
.video-modal-content {
    background: white; width: 90%; max-width: 450px; height: auto;
    border-radius: 32px; padding: 2rem; box-shadow: 0 30px 60px rgba(0,0,0,0.12);
    display: flex; flex-direction: column; position: relative; z-index: 501;
}

/* Markers are hidden */
.btn-marker { display: none; }

/* 1. Close Button Targeting */
div:has(> .marker-close) + div[data-testid="element-container"] {
    position: fixed !important;
    top: 15vh !important;
    left: 50% !important;
    transform: translateX(180px) !important;
    z-index: 2147483647 !important;
}
div:has(> .marker-close) + div[data-testid="element-container"] button {
    border-radius: 50% !important; width: 48px !important; height: 48px !important;
    padding: 0 !important; border: 1px solid #EAECEF !important;
    background: white !important; color: #000000 !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important; min-width: 48px !important;
}

/* 2. Start Button Targeting */
div:has(> .marker-start) + div[data-testid="element-container"] {
    position: fixed !important;
    top: 52% !important; left: 50% !important;
    transform: translate(-50%, -50%) !important;
    z-index: 2147483647 !important;
}
div:has(> .marker-start) + div[data-testid="element-container"] button {
    background: #2B5CD9 !important; color: #FFFFFF !important;
    border: none !important; border-radius: 32px !important;
    padding: 1rem 3.5rem !important; font-weight: 600 !important;
    font-size: 1.1rem !important; box-shadow: 0 10px 25px rgba(43, 92, 217, 0.4) !important;
    width: auto !important;
}

/* 3. Complete Button Targeting */
div:has(> .marker-complete) + div[data-testid="element-container"] {
    position: fixed !important;
    z-index: 2147483647 !important; left: 50% !important;
    bottom: 12vh !important; transform: translateX(-50%) !important;
}

.video-start-overlay {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.5); z-index: 10;
}
</style>
""", unsafe_allow_html=True)

if "started" not in st.session_state:
    st.session_state.started = False

# The "Marker + Button" pairs
# Close Button
st.markdown('<div class="btn-marker marker-close"></div>', unsafe_allow_html=True)
if st.button("X"):
    st.warning("Close clicked!")

# Start Button
if not st.session_state.started:
    st.markdown('<div class="btn-marker marker-start"></div>', unsafe_allow_html=True)
    if st.button("Start  →"):
        st.session_state.started = True
        st.rerun()

# Complete Button
st.markdown('<div class="btn-marker marker-complete"></div>', unsafe_allow_html=True)
if st.button("Mark as complete"):
    st.success("Completed clicked!")

# The Modal Structure
start_overlay = '<div class="video-start-overlay"></div>' if not st.session_state.started else ""
st.markdown(f"""
<div class="video-overlay">
    <div class="video-modal-content">
        <div style="font-size:1.5rem; font-weight:bold; margin-bottom:1rem;">Exercise 1</div>
        <div style="height: 480px; position: relative; border-radius: 24px; overflow: hidden; background: #ddd; display: flex; align-items: center; justify-content: center;">
            {start_overlay}
            <p style="z-index: 5;">[Video Player Area]</p>
        </div>
        <div style="height: 80px;"></div> <!-- Spacer for complete button -->
    </div>
</div>
""", unsafe_allow_html=True)
