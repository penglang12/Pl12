"""微信视频号适配器 - 浏览器自动化登录/发布/互动。"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.browser import browser
from core.config import config
from core.logger import logger


class WeChatVideoAdapter:
    """微信视频号平台适配器。

    功能：
    - Cookie 登录态管理
    - 视频号助手网页登录
    - 内容发布（短视频/图文）
    - 评论查看与回复
    - 数据采集
    """

    # 视频号助手 URL
    CHS_URL = "https://channels.weixin.qq.com/platform"
    PUBLISH_URL = "https://channels.weixin.qq.com/platform/publish/create"
    POST_LIST_URL = "https://channels.weixin.qq.com/platform/post/list"

    def __init__(self) -> None:
        cfg = config()
        self.cookie_file = cfg.get(
            "wechat_video", "account_file", default="./data/accounts/wechat.json"
        )
        self.login_wait = cfg.get("wechat_video", "login_wait_seconds", default=120)

    # ── 登录 ──────────────────────────────────────────────

    def is_logged_in(self) -> bool:
        """检查是否已有有效登录态。"""
        if os.path.exists(self.cookie_file):
            return browser.load_cookies(self.cookie_file)
        return False

    def login(self) -> bool:
        """微信扫码登录视频号助手。

        流程：
        1. 打开视频号助手
        2. 等待用户扫码（最长 self.login_wait 秒）
        3. 检测登录成功
        4. 保存 Cookie
        """
        page = browser.page

        logger.info("正在打开视频号助手...")
        page.goto(self.CHS_URL, wait_until="networkidle")

        # 尝试加载已有 Cookie
        if self.is_logged_in():
            page.goto(self.CHS_URL, wait_until="networkidle")
            if self._check_login_success(page):
                logger.info("Cookie 登录成功")
                return True
            logger.info("Cookie 已过期，需要重新登录")

        # 等待扫码
        logger.info(f"请使用微信扫描二维码登录（等待 {self.login_wait} 秒）...")
        browser.screenshot("wechat_login")

        for i in range(self.login_wait):
            time.sleep(1)
            if self._check_login_success(page):
                browser.save_cookies(self.cookie_file)
                logger.info("微信登录成功！")
                return True
            if i % 10 == 9:
                logger.info(f"等待登录中... ({i+1}/{self.login_wait})")

        logger.error(f"登录超时（{self.login_wait} 秒）")
        return False

    def _check_login_success(self, page) -> bool:
        """检查是否已登录成功。"""
        try:
            # 视频号助手登录后的页面包含特定元素
            return page.locator(".post-list-page, .publish-entry").count() > 0
        except Exception:
            return False

    # ── 发布内容 ──────────────────────────────────────────

    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """发布短视频。

        Args:
            video_path: 本地视频文件路径
            title: 视频标题
            description: 视频简介
            hashtags: 标签列表

        Returns:
            包含发布结果的 dict
        """
        if not self.is_logged_in():
            raise RuntimeError("未登录，请先调用 login()")

        page = browser.page
        logger.info(f"开始发布视频: {title}")

        try:
            page.goto(self.PUBLISH_URL, wait_until="networkidle")
            time.sleep(2)

            # 上传视频文件
            file_input = page.locator('input[type="file"]')
            if file_input.count() == 0:
                # 可能在上传区域中
                file_input = page.locator(".upload-area input[type='file']")

            if file_input.count() > 0:
                file_input.set_input_files(video_path)
                logger.info("视频文件已上传")
                # 等待上传处理
                time.sleep(5)
            else:
                raise RuntimeError("未找到视频上传控件")

            # 填写标题
            title_input = page.locator(
                'input[placeholder*="标题"], .title-input'
            ).first
            if title_input.count() > 0:
                title_input.fill(title)

            # 填写简介
            desc_input = page.locator(
                'textarea[placeholder*="简介"], .desc-input'
            ).first
            if desc_input.count() > 0:
                desc_input.fill(description)

            # 添加标签
            if hashtags:
                tag_input = page.locator(
                    'input[placeholder*="标签"], .tag-input'
                ).first
                for tag in hashtags:
                    if tag_input.count() > 0:
                        tag_input.fill(tag)
                        time.sleep(0.5)
                        # 回车添加
                        tag_input.press("Enter")
                        time.sleep(0.3)

            browser.screenshot("publish_ready")

            # 点击发布（根据配置决定是否自动发布）
            auto_publish = config().get("content_strategy", "auto_publish", default=False)
            if auto_publish:
                publish_btn = page.locator('button:has-text("发布"), .publish-btn').first
                if publish_btn.count() > 0:
                    publish_btn.click()
                    time.sleep(3)
                    logger.info("视频已发布")
                    return {"status": "published", "title": title}
                else:
                    logger.warning("未找到发布按钮")
                    return {"status": "pending_manual", "title": title}
            else:
                logger.info("自动发布已禁用，留在草稿状态")
                return {"status": "draft", "title": title}

        except Exception as e:
            logger.error(f"发布失败: {e}")
            browser.screenshot("publish_error")
            return {"status": "error", "error": str(e)}

    def publish_post(self, title: str, body: str, images: List[str]) -> Dict[str, Any]:
        """发布图文笔记（预留）。"""
        # TODO: 视频号图文发布流程
        logger.info("图文发布功能待实现")
        return {"status": "not_implemented"}

    # ── 互动管理 ──────────────────────────────────────────

    def get_comments(self, post_id: str, limit: int = 20) -> List[Dict]:
        """获取指定作品的评论列表（预留）。"""
        # TODO: 评论采集
        logger.info(f"评论采集功能待实现: post_id={post_id}")
        return []

    def reply_comment(self, comment_id: str, reply_text: str) -> bool:
        """回复评论（预留）。"""
        # TODO: 评论回复
        logger.info(f"评论回复功能待实现: comment_id={comment_id}")
        return False

    # ── 数据采集 ──────────────────────────────────────────

    def get_post_list(self, page_num: int = 1) -> List[Dict]:
        """获取已发布作品列表（预留）。"""
        # TODO: 作品列表采集
        logger.info(f"作品列表采集功能待实现: page={page_num}")
        return []

    def get_performance(self, post_id: str) -> Dict:
        """获取单个作品表现数据（预留）。"""
        # TODO: 表现数据采集
        logger.info(f"表现数据采集功能待实现: post_id={post_id}")
        return {}
