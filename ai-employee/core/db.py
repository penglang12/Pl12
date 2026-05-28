"""数据库管理 - SQLAlchemy 引擎与会话工厂。"""

from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .logger import logger
from .models import Base


class Database:
    """数据库连接管理器。"""

    def __init__(self, db_url: Optional[str] = None) -> None:
        self._engine = None
        self._session_factory = None
        self._db_url = db_url

    def connect(self, db_url: Optional[str] = None) -> None:
        """建立数据库连接。"""
        from .config import config

        cfg = config()
        url = db_url or self._db_url or cfg.get("database", "sqlite_path")
        echo = cfg.get("database", "echo_sql", default=False)

        if url and url.endswith(".db"):
            # 文件路径 → sqlite:/// 格式
            Path(url).parent.mkdir(parents=True, exist_ok=True)
            url = f"sqlite:///{url}"
        elif url and url.startswith("sqlite"):
            # 已经是完整 URL
            pass
        else:
            url = "sqlite:///./data/ai_employee.db"

        self._engine = create_engine(url, echo=echo, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine)

        # 自动建表
        Base.metadata.create_all(self._engine)
        logger.info(f"数据库已连接: {url}")

    @property
    def session(self) -> Session:
        if self._session_factory is None:
            self.connect()
        return self._session_factory()

    def close(self) -> None:
        if self._engine:
            self._engine.dispose()
            logger.info("数据库连接已关闭")


# 全局单例
db = Database()
