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


def render_sidebar_chat(page_context: str):
    """
    Renders a mini AI chat panel in the sidebar.
    Call this at the bottom of any page file.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💬 Quick AI Chat")
    st.sidebar.markdown(f"*Ask anything about {page_context}*")

    # Session state keys unique per page to avoid conflicts
    chat_key = f"sidebar_messages_{page_context}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    # Display chat history in sidebar
    for msg in st.session_state[chat_key]:
        if msg["role"] == "user":
            st.sidebar.markdown(f"**You:** {msg['content']}")
        else:
            st.sidebar.markdown(f"**🌍 AI:** {msg['content']}")

    # Input
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