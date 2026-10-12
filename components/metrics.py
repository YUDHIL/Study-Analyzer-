"""
components/metrics.py - Inspiring, high-aesthetic UI cards and headers.
"""

import streamlit as st
import textwrap


def render_html(html_content: str) -> None:
    """Safely render HTML without Markdown 4-space code block indentation issues."""
    st.markdown(textwrap.dedent(html_content).strip(), unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "", badge: str = "", color: str = "#38bdf8") -> None:
    """Render a premium glassmorphic metric card with glowing accent and compact typography."""
    badge_html = f'<span style="background: {color}20; color: {color}; border: 1px solid {color}40; padding: 2px 7px; border-radius: 9999px; font-size: 0.68rem; font-weight: 700; letter-spacing: 0.03em;">{badge}</span>' if badge else ''
    subtitle_html = f'<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{subtitle}</div>' if subtitle else ''

    html = f"""
<div style="background: linear-gradient(145deg, rgba(20, 29, 47, 0.75) 0%, rgba(13, 19, 33, 0.85) 100%); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); border-top: 3px solid {color}; border-radius: 12px; padding: 14px 16px; box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.4); margin-bottom: 12px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
<span style="font-size: 0.72rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;">{title}</span>
{badge_html}
</div>
<div style="font-size: 1.65rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; line-height: 1.15; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
{value}
</div>
{subtitle_html}
</div>
"""
    render_html(html)


def render_header(title: str, subtitle: str = "") -> None:
    """Render a clean, polished page header."""
    sub_html = f'<p style="color: #94a3b8; font-size: 0.95rem; margin: 0; line-height: 1.4;">{subtitle}</p>' if subtitle else ''
    html = f"""
<div style="margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
<h1 style="color: #ffffff; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0; letter-spacing: -0.02em;">{title}</h1>
{sub_html}
</div>
"""
    render_html(html)


def render_empty_state(message: str, action_text: str = "") -> None:
    """Render a modern glassmorphic empty state."""
    act_html = f'<div style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; margin-top: 4px;">{action_text}</div>' if action_text else ''
    html = f"""
<div style="background: rgba(15, 23, 42, 0.4); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 14px; padding: 32px 20px; text-align: center; margin: 16px 0;">
<div style="font-size: 1.3rem; margin-bottom: 6px;">✨</div>
<div style="color: #cbd5e1; font-size: 0.95rem; font-weight: 600; margin-bottom: 4px;">{message}</div>
{act_html}
</div>
"""
    render_html(html)
