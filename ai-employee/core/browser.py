"""浏览器管理器 - 封装 Playwright，管理 Cookie 和登录态。"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import config
from .logger import logger


class BrowserManager:
    """Playwright 浏览器实例管理。

    提供统一的浏览器启动/关闭、Cookie 持久化、登录态管理。
    """

    def __init__(self) -> None:
        self._browser = None
        self._context = None
        self._page = None
        self._headless: bool = False
        self._user_data_dir: Optional[str] = None

    def start(self) -> None:
        """启动浏览器实例。"""
        cfg = config()
        self._headless = cfg.get("browser", "headless", default=False)
        self._user_data_dir = cfg.get(
            "browser", "user_data_dir", default="./data/browser-profiles"
        )
        viewport = cfg.get("browser", "viewport", default={"width": 1280, "height": 720})
        timeout = cfg.get("browser", "timeout", default=30000)
        launch_args = cfg.get("browser", "launch_args", default=[])

        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()

        browser_type = self._playwright.chromium
        self._browser = browser_type.launch(
            headless=self._headless,
            args=launch_args,
        )

        self._context = self._browser.new_context(
            viewport=viewport,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
        )

        if timeout:
            self._context.set_default_timeout(timeout)

        self._page = self._context.new_page()
        logger.info(
            f"浏览器已启动 (headless={self._headless}, "
            f"viewport={viewport['width']}x{viewport['height']})"
        )

    @property
    def page(self):
        if self._page is None:
            self.start()
        return self._page

    def save_cookies(self, file_path: str) -> None:
        """保存 Cookie 到文件。"""
        if not self._context:
            return
        cookies = self._context.cookies()
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        logger.info(f"Cookie 已保存到 {file_path}")

    def load_cookies(self, file_path: str) -> bool:
        """从文件加载 Cookie。"""
        if not self._context or not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            self._context.add_cookies(cookies)
            logger.info(f"Cookie 已加载: {len(cookies)} 条")
            return True
        except Exception as e:
            logger.warning(f"Cookie 加载失败: {e}")
            return False

    def screenshot(self, name: str) -> None:
        """保存截图用于调试。"""
        if self._page:
            path = f"./data/screenshots/{name}.png"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self._page.screenshot(path=path)
            logger.info(f"截图已保存: {path}")

    def close(self) -> None:
        """关闭浏览器并清理。"""
        if self._context:
            self._context.close()
        if self._browser:
            self._browser.close()
        if hasattr(self, "_playwright"):
            self._playwright.stop()
        self._page = None
        self._context = None
        self._browser = None
        logger.info("浏览器已关闭")


# 全局单例
browser = BrowserManager()
