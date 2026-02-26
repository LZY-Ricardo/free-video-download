"""
任务管理器
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class DownloadTask:
    """下载任务"""

    task_id: str
    url: str
    status: str = "pending"  # pending, downloading, completed, failed
    progress: float = 0.0
    speed: str = "0KB/s"
    eta: int = 0
    file_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class TaskManager:
    """任务管理器"""

    def __init__(self):
        self.tasks: Dict[str, DownloadTask] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}

    def create_task(self, url: str) -> str:
        """
        创建新任务

        Args:
            url: 视频 URL

        Returns:
            str: 任务 ID
        """
        task_id = str(uuid.uuid4())
        task = DownloadTask(task_id=task_id, url=url)
        self.tasks[task_id] = task
        return task_id

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """获取任务"""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs):
        """更新任务"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now()

    def delete_task(self, task_id: str):
        """删除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        to_remove = [
            task_id
            for task_id, task in self.tasks.items()
            if task.created_at < cutoff and task.status in ["completed", "failed"]
        ]

        for task_id in to_remove:
            self.delete_task(task_id)


# 全局实例
task_manager = TaskManager()
