#!/usr/bin/env python3
"""
格式化工具模块

提供各种数据格式化和显示功能
"""

from datetime import datetime, timedelta
from typing import Union, Optional
import pandas as pd


class DataFormatter:
    """数据格式化器"""

    @staticmethod
    def format_hours(hours: float, precision: int = 1) -> str:
        """
        格式化小时数

        Args:
            hours: 小时数
            precision: 小数精度

        Returns:
            格式化后的字符串
        """
        return f"{hours:.{precision}f}h"

    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """
        格式化百分比

        Args:
            value: 数值
            precision: 小数精度

        Returns:
            格式化后的字符串
        """
        return f"{value:.{precision}f}%"

    @staticmethod
    def format_change(change: float, precision: int = 1, show_plus: bool = True) -> str:
        """
        格式化变化值

        Args:
            change: 变化值
            precision: 小数精度
            show_plus: 是否显示正号

        Returns:
            格式化后的字符串
        """
        if change > 0:
            sign = "+" if show_plus else ""
            return f"{sign}{change:.{precision}f}h"
        elif change < 0:
            return f"{change:.{precision}f}h"
        else:
            return "0h"

    @staticmethod
    def format_date(date: Union[str, datetime, pd.Timestamp], format_str: str = "%Y-%m-%d") -> str:
        """
        格式化日期

        Args:
            date: 日期对象
            format_str: 格式字符串

        Returns:
            格式化后的日期字符串
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)

        if isinstance(date, pd.Timestamp):
            date = date.to_pydatetime()

        return date.strftime(format_str)

    @staticmethod
    def format_date_range(start_date: datetime, end_date: datetime) -> str:
        """
        格式化日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            格式化后的日期范围字符串
        """
        return f"{start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}"

    @staticmethod
    def format_week_label(week_name: str, start_date: datetime, end_date: datetime) -> str:
        """
        格式化周标签

        Args:
            week_name: 周名称(本周/下周/下下周)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            格式化后的周标签
        """
        date_range = DataFormatter.format_date_range(start_date, end_date)
        return f"{week_name} ({date_range})"

    @staticmethod
    def get_status_emoji(status: str) -> str:
        """
        获取状态对应的emoji

        Args:
            status: 状态名称

        Returns:
            emoji字符
        """
        emoji_map = {
            '超负荷': '🔴',
            '正常': '🟢',
            '不饱和': '🔵',
            '空闲': '⚪'
        }
        return emoji_map.get(status, '❓')

    @staticmethod
    def get_change_arrow(change: float) -> str:
        """
        获取变化方向箭头

        Args:
            change: 变化值

        Returns:
            箭头字符
        """
        if change > 0:
            return '↑'
        elif change < 0:
            return '↓'
        else:
            return '→'

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            格式化后的文件大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        格式化时长

        Args:
            seconds: 秒数

        Returns:
            格式化后的时长字符串
        """
        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}分钟"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"

    @staticmethod
    def format_member_label(member: str, status: str, change: Optional[float] = None) -> str:
        """
        格式化成员标签

        Args:
            member: 成员名称
            status: 状态
            change: 变化值(可选)

        Returns:
            格式化后的成员标签
        """
        emoji = DataFormatter.get_status_emoji(status)
        label = f"{member} {emoji}"

        if change is not None and change != 0:
            arrow = DataFormatter.get_change_arrow(change)
            label += f" {arrow}{abs(change):.1f}h"

        return label

    @staticmethod
    def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
        """
        截断文本

        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 后缀

        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def format_summary_stats(stats: dict) -> str:
        """
        格式化统计摘要

        Args:
            stats: 统计数据字典

        Returns:
            格式化后的摘要字符串
        """
        lines = []
        lines.append(f"总人数: {stats['total_members']}")
        lines.append(f"平均饱和度: {stats.get('avg_saturation', 0):.1f}%")
        lines.append(f"超负荷: {stats.get('overloaded', 0)}人")
        lines.append(f"正常: {stats.get('normal', 0)}人")
        lines.append(f"不饱和: {stats.get('under_saturated', 0)}人")
        lines.append(f"空闲: {stats.get('idle', 0)}人")

        return "\n".join(lines)
