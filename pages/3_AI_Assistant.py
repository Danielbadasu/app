import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AI Climate Assistant", layout="wide")

# ---- CONFIGURE GEMINI ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction="""You are an expert climate data analyst and environmental scientist 
    embedded inside a Global Climate Intelligence Dashboard. You have deep knowledge of:
    - CO₂ emissions trends by country and sector
    - Global temperature anomalies and climate science
    - Renewable energy transition (solar, wind, fossil fuels)
    - Climate vulnerability and environmental policy
    
    Be concise, insightful, and data-driven in your responses. 
    When relevant, reference what users might see in the dashboard charts.
    You can also answer general questions outside climate if asked."""
)

# ---- CUSTOM CSS ----
st.markdown("""
<style>
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-bottom: 20px;
}
.chat-bubble {
    padding: 16px 20px;
    border-radius: 16px;
    max-width: 80%;
    line-height: 1.6;
    font-size: 15px;
}
.user-bubble {
    background: linear-gradient(135deg, #6a11cb, #a855f7);
    color: white;
    align-self: flex-end;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}
.assistant-bubble {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: rgba(255,255,255,0.9);
    border: 1px solid rgba(255,255,255,0.08);
    border-bottom-left-radius: 4px;
}
.assistant-name {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38ef7d;
    margin-bottom: 8px;
    font-weight: 700;
}
.user-name {
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
    margin-bottom: 8px;
    font-weight: 700;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("🤖 AI Climate Assistant")
st.markdown("Ask me anything about climate change, the data in this dashboard, or environmental trends.")

st.markdown("---")

# ---- SUGGESTED QUESTIONS ----
st.markdown("**💡 Try asking:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🌡️ Why are temperature anomalies rising?"):
        st.session_state.suggested = "Why are global temperature anomalies rising?"
with col2:
    if st.button("🏭 Which country emits the most CO₂?"):
        st.session_state.suggested = "Which country emits the most CO₂ and why?"
with col3:
    if st.button("⚡ How fast is renewable energy growing?"):
        st.session_state.suggested = "How fast is renewable energy growing globally?"

st.markdown("---")

# ---- CHAT HISTORY ----
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# ---- DISPLAY CHAT ----
if st.session_state.messages:
    chat_html = '<div class="chat-container">'
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'''
            <div style="text-align:right">
                <div class="user-name">You</div>
                <div class="chat-bubble user-bubble">{msg["content"]}</div>
            </div>'''
        else:
            chat_html += f'''
            <div>
                <div class="assistant-name">🌍 Climate AI</div>
                <div class="chat-bubble assistant-bubble">{msg["content"]}</div>
            </div>'''
    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

# ---- CHAT INPUT ----
user_input = st.chat_input("Ask a climate question...")

# handle suggested question buttons
if "suggested" in st.session_state and st.session_state.suggested:
    user_input = st.session_state.suggested
    st.session_state.suggested = None

# ---- SEND MESSAGE ----
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        response = st.session_state.chat_session.send_message(user_input)
        assistant_reply = response.text

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

# ---- CLEAR CHAT ----
if st.session_state.messages:
    if st.button("🗑️ Clear conversation"):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()