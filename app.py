#!/usr/bin/env python3
"""
工作负载饱和度分析系统 - Web应用主入口

这是一个基于Streamlit的Web应用,用于分析团队工作负载饱和度
支持数据上传、处理、可视化分析和历史趋势追踪

使用方法:
    streamlit run app.py

作者: Workload Analysis System
版本: 2.0.0
"""

import streamlit as st
import yaml
import os
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_sidebar

# 设置页面配置(必须在最前面)
st.set_page_config(
    page_title="工作负载饱和度分析系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用自定义样式
apply_custom_styles()

# 加载配置文件
@st.cache_resource
def load_config():
    """加载配置文件"""
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # 默认配置
        return {
            'standard_hours_per_week': 40,
            'other_tasks': {
                'enabled': True,
                'weekly_minutes_per_person': 92
            },
            'saturation_thresholds': {
                'under_saturated_max': 90,
                'normal_min': 90,
                'normal_max': 110,
                'over_saturated_min': 110
            }
        }

# 自动加载最近的分析数据
def load_latest_analysis():
    """加载最近一次的分析数据"""
    from core.storage import StorageManager
    import pandas as pd

    storage = StorageManager()
    processed_files = storage.get_processed_files(limit=1)

    if processed_files:
        latest_file = processed_files[0]
        try:
            data = storage.load_processed_data(latest_file['path'])

            # 重建 DataFrame
            result_df = pd.DataFrame(data['results'])

            return {
                'result_df': result_df,
                'date_info': data['date_info'],
                'stats': data['stats'],
                'processed_path': latest_file['path']
            }
        except Exception as e:
            st.warning(f"加载最近数据失败: {e}")
            return None
    return None

# 初始化session state
if 'config' not in st.session_state:
    st.session_state.config = load_config()

if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if 'current_analysis' not in st.session_state:
    # 尝试自动加载最近的分析数据
    st.session_state.current_analysis = load_latest_analysis()

if 'show_preview' not in st.session_state:
    st.session_state.show_preview = st.session_state.current_analysis is not None

if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = st.session_state.current_analysis is not None

# 主页面
def main():
    """主页面内容"""

    # 渲染侧边栏
    render_sidebar()

    # 主内容区域
    st.title("🎯 工作负载饱和度分析系统")
    st.markdown("### 欢迎使用工作负载分析系统!")

    # 功能介绍
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 📊 数据管理
        - 上传Excel工作负载数据
        - 历史数据记录和管理
        - 数据预览和验证
        """)

    with col2:
        st.markdown("""
        #### 📈 智能分析
        - 三周工作负载分析
        - 负载变化率追踪
        - 超负荷预警
        """)

    with col3:
        st.markdown("""
        #### 📉 趋势洞察
        - 历史趋势对比
        - 团队状态分布
        - 报告导出功能
        """)

    st.markdown("---")

    # 使用指南
    with st.expander("📖 使用指南", expanded=False):
        st.markdown("""
        ### 快速开始

        1. **上传数据** - 在"数据上传"页面上传Excel文件
        2. **预览数据** - 在"数据预览"页面检查处理后的数据
        3. **分析负载** - 在"负载分析"页面查看详细的饱和度分析
        4. **趋势对比** - 在"趋势对比"页面查看历史数据对比
        5. **配置管理** - 在"配置管理"页面调整分析参数

        ### 数据格式要求

        Excel文件必须包含以下内容:
        - **Sheet名称**: "预估工时"
        - **第一列**: 成员名称
        - **其他列**: 日期列(格式: YYYY-MM-DD),值为工时(小时)

        ### 状态说明

        - 🔴 **超负荷**: 饱和度 > 110%
        - 🟢 **正常**: 饱和度 90% - 110%
        - 🔵 **不饱和**: 饱和度 < 90%
        - ⚪ **空闲**: 饱和度 = 0%
        """)

    # 系统状态
    st.markdown("---")
    st.subheader("📊 系统状态")

    status_col1, status_col2, status_col3 = st.columns(3)

    with status_col1:
        if st.session_state.current_analysis is not None:
            st.success("✅ 数据已加载")
            # 显示加载的数据信息
            stats = st.session_state.current_analysis.get('stats', {})
            date_info = st.session_state.current_analysis.get('date_info', {})
            if stats and date_info:
                st.caption(f"成员数: {stats.get('total_members', 0)} | 基准日期: {date_info.get('base_date', 'N/A')}")
        else:
            st.info("ℹ️ 未加载数据")

    with status_col2:
        if st.session_state.current_analysis is not None:
            stats = st.session_state.current_analysis.get('stats', {})
            if stats:
                next_week = stats.get('next_week', {})
                avg_sat = next_week.get('avg_saturation', 0)
                st.metric("下周平均饱和度", f"{avg_sat}%")
        else:
            st.info("ℹ️ 未进行分析")

    with status_col3:
        data_dir = 'data/uploads'
        if os.path.exists(data_dir):
            file_count = len([f for f in os.listdir(data_dir) if f.endswith('.xlsx')])
            st.metric("历史文件", f"{file_count} 个")
        else:
            st.metric("历史文件", "0 个")

    # 如果有加载的数据，显示快捷操作按钮
    if st.session_state.current_analysis is not None:
        st.markdown("---")
        st.success("✅ 已自动加载最近一次的分析数据！")

        st.markdown("### 🚀 快捷操作")
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            st.page_link("pages/2_数据预览.py", label="📋 查看数据预览", icon="🔍", use_container_width=True)

        with col_btn2:
            st.page_link("pages/3_负载分析.py", label="📊 查看负载分析", icon="📈", use_container_width=True)

        with col_btn3:
            st.page_link("pages/4_趋势对比.py", label="📉 查看趋势对比", icon="📉", use_container_width=True)

if __name__ == "__main__":
    main()
