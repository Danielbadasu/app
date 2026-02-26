import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Climate Assistant", layout="wide")

# ---- CONFIGURE GROQ ----
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
.topic-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
    margin-bottom: 8px;
    cursor: pointer;
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

# ---- TITLE ----
st.title("🤖 AI Climate Assistant")
st.markdown("Ask me anything about climate change, the data in this dashboard, or environmental trends.")

st.markdown("---")

# ---- SIDEBAR TOPIC FILTER ----
st.sidebar.header("🎯 Topic Filter")
st.sidebar.markdown("Filter suggested questions by topic:")

selected_topic = st.sidebar.radio(
    "Select Topic",
    options=["All Topics", "🌍 CO₂ Emissions", "🌡️ Temperature", "⚡ Renewable Energy", "🌎 Vulnerability"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("**💬 Conversation**")
st.sidebar.markdown(f"Messages: **{len(st.session_state.get('messages', []))}**")

# ---- TOPIC-BASED SUGGESTED QUESTIONS ----
questions = {
    "🌍 CO₂ Emissions": [
        ("🏭 Which country emits the most CO₂?", "Which country emits the most CO₂ and why?"),
        ("📉 Did COVID-19 reduce emissions?", "Did COVID-19 significantly reduce global CO₂ emissions?"),
        ("🛢️ Which sector emits the most?", "Which economic sector is responsible for the most CO₂ emissions globally?"),
    ],
    "🌡️ Temperature": [
        ("🌡️ Why are anomalies rising?", "Why are global temperature anomalies rising?"),
        ("❄️ What was the coldest decade?", "Which decade had the lowest average global temperature anomaly?"),
        ("🔥 When did warming accelerate?", "When did global temperature warming start to accelerate significantly?"),
    ],
    "⚡ Renewable Energy": [
        ("⚡ How fast is renewable energy growing?", "How fast is renewable energy growing globally?"),
        ("☀️ Which country leads in solar?", "Which country leads the world in solar energy production?"),
        ("🌬️ Is wind energy reliable?", "How reliable is wind energy compared to fossil fuels?"),
    ],
    "🌎 Vulnerability": [
        ("⚠️ Most vulnerable regions?", "Which regions of the world are most vulnerable to climate change?"),
        ("🌊 How does sea level affect vulnerability?", "How does sea level rise affect climate vulnerability scores?"),
        ("💰 Does wealth reduce vulnerability?", "Does a country's wealth reduce its climate vulnerability?"),
    ]
}

# build filtered question list
if selected_topic == "All Topics":
    filtered_questions = [q for qs in questions.values() for q in qs]
else:
    filtered_questions = questions.get(selected_topic, [])

# ---- SUGGESTED QUESTIONS ----
st.markdown(f"**💡 Suggested questions — {selected_topic}:**")

cols = st.columns(3)
for i, (label, full_question) in enumerate(filtered_questions):
    with cols[i % 3]:
        if st.button(label, key=f"q_{i}"):
            st.session_state.suggested = full_question

st.markdown("---")

# ---- CHAT HISTORY ----
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an expert climate data analyst and environmental scientist
                    embedded inside a Global Climate Intelligence Dashboard. You have deep knowledge of:
                    - CO₂ emissions trends by country and sector
                    - Global temperature anomalies and climate science
                    - Renewable energy transition (solar, wind, fossil fuels)
                    - Climate vulnerability and environmental policy

                    The user is currently exploring the topic: {selected_topic}.
                    Tailor your responses to be relevant to this topic where possible.
                    Be concise, insightful, and data-driven in your responses.
                    When relevant, reference what users might see in the dashboard charts.
                    You can also answer general questions outside climate if asked."""
                }
            ] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        )

    assistant_reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

# ---- CLEAR CHAT ----
if st.session_state.messages:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear conversation"):
            st.session_state.messages = []
            st.rerun()