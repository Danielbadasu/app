import streamlit as st
from groq import Groq

CLIMATE_CONTEXT = """
You are an expert climate data analyst embedded inside the Global Climate Intelligence Dashboard.
You have deep expertise in:

- CO₂ emissions trends by country and sector
- Global temperature anomalies and climate science
- Renewable energy transition (solar, wind, fossil fuels)
- Climate vulnerability and environmental policy
- Climate scenario projections and the Paris Agreement

Key facts you know:
- Global CO₂ emissions reached ~37 billion tonnes in 2022
- China is the largest emitter (~31% of global emissions)
- The Paris Agreement targets limiting warming to 1.5°C above pre-industrial levels
- Renewable energy now accounts for ~30% of global electricity generation
- The most climate-vulnerable countries are often the lowest emitters

Be concise, data-driven, and always relate answers back to the dashboard data where relevant.
"""

GLOBAL_CSS = """
<style>
div[data-testid="stSidebarContent"] textarea:focus::placeholder { color: transparent !important; }
div[data-testid="stSidebarContent"] textarea::placeholder {
    color: rgba(255,255,255,0.25) !important; font-style: italic;
}
div[data-testid="stSidebarContent"] textarea { min-height: 80px !important; resize: vertical !important; }
</style>
"""


def get_groq_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None


def render_ai_banner(page_context: str):
    """Renders a glowing CTA banner on each page."""
    st.markdown(f"""
    <style>
    .ai-banner {{
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-left: 4px solid #a855f7;
        border-radius: 14px;
        padding: 16px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 28px;
        animation: glowpulse 3s ease-in-out infinite;
    }}
    @keyframes glowpulse {{
        0%   {{ box-shadow: 0 0 20px rgba(168, 85, 247, 0.15); }}
        50%  {{ box-shadow: 0 0 40px rgba(168, 85, 247, 0.35); }}
        100% {{ box-shadow: 0 0 20px rgba(168, 85, 247, 0.15); }}
    }}
    .ai-banner-text {{
        display: flex;
        flex-direction: column;
        gap: 3px;
    }}
    .ai-banner-title {{
        font-size: 14px;
        font-weight: 700;
        color: #ffffff !important;
        letter-spacing: 0.3px;
    }}
    .ai-banner-sub {{
        font-size: 12px;
        color: rgba(255,255,255,0.7) !important;
    }}
    .ai-banner-btn {{
        background: rgba(255,255,255,0.1);
        color: #ffffff !important;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none !important;
        white-space: nowrap;
        letter-spacing: 0.3px;
        border: 2px solid #ffffff;
        box-shadow: 0 0 15px rgba(255,255,255,0.15);
        cursor: pointer;
    }}
    </style>
    <div class="ai-banner">
        <div class="ai-banner-text">
            <div class="ai-banner-title">Want deeper insights on {page_context}?</div>
            <div class="ai-banner-sub">Ask our Climate AI Assistant — it knows this data inside out.</div>
        </div>
        <a class="ai-banner-btn" href="/AI_Assistant" target="_self">💬 Ask AI Assistant →</a>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer(page_context: str = ""):
    """Renders a data disclaimer footer on every page."""
    extra = ""
    if "Simulator" in page_context or "Projection" in page_context:
        extra = "Scenario projections are mathematical estimates based on historical trends and are <strong>not official forecasts</strong>. They are intended for educational and exploratory purposes only. "

    st.markdown("---")
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-left: 4px solid rgba(168, 85, 247, 0.5);
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 10px;
    ">
        <p style="font-size:12px; color:rgba(255,255,255,0.5); margin:0 0 6px 0; font-weight:700; letter-spacing:1px; text-transform:uppercase;">
            📋 Data Sources & Disclaimer
        </p>
        <p style="font-size:12px; color:rgba(255,255,255,0.55); margin:0; line-height:1.7;">
            Data sourced from <a href="https://ourworldindata.org" target="_blank" style="color:#a855f7;">Our World in Data (OWID)</a>,
            the <a href="https://www.metoffice.gov.uk/hadobs/hadcrut5/" target="_blank" style="color:#a855f7;">Hadley Centre (HadCRUT)</a>,
            and <a href="https://berkeleyearth.org" target="_blank" style="color:#a855f7;">Berkeley Earth</a>,
            made available under open licences for public use. {extra}
            This dashboard is intended for <strong>informational and educational purposes only</strong>
            and does not constitute professional, legal, or commercial advice.
            Users are encouraged to verify data independently before making decisions.
            The developer assumes no liability for the use or interpretation of this information.
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar_chat(page_context: str):
    """Renders a collapsible AI chat panel in the sidebar."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Quick AI Chat")
    st.sidebar.markdown(f"*Ask anything about {page_context}*")

    chat_key = f"sidebar_messages_{page_context}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    # ---- DISPLAY EXCHANGES AS COLLAPSIBLE ITEMS ----
    if st.session_state[chat_key]:
        msgs = st.session_state[chat_key]
        exchanges = []
        i = 0
        while i < len(msgs):
            user_msg = msgs[i]['content'] if msgs[i]['role'] == 'user' else None
            ai_msg = (
                msgs[i + 1]['content']
                if (i + 1 < len(msgs) and msgs[i + 1]['role'] == 'assistant')
                else None
            )
            if user_msg:
                exchanges.append((user_msg, ai_msg))
            i += 2

        for idx, (user_msg, ai_msg) in enumerate(exchanges):
            label = f"🗨️ {user_msg[:35]}{'...' if len(user_msg) > 35 else ''}"
            with st.sidebar.expander(label, expanded=(idx == len(exchanges) - 1)):
                st.markdown(f"**You:** {user_msg}")
                if ai_msg:
                    st.markdown(f"**🌍 Climate AI:** {ai_msg}")

    # ---- INPUT FORM WITH BUTTONS INSIDE ----
    with st.sidebar.form(key=f"chat_form_{page_context}", clear_on_submit=True):
        st.markdown(
            "<p style='font-size:11px;color:rgba(255,255,255,0.35);margin:0 0 4px 0;'>"
            "Ctrl+Enter to send</p>",
            unsafe_allow_html=True
        )
        user_input = st.text_area(
            "message",
            label_visibility="collapsed",
            placeholder="Type your question here...",
            height=100,
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            send = st.form_submit_button("Send ➤", use_container_width=True)
        with col2:
            clear = st.form_submit_button("Clear", use_container_width=True)

    if clear:
        st.session_state[chat_key] = []
        st.rerun()

    if send and user_input.strip():
        st.session_state[chat_key].append({"role": "user", "content": user_input})
        client = get_groq_client()
        with st.sidebar:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                CLIMATE_CONTEXT
                                + f"\nThe user is currently viewing the {page_context} page. "
                                "Give concise answers — 2-3 sentences max for sidebar chat."
                            )
                        }
                    ] + [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state[chat_key]
                    ]
                )
        reply = response.choices[0].message.content
        st.session_state[chat_key].append({"role": "assistant", "content": reply})
        st.rerun()