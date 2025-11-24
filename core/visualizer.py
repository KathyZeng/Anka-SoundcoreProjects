#!/usr/bin/env python3
"""
可视化模块

负责生成各类图表,重构自 visualization.py
增加了更好的模块化和可复用性
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class WorkloadVisualizer:
    """工作负载可视化器"""

    def __init__(self):
        """初始化可视化器"""
        self.colors = {
            '超负荷': '#FF6B6B',
            '正常': '#4ECDC4',
            '不饱和': '#95E1D3',
            '空闲': '#F3F3F3'
        }
        self.status_order = ['超负荷', '正常', '不饱和', '空闲']

        logger.info("可视化器初始化完成")

    def create_weekly_bar_chart(
        self,
        result_df: pd.DataFrame,
        week_name: str,
        project_col: str,
        other_col: str,
        status_col: str,
        change_col: Optional[str] = None,
        change_rate_col: Optional[str] = None
    ) -> go.Figure:
        """
        创建周度工作负载条形图

        Args:
            result_df: 数据DataFrame
            week_name: 周名称(本周/下周/下下周)
            project_col: 项目工时列名
            other_col: 其他事务列名
            status_col: 状态列名
            change_col: 变化值列名(可选)
            change_rate_col: 变化率列名(可选)

        Returns:
            Plotly图表对象
        """
        fig = go.Figure()

        # 按状态分组数据
        data_by_status = []
        for status in self.status_order:
            status_data = result_df[result_df[status_col] == status]
            if len(status_data) > 0:
                members = status_data['成员'].tolist()
                project_hours = status_data[project_col].tolist()
                other_hours = status_data[other_col].tolist()
                changes = status_data[change_col].tolist() if change_col else None
                change_rates = status_data[change_rate_col].tolist() if change_rate_col else None

                data_by_status.append({
                    'status': status,
                    'members': members,
                    'project_hours': project_hours,
                    'other_hours': other_hours,
                    'changes': changes,
                    'change_rates': change_rates,
                    'color': self.colors[status]
                })

        # 为每个状态的每个成员添加条形
        y_position = 0
        y_labels = []
        y_positions = []

        for status_info in data_by_status:
            status = status_info['status']
            members = status_info['members']
            project_hours = status_info['project_hours']
            other_hours = status_info['other_hours']
            changes = status_info['changes']
            change_rates = status_info['change_rates']
            color = status_info['color']

            for i, member in enumerate(members):
                # 构建悬停提示信息
                hover_text = f'<b>{member}</b><br>项目工时: {project_hours[i]:.1f}小时'

                # 如果有变化数据,添加到悬停提示中
                if changes is not None and change_rates is not None:
                    change_val = changes[i]
                    change_rate_val = change_rates[i]

                    if change_val > 0:
                        arrow = '↑'
                    elif change_val < 0:
                        arrow = '↓'
                    else:
                        arrow = '='

                    hover_text += f'<br><span style="color:#000000;">{arrow} 变化: {change_val:+.1f}小时 ({change_rate_val:+.1f}%)</span>'

                hover_text += '<extra></extra>'

                # 添加项目工时条形
                fig.add_trace(go.Bar(
                    name='项目工时' if y_position == 0 and status == self.status_order[0] else '',
                    x=[project_hours[i]],
                    y=[y_position],
                    orientation='h',
                    marker=dict(color=color),
                    text=f"{member}: {project_hours[i]:.1f}h",
                    textposition='inside',
                    showlegend=(y_position == 0 and status == self.status_order[0]),
                    hovertemplate=hover_text
                ))

                # 添加其他事务工时条形
                other_hover = f'<b>{member}</b><br>其他事务: {other_hours[i]:.2f}小时<extra></extra>'
                fig.add_trace(go.Bar(
                    name='其他事务(会议等)' if y_position == 0 and status == self.status_order[0] else '',
                    x=[other_hours[i]],
                    y=[y_position],
                    orientation='h',
                    marker=dict(color='#FFD93D', pattern=dict(shape="/")),
                    showlegend=(y_position == 0 and status == self.status_order[0]),
                    hovertemplate=other_hover
                ))

                # 构建Y轴标签
                label = f"{member} ({status})"
                if changes is not None and change_rates is not None:
                    change_val = changes[i]
                    if change_val > 0:
                        label += f" ↑{change_val:+.1f}h"
                    elif change_val < 0:
                        label += f" ↓{change_val:+.1f}h"

                y_labels.append(label)
                y_positions.append(y_position)
                y_position += 1

            # 在不同状态之间添加间隔
            if status != self.status_order[-1]:
                y_position += 0.5

        # 更新布局
        fig.update_layout(
            title=dict(
                text=f'{week_name}工作负载分布',
                x=0,
                xanchor='left',
                font=dict(size=18, color='#333')
            ),
            barmode='stack',
            height=max(400, len(y_labels) * 25),
            xaxis_title='工作时长(小时)',
            yaxis=dict(
                tickmode='array',
                tickvals=y_positions,
                ticktext=y_labels,
                autorange='reversed'
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=200, t=60)
        )

        # 添加40小时参考线
        fig.add_vline(x=40, line_dash="dash", line_color="gray",
                      annotation_text="标准工时(40h)", annotation_position="top")

        return fig

    def create_status_summary_chart(self, result_df: pd.DataFrame) -> go.Figure:
        """
        创建三周状态汇总对比图

        Args:
            result_df: 数据DataFrame

        Returns:
            Plotly图表对象
        """
        weeks = ['本周', '下周', '下下周']
        statuses = self.status_order

        fig = go.Figure()

        for status in statuses:
            counts = []
            for week in weeks:
                status_col = f'{week}状态'
                count = len(result_df[result_df[status_col] == status])
                counts.append(count)

            fig.add_trace(go.Bar(
                name=status,
                x=weeks,
                y=counts,
                marker_color=self.colors[status],
                text=counts,
                textposition='auto',
            ))

        fig.update_layout(
            title=dict(
                text='三周人员状态分布对比',
                x=0,
                xanchor='left',
                font=dict(size=18, color='#333')
            ),
            xaxis_title='周期',
            yaxis_title='人数',
            barmode='group',
            height=400,
            showlegend=True,
            margin=dict(t=60)
        )

        return fig

    def create_trend_chart(self, historical_data: list) -> go.Figure:
        """
        创建历史趋势图

        Args:
            historical_data: 历史数据列表

        Returns:
            Plotly图表对象
        """
        fig = go.Figure()

        dates = [d['date'] for d in historical_data]
        avg_saturations = [d['avg_saturation'] for d in historical_data]

        fig.add_trace(go.Scatter(
            x=dates,
            y=avg_saturations,
            mode='lines+markers',
            name='平均饱和度',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=dict(
                text='团队平均饱和度趋势',
                x=0,
                xanchor='left',
                font=dict(size=18, color='#333')
            ),
            xaxis_title='日期',
            yaxis_title='平均饱和度(%)',
            height=400,
            hovermode='x unified'
        )

        return fig
