"""AI Employee - 炼刀 AI 复刻
新媒体运营自动化系统入口。"""

import signal
import sys
from pathlib import Path


def main() -> None:
    """启动 AI Employee 系统。"""
    # 确保数据目录存在
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # 初始化配置
    from core.config import config

    cfg = config()
    print(f"  AI Employee v{cfg.get('app', 'version', default='0.1.0')}")
    print(f"  环境: {cfg.get('app', 'env', default='development')}")

    # 初始化日志
    from core.logger import setup_logging, logger

    setup_logging()

    # 连接数据库
    from core.db import db

    db.connect()

    # 启动调度器
    from core.scheduler import scheduler

    scheduler.start()

    logger.info("=" * 50)
    logger.info("AI Employee 系统已启动")
    logger.info("=" * 50)

    # 注册优雅退出
    def _shutdown(sig, frame):
        logger.info("收到停止信号，正在关闭...")
        scheduler.shutdown()
        db.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    print("\nAI Employee 已启动。按 Ctrl+C 停止。")
    signal.pause()


if __name__ == "__main__":
    main()
