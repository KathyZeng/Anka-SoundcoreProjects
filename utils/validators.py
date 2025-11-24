#!/usr/bin/env python3
"""
数据验证工具模块

提供各种数据验证功能,确保输入数据的正确性
"""

import pandas as pd
from datetime import datetime
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""

    @staticmethod
    def validate_excel_structure(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        验证Excel数据结构

        Args:
            df: DataFrame对象

        Returns:
            (是否有效, 错误信息)
        """
        # 检查是否为空
        if df.empty:
            return False, "数据表为空"

        # 检查是否至少有2列(成员列 + 至少一个日期列)
        if len(df.columns) < 2:
            return False, "数据表列数不足,至少需要包含成员列和日期列"

        # 检查第一列是否为成员列
        first_col = df.columns[0]
        if df[first_col].isna().all():
            return False, "第一列(成员列)不能全部为空"

        # 检查是否有日期列
        date_cols = df.columns[1:]
        if len(date_cols) == 0:
            return False, "缺少日期列"

        # 验证日期列格式
        invalid_dates = []
        for col in date_cols:
            try:
                pd.to_datetime(col)
            except:
                invalid_dates.append(col)

        if invalid_dates:
            return False, f"日期列格式错误: {', '.join(invalid_dates)}"

        return True, None

    @staticmethod
    def validate_workload_data(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        验证工作负载数据

        Args:
            df: DataFrame对象

        Returns:
            (是否有效, 错误信息)
        """
        # 检查数值列
        numeric_cols = df.select_dtypes(include=['number']).columns

        # 检查是否有负数
        for col in numeric_cols:
            if (df[col] < 0).any():
                return False, f"列 '{col}' 包含负数,工时不能为负值"

        # 检查是否有异常大的值(单日工时超过24小时)
        for col in numeric_cols:
            if (df[col] > 24).any():
                max_val = df[col].max()
                return False, f"列 '{col}' 包含异常值({max_val}小时),单日工时不应超过24小时"

        return True, None

    @staticmethod
    def validate_date_range(df: pd.DataFrame, base_date: str) -> Tuple[bool, Optional[str]]:
        """
        验证日期范围

        Args:
            df: DataFrame对象
            base_date: 基准日期(YYYY-MM-DD格式)

        Returns:
            (是否有效, 错误信息)
        """
        try:
            base_dt = pd.to_datetime(base_date)
        except:
            return False, f"基准日期格式错误: {base_date}"

        # 获取所有日期列
        date_cols = df.columns[1:]

        try:
            dates = [pd.to_datetime(col) for col in date_cols]
        except Exception as e:
            return False, f"日期列解析失败: {str(e)}"

        # 检查日期是否在合理范围内(基准日期前后3个月)
        min_date = base_dt - pd.Timedelta(days=90)
        max_date = base_dt + pd.Timedelta(days=90)

        out_of_range = [d for d in dates if d < min_date or d > max_date]
        if out_of_range:
            return False, f"部分日期超出合理范围(基准日期±90天): {[d.strftime('%Y-%m-%d') for d in out_of_range]}"

        return True, None

    @staticmethod
    def validate_members(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        验证成员数据

        Args:
            df: DataFrame对象

        Returns:
            (是否有效, 错误信息)
        """
        member_col = df.columns[0]

        # 检查是否有空成员名
        if df[member_col].isna().any():
            return False, "存在空的成员名称"

        # 检查是否有重复的成员名
        duplicates = df[member_col][df[member_col].duplicated()].tolist()
        if duplicates:
            return False, f"存在重复的成员名称: {', '.join(map(str, duplicates))}"

        # 检查成员数量
        member_count = len(df)
        if member_count == 0:
            return False, "没有成员数据"

        if member_count > 1000:
            return False, f"成员数量过多({member_count}),可能存在数据错误"

        return True, None

    @staticmethod
    def validate_config(config: dict) -> Tuple[bool, Optional[str]]:
        """
        验证配置参数

        Args:
            config: 配置字典

        Returns:
            (是否有效, 错误信息)
        """
        # 检查必需字段
        required_fields = ['standard_hours_per_week', 'other_tasks', 'saturation_thresholds']
        for field in required_fields:
            if field not in config:
                return False, f"缺少必需配置项: {field}"

        # 验证标准工时
        standard_hours = config.get('standard_hours_per_week', 0)
        if not isinstance(standard_hours, (int, float)) or standard_hours <= 0:
            return False, "标准工时必须为正数"

        if standard_hours > 168:
            return False, "标准工时不能超过168小时(一周总时长)"

        # 验证饱和度阈值
        thresholds = config.get('saturation_thresholds', {})
        required_threshold_keys = ['under_saturated_max', 'normal_min', 'normal_max', 'over_saturated_min']

        for key in required_threshold_keys:
            if key not in thresholds:
                return False, f"缺少饱和度阈值配置: {key}"

            value = thresholds[key]
            if not isinstance(value, (int, float)) or value < 0:
                return False, f"饱和度阈值 '{key}' 必须为非负数"

        # 验证阈值逻辑
        if not (thresholds['under_saturated_max'] <= thresholds['normal_min'] <=
                thresholds['normal_max'] <= thresholds['over_saturated_min']):
            return False, "饱和度阈值逻辑错误: under_saturated_max ≤ normal_min ≤ normal_max ≤ over_saturated_min"

        return True, None

    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> dict:
        """
        生成数据质量报告

        Args:
            df: DataFrame对象

        Returns:
            数据质量报告字典
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'member_count': len(df),
            'date_columns': len(df.columns) - 1,
            'missing_values': {},
            'zero_hours_count': 0,
            'high_hours_count': 0,
            'data_completeness': 0.0
        }

        # 检查缺失值
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                report['missing_values'][col] = missing

        # 检查数值列
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            # 统计零值数量
            report['zero_hours_count'] = (df[numeric_cols] == 0).sum().sum()

            # 统计高工时数量(>16小时/天)
            report['high_hours_count'] = (df[numeric_cols] > 16).sum().sum()

            # 计算数据完整度
            total_cells = len(df) * len(numeric_cols)
            non_zero_cells = (df[numeric_cols] != 0).sum().sum()
            report['data_completeness'] = (non_zero_cells / total_cells) * 100 if total_cells > 0 else 0

        return report
