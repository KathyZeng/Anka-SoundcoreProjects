#!/usr/bin/env python3
"""
数据上传页面

允许用户上传Excel工作负载数据文件
显示上传历史和文件管理功能
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_processor import WorkloadDataProcessor
from core.storage import StorageManager
from utils.config_loader import init_session_config
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_compact_sidebar

st.set_page_config(page_title="数据上传", page_icon="📊", layout="wide")

# 应用自定义样式
apply_custom_styles()

# 初始化配置
init_session_config()

# 初始化
storage = StorageManager()

# 渲染紧凑版侧边栏
render_compact_sidebar()

# 渲染页面头部
render_page_header("数据上传", "上传您的工作负载Excel数据文件进行分析", "📊")

# 文件上传区域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📁 上传新文件")

    uploaded_file = st.file_uploader(
        "选择Excel文件",
        type=['xlsx', 'xls'],
        help="请上传包含'预估工时'工作表的Excel文件"
    )

    if uploaded_file is not None:
        # 显示文件信息
        st.success(f"✅ 文件已选择: {uploaded_file.name}")
        st.write(f"文件大小: {uploaded_file.size / 1024:.2f} KB")

        # 基准日期选择(从配置读取默认值)
        config = st.session_state.get('config', {})
        use_today_default = config.get('base_date', {}).get('use_today_by_default', True)

        use_today = st.checkbox("使用今天作为基准日期", value=use_today_default)

        if use_today:
            base_date = datetime.now().strftime('%Y-%m-%d')
            st.info(f"📅 基准日期: {base_date}")
        else:
            base_date = st.date_input("选择基准日期").strftime('%Y-%m-%d')

        # 主责成员选择
        st.markdown("---")
        st.subheader("👤 主责成员设置")
        st.info("💡 主责成员需要额外时间进行项目对接,系统会自动为其增加主责事务工时")

        # 获取配置文件中的默认主责成员
        default_primary_members = st.session_state.config.get('primary_responsibility', {}).get('members', [])

        if default_primary_members:
            st.info(f"📋 配置文件中已设置默认主责成员({len(default_primary_members)}人): {', '.join(default_primary_members)}")

        # 允许用户自定义主责成员
        customize_primary = st.checkbox("自定义主责成员(覆盖默认配置)", value=False)

        if customize_primary:
            try:
                # 临时读取Excel获取成员列表
                temp_df = pd.read_excel(uploaded_file, sheet_name='预估工时')
                member_list = temp_df['成员'].tolist()

                # 多选框选择主责成员
                primary_members = st.multiselect(
                    "选择主责成员(可多选)",
                    options=member_list,
                    default=default_primary_members if default_primary_members else [],
                    help="主责成员会额外增加主责事务工时(默认50分钟/周)"
                )

                if primary_members:
                    st.success(f"✅ 已选择 {len(primary_members)} 名主责成员: {', '.join(primary_members)}")
            except Exception as e:
                st.warning(f"⚠️ 无法读取成员列表: {str(e)}")
                primary_members = default_primary_members
        else:
            # 使用默认配置
            primary_members = default_primary_members
            if primary_members:
                st.success(f"✅ 使用默认配置的 {len(primary_members)} 名主责成员")

        # 处理按钮
        if st.button("🚀 开始处理", type="primary", use_container_width=True):
            with st.spinner("正在处理数据..."):
                try:
                    # 保存上传的文件
                    file_path = storage.save_uploaded_file(uploaded_file)
                    st.success(f"✅ 文件已保存: {os.path.basename(file_path)}")

                    # 读取并处理数据
                    processor = WorkloadDataProcessor(st.session_state.config)

                    # 读取Excel
                    df = processor.read_excel(file_path)
                    st.success(f"✅ 成功读取数据: {len(df)} 名成员")

                    # 显示主责信息
                    if primary_members:
                        st.info(f"📌 主责成员({len(primary_members)}人): {', '.join(primary_members)}")

                    # 计算分析
                    result_df, date_info = processor.calculate_workload(df, base_date, primary_members)

                    # 获取统计摘要
                    stats = processor.get_summary_stats(result_df)

                    # 保存处理后的数据
                    identifier = date_info['base_date'].strftime('%Y%m%d')
                    processed_path = storage.save_processed_data(result_df, date_info, stats, identifier)

                    # 保存到session state (确保日期对象转换为字符串)
                    st.session_state.current_data = result_df

                    # 转换日期对象为字符串以便序列化
                    serializable_date_info = {}
                    for k, v in date_info.items():
                        if hasattr(v, 'strftime'):
                            serializable_date_info[k] = v.strftime('%Y-%m-%d') if hasattr(v, 'strftime') else str(v)
                        else:
                            serializable_date_info[k] = v

                    st.session_state.current_analysis = {
                        'result_df': result_df,
                        'date_info': serializable_date_info,
                        'stats': stats,
                        'processed_path': processed_path
                    }

                    st.success("✅ 数据处理完成!")

                    # 显示快速统计
                    st.markdown("### 📊 快速统计")
                    col_a, col_b, col_c, col_d = st.columns(4)

                    with col_a:
                        st.metric("总人数", stats['total_members'])

                    with col_b:
                        st.metric("本周平均饱和度", f"{stats['current_week']['avg_saturation']}%")

                    with col_c:
                        st.metric("下周平均饱和度", f"{stats['next_week']['avg_saturation']}%")

                    with col_d:
                        overloaded = stats['next_week']['overloaded']
                        st.metric("下周超负荷", f"{overloaded} 人", delta=None if overloaded == 0 else "⚠️")

                    # 设置标志表示数据已处理完成
                    st.session_state.show_preview = True
                    st.session_state.show_analysis = True

                    st.markdown("---")

                    # 提示用户前往其他页面查看详细结果
                    st.success("✅ 数据已成功保存到 session_state，可以前往其他页面查看详细分析")

                    st.info("""
                    ### 📋 数据上传完成！请通过左侧边栏导航查看结果

                    **下一步操作**:
                    1. 点击左侧边栏的 **数据预览** 查看完整数据表格
                    2. 点击左侧边栏的 **负载分析** 查看三周对比图表
                    3. 点击左侧边栏的 **趋势对比** 查看历史趋势分析

                    **数据已保存**: {0} 名成员，基准日期 {1}
                    """.format(stats['total_members'], serializable_date_info['base_date']))

                    # 添加调试信息
                    with st.expander("🔧 调试信息 (点击展开)"):
                        st.write("Session State Keys:", list(st.session_state.keys()))
                        st.write("current_analysis 存在:", 'current_analysis' in st.session_state)
                        if 'current_analysis' in st.session_state:
                            st.write("result_df shape:", st.session_state.current_analysis['result_df'].shape)
                            st.write("date_info keys:", list(st.session_state.current_analysis['date_info'].keys()))
                            st.write("stats keys:", list(st.session_state.current_analysis['stats'].keys()))

                except Exception as e:
                    st.error(f"❌ 处理失败: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

with col2:
    st.subheader("📋 数据格式要求")

    with st.expander("点击查看详情"):
        st.markdown("""
        **Excel文件要求:**

        1. **Sheet名称**: "预估工时"
        2. **第一列**: 成员名称
        3. **其他列**: 日期(格式: YYYY-MM-DD)

        **示例:**

        | 成员 | 2025-11-17 | 2025-11-18 | 2025-11-19 |
        |------|-----------|-----------|-----------|
        | 张三 | 8 | 8 | 0 |
        | 李四 | 8 | 8 | 8 |

        **注意事项:**
        - 工时单位为小时
        - 日期必须是YYYY-MM-DD格式
        - 确保数据完整无缺失
        """)

st.markdown("---")

# 上传历史
st.subheader("📜 上传历史")

# 添加清空所有历史的按钮
col_history_title, col_history_clear = st.columns([4, 1])

with col_history_clear:
    if st.button("🗑️ 清空所有", type="secondary", use_container_width=True):
        # 删除所有上传的文件
        if os.path.exists(storage.uploads_dir):
            for filename in os.listdir(storage.uploads_dir):
                file_path = os.path.join(storage.uploads_dir, filename)
                if os.path.isfile(file_path):
                    storage.delete_file(file_path)

        # 删除所有处理后的文件
        if os.path.exists(storage.processed_dir):
            for filename in os.listdir(storage.processed_dir):
                file_path = os.path.join(storage.processed_dir, filename)
                if os.path.isfile(file_path):
                    storage.delete_file(file_path)

        # 清空历史记录
        if os.path.exists(storage.history_file):
            os.remove(storage.history_file)

        st.success("✅ 已清空所有历史记录和文件")
        st.rerun()

history = storage.get_upload_history(limit=10)

if history:
    for i, record in enumerate(history):
        with st.expander(f"📄 {record['original_name']} - {record['timestamp'][:19].replace('T', ' ')}"):
            col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])

            with col_a:
                st.write(f"**原始文件名**: {record['original_name']}")
                st.write(f"**保存文件名**: {record['filename']}")
                st.write(f"**文件大小**: {record['size'] / 1024:.2f} KB")

            with col_b:
                if os.path.exists(record['file_path']):
                    with open(record['file_path'], 'rb') as f:
                        st.download_button(
                            "📥 下载",
                            f,
                            file_name=record['original_name'],
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key=f"download_{i}"
                        )
                else:
                    st.warning("文件不存在")

            with col_c:
                # 重新分析按钮
                if os.path.exists(record['file_path']):
                    if st.button("📊 重新分析", key=f"reanalyze_{i}", type="primary"):
                        with st.spinner("正在重新处理数据..."):
                            try:
                                # 获取配置中的默认主责成员
                                default_primary_members = st.session_state.config.get('primary_responsibility', {}).get('members', [])

                                # 使用今天作为基准日期
                                base_date = datetime.now().strftime('%Y-%m-%d')

                                # 读取并处理数据
                                processor = WorkloadDataProcessor(st.session_state.config)
                                df = processor.read_excel(record['file_path'])

                                # 计算分析
                                result_df, date_info = processor.calculate_workload(df, base_date, default_primary_members)

                                # 获取统计摘要
                                stats = processor.get_summary_stats(result_df)

                                # 保存处理后的数据
                                identifier = date_info['base_date'].strftime('%Y%m%d')
                                processed_path = storage.save_processed_data(result_df, date_info, stats, identifier)

                                # 保存到session state
                                st.session_state.current_data = result_df

                                # 转换日期对象为字符串
                                serializable_date_info = {}
                                for k, v in date_info.items():
                                    if hasattr(v, 'strftime'):
                                        serializable_date_info[k] = v.strftime('%Y-%m-%d')
                                    else:
                                        serializable_date_info[k] = v

                                st.session_state.current_analysis = {
                                    'result_df': result_df,
                                    'date_info': serializable_date_info,
                                    'stats': stats,
                                    'processed_path': processed_path
                                }

                                st.session_state.show_preview = True
                                st.session_state.show_analysis = True

                                st.success(f"✅ 重新分析完成！成员数: {stats['total_members']}, 基准日期: {serializable_date_info['base_date']}")

                                # 显示导航提示
                                st.info("""
                                ### 📋 数据已更新！请通过左侧边栏导航查看结果

                                **下一步操作**:
                                1. 点击左侧边栏的 **数据预览** 查看完整数据表格
                                2. 点击左侧边栏的 **负载分析** 查看三周对比图表
                                3. 点击左侧边栏的 **趋势对比** 查看历史趋势分析
                                """)

                            except Exception as e:
                                st.error(f"❌ 重新分析失败: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())

            with col_d:
                if st.button("🗑️ 删除", key=f"delete_{i}", type="secondary"):
                    try:
                        # 1. 删除上传的文件
                        storage.delete_file(record['file_path'])

                        # 2. 删除对应的处理后数据
                        # 查找对应的 processed 文件（基于文件名时间戳）
                        timestamp = record['filename'].split('_')[0]  # 提取时间戳
                        processed_dir = os.path.join(storage.processed_dir)
                        if os.path.exists(processed_dir):
                            for filename in os.listdir(processed_dir):
                                if filename.startswith(timestamp):
                                    processed_path = os.path.join(processed_dir, filename)
                                    storage.delete_file(processed_path)

                        # 3. 从历史记录中移除
                        storage.remove_from_history(record['file_path'])

                        st.success("✅ 已删除文件、相关数据及历史记录")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 删除失败: {str(e)}")
else:
    st.info("📭 暂无上传历史")

# 底部信息
st.markdown("---")
st.caption("💡 提示: 上传的文件会自动保存在 data/uploads 目录下")
