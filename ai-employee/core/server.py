"""常驻服务模式 - 后台守护进程，支持健康检查和自动恢复。"""

import signal
import sys
import time
from threading import Thread
from typing import Any, Dict, Optional


class HealthChecker:
    """定期检查各组件健康状态。"""

    def __init__(self, interval: int = 60):
        self.interval = interval
        self._running = False
        self._checks: Dict[str, Dict[str, Any]] = {}

    def start(self):
        self._running = True
        Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            self._run_checks()
            time.sleep(self.interval)

    def _run_checks(self):
        from .db import db
        from .logger import logger

        # DB 检查
        try:
            session = db.session
            session.execute(session.bind.dialect.statement_compiler(
                session.bind, None
            ).__class__.__module__)
            self._checks["database"] = {"status": "ok"}
        except Exception as e:
            self._checks["database"] = {"status": "error", "error": str(e)}
            logger.warning(f"健康检查 - 数据库异常: {e}")

        # 调度器检查
        from .scheduler import scheduler

        try:
            if scheduler._started:
                self._checks["scheduler"] = {"status": "ok"}
            else:
                self._checks["scheduler"] = {"status": "stopped"}
        except Exception as e:
            self._checks["scheduler"] = {"status": "error", "error": str(e)}

    def report(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "checks": self._checks,
            "timestamp": time.time(),
        }


class Server:
    """常驻服务管理器。"""

    def __init__(self):
        self._health = HealthChecker(interval=60)

    def start(self):
        from .config import config
        from .db import db
        from .logger import logger, setup_logging
        from .scheduler import scheduler

        setup_logging()
        cfg = config()

        print(f"  AI Employee v{cfg.get('app', 'version', default='0.1.0')}")
        print(f"  环境: {cfg.get('app', 'env', default='development')}")

        db.connect()
        scheduler.start()
        self._health.start()

        logger.info("=" * 50)
        logger.info("AI Employee 服务已启动 (常驻模式)")
        logger.info("=" * 50)

        def _shutdown(sig, frame):
            logger.info("收到停止信号，正在关闭...")
            scheduler.shutdown()
            self._health.stop()
            db.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        print("\nAI Employee 服务运行中。按 Ctrl+C 停止。")
        while True:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                _shutdown(None, None)


server = Server()
