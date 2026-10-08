import streamlit as st
from typing import Optional

PALETTE = {
    "bg": "#131314",
    "surface": "#1E1F20",
    "accent": "#4F8BF9",
    "accent_2": "#4F8BF9",
    "accent_3": "#4F8BF9",
    "text": "#FAFAFA",
    "muted": "#A0AAB2",
    "border": "#A0AAB2",
    "target": "#FAFAFA",
    "success": "#09AB3B",
    "warning": "#FF4B4B",
    "danger": "#FF4B4B",
}

def apply_global_theme() -> None:
    st.markdown(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet">
        <style>
            /* Consider self-hosting or using system fonts */
            @import url('https://fonts.bunny.net/css2?family=Cutive+Mono&family=Google+Sans+Flex&display=swap');
            
            :root {{
                --bg: {PALETTE['bg']};
                --surface: {PALETTE['surface']};
                --border: {PALETTE['border']};
                --text: {PALETTE['text']};
                --muted: {PALETTE['muted']};
                --accent: {PALETTE['accent']};
                --accent-2: {PALETTE['accent_2']};
            }}

            h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText {{
                font-family: 'Google Sans Flex', sans-serif !important;
            }}

            .cutive-mono, .metric-value, [data-testid="stMetricValue"], table, th, td {{
                font-family: 'Cutive Mono', monospace !important;
            }}

            .stApp {{
                background-color: var(--bg) !important;
                background-image: none !important;
                color: var(--text);
            }}

            section[data-testid="stSidebar"] {{
                background-color: #1E1F20 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}

            section[data-testid="stSidebar"]::after {{
                border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
            }}

            [data-testid="stSidebar"] .block-container {{
                padding-top: 0.9rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }}

            [data-testid="stHeader"] {{
                background: transparent;
            }}

            .block-container {{
                padding-top: 0.42rem;
                padding-bottom: 1.0rem;
                max-width: 1600px;
            }}

            .hero-wrap {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0.5rem 0;
                margin-bottom: 0.75rem;
                box-shadow: none;
            }}

            .hero-wrap.compact {{
                padding: 0.35rem 0;
                margin-bottom: 0.5rem;
            }}

            .hero-kicker {{
                font-size: 0.75rem;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                color: #75b6da;
                margin-bottom: 0.25rem;
            }}

            .hero-title {{
                font-size: 2.2rem;
                font-weight: 800;
                color: var(--text);
                margin: 0;
                letter-spacing: -0.02em;
            }}

            .hero-wrap.compact .hero-title {{
                font-size: 1.75rem;
                font-weight: 700;
            }}

            .hero-desc {{
                color: var(--muted);
                margin-top: 0.5rem;
                margin-bottom: 0;
                font-size: 1.05rem;
                max-width: 800px;
                line-height: 1.5;
            }}

            .hero-wrap.compact .hero-desc {{
                margin-top: 0.25rem;
                font-size: 0.95rem;
            }}

            div[data-testid="metric-container"] {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0;
            }}

            div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
                font-size: 2.2rem;
                font-weight: 700;
                line-height: 1;
                color: var(--text);
            }}

            div[data-testid="metric-container"] label {{
                color: var(--muted) !important;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 2rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid var(--border);
            }}

            .stTabs [data-baseweb="tab"] {{
                background: transparent;
                border: none;
                border-radius: 0;
                color: var(--muted);
                padding: 0.5rem 0;
                min-height: 40px;
            }}

            .stTabs [aria-selected="true"] {{
                color: var(--accent-2) !important;
                background: transparent !important;
                border-bottom: 2px solid var(--accent-2) !important;
            }}

            .stButton button {{
                border-radius: 6px;
                border: 1px solid var(--accent);
                background: transparent;
                color: var(--text);
                min-height: 2.5rem;
                padding: 0.5rem 1.5rem;
                font-weight: 600;
                transition: all 0.2s ease;
            }}

            .stButton button:hover {{
                background: var(--accent);
                color: white;
                border-color: var(--accent);
            }}

            .stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--border);
                border-radius: 6px;
                color: var(--text);
            }}

            .panel {{
                background: transparent;
                border: none;
                border-radius: 0;
                padding: 0.75rem 0;
                margin-bottom: 1rem;
                border-bottom: 1px solid var(--border);
            }}

            .panel-title {{
                color: var(--text);
                font-weight: 700;
                font-size: 1.1rem;
                margin-bottom: 0.25rem;
                letter-spacing: -0.01em;
            }}

            .panel-kicker {{
                color: #75b6da;
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 0.25rem;
            }}

            div.stDivider {{
                margin-top: 1.5rem;
                margin-bottom: 1.5rem;
                opacity: 0.3;
            }}

            .stPlotlyChart > div {{
                border-radius: 0;
                overflow: visible;
                border: none;
                background: transparent;
            }}
            /* Force Button Background and Border */
            div.stButton > button {{
                background-color: #75b6da !important;
                border-color: #75b6da !important;
                color: #0E1117 !important; /* Dark text for contrast against the blue */
            }}

            /* Force Active Tab Text Color */
            button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {{
                color: #75b6da !important;
            }}

            /* Force Active Tab Underline / Highlight */
            div[data-baseweb="tab-highlight"] {{
                background-color: #75b6da !important;
            }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    title: str,
    description: str,
    kicker: str = "Predictive Atmospheres",
    compact: bool = False,
) -> None:
    hero_class = "hero-wrap compact" if compact else "hero-wrap"
    st.markdown(
        f"""
        <div class="{hero_class}">
            <div class="hero-kicker">{kicker}</div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-desc">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig, title: Optional[str] = None, height: int = 360):
    fig.update_layout(
        title=title,
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": PALETTE["text"], "size": 12},
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "orientation": "h",
            "y": -0.2,
        },
        margin={"l": 30, "r": 30, "t": 45, "b": 30},
    )
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='rgba(255, 255, 255, 0.2)'
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.1)', 
        zeroline=False
    )
    return fig


def panel_header(title: str, kicker: Optional[str] = None) -> None:
    kicker_html = f'<div class="panel-kicker">{kicker}</div>' if kicker else ""
    st.markdown(
        f"""
        <div class="panel">
            {kicker_html}
            <div class="panel-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
