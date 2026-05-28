"""微信视频号适配器 - 浏览器自动化登录/发布/互动/数据采集。

所有方法通过 Playwright 操作视频号助手网页 (channels.weixin.qq.com/platform) 实现。
"""

import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.browser import browser
from core.config import config
from core.errors import NotFoundError
from core.logger import logger


class WeChatVideoAdapter:
    """微信视频号平台适配器。"""

    BASE_URL = "https://channels.weixin.qq.com/platform"
    POST_LIST_URL = f"{BASE_URL}/post/list"
    PUBLISH_URL = f"{BASE_URL}/publish/create"
    COMMENT_URL = f"{BASE_URL}/post/comment"

    def __init__(self) -> None:
        cfg = config()
        self.cookie_file = cfg.get(
            "wechat_video", "account_file", default="./data/accounts/wechat.json"
        )
        self.login_wait = cfg.get("wechat_video", "login_wait_seconds", default=120)
        self.publish_interval = cfg.get(
            "wechat_video", "publish_interval_minutes", default=30
        )

    # ── 登录 ──────────────────────────────────────────────

    def is_logged_in(self) -> bool:
        if os.path.exists(self.cookie_file):
            return browser.load_cookies(self.cookie_file)
        return False

    def login(self) -> bool:
        page = browser.page
        logger.info("打开视频号助手...")
        page.goto(self.BASE_URL, wait_until="networkidle")

        if self.is_logged_in():
            page.goto(self.BASE_URL, wait_until="networkidle")
            if page.locator(".post-list-page, .publish-entry, .nav-container").count() > 0:
                logger.info("Cookie 登录成功")
                return True
            logger.info("Cookie 过期，需要重新扫码")

        logger.info(f"请用微信扫码登录（等待 {self.login_wait} 秒）...")
        browser.screenshot("login_qrcode")

        for i in range(self.login_wait):
            time.sleep(1)
            try:
                if page.locator(".post-list-page, .publish-entry, .nav-container").count() > 0:
                    browser.save_cookies(self.cookie_file)
                    logger.info("微信登录成功")
                    return True
            except Exception:
                pass
            if i % 15 == 14:
                logger.info(f"等待中... ({i+1}/{self.login_wait})")

        logger.error(f"登录超时 ({self.login_wait}s)")
        return False

    # ── 发布 ──────────────────────────────────────────────

    def publish_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not self.is_logged_in():
            raise RuntimeError("未登录，请先 login()")

        page = browser.page
        page.goto(self.PUBLISH_URL, wait_until="networkidle")
        time.sleep(3)

        try:
            # 上传视频
            file_input = page.locator("input[type=file]").first
            if file_input.count() == 0:
                file_input = page.locator(".upload-area input[type=file], .upload-box input[type=file]").first
            if file_input.count() > 0:
                file_input.set_input_files(video_path)
                logger.info("视频上传中...")
                time.sleep(5)
                # 等待上传完成（上传进度条消失）
                try:
                    page.wait_for_selector(".upload-progress", state="hidden", timeout=120000)
                except Exception:
                    logger.warning("上传进度监控超时，继续下一步")
                logger.info("视频上传完成")
            else:
                raise RuntimeError("未找到上传控件")

            # 填写标题
            title_sel = page.locator(
                ".title-input input, input[placeholder*='标题'], input[placeholder*='视频']"
            ).first
            if title_sel.count() > 0:
                title_sel.fill(title)

            # 填写简介
            desc_sel = page.locator(
                "textarea[placeholder*='简介'], .desc-input textarea"
            ).first
            if desc_sel.count() > 0:
                desc_sel.fill(description)

            # 添加标签
            if hashtags:
                tag_sel = page.locator("input[placeholder*='标签'], .tag-input input").first
                for tag in hashtags:
                    if tag_sel.count() > 0:
                        tag_sel.fill(tag)
                        time.sleep(0.3)
                        tag_sel.press("Enter")
                        time.sleep(0.3)

            browser.screenshot("publish_ready")
            auto = config().get("content_strategy", "auto_publish", default=False)

            if auto:
                btn = page.locator("button:has-text('发布'), .publish-btn, button:has-text('发表')").first
                if btn.count() > 0:
                    btn.click()
                    time.sleep(3)
                    logger.info(f"视频已发布: {title}")
                    return {"status": "published", "title": title}
                return {"status": "error", "error": "未找到发布按钮"}
            else:
                return {"status": "draft", "title": title}

        except Exception as e:
            logger.error(f"发布失败: {e}")
            browser.screenshot("publish_error")
            return {"status": "error", "error": str(e)}

    def publish_post(self, title: str, body: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布图文笔记。"""
        if not self.is_logged_in():
            raise RuntimeError("未登录")

        page = browser.page
        page.goto(self.PUBLISH_URL, wait_until="networkidle")
        time.sleep(2)

        try:
            # 切换到图文模式（视频号助手支持纯图文）
            img_tab = page.locator("text=图文, .image-mode-tab, [data-type='image']").first
            if img_tab.count() > 0:
                img_tab.click()
                time.sleep(1)

            # 上传图片
            file_input = page.locator("input[type=file]").first
            if image_paths and file_input.count() > 0:
                file_input.set_input_files(image_paths)
                logger.info(f"上传 {len(image_paths)} 张图片...")
                time.sleep(3)

            # 填写正文
            text_area = page.locator(
                "textarea[placeholder*='正文'], .content-editor, [contenteditable]"
            ).first
            if text_area.count() > 0:
                text_area.fill(body)

            # 填写标题
            title_input = page.locator(
                "input[placeholder*='标题']"
            ).first
            if title_input.count() > 0:
                title_input.fill(title)

            browser.screenshot("post_ready")
            auto = config().get("content_strategy", "auto_publish", default=False)
            if auto:
                btn = page.locator("button:has-text('发布'), button:has-text('发表')").first
                if btn.count() > 0:
                    btn.click()
                    time.sleep(3)
                    return {"status": "published", "title": title}

            return {"status": "draft", "title": title}

        except Exception as e:
            logger.error(f"图文发布失败: {e}")
            browser.screenshot("post_error")
            return {"status": "error", "error": str(e)}

    # ── 作品管理 ──────────────────────────────────────────

    def get_post_list(self, page_num: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """获取已发布作品列表。"""
        if not self.is_logged_in():
            raise RuntimeError("未登录")

        page = browser.page
        page.goto(f"{self.POST_LIST_URL}?page={page_num}", wait_until="networkidle")
        time.sleep(3)

        posts = []
        try:
            # 尝试多种选择器匹配作品列表
            rows = page.locator(
                ".post-row, .post-item, .post-card, table tbody tr, .list-item"
            ).all()
            for row in rows:
                try:
                    title_el = row.locator(
                        ".post-title a, .title-cell, .post-name, td:nth-child(2)"
                    ).first
                    title = title_el.text_content() or ""

                    status_el = row.locator(
                        ".post-status, .status-cell, td:nth-child(3)"
                    ).first
                    status = status_el.text_content() or ""

                    date_el = row.locator(
                        ".post-date, .date-cell, td:nth-child(4)"
                    ).first
                    date = date_el.text_content() or ""

                    link = ""
                    link_el = title_el.locator("a").first
                    if link_el.count() > 0:
                        link = link_el.get_attribute("href") or ""

                    posts.append({
                        "title": title.strip(),
                        "status": status.strip(),
                        "date": date.strip(),
                        "link": link,
                    })
                except Exception:
                    continue

            return posts

        except Exception as e:
            logger.error(f"获取作品列表失败: {e}")
            return posts

    def get_performance(self, post_id: str) -> Dict[str, Any]:
        """获取单个作品的表现数据。"""
        if not self.is_logged_in():
            raise RuntimeError("未登录")

        page = browser.page
        page.goto(f"{self.POST_LIST_URL}?id={post_id}", wait_until="networkidle")
        time.sleep(3)

        data = {"views": 0, "likes": 0, "comments": 0, "shares": 0, "collected_at": datetime.now().isoformat()}
        try:
            stats = page.locator(
                ".stat-item, .performance-item, .data-item, .stats span"
            ).all()
            for stat in stats:
                text = stat.text_content() or ""
                # 匹配 "阅读 1234"、"点赞 56" 等格式
                m = re.search(r"(阅读|播放|点赞|评论|分享|转发)\s*(\d+)", text)
                if m:
                    key = {"阅读": "views", "播放": "views", "点赞": "likes",
                           "评论": "comments", "分享": "shares", "转发": "shares"}.get(m.group(1), "")
                    if key:
                        data[key] = int(m.group(2))

        except Exception as e:
            logger.warning(f"表现数据解析失败: {e}")

        return data

    # ── 评论管理 ──────────────────────────────────────────

    def get_comments(self, post_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取作品评论列表。"""
        if not self.is_logged_in():
            raise RuntimeError("未登录")

        page = browser.page
        page.goto(f"{self.COMMENT_URL}?id={post_id}", wait_until="networkidle")
        time.sleep(3)

        comments = []
        try:
            items = page.locator(
                ".comment-item, .comment-row, .reply-item"
            ).all()
            for item in items[:limit]:
                try:
                    user = item.locator(
                        ".comment-user, .user-name, .commenter"
                    ).first.text_content() or ""

                    text = item.locator(
                        ".comment-text, .comment-content, .content-text"
                    ).first.text_content() or ""

                    time_el = item.locator(
                        ".comment-time, .time, .create-time"
                    ).first.text_content() or ""

                    like_el = item.locator(
                        ".comment-like-count, .like-count"
                    ).first
                    likes = int(re.search(r"\d+", like_el.text_content() or "0").group()) \
                        if like_el.count() > 0 else 0

                    comments.append({
                        "user": user.strip(),
                        "content": text.strip(),
                        "time": time_el.strip(),
                        "likes": likes,
                    })
                except Exception:
                    continue

        except Exception as e:
            logger.error(f"获取评论失败: {e}")

        return comments

    def reply_comment(self, comment_id: str, reply_text: str) -> bool:
        """回复评论。"""
        if not self.is_logged_in():
            raise RuntimeError("未登录")

        page = browser.page
        try:
            reply_btn = page.locator(
                f"[data-comment-id='{comment_id}'] .reply-btn, "
                f"text=回复 >> nth=0"
            ).first
            if reply_btn.count() > 0:
                reply_btn.click()
                time.sleep(1)
            else:
                logger.warning(f"未找到回复按钮: comment={comment_id}")
                return False

            textarea = page.locator(
                ".reply-textarea textarea, .comment-reply-input, textarea:visible"
            ).first
            if textarea.count() > 0:
                textarea.fill(reply_text)
                time.sleep(0.5)

            submit = page.locator(
                "button:has-text('发送'), .submit-reply, button:has-text('回复')"
            ).first
            if submit.count() > 0:
                submit.click()
                time.sleep(1)
                logger.info(f"评论回复成功: {reply_text[:30]}...")
                return True

        except Exception as e:
            logger.error(f"回复评论失败: {e}")

        return False

    # ── 批量采集 ──────────────────────────────────────────

    def collect_all_posts_performance(self) -> List[Dict[str, Any]]:
        """采集所有已发布作品的表现数据。"""
        posts = self.get_post_list(page_num=1, page_size=100)
        results = []
        for post in posts:
            try:
                perf = self.get_performance(post.get("link", ""))
                results.append({**post, **perf})
            except Exception as e:
                logger.warning(f"采集失败: {post.get('title')}: {e}")
        return results
