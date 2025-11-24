#!/usr/bin/env python3
"""
文件存储管理模块

负责数据文件的上传、保存、读取和管理
支持历史记录追踪和文件版本控制
"""

import os
import json
import shutil
from datetime import datetime, date
from typing import List, Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class StorageManager:
    """文件存储管理器"""

    def __init__(self, base_dir: str = '/Users/admin/Desktop/Workload'):
        """
        初始化存储管理器

        Args:
            base_dir: 基础目录路径
        """
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, 'data', 'uploads')
        self.processed_dir = os.path.join(base_dir, 'data', 'processed')
        self.reports_dir = os.path.join(base_dir, 'data', 'reports')

        # 确保目录存在
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        # 历史记录文件
        self.history_file = os.path.join(base_dir, 'data', 'upload_history.json')

        logger.info(f"存储管理器初始化完成: {base_dir}")

    def save_uploaded_file(self, uploaded_file, custom_name: Optional[str] = None) -> str:
        """
        保存上传的文件

        Args:
            uploaded_file: Streamlit上传的文件对象
            custom_name: 自定义文件名(可选)

        Returns:
            保存后的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if custom_name:
            filename = f"{timestamp}_{custom_name}"
        else:
            filename = f"{timestamp}_{uploaded_file.name}"

        file_path = os.path.join(self.uploads_dir, filename)

        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        logger.info(f"文件已保存: {file_path}")

        # 更新历史记录
        self._add_to_history({
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'original_name': uploaded_file.name,
            'file_path': file_path,
            'size': uploaded_file.size
        })

        return file_path

    def save_processed_data(self, result_df: pd.DataFrame, date_info: Dict, stats: Dict, identifier: str) -> str:
        """
        保存处理后的数据

        Args:
            result_df: 分析结果DataFrame
            date_info: 日期信息字典
            stats: 统计信息字典
            identifier: 标识符(通常是日期)

        Returns:
            保存后的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{identifier}_analysis.json"
        file_path = os.path.join(self.processed_dir, filename)

        # 准备保存的数据
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'identifier': identifier
            },
            'date_info': {k: str(v) if isinstance(v, date) else v for k, v in date_info.items()},
            'stats': stats,
            'results': result_df.to_dict(orient='records')
        }

        # 保存为JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"处理后的数据已保存: {file_path}")

        return file_path

    def save_report(self, html_content: str, identifier: str) -> str:
        """
        保存HTML报告

        Args:
            html_content: HTML内容
            identifier: 标识符

        Returns:
            保存后的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{identifier}_report.html"
        file_path = os.path.join(self.reports_dir, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"报告已保存: {file_path}")

        return file_path

    def get_upload_history(self, limit: int = 10) -> List[Dict]:
        """
        获取上传历史记录

        Args:
            limit: 返回的记录数量限制

        Returns:
            历史记录列表
        """
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # 按时间倒序排序
            history.sort(key=lambda x: x['timestamp'], reverse=True)

            return history[:limit]
        except Exception as e:
            logger.error(f"读取历史记录失败: {e}")
            return []

    def get_processed_files(self, limit: int = 10) -> List[Dict]:
        """
        获取处理后的文件列表

        Args:
            limit: 返回的文件数量限制

        Returns:
            文件信息列表
        """
        files = []
        for filename in os.listdir(self.processed_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.processed_dir, filename)
                files.append({
                    'filename': filename,
                    'path': file_path,
                    'modified_time': os.path.getmtime(file_path)
                })

        # 按修改时间倒序排序
        files.sort(key=lambda x: x['modified_time'], reverse=True)

        return files[:limit]

    def load_processed_data(self, file_path: str) -> Dict:
        """
        加载处理后的数据

        Args:
            file_path: 文件路径

        Returns:
            数据字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"加载处理后的数据: {file_path}")
            return data
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            raise

    def delete_file(self, file_path: str) -> bool:
        """
        删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功删除
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"文件已删除: {file_path}")
                return True
            else:
                logger.warning(f"文件不存在: {file_path}")
                # 文件不存在也返回True,表示删除操作已达到目的
                return True
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False

    def remove_from_history(self, file_path: str) -> bool:
        """
        从历史记录中移除指定文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功移除
        """
        try:
            if not os.path.exists(self.history_file):
                return True

            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)

            # 过滤掉要删除的记录
            new_history = [h for h in history if h.get('file_path') != file_path]

            # 保存更新后的历史记录
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(new_history, f, ensure_ascii=False, indent=2)

            logger.info(f"已从历史记录中移除: {file_path}")
            return True
        except Exception as e:
            logger.error(f"从历史记录中移除失败: {e}")
            return False

    def clean_old_files(self, days: int = 90):
        """
        清理旧文件

        Args:
            days: 保留天数,超过此天数的文件将被删除
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        deleted_count = 0

        for directory in [self.uploads_dir, self.processed_dir, self.reports_dir]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    self.delete_file(file_path)
                    deleted_count += 1

        logger.info(f"清理完成: 删除了 {deleted_count} 个旧文件")

    def _add_to_history(self, record: Dict):
        """
        添加记录到历史文件

        Args:
            record: 记录字典
        """
        history = []
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []

        history.append(record)

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
