#!/usr/bin/env python3
"""
统一的侧边栏管理
提供简洁的侧边栏布局和状态显示
"""

import streamlit as st


def render_sidebar():
    """渲染统一的侧边栏"""
    with st.sidebar:
        # Logo和标题 - 放在最上方
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 1rem; margin-bottom: 0;">
            <h2 style="color: white; margin: 0; font-size: 2rem;">📊</h2>
            <h3 style="color: white; margin: 0.75rem 0 0 0; font-size: 1.1rem; font-weight: 600; line-height: 1.4;">工作负载饱和度分析系统</h3>
        </div>
        """, unsafe_allow_html=True)


def render_compact_sidebar():
    """渲染紧凑版侧边栏(用于子页面)"""
    with st.sidebar:
        # Logo和标题 - 放在最上方
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0.5rem; margin-bottom: 0;">
            <h2 style="color: white; margin: 0; font-size: 1.75rem;">📊</h2>
            <p style="color: white; margin: 0.5rem 0 0 0; font-size: 0.95rem; font-weight: 600; line-height: 1.4;">工作负载饱和度分析系统</p>
        </div>
        """, unsafe_allow_html=True)
