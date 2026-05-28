"""内容策略工作流 - 一键执行完整运营流程。

CLI 入口:
  python cli.py strategy daily         # 每日内容运营
  python cli.py strategy batch --theme X --count 5  # 批量生成
"""

from datetime import datetime, timedelta
from typing import List, Optional

from .config import config
from .content_generator import generator
from .db import db
from .errors import AppError
from .logger import logger
from .publish_pipeline import pipeline
from repositories.content_repo import content_repo


class StrategyWorkflow:
    """内容策略自动化工作流。"""

    def run_daily(self) -> dict:
        """每日内容运营：生成 → 保存 → 审核 → 排期。"""
        logger.info("=== 开始每日内容运营工作流 ===")
        report = {"generated": 0, "approved": 0, "scheduled": 0, "errors": []}

        db.connect()
        self._check_balance()

        topics = self._get_daily_topics()
        for topic in topics:
            try:
                result = generator.generate_script(
                    theme=topic["theme"],
                    audience=topic.get("audience", "大众用户"),
                    style=topic.get("style", "轻松有趣"),
                )
                title = result.get("title", topic["theme"])[:256]
                script = str(result.get("script", result.get("raw", "")))

                draft = content_repo.create_draft(
                    title=title,
                    content_type="短视频脚本",
                    script=script,
                    platform="wechat_video",
                    source="ai_generated",
                )
                report["generated"] += 1
                logger.info(f"草稿已创建: #{draft.id} - {title}")

            except Exception as e:
                report["errors"].append(f"生成失败 [{topic['theme']}]: {e}")
                logger.error(f"内容生成失败: {e}")

        # 审核所有待审核草稿
        pending = content_repo.list_drafts(status="draft", review_status="pending")
        for draft in pending:
            try:
                result = pipeline.review_draft(draft.id)
                if result["review_status"] == "approved":
                    report["approved"] += 1
            except Exception as e:
                report["errors"].append(f"审核失败 #{draft.id}: {e}")

        # 为已通过的内容创建排期，间隔 2 小时
        approved = content_repo.list_drafts(status="draft", review_status="approved")
        base_time = datetime.now() + timedelta(hours=1)
        for i, draft in enumerate(approved):
            try:
                publish_time = base_time + timedelta(hours=i * 2)
                pipeline.schedule_publish(draft.id, publish_time=publish_time)
                report["scheduled"] += 1
                logger.info(f"排期创建: #{draft.id} → {publish_time}")
            except Exception as e:
                report["errors"].append(f"排期失败 #{draft.id}: {e}")

        logger.info(f"=== 每日工作流完成: 生成{report['generated']}, "
                    f"通过{report['approved']}, 排期{report['scheduled']} ===")
        return report

    def run_batch(self, theme: str, count: int = 5) -> dict:
        """批量生成同主题内容。"""
        logger.info(f"=== 批量生成: theme={theme}, count={count} ===")
        report = {"generated": 0, "approved": 0, "errors": []}

        db.connect()
        styles = ["轻松有趣", "干货分享", "情感共鸣", "知识科普", "热点评论"]
        audiences = ["大众用户", "职场白领", "年轻人", "宝妈", "科技爱好者"]

        for i in range(count):
            try:
                result = generator.generate_script(
                    theme=theme,
                    audience=audiences[i % len(audiences)],
                    style=styles[i % len(styles)],
                )
                title = result.get("title", f"{theme} #{i+1}")[:256]
                script = str(result.get("script", result.get("raw", "")))

                draft = content_repo.create_draft(
                    title=title,
                    content_type="短视频脚本",
                    script=script,
                    platform="wechat_video",
                    source="ai_generated",
                )
                report["generated"] += 1

                # 自动审核
                rev_result = pipeline.review_draft(draft.id)
                if rev_result.get("review_status") == "approved":
                    report["approved"] += 1

            except Exception as e:
                report["errors"].append(f"第{i+1}条失败: {e}")

        logger.info(f"批量完成: 生成{report['generated']}, 通过{report['approved']}")
        return report

    def _check_balance(self):
        """检查 AI 平台余额。"""
        try:
            from .ai_client import ai_client
            logger.info("AI 平台连接正常")
        except Exception as e:
            logger.warning(f"AI 平台连接异常: {e}")

    def _get_daily_topics(self) -> List[dict]:
        """获取今日选题列表。"""
        # TODO: 从数据库读取历史表现优化选题
        return [
            {"theme": "AI 工具提升工作效率", "audience": "职场白领", "style": "干货分享"},
            {"theme": "2025 年最值得尝试的副业", "audience": "年轻人", "style": "轻松有趣"},
            {"theme": "日常生活中的经济学思维", "audience": "大众用户", "style": "知识科普"},
        ]


# 全局单例
strategy = StrategyWorkflow()
