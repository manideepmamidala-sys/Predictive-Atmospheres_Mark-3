import streamlit as st
from typing import Optional

PALETTE = {
    "bg": "#041122",          # Deepest Navy
    "surface": "#0A2240",     # Elevated Navy
    "accent": "#1C5B99",      # Mid-tone Blue
    "accent_2": "#4287C6",    # Bright Blue
    "accent_3": "#11365E",    # Dark Blue
    "text": "#F4F8FC",        # Ice Blue / Off-White
    "muted": "#8AA4C1",       # Muted Blue-Gray
    "border": "#0F2D53",      # Dividers/Gridlines
    "target": "#FFFFFF",      # Fused Point
    # Additional semantic colors mapped roughly to the same vibe
    "success": "#38D39F",
    "warning": "#F6C76D",
    "danger": "#FF6B8A",
}

def apply_global_theme() -> None:
    st.markdown(
        f"""
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

            h1, h2, h3, p, span, div, label, .stMarkdown, .stTab, .stSelectbox, .stTextInput {{
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

            [data-testid="stSidebar"] {{
                background: var(--surface) !important;
                border-right: 1px solid var(--border) !important;
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
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 14px;
                padding: 0.66rem 0.88rem;
                margin-bottom: 0.45rem;
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
            }}

            .hero-wrap.compact {{
                padding: 0.45rem 0.75rem;
                border-radius: 12px;
                margin-bottom: 0.32rem;
            }}

            .hero-kicker {{
                font-size: 0.7rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: var(--muted);
                margin-bottom: 0.16rem;
            }}

            .hero-title {{
                font-size: 1.38rem;
                font-weight: 700;
                color: var(--text);
                margin: 0;
            }}

            .hero-wrap.compact .hero-title {{
                font-size: 1.12rem;
                font-weight: 650;
            }}

            .hero-desc {{
                color: var(--muted);
                margin-top: 0.26rem;
                margin-bottom: 0;
                font-size: 0.92rem;
            }}

            .hero-wrap.compact .hero-desc {{
                margin-top: 0.15rem;
                font-size: 0.84rem;
            }}

            div[data-testid="metric-container"] {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.35rem 0.62rem;
            }}

            div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
                font-size: 1.35rem;
                line-height: 1.1;
                color: var(--accent-2);
            }}

            div[data-testid="metric-container"] label {{
                color: var(--muted) !important;
                letter-spacing: 0.01em;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.35rem;
                margin-bottom: 0.2rem;
            }}

            .stTabs [data-baseweb="tab"] {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 999px;
                color: var(--muted);
                padding: 0.32rem 0.78rem;
                min-height: 34px;
            }}

            .stTabs [aria-selected="true"] {{
                color: var(--text) !important;
                border-color: var(--accent) !important;
                background: var(--surface) !important;
            }}

            .stButton button {{
                border-radius: 10px;
                border: 1px solid var(--border);
                background: var(--surface);
                color: var(--text);
                min-height: 2.25rem;
                padding: 0.35rem 0.75rem;
            }}

            .stButton button:hover {{
                border-color: var(--accent);
                color: var(--text);
            }}

            .stSlider [data-baseweb="slider"] > div > div {{
                background: var(--accent);
            }}

            .stSlider [role="slider"] {{
                border: 2px solid var(--accent-2);
            }}

            .stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 10px;
                color: var(--text);
            }}

            .panel {{
                background: var(--surface);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.62rem 0.75rem;
                margin-bottom: 0.42rem;
            }}

            .panel-title {{
                color: var(--text);
                font-weight: 600;
                font-size: 0.92rem;
                margin-bottom: 0.2rem;
            }}

            .panel-kicker {{
                color: var(--muted);
                font-size: 0.73rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.14rem;
            }}

            div.stDivider {{
                margin-top: 0.4rem;
                margin-bottom: 0.4rem;
            }}

            .stPlotlyChart > div {{
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid var(--border);
                background: transparent;
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
        font={"color": PALETTE["text"], "size": 12, "family": "Google Sans Flex"},
        title_font_family="Google Sans Flex",
        xaxis_title_font_family="Google Sans Flex",
        yaxis_title_font_family="Google Sans Flex",
        hoverlabel_font_family="Cutive Mono",
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "orientation": "h",
            "y": -0.2,
        },
        margin={"l": 30, "r": 30, "t": 45, "b": 30},
    )
    fig.update_xaxes(
        gridcolor=PALETTE["border"],
        zerolinecolor=PALETTE["border"],
        linecolor=PALETTE["border"],
        showgrid=True,
        tickfont_family="Cutive Mono"
    )
    fig.update_yaxes(
        gridcolor=PALETTE["border"],
        zerolinecolor=PALETTE["border"],
        linecolor=PALETTE["border"],
        showgrid=True,
        tickfont_family="Cutive Mono"
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