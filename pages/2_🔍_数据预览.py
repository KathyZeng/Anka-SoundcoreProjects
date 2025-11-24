#!/usr/bin/env python3
"""
数据预览页面

显示处理后的数据,方便查看数据处理是否有误
支持数据筛选、排序和导出
"""

import streamlit as st
import pandas as pd
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.storage import StorageManager
from utils.config_loader import init_session_config
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_compact_sidebar

st.set_page_config(page_title="数据预览", page_icon="🔍", layout="wide")

# 应用自定义样式
apply_custom_styles()

# 初始化配置
init_session_config()

# 渲染紧凑版侧边栏
render_compact_sidebar()

# 渲染页面头部
render_page_header("数据预览", "查看处理后的数据,验证计算是否正确", "🔍")

# 初始化存储管理器
storage = StorageManager()

# 获取所有历史数据
processed_files = storage.get_processed_files(limit=50)

if not processed_files:
    st.warning("⚠️ 暂无数据,请先在 [数据上传](1_📊_数据上传) 页面上传文件")
    st.stop()

# 创建历史数据选择器
st.subheader("📂 选择要查看的数据")

# 加载所有历史数据的基本信息
data_options = {}
default_index = 0

for idx, file_info in enumerate(processed_files):
    try:
        data = storage.load_processed_data(file_info['path'])
        base_date = data['date_info'].get('base_date', 'Unknown')
        total_members = data['stats'].get('total_members', 0)

        # 创建选项标签
        option_label = f"{base_date} - {total_members}名成员"
        data_options[option_label] = file_info['path']

        # 如果是当前 session_state 中的数据,设为默认选项
        if st.session_state.get('current_analysis') and \
           st.session_state.current_analysis.get('processed_path') == file_info['path']:
            default_index = idx
    except Exception as e:
        st.warning(f"⚠️ 加载文件信息失败: {file_info['filename']} - {str(e)}")

if not data_options:
    st.error("❌ 无法加载任何历史数据")
    st.stop()

# 数据选择下拉框
col_select, col_info = st.columns([3, 1])

with col_select:
    selected_option = st.selectbox(
        "选择数据集",
        options=list(data_options.keys()),
        index=default_index,
        help="选择要查看的历史数据"
    )

with col_info:
    st.info(f"📊 共有 {len(data_options)} 条历史记录")

# 加载选中的数据
selected_path = data_options[selected_option]

try:
    data = storage.load_processed_data(selected_path)
    result_df = pd.DataFrame(data['results'])
    date_info = data['date_info']
    stats = data['stats']

    # 更新 session_state (可选)
    st.session_state.current_analysis = {
        'result_df': result_df,
        'date_info': date_info,
        'stats': stats,
        'processed_path': selected_path
    }
except Exception as e:
    st.error(f"❌ 加载数据失败: {str(e)}")
    st.stop()

st.markdown("---")

# 基本信息
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📅 基准日期", str(date_info['base_date']))

with col2:
    st.metric("👥 总人数", stats['total_members'])

with col3:
    st.metric("📊 数据行数", len(result_df))

with col4:
    st.metric("📈 数据列数", len(result_df.columns))

st.markdown("---")

# 数据筛选选项
st.subheader("🔧 数据筛选")

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    # 按状态筛选
    status_options = ['全部', '超负荷', '正常', '不饱和', '空闲']
    selected_status = st.selectbox("本周状态", status_options)

with col_filter2:
    # 按下周状态筛选
    next_week_status = st.selectbox("下周状态", status_options, key="next_week_status")

with col_filter3:
    # 按成员名称筛选
    member_search = st.text_input("搜索成员", placeholder="输入成员名称...")

# 应用筛选
filtered_df = result_df.copy()

if selected_status != '全部':
    filtered_df = filtered_df[filtered_df['本周状态'] == selected_status]

if next_week_status != '全部':
    filtered_df = filtered_df[filtered_df['下周状态'] == next_week_status]

if member_search:
    filtered_df = filtered_df[filtered_df['成员'].str.contains(member_search, case=False, na=False)]

st.info(f"📊 筛选后: {len(filtered_df)} 行数据")

st.markdown("---")

# 数据显示选项卡
tab1, tab2, tab3 = st.tabs(["📊 本周数据", "📈 下周数据", "📉 下下周数据"])

with tab1:
    st.subheader("本周工作负载数据")

    # 选择要显示的列
    current_week_cols = ['成员', '本周项目工时', '本周其他事务', '本周总工时', '本周饱和度(%)', '本周状态']

    # 显示数据表
    display_df_current = filtered_df[current_week_cols].copy()

    # 添加颜色标记
    def highlight_status(row):
        if row['本周状态'] == '超负荷':
            return ['background-color: #ffebee'] * len(row)
        elif row['本周状态'] == '正常':
            return ['background-color: #e8f5e9'] * len(row)
        elif row['本周状态'] == '不饱和':
            return ['background-color: #e3f2fd'] * len(row)
        else:
            return ['background-color: #f5f5f5'] * len(row)

    st.dataframe(
        display_df_current.style.apply(highlight_status, axis=1),
        use_container_width=True,
        height=500
    )

    # 本周统计
    st.markdown("### 📊 本周统计")
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)

    with col_stat1:
        st.metric("平均饱和度", f"{stats['current_week']['avg_saturation']}%")

    with col_stat2:
        st.metric("🔴 超负荷", f"{stats['current_week']['overloaded']} 人")
        if stats['current_week']['overloaded'] > 0:
            with st.expander("查看详情"):
                overloaded_current = filtered_df[filtered_df['本周状态'] == '超负荷'][['成员', '本周总工时', '本周饱和度(%)']]
                st.dataframe(overloaded_current, use_container_width=True, hide_index=True)

    with col_stat3:
        st.metric("🟢 正常", f"{stats['current_week']['normal']} 人")
        if stats['current_week']['normal'] > 0:
            with st.expander("查看详情"):
                normal_current = filtered_df[filtered_df['本周状态'] == '正常'][['成员', '本周总工时', '本周饱和度(%)']]
                st.dataframe(normal_current, use_container_width=True, hide_index=True)

    with col_stat4:
        st.metric("🔵 不饱和", f"{stats['current_week']['under_saturated']} 人")
        if stats['current_week']['under_saturated'] > 0:
            with st.expander("查看详情"):
                under_current = filtered_df[filtered_df['本周状态'] == '不饱和'][['成员', '本周总工时', '本周饱和度(%)']]
                st.dataframe(under_current, use_container_width=True, hide_index=True)

    with col_stat5:
        st.metric("⚪ 空闲", f"{stats['current_week']['idle']} 人")
        if stats['current_week']['idle'] > 0:
            with st.expander("查看详情"):
                idle_current = filtered_df[filtered_df['本周状态'] == '空闲'][['成员', '本周总工时', '本周饱和度(%)']]
                st.dataframe(idle_current, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("下周工作负载数据(含变化率)")

    # 选择要显示的列
    next_week_cols = ['成员', '下周项目工时', '下周其他事务', '下周总工时', '下周饱和度(%)', '下周状态', '下周变化', '下周变化率(%)']

    # 显示数据表
    display_df_next = filtered_df[next_week_cols].copy()

    # 添加颜色标记和变化方向
    def highlight_next_week(row):
        colors = []
        for i, col in enumerate(display_df_next.columns):
            if row['下周状态'] == '超负荷':
                color = 'background-color: #ffebee'
            elif row['下周状态'] == '正常':
                color = 'background-color: #e8f5e9'
            elif row['下周状态'] == '不饱和':
                color = 'background-color: #e3f2fd'
            else:
                color = 'background-color: #f5f5f5'

            # 变化列添加额外标记
            if col == '下周变化' or col == '下周变化率(%)':
                if row['下周变化'] > 10:
                    color += '; font-weight: bold; color: #d32f2f'  # 红色加粗 - 大幅增加
                elif row['下周变化'] < -10:
                    color += '; font-weight: bold; color: #1976d2'  # 蓝色加粗 - 大幅减少

            colors.append(color)

        return colors

    st.dataframe(
        display_df_next.style.apply(highlight_next_week, axis=1),
        use_container_width=True,
        height=500
    )

    # 下周统计
    st.markdown("### 📊 下周统计")
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)

    with col_stat1:
        st.metric("平均饱和度", f"{stats['next_week']['avg_saturation']}%")

    with col_stat2:
        st.metric("🔴 超负荷", f"{stats['next_week']['overloaded']} 人")
        if stats['next_week']['overloaded'] > 0:
            with st.expander("查看详情"):
                overloaded_next = filtered_df[filtered_df['下周状态'] == '超负荷'][['成员', '下周总工时', '下周饱和度(%)', '下周变化']]
                st.dataframe(overloaded_next, use_container_width=True, hide_index=True)

    with col_stat3:
        st.metric("🟢 正常", f"{stats['next_week']['normal']} 人")
        if stats['next_week']['normal'] > 0:
            with st.expander("查看详情"):
                normal_next = filtered_df[filtered_df['下周状态'] == '正常'][['成员', '下周总工时', '下周饱和度(%)', '下周变化']]
                st.dataframe(normal_next, use_container_width=True, hide_index=True)

    with col_stat4:
        st.metric("🔵 不饱和", f"{stats['next_week']['under_saturated']} 人")
        if stats['next_week']['under_saturated'] > 0:
            with st.expander("查看详情"):
                under_next = filtered_df[filtered_df['下周状态'] == '不饱和'][['成员', '下周总工时', '下周饱和度(%)', '下周变化']]
                st.dataframe(under_next, use_container_width=True, hide_index=True)

    with col_stat5:
        st.metric("⚪ 空闲", f"{stats['next_week']['idle']} 人")
        if stats['next_week']['idle'] > 0:
            with st.expander("查看详情"):
                idle_next = filtered_df[filtered_df['下周状态'] == '空闲'][['成员', '下周总工时', '下周饱和度(%)', '下周变化']]
                st.dataframe(idle_next, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("下下周工作负载数据(含变化率)")

    # 选择要显示的列
    next_next_week_cols = ['成员', '下下周项目工时', '下下周其他事务', '下下周总工时', '下下周饱和度(%)', '下下周状态', '下下周变化', '下下周变化率(%)']

    # 显示数据表
    display_df_next_next = filtered_df[next_next_week_cols].copy()

    # 添加颜色标记和变化方向
    def highlight_next_next_week(row):
        colors = []
        for i, col in enumerate(display_df_next_next.columns):
            if row['下下周状态'] == '超负荷':
                color = 'background-color: #ffebee'
            elif row['下下周状态'] == '正常':
                color = 'background-color: #e8f5e9'
            elif row['下下周状态'] == '不饱和':
                color = 'background-color: #e3f2fd'
            else:
                color = 'background-color: #f5f5f5'

            # 变化列添加额外标记
            if col == '下下周变化' or col == '下下周变化率(%)':
                if row['下下周变化'] > 10:
                    color += '; font-weight: bold; color: #d32f2f'  # 红色加粗 - 大幅增加
                elif row['下下周变化'] < -10:
                    color += '; font-weight: bold; color: #1976d2'  # 蓝色加粗 - 大幅减少

            colors.append(color)

        return colors

    st.dataframe(
        display_df_next_next.style.apply(highlight_next_next_week, axis=1),
        use_container_width=True,
        height=500
    )

    # 下下周统计
    st.markdown("### 📊 下下周统计")
    col_stat1, col_stat2, col_stat3, col_stat4, col_stat5 = st.columns(5)

    with col_stat1:
        st.metric("平均饱和度", f"{stats['next_next_week']['avg_saturation']}%")

    with col_stat2:
        st.metric("🔴 超负荷", f"{stats['next_next_week']['overloaded']} 人")
        if stats['next_next_week']['overloaded'] > 0:
            with st.expander("查看详情"):
                overloaded_next_next = filtered_df[filtered_df['下下周状态'] == '超负荷'][['成员', '下下周总工时', '下下周饱和度(%)', '下下周变化']]
                st.dataframe(overloaded_next_next, use_container_width=True, hide_index=True)

    with col_stat3:
        st.metric("🟢 正常", f"{stats['next_next_week']['normal']} 人")
        if stats['next_next_week']['normal'] > 0:
            with st.expander("查看详情"):
                normal_next_next = filtered_df[filtered_df['下下周状态'] == '正常'][['成员', '下下周总工时', '下下周饱和度(%)', '下下周变化']]
                st.dataframe(normal_next_next, use_container_width=True, hide_index=True)

    with col_stat4:
        st.metric("🔵 不饱和", f"{stats['next_next_week']['under_saturated']} 人")
        if stats['next_next_week']['under_saturated'] > 0:
            with st.expander("查看详情"):
                under_next_next = filtered_df[filtered_df['下下周状态'] == '不饱和'][['成员', '下下周总工时', '下下周饱和度(%)', '下下周变化']]
                st.dataframe(under_next_next, use_container_width=True, hide_index=True)

    with col_stat5:
        st.metric("⚪ 空闲", f"{stats['next_next_week']['idle']} 人")
        if stats['next_next_week']['idle'] > 0:
            with st.expander("查看详情"):
                idle_next_next = filtered_df[filtered_df['下下周状态'] == '空闲'][['成员', '下下周总工时', '下下周饱和度(%)', '下下周变化']]
                st.dataframe(idle_next_next, use_container_width=True, hide_index=True)

st.markdown("---")

# 数据导出
st.subheader("📥 数据导出")

col_export1, col_export2 = st.columns(2)

with col_export1:
    # 导出当前筛选的数据
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📄 导出CSV (筛选后的数据)",
        csv,
        f"workload_filtered_{date_info['base_date']}.csv",
        "text/csv",
        key='download-csv-filtered',
        use_container_width=True
    )

with col_export2:
    # 导出完整数据
    csv_full = result_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📄 导出CSV (完整数据)",
        csv_full,
        f"workload_full_{date_info['base_date']}.csv",
        "text/csv",
        key='download-csv-full',
        use_container_width=True
    )

# 数据验证提示
st.markdown("---")
st.subheader("✅ 数据验证检查项")

check_col1, check_col2 = st.columns(2)

with check_col1:
    st.markdown("""
    **基础验证:**
    - ✅ 成员数量是否正确
    - ✅ 工时数据是否合理(无异常值)
    - ✅ 饱和度计算是否准确
    - ✅ 状态分类是否正确
    """)

with check_col2:
    st.markdown("""
    **变化率验证:**
    - ✅ 下周变化计算是否正确
    - ✅ 变化率百分比是否合理
    - ✅ 大幅变化(±10h以上)是否符合预期
    - ✅ 趋势变化是否符合实际情况
    """)

# 异常数据提示
st.markdown("---")
st.subheader("⚠️ 异常数据提醒")

st.info("""
💡 **异常判断标准:**
- 🚨 **极度超负荷**: 下周饱和度 > 150% (工作量超过标准工时的1.5倍)
- ⚠️ **工时大幅增加**: 下周工时比本周增加 > 20小时 (工作量突然大幅增长)
""")

# 检查超负荷成员
overloaded_members = result_df[result_df['下周饱和度(%)'] > 150]
if len(overloaded_members) > 0:
    st.error(f"🚨 发现 {len(overloaded_members)} 名成员下周饱和度超过150%,请关注:")
    st.dataframe(overloaded_members[['成员', '下周总工时', '下周饱和度(%)']], use_container_width=True)
else:
    st.success("✅ 未发现极度超负荷成员")

# 检查大幅增加的成员
large_increase = result_df[result_df['下周变化'] > 20]
if len(large_increase) > 0:
    st.warning(f"⚠️ 发现 {len(large_increase)} 名成员下周工时增加超过20小时:")
    st.dataframe(large_increase[['成员', '本周总工时', '下周总工时', '下周变化']], use_container_width=True)
else:
    st.success("✅ 未发现工时大幅增加的成员")

st.markdown("---")
st.caption("💡 提示: 如果发现数据异常,请返回 [数据上传](1_📊_数据上传) 页面重新上传正确的数据")
