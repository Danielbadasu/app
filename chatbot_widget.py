import streamlit as st

def render_ai_banner(page_context: str):
    """
    Renders a glowing CTA banner that redirects to the AI Assistant page.
    page_context: short string describing the current page e.g. 'CO₂ Emissions'
    """

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
        box-shadow: 0 0 30px rgba(168, 85, 247, 0.15);
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
        color: #ffffff;
        letter-spacing: 0.3px;
    }}
    .ai-banner-sub {{
        font-size: 12px;
        color: rgba(255,255,255,0.5);
    }}
    .ai-banner-btn {{
        background: transparent;
        color: #a855f7;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none;
        white-space: nowrap;
        letter-spacing: 0.3px;
        border: 2px solid #a855f7;
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .ai-banner-btn:hover {{
        background: rgba(168, 85, 247, 0.15);
        color: #ffffff;
        text-decoration: none;
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