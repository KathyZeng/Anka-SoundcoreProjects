#!/usr/bin/env python3
"""
趋势对比页面

显示历史数据趋势对比,帮助了解团队负载变化规律
支持多期数据选择和对比分析
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import plotly.graph_objects as go

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.storage import StorageManager
from core.visualizer import WorkloadVisualizer
from utils.config_loader import init_session_config
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_compact_sidebar

st.set_page_config(page_title="趋势对比", page_icon="📉", layout="wide")

# 应用自定义样式
apply_custom_styles()

# 初始化配置
init_session_config()

# 渲染紧凑版侧边栏
render_compact_sidebar()

# 渲染页面头部
render_page_header("趋势对比", "对比不同时期的工作负载数据,分析变化趋势", "📉")

# 初始化
storage = StorageManager()
visualizer = WorkloadVisualizer()

# 获取所有历史数据
processed_files = storage.get_processed_files(limit=50)

if not processed_files:
    st.warning("⚠️ 暂无历史数据,请先在 [数据上传](1_数据上传) 页面上传并处理数据")
    st.stop()

# 显示可用的历史数据
st.subheader("📚 可用的历史数据")

col_info1, col_info2 = st.columns(2)

with col_info1:
    st.info(f"📊 共有 **{len(processed_files)}** 条历史记录")

with col_info2:
    if st.session_state.get('current_analysis'):
        st.success("✅ 当前分析数据已加载")
    else:
        st.warning("⚠️ 未加载当前分析数据")

st.markdown("---")

# 历史数据列表
st.subheader("📋 历史记录列表")

# 加载所有历史数据的基本信息
historical_summary = []
for file_info in processed_files:
    try:
        data = storage.load_processed_data(file_info['path'])
        base_date = data['date_info'].get('base_date', 'Unknown')
        total_members = data['stats'].get('total_members', 0)
        current_avg = data['stats']['current_week']['avg_saturation']
        next_avg = data['stats']['next_week']['avg_saturation']

        historical_summary.append({
            '基准日期': base_date,
            '总人数': total_members,
            '本周平均饱和度(%)': current_avg,
            '下周平均饱和度(%)': next_avg,
            '文件名': file_info['filename'],
            '路径': file_info['path']
        })
    except Exception as e:
        st.warning(f"⚠️ 加载文件失败: {file_info['filename']} - {str(e)}")

if historical_summary:
    summary_df = pd.DataFrame(historical_summary)

    # 显示历史数据表格和删除按钮
    st.markdown("##### 历史数据列表 (点击删除按钮可移除)")

    for idx, row in summary_df.iterrows():
        col_info, col_action = st.columns([4, 1])

        with col_info:
            st.markdown(f"""
            **{row['基准日期']}** | 总人数: {row['总人数']} | 本周饱和度: {row['本周平均饱和度(%)']}% | 下周饱和度: {row['下周平均饱和度(%)']}%
            """)

        with col_action:
            if st.button("🗑️ 删除", key=f"delete_trend_{idx}", type="secondary"):
                try:
                    # 删除处理后的数据文件
                    storage.delete_file(row['路径'])

                    # 从历史记录中移除
                    storage.remove_from_history(row['路径'])

                    st.success(f"✅ 已删除 {row['基准日期']} 的数据")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败: {str(e)}")

    st.markdown("---")

    # 数据选择器
    st.subheader("🔍 选择对比数据")

    # 添加对比模式选择
    comparison_mode = st.radio(
        "选择对比模式",
        ["团队对比", "成员对比"],
        horizontal=True,
        help="团队对比显示整体趋势，成员对比显示单个成员的工作负载变化"
    )

    col_select1, col_select2 = st.columns(2)

    with col_select1:
        # 选择第一个数据集
        selected_dates_1 = st.multiselect(
            "选择要对比的时期(可多选)",
            options=summary_df['基准日期'].tolist(),
            default=summary_df['基准日期'].tolist()[:min(3, len(summary_df))],
            key="dates_1"
        )

    with col_select2:
        # 选择对比维度
        if comparison_mode == "团队对比":
            compare_metric = st.selectbox(
                "选择对比指标",
                options=[
                    "平均饱和度",
                    "超负荷人数",
                    "正常人数",
                    "不饱和人数",
                    "空闲人数"
                ]
            )
        else:
            # 成员对比模式 - 获取成员列表
            member_options = []
            if selected_dates_1:
                # 从第一个选中的数据中获取成员列表
                first_date = selected_dates_1[0]
                file_path = summary_df[summary_df['基准日期'] == first_date]['路径'].iloc[0]
                data = storage.load_processed_data(file_path)
                result_df = pd.DataFrame(data['results'])
                member_options = sorted(result_df['成员'].tolist())

            selected_member = st.selectbox(
                "选择要对比的成员",
                options=member_options if member_options else ["请先选择时期"],
                disabled=not member_options
            )

            compare_metric = st.selectbox(
                "选择对比指标",
                options=[
                    "饱和度",
                    "总工时",
                    "本周工时",
                    "下周工时",
                    "下下周工时"
                ]
            )

    if selected_dates_1:
        st.markdown("---")

        # 准备对比数据
        if comparison_mode == "团队对比":
            # 团队对比 - 使用统计数据
            trend_data = []
            for date in selected_dates_1:
                file_path = summary_df[summary_df['基准日期'] == date]['路径'].iloc[0]
                data = storage.load_processed_data(file_path)

                # 提取三周数据
                for week_key, week_name in [('current_week', '本周'),
                                             ('next_week', '下周'),
                                             ('next_next_week', '下下周')]:
                    week_stats = data['stats'][week_key]

                    trend_data.append({
                        '基准日期': date,
                        '周期': week_name,
                        '平均饱和度': week_stats['avg_saturation'],
                        '超负荷人数': week_stats['overloaded'],
                        '正常人数': week_stats['normal'],
                        '不饱和人数': week_stats['under_saturated'],
                        '空闲人数': week_stats['idle']
                    })

            trend_df = pd.DataFrame(trend_data)
        else:
            # 成员对比 - 提取单个成员数据
            if not member_options or selected_member == "请先选择时期":
                st.warning("⚠️ 请先选择时期以获取成员列表")
                st.stop()

            trend_data = []
            for date in selected_dates_1:
                file_path = summary_df[summary_df['基准日期'] == date]['路径'].iloc[0]
                data = storage.load_processed_data(file_path)
                result_df = pd.DataFrame(data['results'])

                # 查找指定成员
                member_data = result_df[result_df['成员'] == selected_member]
                if member_data.empty:
                    st.warning(f"⚠️ 在 {date} 的数据中未找到成员 {selected_member}")
                    continue

                member_row = member_data.iloc[0]

                # 提取三周数据
                for week_col, week_name in [('本周工时', '本周'),
                                              ('下周工时', '下周'),
                                              ('下下周工时', '下下周')]:
                    # 获取对应周的饱和度列
                    saturation_col = week_col.replace('工时', '饱和度(%)')

                    trend_data.append({
                        '基准日期': date,
                        '周期': week_name,
                        '饱和度': member_row.get(saturation_col, 0),
                        '总工时': member_row.get('总工时', 0),
                        '本周工时': member_row.get('本周工时', 0),
                        '下周工时': member_row.get('下周工时', 0),
                        '下下周工时': member_row.get('下下周工时', 0)
                    })

            if not trend_data:
                st.error("❌ 未找到有效的成员数据")
                st.stop()

            trend_df = pd.DataFrame(trend_data)

        # 趋势图表
        if comparison_mode == "团队对比":
            chart_title = f"📈 {compare_metric}趋势对比"
        else:
            chart_title = f"📈 {selected_member} - {compare_metric}趋势对比"

        st.subheader(chart_title)

        fig = go.Figure()

        # 为每个基准日期添加趋势线
        for date in selected_dates_1:
            date_data = trend_df[trend_df['基准日期'] == date]

            if not date_data.empty:
                fig.add_trace(go.Scatter(
                    x=date_data['周期'],
                    y=date_data[compare_metric],
                    mode='lines+markers',
                    name=f"{date}",
                    line=dict(width=3),
                    marker=dict(size=10),
                    text=date_data[compare_metric].round(1),
                    textposition='top center'
                ))

        fig.update_layout(
            title=dict(
                text=chart_title,
                x=0,
                xanchor='left',
                font=dict(size=18, color='#333')
            ),
            xaxis_title='周期',
            yaxis_title=compare_metric,
            height=500,
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # 详细数据表格
        st.subheader("📊 详细数据对比")

        # 创建透视表
        pivot_df = trend_df.pivot_table(
            index='周期',
            columns='基准日期',
            values=compare_metric,
            aggfunc='first'
        )

        st.dataframe(pivot_df, use_container_width=True)

        st.markdown("---")

        # 跨期对比分析
        st.subheader("📉 跨期变化分析")

        if len(selected_dates_1) >= 2:
            # 计算最早和最晚的数据变化
            earliest_date = min(selected_dates_1)
            latest_date = max(selected_dates_1)

            earliest_data = trend_df[trend_df['基准日期'] == earliest_date]
            latest_data = trend_df[trend_df['基准日期'] == latest_date]

            if not earliest_data.empty and not latest_data.empty:
                col_change1, col_change2, col_change3 = st.columns(3)

                for idx, week in enumerate(['本周', '下周', '下下周']):
                    earliest_week = earliest_data[earliest_data['周期'] == week]
                    latest_week = latest_data[latest_data['周期'] == week]

                    if not earliest_week.empty and not latest_week.empty:
                        earliest_val = earliest_week[compare_metric].iloc[0]
                        latest_val = latest_week[compare_metric].iloc[0]
                        change = latest_val - earliest_val

                        if idx == 0:
                            with col_change1:
                                st.metric(
                                    f"{week} {compare_metric}",
                                    f"{latest_val:.1f}",
                                    delta=f"{change:+.1f}",
                                    delta_color="normal"
                                )
                        elif idx == 1:
                            with col_change2:
                                st.metric(
                                    f"{week} {compare_metric}",
                                    f"{latest_val:.1f}",
                                    delta=f"{change:+.1f}",
                                    delta_color="normal"
                                )
                        else:
                            with col_change3:
                                st.metric(
                                    f"{week} {compare_metric}",
                                    f"{latest_val:.1f}",
                                    delta=f"{change:+.1f}",
                                    delta_color="normal"
                                )

                if comparison_mode == "团队对比":
                    st.info(f"📊 对比时间段: {earliest_date} → {latest_date}")
                else:
                    st.info(f"📊 成员 {selected_member} 的数据对比: {earliest_date} → {latest_date}")

        st.markdown("---")

        # 团队状态分布对比 - 仅在团队对比模式下显示
        if comparison_mode == "团队对比":
            st.subheader("👥 团队状态分布对比")

            # 为每个选中的日期创建柱状图
            status_comparison = []
            for date in selected_dates_1:
                file_path = summary_df[summary_df['基准日期'] == date]['路径'].iloc[0]
                data = storage.load_processed_data(file_path)

                for week_key, week_name in [('current_week', '本周'),
                                             ('next_week', '下周'),
                                             ('next_next_week', '下下周')]:
                    week_stats = data['stats'][week_key]
                    status_comparison.append({
                        '基准日期': date,
                        '周期': week_name,
                        '超负荷': week_stats['overloaded'],
                        '正常': week_stats['normal'],
                        '不饱和': week_stats['under_saturated'],
                        '空闲': week_stats['idle']
                    })

            status_df = pd.DataFrame(status_comparison)

            # 创建分组柱状图
            fig_status = go.Figure()

            colors = {
                '超负荷': '#FF6B6B',
                '正常': '#4ECDC4',
                '不饱和': '#95E1D3',
                '空闲': '#F3F3F3'
            }

            for status in ['超负荷', '正常', '不饱和', '空闲']:
                fig_status.add_trace(go.Bar(
                    name=status,
                    x=[f"{row['基准日期']}-{row['周期']}" for _, row in status_df.iterrows()],
                    y=status_df[status],
                    marker_color=colors[status],
                    text=status_df[status],
                    textposition='auto'
                ))

            fig_status.update_layout(
                title=dict(
                    text='团队状态分布对比',
                    x=0,
                    xanchor='left',
                    font=dict(size=18, color='#333')
                ),
                barmode='stack',
                height=500,
                xaxis_title='时期-周期',
                yaxis_title='人数',
                showlegend=True
            )

            st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("---")

    # 导出对比报告
    st.subheader("📥 导出对比报告")

    if selected_dates_1:
        csv_data = trend_df.to_csv(index=False).encode('utf-8-sig')

        col_export1, col_export2 = st.columns(2)

        with col_export1:
            st.download_button(
                "📄 导出CSV对比数据",
                csv_data,
                f"trend_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                use_container_width=True
            )

        with col_export2:
            json_data = trend_df.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                "📄 导出JSON对比数据",
                json_data,
                f"trend_comparison_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json",
                use_container_width=True
            )

else:
    st.error("❌ 无法加载历史数据")

st.markdown("---")

# 数据管理
st.subheader("🗂️ 历史数据管理")

col_manage1, col_manage2 = st.columns(2)

with col_manage1:
    st.info(f"📊 当前存储了 **{len(processed_files)}** 条历史记录")

with col_manage2:
    if st.button("🧹 清理90天前的数据", use_container_width=True):
        with st.spinner("正在清理旧数据..."):
            storage.clean_old_files(days=90)
            st.success("✅ 清理完成!")
            st.rerun()

st.markdown("---")
st.caption("💡 提示: 选择多个时期进行对比,可以更清晰地看到团队负载变化趋势")
