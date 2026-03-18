import streamlit as st
from groq import Groq


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
    """Renders a mini AI chat panel in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Quick AI Chat")
    st.sidebar.markdown(f"*Ask anything about {page_context}*")

    chat_key = f"sidebar_messages_{page_context}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    for msg in st.session_state[chat_key]:
        if msg["role"] == "user":
            st.sidebar.markdown(f"**You:** {msg['content']}")
        else:
            st.sidebar.markdown(f"**🌍 AI:** {msg['content']}")

    user_input = st.sidebar.text_input(
        "Ask a question...",
        key=f"sidebar_input_{page_context}",
        label_visibility="collapsed",
        placeholder="Ask a question..."
    )

    col1, col2 = st.sidebar.columns([2, 1])
    with col1:
        send = st.button("Send ➤", key=f"sidebar_send_{page_context}", use_container_width=True)
    with col2:
        if st.button("Clear", key=f"sidebar_clear_{page_context}", use_container_width=True):
            st.session_state[chat_key] = []
            st.rerun()

    if send and user_input.strip():
        st.session_state[chat_key].append({"role": "user", "content": user_input})

        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        with st.sidebar:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""You are an expert climate data analyst embedded in a
                            Global Climate Intelligence Dashboard. The user is currently viewing
                            the {page_context} page. Give concise, insightful answers —
                            2-3 sentences max for sidebar chat. Be data-driven and direct."""
                        }
                    ] + [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state[chat_key]
                    ]
                )
        reply = response.choices[0].message.content
        st.session_state[chat_key].append({"role": "assistant", "content": reply})
        st.rerun()