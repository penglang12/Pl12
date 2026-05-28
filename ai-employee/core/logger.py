"""日志模块 - 基于 loguru 的日志配置。"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger as _base_logger

# 移除默认 handler
_base_logger.remove()


def setup_logging(
    level: Optional[str] = None,
    file_path: Optional[str] = None,
    max_size_mb: int = 50,
    backup_count: int = 7,
) -> None:
    """配置日志输出。"""
    from .config import config

    cfg = config()
    level = level or cfg.get("logging", "level", default="INFO")
    file_path = file_path or cfg.get("logging", "file", default="./data/logs/ai-employee.log")
    max_size_mb = max_size_mb or cfg.get("logging", "max_size_mb", default=50)
    backup_count = backup_count or cfg.get("logging", "backup_count", default=7)
    log_format = cfg.get(
        "logging",
        "format",
        default="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    # 控制台输出
    _base_logger.add(
        sys.stderr,
        level=level,
        format=log_format,
        colorize=True,
    )

    # 文件输出
    log_dir = Path(file_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    _base_logger.add(
        file_path,
        level=level,
        format=log_format,
        rotation=f"{max_size_mb} MB",
        retention=f"{backup_count} days",
        encoding="utf-8",
        enqueue=True,
    )


# 导出统一 logger
logger = _base_logger
