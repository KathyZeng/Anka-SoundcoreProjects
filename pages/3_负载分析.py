#!/usr/bin/env python3
"""
负载分析页面

主要的可视化分析页面,展示三周工作负载分布图表
支持交互式图表和多格式报告导出
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import io

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.visualizer import WorkloadVisualizer
from core.storage import StorageManager
from utils.config_loader import init_session_config
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_compact_sidebar

st.set_page_config(page_title="负载分析", page_icon="📈", layout="wide")

# 应用自定义样式
apply_custom_styles()

# 初始化配置
init_session_config()

# 渲染紧凑版侧边栏
render_compact_sidebar()

# 渲染页面头部
render_page_header("负载分析", "可视化展示团队工作负载分布和变化趋势", "📈")

# 初始化
visualizer = WorkloadVisualizer()
storage = StorageManager()

# 获取所有历史数据
processed_files = storage.get_processed_files(limit=50)

if not processed_files:
    st.warning("⚠️ 暂无数据,请先在 [数据上传](1_数据上传) 页面上传文件")
    st.stop()

# 创建历史数据选择器
st.subheader("📂 选择要分析的数据")

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
        help="选择要分析的历史数据"
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

# 基本信息展示
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📅 基准日期", str(date_info['base_date']))

with col2:
    st.metric("👥 总人数", stats['total_members'])

with col3:
    current_avg = stats['current_week']['avg_saturation']
    next_avg = stats['next_week']['avg_saturation']
    delta = next_avg - current_avg
    st.metric("📊 本周平均饱和度", f"{current_avg}%", delta=f"{delta:+.1f}%")

with col4:
    overloaded = stats['next_week']['overloaded']
    st.metric("🔴 下周超负荷", f"{overloaded} 人",
              delta="需关注" if overloaded > 0 else "正常",
              delta_color="inverse")

st.markdown("---")

# 图表选项
st.subheader("🎨 图表选项")

col_opt1, col_opt2, col_opt3 = st.columns(3)

with col_opt1:
    show_current = st.checkbox("显示本周数据", value=True)

with col_opt2:
    show_next = st.checkbox("显示下周数据", value=True)

with col_opt3:
    show_next_next = st.checkbox("显示下下周数据", value=True)

st.markdown("---")

# 本周工作负载分布
if show_current:
    st.subheader("📊 本周工作负载分布")

    with st.spinner("正在生成图表..."):
        try:
            fig_current = visualizer.create_weekly_bar_chart(
                result_df=result_df,
                week_name='本周',
                project_col='本周项目工时',
                other_col='本周其他事务',
                status_col='本周状态'
            )

            st.plotly_chart(fig_current, use_container_width=True)

            # 本周统计摘要
            with st.expander("📊 本周统计详情", expanded=False):
                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

                with col_s1:
                    st.metric("平均饱和度", f"{stats['current_week']['avg_saturation']}%")

                with col_s2:
                    st.metric("🔴 超负荷", f"{stats['current_week']['overloaded']} 人")

                with col_s3:
                    st.metric("🟢 正常", f"{stats['current_week']['normal']} 人")

                with col_s4:
                    st.metric("🔵 不饱和", f"{stats['current_week']['under_saturated']} 人")

                with col_s5:
                    st.metric("⚪ 空闲", f"{stats['current_week']['idle']} 人")

        except Exception as e:
            st.error(f"❌ 生成本周图表失败: {str(e)}")

    st.markdown("---")

# 下周工作负载分布
if show_next:
    st.subheader("📈 下周工作负载分布(含变化率)")

    with st.spinner("正在生成图表..."):
        try:
            fig_next = visualizer.create_weekly_bar_chart(
                result_df=result_df,
                week_name='下周',
                project_col='下周项目工时',
                other_col='下周其他事务',
                status_col='下周状态',
                change_col='下周变化',
                change_rate_col='下周变化率(%)'
            )

            st.plotly_chart(fig_next, use_container_width=True)

            # 下周统计摘要
            with st.expander("📊 下周统计详情", expanded=False):
                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

                with col_s1:
                    st.metric("平均饱和度", f"{stats['next_week']['avg_saturation']}%")

                with col_s2:
                    st.metric("🔴 超负荷", f"{stats['next_week']['overloaded']} 人")

                with col_s3:
                    st.metric("🟢 正常", f"{stats['next_week']['normal']} 人")

                with col_s4:
                    st.metric("🔵 不饱和", f"{stats['next_week']['under_saturated']} 人")

                with col_s5:
                    st.metric("⚪ 空闲", f"{stats['next_week']['idle']} 人")

            # 变化预警
            large_changes = result_df[abs(result_df['下周变化']) > 20]
            if len(large_changes) > 0:
                st.warning(f"⚠️ 发现 {len(large_changes)} 名成员下周工时变化超过20小时")

                with st.expander("查看详情"):
                    display_cols = ['成员', '本周总工时', '下周总工时', '下周变化', '下周变化率(%)', '下周状态']
                    st.dataframe(large_changes[display_cols], use_container_width=True)

        except Exception as e:
            st.error(f"❌ 生成下周图表失败: {str(e)}")

    st.markdown("---")

# 下下周工作负载分布
if show_next_next:
    st.subheader("📉 下下周工作负载分布(含变化率)")

    with st.spinner("正在生成图表..."):
        try:
            fig_next_next = visualizer.create_weekly_bar_chart(
                result_df=result_df,
                week_name='下下周',
                project_col='下下周项目工时',
                other_col='下下周其他事务',
                status_col='下下周状态',
                change_col='下下周变化',
                change_rate_col='下下周变化率(%)'
            )

            st.plotly_chart(fig_next_next, use_container_width=True)

            # 下下周统计摘要
            with st.expander("📊 下下周统计详情", expanded=False):
                col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

                with col_s1:
                    st.metric("平均饱和度", f"{stats['next_next_week']['avg_saturation']}%")

                with col_s2:
                    st.metric("🔴 超负荷", f"{stats['next_next_week']['overloaded']} 人")

                with col_s3:
                    st.metric("🟢 正常", f"{stats['next_next_week']['normal']} 人")

                with col_s4:
                    st.metric("🔵 不饱和", f"{stats['next_next_week']['under_saturated']} 人")

                with col_s5:
                    st.metric("⚪ 空闲", f"{stats['next_next_week']['idle']} 人")

        except Exception as e:
            st.error(f"❌ 生成下下周图表失败: {str(e)}")

    st.markdown("---")

# 三周状态对比
st.subheader("📊 三周状态分布对比")

with st.spinner("正在生成对比图表..."):
    try:
        fig_summary = visualizer.create_status_summary_chart(result_df)
        st.plotly_chart(fig_summary, use_container_width=True)

        # 趋势分析
        st.markdown("### 📈 趋势分析")

        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown("**饱和度趋势:**")
            current_avg = stats['current_week']['avg_saturation']
            next_avg = stats['next_week']['avg_saturation']
            next_next_avg = stats['next_next_week']['avg_saturation']

            if next_avg > current_avg and next_next_avg > next_avg:
                st.error("📈 工作负载持续上升,需要关注!")
            elif next_avg < current_avg and next_next_avg < next_avg:
                st.success("📉 工作负载持续下降,负载趋于合理")
            else:
                st.info("📊 工作负载波动,保持观察")

        with col_t2:
            st.markdown("**超负荷人员趋势:**")
            current_overloaded = stats['current_week']['overloaded']
            next_overloaded = stats['next_week']['overloaded']
            next_next_overloaded = stats['next_next_week']['overloaded']

            if next_overloaded > current_overloaded:
                st.warning(f"⚠️ 下周超负荷人数增加 {next_overloaded - current_overloaded} 人")
            elif next_overloaded < current_overloaded:
                st.success(f"✅ 下周超负荷人数减少 {current_overloaded - next_overloaded} 人")
            else:
                st.info("➡️ 下周超负荷人数保持不变")

    except Exception as e:
        st.error(f"❌ 生成对比图表失败: {str(e)}")

st.markdown("---")

# 报告导出
st.subheader("📥 报告导出")

col_export1, col_export2, col_export3 = st.columns(3)

with col_export1:
    # 导出Excel报告
    if st.button("📄 导出Excel报告", use_container_width=True):
        with st.spinner("正在生成Excel报告..."):
            try:
                # 创建Excel writer
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # 写入主数据
                    result_df.to_excel(writer, sheet_name='工作负载分析', index=False)

                    # 写入统计摘要
                    summary_data = []
                    for week_key, week_name in [('current_week', '本周'),
                                                 ('next_week', '下周'),
                                                 ('next_next_week', '下下周')]:
                        week_stats = stats[week_key]
                        summary_data.append({
                            '周期': week_name,
                            '平均饱和度(%)': week_stats['avg_saturation'],
                            '超负荷人数': week_stats['overloaded'],
                            '正常人数': week_stats['normal'],
                            '不饱和人数': week_stats['under_saturated'],
                            '空闲人数': week_stats['idle']
                        })

                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='统计摘要', index=False)

                output.seek(0)

                st.download_button(
                    "⬇️ 下载Excel报告",
                    output,
                    f"workload_analysis_{date_info['base_date']}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

                st.success("✅ Excel报告已生成!")

            except Exception as e:
                st.error(f"❌ 生成Excel报告失败: {str(e)}")

with col_export2:
    # 导出CSV报告
    csv = result_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📄 导出CSV数据",
        csv,
        f"workload_data_{date_info['base_date']}.csv",
        "text/csv",
        use_container_width=True
    )

with col_export3:
    # 导出JSON数据
    json_str = result_df.to_json(orient='records', force_ascii=False, indent=2)
    st.download_button(
        "📄 导出JSON数据",
        json_str,
        f"workload_data_{date_info['base_date']}.json",
        "application/json",
        use_container_width=True
    )

st.markdown("---")

# 分析建议
st.subheader("💡 分析建议")

# 检查超负荷成员
overloaded_next = result_df[result_df['下周饱和度(%)'] > 110]
if len(overloaded_next) > 0:
    st.warning(f"⚠️ 下周有 {len(overloaded_next)} 名成员超负荷,建议:")
    st.markdown("""
    - 🔄 重新分配部分工作任务
    - 📅 调整项目优先级和时间线
    - 👥 考虑增加资源支持
    - 💬 与团队成员沟通工作安排
    """)

# 检查空闲成员
idle_next = result_df[result_df['下周饱和度(%)'] == 0]
if len(idle_next) > 0:
    st.info(f"ℹ️ 下周有 {len(idle_next)} 名成员空闲,建议:")
    st.markdown("""
    - 📋 安排新的项目任务
    - 📚 提供培训和学习机会
    - 🔧 进行技术债务清理
    - 🤝 支持其他忙碌的团队成员
    """)

# 检查负载波动较大的成员
large_fluctuation = result_df[(abs(result_df['下周变化']) > 15) | (abs(result_df['下下周变化']) > 15)]
if len(large_fluctuation) > 0:
    st.warning(f"⚠️ 有 {len(large_fluctuation)} 名成员工作负载波动较大,建议:")
    st.markdown("""
    - 📊 检查任务分配的平衡性
    - 🔄 平滑工作负载分布
    - 📅 优化项目时间规划
    - 💡 考虑引入缓冲机制
    """)

st.markdown("---")
st.caption("💡 提示: 图表支持交互操作,可以缩放、平移和导出图片")
