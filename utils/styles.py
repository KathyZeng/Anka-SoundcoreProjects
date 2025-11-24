#!/usr/bin/env python3
"""
统一的UI样式管理
提供自定义CSS样式和主题配置
"""

import streamlit as st


def apply_custom_styles():
    """应用自定义CSS样式"""
    st.markdown("""
    <style>
    /* ==================== 全局样式 ==================== */

    /* 主容器样式 */
    .main {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
    }

    /* ==================== 标题样式 ==================== */

    /* 主标题 h1 */
    h1 {
        color: #667eea !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(102, 126, 234, 0.1);
        letter-spacing: -0.5px;
    }

    /* 二级标题 h2 */
    h2 {
        color: #4c51bf !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }

    /* 三级标题 h3 */
    h3 {
        color: #5a67d8 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.75rem !important;
    }

    /* 四级标题 h4 */
    h4 {
        color: #667eea !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    /* ==================== 卡片和容器样式 ==================== */

    /* 信息卡片 */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid #667eea !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
        background: white !important;
        padding: 1rem 1.5rem !important;
    }

    /* 成功提示 */
    .stAlert[data-baseweb="notification"] [data-testid="stNotificationContentSuccess"] {
        border-left: 4px solid #10b981 !important;
    }

    /* 警告提示 */
    .stAlert[data-baseweb="notification"] [data-testid="stNotificationContentWarning"] {
        border-left: 4px solid #f59e0b !important;
    }

    /* 错误提示 */
    .stAlert[data-baseweb="notification"] [data-testid="stNotificationContentError"] {
        border-left: 4px solid #ef4444 !important;
    }

    /* Expander样式 */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1rem !important;
    }

    .streamlit-expanderContent {
        background: white !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 0 0 8px 8px !important;
        padding: 1rem !important;
    }

    /* ==================== 按钮样式 ==================== */

    /* 主按钮 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4) !important;
    }

    /* 次要按钮 */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #667eea !important;
        color: white !important;
        transform: translateY(-2px) !important;
    }

    /* 下载按钮 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }

    /* ==================== 输入框样式 ==================== */

    /* 文本输入框 */
    .stTextInput > div > div > input {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* 数字输入框 */
    .stNumberInput > div > div > input {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }

    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* 文本区域 */
    .stTextArea > div > div > textarea {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* 下拉框 */
    .stSelectbox > div > div {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    /* 多选框 */
    .stMultiSelect > div > div {
        border: 2px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    /* ==================== 指标卡片样式 ==================== */

    /* Metric卡片 */
    [data-testid="stMetric"] {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #e5e7eb !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    }

    [data-testid="stMetricLabel"] {
        color: #6b7280 !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    [data-testid="stMetricValue"] {
        color: #667eea !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    /* ==================== 侧边栏样式 ==================== */

    /* 侧边栏背景 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
    }

    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent !important;
    }

    /* 使用 flexbox 重新排列侧边栏元素顺序 */
    [data-testid="stSidebar"] > div:first-child {
        display: flex !important;
        flex-direction: column !important;
    }

    /* 导航区域放在后面 */
    [data-testid="stSidebarNav"] {
        order: 2 !important;
    }

    /* 自定义内容放在前面 */
    [data-testid="stSidebar"] > div:first-child > div:not([data-testid="stSidebarNav"]) {
        order: 1 !important;
    }

    /* 侧边栏文字 */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: white !important;
    }

    /* 侧边栏导航链接卡片样式 */
    [data-testid="stSidebar"] a {
        color: white !important;
        text-decoration: none !important;
        padding: 0.875rem 1rem !important;
        border-radius: 10px !important;
        display: block !important;
        margin: 0.5rem 0 !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.3px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    [data-testid="stSidebar"] a:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateX(4px) translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
    }

    /* 侧边栏导航激活状态 */
    [data-testid="stSidebar"] a[aria-current="page"] {
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }

    /* 侧边栏导航图标样式 */
    [data-testid="stSidebar"] a > span {
        font-size: 1.1rem !important;
        margin-right: 0.5rem !important;
    }

    /* 隐藏第一个导航链接(app主页) - 多种选择器确保生效 */
    [data-testid="stSidebar"] nav ul li:first-child {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 隐藏包含"app"文本的第一个导航项 */
    [data-testid="stSidebar"] a[href="/"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* 隐藏导航中第一个链接 */
    [data-testid="stSidebarNav"] ul li:first-child,
    [data-testid="stSidebarNav"] li:first-child,
    section[data-testid="stSidebar"] nav ul li:first-child {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
    }

    /* 通过内容匹配隐藏 app 链接 */
    [data-testid="stSidebar"] a[href="/"]:first-of-type {
        display: none !important;
    }

    /* 统一侧边栏所有文字颜色 */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    /* 统一侧边栏卡片样式 */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }

    /* 侧边栏信息框统一样式 */
    [data-testid="stSidebar"] .stAlert,
    [data-testid="stSidebar"] [data-baseweb="notification"] {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 10px !important;
        padding: 0.875rem !important;
        margin: 0.5rem 0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        border-left: 4px solid rgba(255, 255, 255, 0.5) !important;
    }

    [data-testid="stSidebar"] .stAlert *,
    [data-testid="stSidebar"] [data-baseweb="notification"] * {
        color: white !important;
    }

    /* 侧边栏标题统一样式 */
    [data-testid="stSidebar"] h3 {
        color: white !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin: 1rem 0 0.5rem 0 !important;
        padding-bottom: 0.5rem !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* ==================== 表格样式 ==================== */

    /* DataFrame表格 */
    .dataframe {
        border: none !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }

    .dataframe thead tr {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    .dataframe thead th {
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border: none !important;
    }

    .dataframe tbody tr:nth-child(even) {
        background: #f9fafb !important;
    }

    .dataframe tbody tr:hover {
        background: #f3f4f6 !important;
        transition: all 0.2s ease !important;
    }

    .dataframe tbody td {
        padding: 0.75rem 1rem !important;
        border: none !important;
    }

    /* ==================== 文件上传样式 ==================== */

    [data-testid="stFileUploader"] {
        background: white !important;
        border: 2px dashed #667eea !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        text-align: center !important;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #764ba2 !important;
        background: #f8f9fa !important;
    }

    /* ==================== 分隔线样式 ==================== */

    hr {
        margin: 2rem 0 !important;
        border: none !important;
        border-top: 2px solid #e5e7eb !important;
        opacity: 0.5 !important;
    }

    /* ==================== 图表容器样式 ==================== */

    .js-plotly-plot {
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        background: white !important;
        padding: 1rem !important;
    }

    /* ==================== 滚动条样式 ==================== */

    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 4px !important;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 4px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #5a67d8 0%, #6b46a0 100%) !important;
    }

    /* ==================== 动画效果 ==================== */

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .main > div {
        animation: fadeIn 0.5s ease-out;
    }

    /* ==================== 响应式设计 ==================== */

    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }

        h2 {
            font-size: 1.5rem !important;
        }

        .main {
            padding: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_page_header(title, subtitle=None, icon=None):
    """渲染统一的页面头部

    Args:
        title: 页面标题
        subtitle: 页面副标题（可选,已废弃不显示）
        icon: 页面图标（可选）
    """
    if icon:
        st.markdown(f"# {icon} {title}")
    else:
        st.markdown(f"# {title}")


def render_section_header(title, icon=None):
    """渲染统一的章节头部

    Args:
        title: 章节标题
        icon: 章节图标（可选）
    """
    if icon:
        st.markdown(f"## {icon} {title}")
    else:
        st.markdown(f"## {title}")
