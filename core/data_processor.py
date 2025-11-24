#!/usr/bin/env python3
"""
数据处理模块

负责Excel数据的读取、清洗、计算和分析
重构自 workload_analysis.py,增加了更好的模块化和扩展性
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkloadDataProcessor:
    """工作负载数据处理器"""

    def __init__(self, config: Dict):
        """
        初始化数据处理器

        Args:
            config: 配置字典,包含标准工时、阈值等参数
        """
        self.config = config
        self.standard_hours = config.get('standard_hours_per_week', 40)
        self.other_tasks_enabled = config.get('other_tasks', {}).get('enabled', True)
        self.other_tasks_minutes = config.get('other_tasks', {}).get('weekly_minutes_per_person', 92)
        self.other_tasks_hours = self.other_tasks_minutes / 60 if self.other_tasks_enabled else 0

        # 主责事务配置
        self.primary_responsibility_enabled = config.get('primary_responsibility', {}).get('enabled', True)
        self.primary_responsibility_percentage = config.get('primary_responsibility', {}).get('weekly_percentage', 0.5)
        # 主责工时 = 标准工时 × 百分比 (例如: 40 × 0.5 = 20小时)
        self.primary_responsibility_hours = self.standard_hours * self.primary_responsibility_percentage if self.primary_responsibility_enabled else 0

        # 饱和度阈值
        thresholds = config.get('saturation_thresholds', {})
        self.under_saturated_max = thresholds.get('under_saturated_max', 90)
        self.normal_max = thresholds.get('normal_max', 110)

        logger.info(f"数据处理器初始化完成: 标准工时={self.standard_hours}h/周, 其他事务={self.other_tasks_hours:.2f}h/周, 主责事务={self.primary_responsibility_hours:.2f}h/周")

    def read_excel(self, file_path: str, sheet_name: str = '预估工时') -> pd.DataFrame:
        """
        读取Excel文件

        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称,默认为"预估工时"

        Returns:
            DataFrame: 原始数据
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"成功读取Excel文件: {file_path}, Sheet: {sheet_name}, 行数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise

    def get_week_range(self, base_date: datetime.date, weeks_offset: int = 0) -> Tuple[datetime.date, datetime.date]:
        """
        获取指定周的日期范围(周一到周日)

        Args:
            base_date: 基准日期
            weeks_offset: 周偏移量,0=本周,1=下周,2=下下周

        Returns:
            (start_date, end_date): 周一和周日的日期
        """
        # 找到base_date所在周的周一
        current_monday = base_date - timedelta(days=base_date.weekday())

        # 计算目标周的周一
        target_monday = current_monday + timedelta(weeks=weeks_offset)

        # 周日是周一+6天
        target_sunday = target_monday + timedelta(days=6)

        return target_monday, target_sunday

    def get_status(self, saturation: float) -> str:
        """
        根据饱和度返回状态

        Args:
            saturation: 饱和度百分比

        Returns:
            状态字符串: 空闲/不饱和/正常/超负荷
        """
        if saturation == 0:
            return '空闲'
        elif saturation < self.under_saturated_max:
            return '不饱和'
        elif saturation <= self.normal_max:
            return '正常'
        else:
            return '超负荷'

    def calculate_workload(
        self,
        df: pd.DataFrame,
        base_date: Optional[str] = None,
        primary_members: Optional[list] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        计算工作负载饱和度

        Args:
            df: 原始数据DataFrame
            base_date: 基准日期字符串(YYYY-MM-DD),None则使用当天
            primary_members: 主责成员列表,这些成员会额外计算主责事务工时

        Returns:
            (result_df, date_info): 分析结果DataFrame和日期信息字典
        """
        # 如果未指定主责成员列表,设为空列表
        if primary_members is None:
            primary_members = []
        # 确定基准日期
        if base_date is None or base_date == '':
            today = datetime.now().date()
        else:
            today = datetime.strptime(base_date, '%Y-%m-%d').date()

        logger.info(f"基准日期: {today}")

        # 获取三周的日期范围
        current_week_start, current_week_end = self.get_week_range(today, 0)
        next_week_start, next_week_end = self.get_week_range(today, 1)
        next_next_week_start, next_next_week_end = self.get_week_range(today, 2)

        logger.info(f"本周: {current_week_start} 至 {current_week_end}")
        logger.info(f"下周: {next_week_start} 至 {next_week_end}")
        logger.info(f"下下周: {next_next_week_start} 至 {next_next_week_end}")

        # 提取日期列
        date_columns = df.columns[1:]
        date_columns_parsed = []
        for col in date_columns:
            try:
                date_columns_parsed.append(datetime.strptime(col, '%Y-%m-%d').date())
            except:
                date_columns_parsed.append(None)

        # 筛选三周的列
        current_week_cols = [
            df.columns[i+1] for i, date in enumerate(date_columns_parsed)
            if date and current_week_start <= date <= current_week_end
        ]

        next_week_cols = [
            df.columns[i+1] for i, date in enumerate(date_columns_parsed)
            if date and next_week_start <= date <= next_week_end
        ]

        next_next_week_cols = [
            df.columns[i+1] for i, date in enumerate(date_columns_parsed)
            if date and next_next_week_start <= date <= next_next_week_end
        ]

        logger.info(f"本周工作日数: {len(current_week_cols)}, 下周: {len(next_week_cols)}, 下下周: {len(next_next_week_cols)}")

        # 计算每个成员的工时统计
        results = []

        for _, row in df.iterrows():
            member_name = row['成员']

            # 判断是否为主责成员
            is_primary = member_name in primary_members
            primary_hours = self.primary_responsibility_hours if is_primary else 0

            # 计算本周工时
            current_week_project_hours = row[current_week_cols].sum() if current_week_cols else 0
            current_week_other_tasks = self.other_tasks_hours + primary_hours
            current_week_total_hours = current_week_project_hours + current_week_other_tasks
            current_week_saturation = (current_week_total_hours / self.standard_hours) * 100 if self.standard_hours > 0 else 0

            # 计算下周工时
            next_week_project_hours = row[next_week_cols].sum() if next_week_cols else 0
            next_week_other_tasks = self.other_tasks_hours + primary_hours
            next_week_total_hours = next_week_project_hours + next_week_other_tasks
            next_week_saturation = (next_week_total_hours / self.standard_hours) * 100 if self.standard_hours > 0 else 0

            # 计算下下周工时
            next_next_week_project_hours = row[next_next_week_cols].sum() if next_next_week_cols else 0
            next_next_week_other_tasks = self.other_tasks_hours + primary_hours
            next_next_week_total_hours = next_next_week_project_hours + next_next_week_other_tasks
            next_next_week_saturation = (next_next_week_total_hours / self.standard_hours) * 100 if self.standard_hours > 0 else 0

            # 计算变化率
            if current_week_total_hours > 0:
                next_week_change = next_week_total_hours - current_week_total_hours
                next_week_change_rate = (next_week_change / current_week_total_hours) * 100
            else:
                next_week_change = next_week_total_hours
                next_week_change_rate = 0 if next_week_total_hours == 0 else float('inf')

            if next_week_total_hours > 0:
                next_next_week_change = next_next_week_total_hours - next_week_total_hours
                next_next_week_change_rate = (next_next_week_change / next_week_total_hours) * 100
            else:
                next_next_week_change = next_next_week_total_hours
                next_next_week_change_rate = 0 if next_next_week_total_hours == 0 else float('inf')

            results.append({
                '成员': member_name,
                '是否主责': '是' if is_primary else '否',
                '本周项目工时': current_week_project_hours,
                '本周其他事务': current_week_other_tasks,
                '本周总工时': current_week_total_hours,
                '本周饱和度(%)': round(current_week_saturation, 1),
                '本周状态': self.get_status(current_week_saturation),
                '下周项目工时': next_week_project_hours,
                '下周其他事务': next_week_other_tasks,
                '下周总工时': next_week_total_hours,
                '下周饱和度(%)': round(next_week_saturation, 1),
                '下周状态': self.get_status(next_week_saturation),
                '下周变化': round(next_week_change, 1),
                '下周变化率(%)': round(next_week_change_rate, 1) if next_week_change_rate != float('inf') else 0,
                '下下周项目工时': next_next_week_project_hours,
                '下下周其他事务': next_next_week_other_tasks,
                '下下周总工时': next_next_week_total_hours,
                '下下周饱和度(%)': round(next_next_week_saturation, 1),
                '下下周状态': self.get_status(next_next_week_saturation),
                '下下周变化': round(next_next_week_change, 1),
                '下下周变化率(%)': round(next_next_week_change_rate, 1) if next_next_week_change_rate != float('inf') else 0
            })

        # 创建结果DataFrame
        result_df = pd.DataFrame(results)

        # 按下周饱和度降序排序
        result_df = result_df.sort_values('下周饱和度(%)', ascending=False)

        # 日期信息
        date_info = {
            'base_date': today,
            'current_week_start': current_week_start,
            'current_week_end': current_week_end,
            'next_week_start': next_week_start,
            'next_week_end': next_week_end,
            'next_next_week_start': next_next_week_start,
            'next_next_week_end': next_next_week_end,
            'current_week_days': len(current_week_cols),
            'next_week_days': len(next_week_cols),
            'next_next_week_days': len(next_next_week_cols)
        }

        logger.info(f"分析完成: 共{len(result_df)}名成员")

        return result_df, date_info

    def get_summary_stats(self, result_df: pd.DataFrame) -> Dict:
        """
        获取统计摘要

        Args:
            result_df: 分析结果DataFrame

        Returns:
            统计信息字典
        """
        stats = {
            'total_members': len(result_df),
            'current_week': {
                'avg_saturation': round(result_df['本周饱和度(%)'].mean(), 1),
                'idle': len(result_df[result_df['本周状态'] == '空闲']),
                'under_saturated': len(result_df[result_df['本周状态'] == '不饱和']),
                'normal': len(result_df[result_df['本周状态'] == '正常']),
                'overloaded': len(result_df[result_df['本周状态'] == '超负荷'])
            },
            'next_week': {
                'avg_saturation': round(result_df['下周饱和度(%)'].mean(), 1),
                'idle': len(result_df[result_df['下周状态'] == '空闲']),
                'under_saturated': len(result_df[result_df['下周状态'] == '不饱和']),
                'normal': len(result_df[result_df['下周状态'] == '正常']),
                'overloaded': len(result_df[result_df['下周状态'] == '超负荷'])
            },
            'next_next_week': {
                'avg_saturation': round(result_df['下下周饱和度(%)'].mean(), 1),
                'idle': len(result_df[result_df['下下周状态'] == '空闲']),
                'under_saturated': len(result_df[result_df['下下周状态'] == '不饱和']),
                'normal': len(result_df[result_df['下下周状态'] == '正常']),
                'overloaded': len(result_df[result_df['下下周状态'] == '超负荷'])
            }
        }

        return stats
