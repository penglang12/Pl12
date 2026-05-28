"""任务队列 - 基于 APScheduler 的异步任务管理。"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from .config import config
from .logger import logger


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class TaskQueue:
    """异步任务队列，封装 APScheduler。"""

    def __init__(self) -> None:
        self._scheduler: Optional[BackgroundScheduler] = None
        self._registry: Dict[str, Callable] = {}

    def start(self) -> None:
        cfg = config()
        db_path = cfg.get("scheduler", "sqlite_path", default="./data/scheduler.db")
        jobstore = SQLAlchemyJobStore(url=f"sqlite:///{db_path}")

        self._scheduler = BackgroundScheduler(jobstores={"default": jobstore})
        self._scheduler.start()
        logger.info("任务队列已启动")

    def register(self, name: str, func: Callable) -> None:
        """注册可调用的任务函数。"""
        self._registry[name] = func
        logger.debug(f"任务已注册: {name}")

    def enqueue(
        self,
        task_type: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        run_date: Optional[datetime] = None,
    ) -> str:
        """将任务加入队列。"""
        if task_type not in self._registry:
            raise ValueError(f"未注册的任务类型: {task_type}")

        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        job_id = f"task_{task_id}"

        args = json.dumps(payload or {})

        if run_date:
            self._scheduler.add_job(
                self._registry[task_type],
                "date",
                run_date=run_date,
                args=[args],
                id=job_id,
                replace_existing=False,
            )
            logger.info(f"定时任务已添加: {task_id} @ {run_date}")
        else:
            self._scheduler.add_job(
                self._registry[task_type],
                "date",
                run_date=datetime.now(),
                args=[args],
                id=job_id,
            )
            logger.info(f"即时任务已添加: {task_id}")

        return task_id

    def schedule_cron(
        self,
        task_type: str,
        cron_expr: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """添加 cron 定时任务。"""
        if task_type not in self._registry:
            raise ValueError(f"未注册的任务类型: {task_type}")

        job_id = f"cron_{task_type}"
        args = json.dumps(payload or {})

        # cron_expr: "minute hour day month day_of_week"
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"cron 表达式需为 5 字段格式，收到: {cron_expr}")

        self._scheduler.add_job(
            self._registry[task_type],
            "cron",
            minute=parts[0],
            hour=parts[1],
            day=parts[2],
            month=parts[3],
            day_of_week=parts[4],
            args=[args],
            id=job_id,
            replace_existing=True,
            misfire_grace_time=300,
        )
        logger.info(f"Cron 任务已添加: {task_type} → '{cron_expr}'")
        return job_id

    def shutdown(self) -> None:
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("任务队列已关闭")


# 全局单例
queue = TaskQueue()
