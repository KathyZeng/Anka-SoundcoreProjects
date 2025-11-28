#!/usr/bin/env python3
"""
配置管理页面

允许用户调整系统配置参数,包括标准工时、饱和度阈值等
支持配置的保存和恢复
"""

import streamlit as st
import yaml
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import init_session_config
from utils.styles import apply_custom_styles, render_page_header
from utils.sidebar import render_compact_sidebar

st.set_page_config(page_title="配置管理", page_icon="⚙️", layout="wide")

# 应用自定义样式
apply_custom_styles()

# 初始化配置
init_session_config()

# 渲染紧凑版侧边栏
render_compact_sidebar()

# 渲染页面头部
render_page_header("配置管理", "调整系统分析参数和配置", "⚙️")

# 配置文件路径
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')


def load_config():
    """加载配置文件"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        # 返回默认配置
        return {
            'base_date': {
                'use_today_by_default': True
            },
            'standard_hours_per_week': 40,
            'other_tasks': {
                'enabled': True,
                'weekly_minutes_per_person': 92
            },
            'primary_responsibility': {
                'enabled': True,
                'weekly_minutes_per_primary': 50,
                'members': []
            },
            'saturation_thresholds': {
                'under_saturated_max': 90,
                'normal_min': 90,
                'normal_max': 110,
                'over_saturated_min': 110
            }
        }


def save_config(config):
    """保存配置文件"""
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        return True
    except Exception as e:
        st.error(f"❌ 保存配置失败: {str(e)}")
        return False


# 加载当前配置
current_config = load_config()

# 配置编辑器
st.subheader("📝 配置编辑")

# 基准日期配置
st.markdown("### 📅 基准日期配置")

use_today_by_default = st.checkbox(
    "默认使用今天作为基准日期",
    value=current_config.get('base_date', {}).get('use_today_by_default', True),
    help="勾选后,在数据上传页面将默认使用今天作为基准日期;取消勾选后,将默认显示日期选择器"
)

st.info("""
💡 **基准日期说明**:
- 勾选: 数据上传时默认使用当天日期,可手动取消勾选选择其他日期
- 取消勾选: 数据上传时默认显示日期选择器,需手动选择日期
""")

st.markdown("---")

# 基础配置
st.markdown("### 1️⃣ 基础配置")

col1, col2 = st.columns(2)

with col1:
    standard_hours = st.number_input(
        "标准工时(小时/周)",
        min_value=1,
        max_value=168,
        value=current_config.get('standard_hours_per_week', 40),
        step=1,
        help="每周标准工作时长,通常为40小时"
    )

with col2:
    other_tasks_enabled = st.checkbox(
        "启用其他事务工时",
        value=current_config.get('other_tasks', {}).get('enabled', True),
        help="是否在计算中包含其他事务(如会议、培训等)的工时"
    )

if other_tasks_enabled:
    other_tasks_minutes = st.number_input(
        "其他事务工时(分钟/周/人)",
        min_value=0,
        max_value=2400,
        value=current_config.get('other_tasks', {}).get('weekly_minutes_per_person', 92),
        step=1,
        help="每人每周用于其他事务的时间,以分钟为单位"
    )

    st.info(f"💡 其他事务工时: **{other_tasks_minutes / 60:.2f}** 小时/周/人")

# 主责事务配置
st.markdown("### 👤 主责事务配置")

col3, col4 = st.columns(2)

with col3:
    st.markdown("")  # 占位

with col4:
    primary_responsibility_enabled = st.checkbox(
        "启用主责事务工时",
        value=current_config.get('primary_responsibility', {}).get('enabled', True),
        help="主责成员需要额外时间进行项目对接、协调等工作"
    )

if primary_responsibility_enabled:
    st.markdown("#### ⚙️ 主责工时配置")

    primary_responsibility_percentage = st.number_input(
        "主责额外工时百分比(%)",
        min_value=0,
        max_value=100,
        value=int(current_config.get('primary_responsibility', {}).get('weekly_percentage', 0.5) * 100),
        step=5,
        help="主责成员额外增加的工时百分比（基于标准工时）。例如: 50 表示主责成员额外增加 40 × 50% = 20小时/周"
    )

    # 转换为小数
    primary_responsibility_percentage = primary_responsibility_percentage / 100

    # 计算实际增加的小时数
    standard_hours = current_config.get('standard_hours_per_week', 40)
    primary_hours = standard_hours * primary_responsibility_percentage

    # 实时显示影响
    col_impact1, col_impact2 = st.columns(2)

    with col_impact1:
        st.metric(
            "主责额外工时",
            f"{primary_hours:.1f} 小时/周",
            help=f"标准工时 {standard_hours}h × {primary_responsibility_percentage*100:.0f}%"
        )

    with col_impact2:
        st.metric(
            "饱和度增加",
            f"{primary_responsibility_percentage*100:.0f}%",
            help="主责成员的饱和度将增加这个百分比"
        )

    st.info(f"""
    💡 **配置说明**:
    - 修改此百分比后，保存配置即可生效
    - 所有配置为主责的成员都将按此比例增加工时
    - 例如: 当前配置为 {primary_responsibility_percentage*100:.0f}%，每名主责成员将额外增加 {primary_hours:.1f} 小时/周
    """)

    # 主责成员配置
    st.markdown("#### 📋 默认主责成员")

    # 获取当前配置的主责成员列表
    current_primary_members = current_config.get('primary_responsibility', {}).get('members', [])

    # 尝试从最近的数据中获取成员列表
    from core.storage import StorageManager
    import pandas as pd

    member_options = []
    try:
        storage_mgr = StorageManager()
        processed_files = storage_mgr.get_processed_files(limit=1)
        if processed_files:
            data = storage_mgr.load_processed_data(processed_files[0]['path'])
            result_df = pd.DataFrame(data['results'])
            member_options = result_df['成员'].tolist()
            st.info(f"📊 从最近的数据中找到 {len(member_options)} 名成员")
    except:
        pass

    # 选择输入方式
    input_method = st.radio(
        "选择输入方式",
        ["从已上传数据中选择", "手动输入"],
        horizontal=True,
        help="从已上传的数据中选择成员，或手动输入成员名称"
    )

    if input_method == "从已上传数据中选择" and member_options:
        # 多选下拉框
        primary_members = st.multiselect(
            "选择主责成员",
            options=member_options,
            default=[m for m in current_primary_members if m in member_options],
            help="从已上传数据的成员列表中选择主责成员"
        )
    else:
        # 文本区域输入
        if input_method == "从已上传数据中选择" and not member_options:
            st.warning("⚠️ 未找到已上传的数据，请先上传数据或选择手动输入")

        primary_members_text = st.text_area(
            "主责成员列表(每行一个成员名)",
            value='\n'.join(current_primary_members) if current_primary_members else '',
            height=150,
            help="输入主责成员姓名，每行一个。成员名需与Excel中完全一致"
        )
        # 解析输入的成员列表
        primary_members = [name.strip() for name in primary_members_text.split('\n') if name.strip()]

    if primary_members:
        st.success(f"✅ 已配置 {len(primary_members)} 名主责成员: {', '.join(primary_members)}")

        # 显示主责成员将增加的工时
        st.markdown("---")
        st.markdown("##### 📊 主责成员工时预览")
        st.info(f"""
        **主责成员额外工时**: {primary_hours:.1f} 小时/周

        **影响说明**:
        - 每名主责成员的总工时 = 项目工时 + 其他事务 + {primary_hours:.1f}h
        - 饱和度增加: {primary_responsibility_percentage*100:.0f}%
        - 主责成员: {', '.join(primary_members)}
        """)
    else:
        st.warning("⚠️ 未配置主责成员。您也可以在数据上传时动态选择主责成员")

st.markdown("---")

# 饱和度阈值配置
st.markdown("### 2️⃣ 饱和度阈值配置")

st.markdown("""
饱和度是工作时长与标准工时的比值。通过设置不同的阈值,可以将团队成员分为不同的负载状态:
- 🔴 **超负荷**: 饱和度超过阈值,工作量过大
- 🟢 **正常**: 饱和度在正常范围内
- 🔵 **不饱和**: 饱和度低于阈值,工作量不足
- ⚪ **空闲**: 饱和度为0,无工作任务
""")

col_threshold1, col_threshold2, col_threshold3 = st.columns(3)

with col_threshold1:
    under_saturated_max = st.number_input(
        "不饱和上限(%)",
        min_value=0,
        max_value=100,
        value=current_config.get('saturation_thresholds', {}).get('under_saturated_max', 90),
        step=1,
        help="低于此值视为不饱和状态"
    )

with col_threshold2:
    normal_min = st.number_input(
        "正常下限(%)",
        min_value=0,
        max_value=200,
        value=current_config.get('saturation_thresholds', {}).get('normal_min', 90),
        step=1,
        help="正常状态的最小饱和度"
    )

    normal_max = st.number_input(
        "正常上限(%)",
        min_value=0,
        max_value=200,
        value=current_config.get('saturation_thresholds', {}).get('normal_max', 110),
        step=1,
        help="正常状态的最大饱和度"
    )

with col_threshold3:
    over_saturated_min = st.number_input(
        "超负荷下限(%)",
        min_value=0,
        max_value=300,
        value=current_config.get('saturation_thresholds', {}).get('over_saturated_min', 110),
        step=1,
        help="高于此值视为超负荷状态"
    )

# 验证阈值逻辑
if not (under_saturated_max <= normal_min <= normal_max <= over_saturated_min):
    st.error("❌ 阈值设置不合理! 请确保: 不饱和上限 ≤ 正常下限 ≤ 正常上限 ≤ 超负荷下限")

st.markdown("---")

# 可视化阈值设置
st.markdown("### 📊 阈值可视化")

import plotly.graph_objects as go

fig = go.Figure()

# 创建阈值范围可视化
fig.add_trace(go.Bar(
    x=[under_saturated_max],
    y=['饱和度范围'],
    orientation='h',
    name='不饱和',
    marker=dict(color='#95E1D3'),
    text=f"不饱和 (0-{under_saturated_max}%)",
    textposition='inside',
    hoverinfo='text',
    hovertext=f"不饱和范围: 0% - {under_saturated_max}%"
))

fig.add_trace(go.Bar(
    x=[normal_max - normal_min],
    y=['饱和度范围'],
    orientation='h',
    name='正常',
    marker=dict(color='#4ECDC4'),
    text=f"正常 ({normal_min}-{normal_max}%)",
    textposition='inside',
    hoverinfo='text',
    hovertext=f"正常范围: {normal_min}% - {normal_max}%"
))

fig.add_trace(go.Bar(
    x=[200 - over_saturated_min],
    y=['饱和度范围'],
    orientation='h',
    name='超负荷',
    marker=dict(color='#FF6B6B'),
    text=f"超负荷 ({over_saturated_min}%+)",
    textposition='inside',
    hoverinfo='text',
    hovertext=f"超负荷范围: {over_saturated_min}% - 200%+"
))

fig.update_layout(
    barmode='stack',
    height=200,
    xaxis_title='饱和度(%)',
    showlegend=False,
    margin=dict(l=100, r=20, t=20, b=40)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 示例计算
st.markdown("### 🧮 示例计算")

st.markdown("以下是基于当前配置的工时计算示例:")

col_example_input1, col_example_input2 = st.columns(2)

with col_example_input1:
    example_project_hours = st.slider(
        "示例: 项目工时(小时/周)",
        min_value=0,
        max_value=80,
        value=40,
        step=1
    )

with col_example_input2:
    example_is_primary = st.checkbox(
        "该成员是否为主责",
        value=False,
        help="主责成员会额外计算主责事务工时"
    )

example_other_hours = other_tasks_minutes / 60 if other_tasks_enabled else 0
example_primary_hours = primary_hours if (primary_responsibility_enabled and example_is_primary) else 0
example_total_hours = example_project_hours + example_other_hours + example_primary_hours
example_saturation = (example_total_hours / standard_hours) * 100

col_example1, col_example2, col_example3, col_example4, col_example5 = st.columns(5)

with col_example1:
    st.metric("项目工时", f"{example_project_hours}h")

with col_example2:
    st.metric("其他事务", f"{example_other_hours:.2f}h")

with col_example3:
    st.metric("主责事务", f"{example_primary_hours:.2f}h")

with col_example4:
    st.metric("总工时", f"{example_total_hours:.2f}h")

with col_example5:
    # 判断状态
    if example_saturation == 0:
        status = "空闲"
        status_color = "⚪"
    elif example_saturation < under_saturated_max:
        status = "不饱和"
        status_color = "🔵"
    elif normal_min <= example_saturation <= normal_max:
        status = "正常"
        status_color = "🟢"
    else:
        status = "超负荷"
        status_color = "🔴"

    st.metric("饱和度", f"{example_saturation:.1f}%")
    st.markdown(f"**状态**: {status_color} {status}")

st.markdown("---")

# 保存配置
st.subheader("💾 保存配置")

col_save1, col_save2, col_save3 = st.columns([2, 1, 1])

with col_save1:
    if st.button("💾 保存配置", type="primary", use_container_width=True):
        # 构建新配置
        new_config = {
            'base_date': {
                'use_today_by_default': use_today_by_default
            },
            'standard_hours_per_week': standard_hours,
            'other_tasks': {
                'enabled': other_tasks_enabled,
                'weekly_minutes_per_person': other_tasks_minutes if other_tasks_enabled else 92
            },
            'primary_responsibility': {
                'enabled': primary_responsibility_enabled,
                'weekly_percentage': primary_responsibility_percentage if primary_responsibility_enabled else 0.5,
                'members': primary_members if primary_responsibility_enabled else []
            },
            'saturation_thresholds': {
                'under_saturated_max': under_saturated_max,
                'normal_min': normal_min,
                'normal_max': normal_max,
                'over_saturated_min': over_saturated_min
            }
        }

        # 验证配置
        if under_saturated_max <= normal_min <= normal_max <= over_saturated_min:
            if save_config(new_config):
                # 更新session state
                st.session_state.config = new_config
                st.success("✅ 配置已保存!")
                st.info("💡 配置已更新。请重新上传数据以应用新配置")
        else:
            st.error("❌ 配置验证失败! 请检查阈值设置")

with col_save2:
    if st.button("🔄 重置为默认", use_container_width=True):
        default_config = {
            'base_date': {
                'use_today_by_default': True
            },
            'standard_hours_per_week': 40,
            'other_tasks': {
                'enabled': True,
                'weekly_minutes_per_person': 92
            },
            'primary_responsibility': {
                'enabled': True,
                'weekly_percentage': 0.5,
                'members': []
            },
            'saturation_thresholds': {
                'under_saturated_max': 90,
                'normal_min': 90,
                'normal_max': 110,
                'over_saturated_min': 110
            }
        }

        if save_config(default_config):
            st.session_state.config = default_config
            st.success("✅ 已重置为默认配置!")
            st.rerun()

with col_save3:
    if st.button("📥 导出配置", use_container_width=True):
        config_yaml = yaml.dump(current_config, allow_unicode=True, default_flow_style=False)
        st.download_button(
            "⬇️ 下载配置文件",
            config_yaml,
            "workload_config.yaml",
            "text/yaml",
            use_container_width=True
        )

st.markdown("---")

# 当前配置预览
st.subheader("📋 当前配置详情")

with st.expander("查看完整配置", expanded=False):
    st.code(yaml.dump(current_config, allow_unicode=True, default_flow_style=False), language='yaml')

st.markdown("---")

# 配置说明
st.subheader("📖 配置说明")

col_doc1, col_doc2 = st.columns(2)

with col_doc1:
    st.markdown("""
    **标准工时配置:**
    - `standard_hours_per_week`: 每周标准工作时长
    - 通常设置为40小时(每天8小时,每周5天)
    - 饱和度计算的基准值

    **其他事务配置:**
    - `enabled`: 是否启用其他事务工时计算
    - `weekly_minutes_per_person`: 每人每周的其他事务时间(分钟)
    - 包括会议、培训、日常沟通等非项目工作
    """)

with col_doc2:
    st.markdown("""
    **饱和度阈值配置:**
    - `under_saturated_max`: 不饱和状态的上限
    - `normal_min`: 正常状态的下限
    - `normal_max`: 正常状态的上限
    - `over_saturated_min`: 超负荷状态的下限

    **注意事项:**
    - 阈值必须满足逻辑顺序关系
    - 修改配置后需要重新处理数据
    - 建议定期根据实际情况调整阈值
    """)

st.markdown("---")
st.caption("💡 提示: 修改配置后,需要重新上传数据才能应用新的分析参数")
