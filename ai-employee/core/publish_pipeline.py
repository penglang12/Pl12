"""发布管线 - 从草稿到发布的完整流程编排。"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .config import config
from .content_generator import generator
from .content_reviewer import reviewer
from .db import db
from .logger import logger
from .models import ContentDraft, PublishSchedule, TaskRecord


class PublishPipeline:
    """内容发布管线。

    完整流程：
    草稿 → AI 审核 → 人工审核（高风险）→ 排期 → 自动发布 → 数据追踪
    """

    def create_draft(
        self,
        title: str,
        content_type: str,
        script: str,
        platform: str = "wechat_video",
        image_prompt: Optional[str] = None,
        tags: Optional[List[str]] = None,
        scheduled_at: Optional[datetime] = None,
    ) -> ContentDraft:
        """创建内容草稿。"""
        session = db.session
        draft = ContentDraft(
            title=title,
            content_type=content_type,
            platform=platform,
            script=script,
            image_prompt=image_prompt,
            tags=",".join(tags) if tags else None,
            status="draft",
            scheduled_at=scheduled_at,
        )
        session.add(draft)
        session.commit()
        logger.info(f"草稿已创建: id={draft.id}, title={title}")
        return draft

    def review_draft(self, draft_id: int) -> Dict[str, Any]:
        """执行 AI 审核。"""
        session = db.session
        draft = session.query(ContentDraft).get(draft_id)
        if not draft:
            raise ValueError(f"草稿不存在: {draft_id}")

        result = reviewer.review(draft.script)
        draft.review_status = "approved" if result.passed else "rejected"
        session.commit()

        logger.info(f"草稿 {draft_id} 审核结果: {result}")
        return {
            "draft_id": draft_id,
            "review_status": draft.review_status,
            "result": {
                "passed": result.passed,
                "risk_level": result.risk_level,
                "score": result.score,
                "issues": result.issues,
                "suggestions": result.suggestions,
            },
        }

    def schedule_publish(
        self,
        draft_id: int,
        publish_time: Optional[datetime] = None,
    ) -> PublishSchedule:
        """创建发布排期。"""
        if not publish_time:
            publish_time = datetime.now() + timedelta(minutes=30)

        session = db.session
        draft = session.query(ContentDraft).get(draft_id)
        if not draft:
            raise ValueError(f"草稿不存在: {draft_id}")
        if draft.review_status != "approved":
            raise ValueError(f"草稿 {draft_id} 尚未通过审核")

        schedule = PublishSchedule(
            draft_id=draft_id,
            platform=draft.platform,
            scheduled_time=publish_time,
            status="pending",
        )
        session.add(schedule)
        draft.status = "scheduled"
        session.commit()

        # 注册定时发布任务
        from .scheduler import scheduler

        from .task_queue import queue

        queue.register("publish_content", self._execute_publish)
        queue.enqueue(
            "publish_content",
            payload={"draft_id": draft_id, "schedule_id": schedule.id},
            run_date=publish_time,
        )

        logger.info(f"排期已创建: draft={draft_id}, publish_at={publish_time}")
        return schedule

    def _execute_publish(self, args: str) -> None:
        """执行实际发布（由调度器调用）。"""
        payload = json.loads(args)
        draft_id = payload["draft_id"]
        schedule_id = payload.get("schedule_id")

        session = db.session
        draft = session.query(ContentDraft).get(draft_id)
        schedule = session.query(PublishSchedule).get(schedule_id) if schedule_id else None

        if not draft:
            logger.error(f"发布失败: 草稿 {draft_id} 不存在")
            return

        task = TaskRecord(
            task_type="publish_content",
            status="running",
            target_id=draft_id,
        )
        session.add(task)
        session.commit()

        try:
            # 根据平台选择适配器
            if draft.platform == "wechat_video":
                from adapters.wechat_video import WeChatVideoAdapter

                adapter = WeChatVideoAdapter()

                # 确保已登录
                if not adapter.is_logged_in():
                    adapter.login()

                # 执行发布
                result = adapter.publish_video(
                    video_path="",  # TODO: 传入实际视频路径
                    title=draft.title,
                    description=draft.script[:200],
                )

                draft.status = "published" if result["status"] == "published" else "draft"
                draft.published_at = datetime.now()
            else:
                logger.warning(f"不支持的平台: {draft.platform}")
                draft.status = "failed"

            task.status = "success"
            task.result = json.dumps({"status": draft.status})
            if schedule:
                schedule.status = "done"

        except Exception as e:
            logger.error(f"发布失败 draft={draft_id}: {e}")
            draft.status = "failed"
            task.status = "failed"
            task.error_message = str(e)
            if schedule:
                schedule.status = "failed"
                schedule.retry_count = (schedule.retry_count or 0) + 1

        finally:
            session.commit()

    def get_pending_drafts(self) -> List[ContentDraft]:
        """获取待处理的草稿。"""
        session = db.session
        return (
            session.query(ContentDraft)
            .filter(
                ContentDraft.status == "draft",
                ContentDraft.review_status == "pending",
            )
            .all()
        )

    def get_schedule_today(self) -> List[PublishSchedule]:
        """获取今日排期。"""
        session = db.session
        today_start = datetime.now().replace(hour=0, minute=0, second=0)
        today_end = today_start + timedelta(days=1)
        return (
            session.query(PublishSchedule)
            .filter(
                PublishSchedule.scheduled_time >= today_start,
                PublishSchedule.scheduled_time < today_end,
            )
            .all()
        )


# 全局单例
pipeline = PublishPipeline()
