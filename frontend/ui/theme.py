import streamlit as st
from typing import Optional


PALETTE = {
    "bg": "#070912",
    "surface": "#0D1120",
    "surface_alt": "#141A2E",
    "border": "#232A44",
    "text": "#EAF0FF",
    "muted": "#9FAACC",
    "accent": "#8D66FF",
    "accent_2": "#33D4FF",
    "success": "#38D39F",
    "warning": "#F6C76D",
    "danger": "#FF6B8A",
}


def apply_global_theme() -> None:
    st.markdown(
        f"""
        <style>
            :root {{
                --bg: {PALETTE['bg']};
                --surface: {PALETTE['surface']};
                --surface-alt: {PALETTE['surface_alt']};
                --border: {PALETTE['border']};
                --text: {PALETTE['text']};
                --muted: {PALETTE['muted']};
                --accent: {PALETTE['accent']};
                --accent-2: {PALETTE['accent_2']};
            }}

            .stApp {{
                background:
                    radial-gradient(1200px 620px at 4% -8%, rgba(141,102,255,0.24), transparent 56%),
                    radial-gradient(1000px 520px at 104% -6%, rgba(51,212,255,0.14), transparent 52%),
                    var(--bg);
                color: var(--text);
            }}

            [data-testid="stSidebar"] {{
                background: linear-gradient(180deg, #0B0F1A 0%, #090D18 100%);
                border-right: 1px solid var(--border);
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
                background: linear-gradient(130deg, rgba(141,102,255,0.18), rgba(14,18,34,0.94));
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
                background: linear-gradient(180deg, rgba(20,26,46,0.82), rgba(12,17,32,0.88));
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.35rem 0.62rem;
                box-shadow: inset 0 0 0 1px rgba(141,102,255,0.08);
            }}

            div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
                font-size: 1.35rem;
                line-height: 1.1;
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
                background: rgba(20,26,46,0.76);
                border: 1px solid var(--border);
                border-radius: 999px;
                color: var(--muted);
                padding: 0.32rem 0.78rem;
                min-height: 34px;
            }}

            .stTabs [aria-selected="true"] {{
                color: var(--text);
                border-color: rgba(141,102,255,0.74);
                box-shadow: 0 0 0 1px rgba(141,102,255,0.28) inset;
                background: linear-gradient(180deg, rgba(141,102,255,0.22), rgba(20,26,46,0.84));
            }}

            .stButton button {{
                border-radius: 10px;
                border: 1px solid var(--border);
                background: linear-gradient(180deg, #181F36 0%, #10172B 100%);
                color: var(--text);
                min-height: 2.25rem;
                padding: 0.35rem 0.75rem;
            }}

            .stButton button:hover {{
                border-color: rgba(141,102,255,0.8);
                color: #FFFFFF;
            }}

            .stSlider [data-baseweb="slider"] > div > div {{
                background: linear-gradient(90deg, rgba(141,102,255,0.95), rgba(51,212,255,0.9));
            }}

            .stSlider [role="slider"] {{
                border: 2px solid rgba(141,102,255,0.9);
                box-shadow: 0 0 0 4px rgba(141,102,255,0.15);
            }}

            .stRadio > div {{
                gap: 0.28rem;
            }}

            .stRadio [role="radiogroup"] label {{
                padding-top: 0.18rem;
                padding-bottom: 0.18rem;
            }}

            .stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
                background: rgba(13,17,32,0.9);
                border: 1px solid var(--border);
                border-radius: 10px;
            }}

            .panel {{
                background: linear-gradient(180deg, rgba(18,23,40,0.9), rgba(11,15,28,0.92));
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

            h2, h3 {{
                margin-top: 0.22rem;
                margin-bottom: 0.28rem;
            }}

            h1 {{
                margin-top: 0;
                margin-bottom: 0.18rem;
            }}

            .stPlotlyChart > div {{
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid rgba(35,42,68,0.72);
                background: rgba(11,15,28,0.34);
            }}

            p {{
                margin-bottom: 0.4rem;
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
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16,20,34,0.70)",
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
        gridcolor="rgba(167,177,203,0.18)",
        zerolinecolor="rgba(167,177,203,0.20)",
        linecolor="rgba(167,177,203,0.30)",
    )
    fig.update_yaxes(
        gridcolor="rgba(167,177,203,0.18)",
        zerolinecolor="rgba(167,177,203,0.20)",
        linecolor="rgba(167,177,203,0.30)",
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