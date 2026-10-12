"""
components/theme.py - Premium Focus & Motivation Design System for Study Analyzer.

Transforms the application into a distraction-free, deeply motivating,
modern dark productivity space with glassmorphism, ambient gradients,
and sleek developer typography.
"""

import streamlit as st
import random

MOTIVATIONAL_QUOTES = [
    ("⚡ Consistency Over Intensity", "Small daily study sessions compound into effortless exam mastery."),
    ("🎯 Deep Work Mode", "Distraction is the enemy of depth. 90 minutes of pure focus beats 4 hours of multitasking."),
    ("🧠 Neurons That Fire Together, Wire Together", "Active recall and solving problems without hints builds permanent neural pathways."),
    ("🚀 You Are Closer Than You Think", "Every completed module topic reduces exam week anxiety to zero."),
    ("💎 Craft Your Edge", "Code independently. Think systematically. Own your engineering semester."),
]


def inject_focus_theme() -> None:
    """Inject global CSS with Google Fonts, glassmorphism, and study-inducing aesthetics."""
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    
    <style>
        /* Base typography & palette */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            letter-spacing: -0.01em;
        }
        
        code, pre, .stCodeBlock {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Ambient Cosmic Background */
        .stApp {
            background: radial-gradient(circle at 15% 15%, #0f1d36 0%, #070c18 45%, #050811 100%) !important;
            color: #f1f5f9;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #090e1c 0%, #050811 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
            box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
        }

        /* Glassmorphic Cards & Containers */
        div[data-testid="stExpander"] {
            background: rgba(17, 24, 39, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3) !important;
            transition: border-color 0.25s ease, box-shadow 0.25s ease;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(56, 189, 248, 0.25) !important;
            box-shadow: 0 12px 32px -4px rgba(56, 189, 248, 0.1) !important;
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            color: #94a3b8;
            font-weight: 600;
            padding: 8px 18px;
            transition: all 0.2s ease;
            border: none !important;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(99, 102, 241, 0.2) 100%) !important;
            color: #38bdf8 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
        }

        /* High-Energy Primary Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #4f46e5 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0 8px 24px rgba(2, 132, 199, 0.55) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
        }
        .stButton>button:active {
            transform: translateY(0px) scale(0.99) !important;
        }

        /* Inputs & Form Fields */
        .stTextInput>div>div>input,
        .stSelectbox>div>div,
        .stNumberInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stDateInput>div>div>input {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: #f8fafc !important;
            transition: all 0.2s ease !important;
        }
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
        }

        /* Progress Bar */
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #06b6d4 0%, #3b82f6 50%, #10b981 100%) !important;
            border-radius: 9999px !important;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.4);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #090e1c;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    </style>
    """, unsafe_allow_html=True)


def render_focus_hero(title: str = "Deep Study Workspace", subtitle: str = "") -> None:
    """Render an aesthetic, high-motivation hero banner that primes the mind for study."""
    import textwrap
    quote_title, quote_body = random.choice(MOTIVATIONAL_QUOTES)
    
    html = f"""
<div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(99, 102, 241, 0.15) 50%, rgba(16, 185, 129, 0.08) 100%); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 24px 28px; margin-bottom: 24px; box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;">
<div style="position: absolute; right: -20px; top: -20px; width: 140px; height: 140px; background: radial-gradient(circle, rgba(56, 189, 248, 0.2) 0%, transparent 70%); border-radius: 50%; pointer-events: none;"></div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
<div>
<div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 12px; border-radius: 9999px; margin-bottom: 10px;">
<span style="display: inline-block; width: 7px; height: 7px; background-color: #34d399; border-radius: 50%; box-shadow: 0 0 8px #34d399;"></span>
<span style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.06em;">Focus Session Active</span>
</div>
<h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.03em;">{title}</h1>
<p style="color: #94a3b8; font-size: 0.95rem; margin: 0; max-width: 650px;">{subtitle}</p>
</div>
<div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); padding: 12px 18px; border-radius: 12px; max-width: 380px;">
<div style="font-size: 0.8rem; font-weight: 700; color: #fbbf24; margin-bottom: 3px;">{quote_title}</div>
<div style="font-size: 0.8rem; color: #cbd5e1; line-height: 1.35;">"{quote_body}"</div>
</div>
</div>
</div>
"""
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)
