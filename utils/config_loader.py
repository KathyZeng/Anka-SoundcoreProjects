#!/usr/bin/env python3
"""
配置加载工具

提供统一的配置加载和初始化功能
"""

import os
import yaml
import streamlit as st


def init_session_config():
    """
    初始化 session_state 中的配置

    这个函数应该在每个页面的开头调用，确保配置已加载
    """
    if 'config' not in st.session_state:
        # 查找config.yaml路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_path = os.path.join(project_root, 'config.yaml')

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                st.session_state.config = yaml.safe_load(f)
        else:
            # 默认配置
            st.session_state.config = get_default_config()

    return st.session_state.config


def get_default_config():
    """
    获取默认配置

    Returns:
        默认配置字典
    """
    return {
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


def load_config_file(config_path=None):
    """
    直接从文件加载配置（不使用session_state）

    Args:
        config_path: 配置文件路径，None则自动查找

    Returns:
        配置字典
    """
    if config_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        config_path = os.path.join(project_root, 'config.yaml')

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        return get_default_config()
