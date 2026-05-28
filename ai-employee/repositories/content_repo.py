"""内容仓库 - 封装所有 ContentDraft / PublishSchedule / ContentPerformance 的 DB 查询。

对应 be-best-practices 的 Repository 层原则：
- 所有 DB 访问通过仓库类
- 始终 select 需要的字段
- 不在 service 层直接调用 ORM
"""

from datetime import datetime
from typing import List, Optional

from core.db import db
from core.errors import NotFoundError
from core.models import ContentDraft, ContentPerformance, PublishSchedule


class ContentRepository:
    """内容管理相关数据库操作。"""

    # ── 草稿操作 ──

    def create_draft(
        self,
        title: str,
        content_type: str,
        script: str,
        platform: str = "wechat_video",
        **kwargs,
    ) -> ContentDraft:
        session = db.session
        draft = ContentDraft(
            title=title,
            content_type=content_type,
            platform=platform,
            script=script,
            **kwargs,
        )
        session.add(draft)
        session.commit()
        return draft

    def get_draft(self, draft_id: int) -> ContentDraft:
        session = db.session
        draft = session.query(ContentDraft).get(draft_id)
        if not draft:
            raise NotFoundError(f"草稿 {draft_id}")
        return draft

    def list_drafts(
        self,
        status: Optional[str] = None,
        review_status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ContentDraft]:
        session = db.session
        query = session.query(ContentDraft)
        if status:
            query = query.filter(ContentDraft.status == status)
        if review_status:
            query = query.filter(ContentDraft.review_status == review_status)
        return query.order_by(ContentDraft.created_at.desc()).limit(limit).offset(offset).all()

    def update_draft_status(self, draft_id: int, status: str) -> ContentDraft:
        draft = self.get_draft(draft_id)
        draft.status = status
        if status == "published":
            draft.published_at = datetime.now()
        db.session.commit()
        return draft

    # ── 排期操作 ──

    def create_schedule(
        self,
        draft_id: int,
        platform: str,
        scheduled_time: datetime,
    ) -> PublishSchedule:
        session = db.session
        schedule = PublishSchedule(
            draft_id=draft_id,
            platform=platform,
            scheduled_time=scheduled_time,
            status="pending",
        )
        session.add(schedule)
        session.commit()
        return schedule

    def get_pending_schedules(self, before: Optional[datetime] = None) -> List[PublishSchedule]:
        session = db.session
        query = session.query(PublishSchedule).filter(PublishSchedule.status == "pending")
        if before:
            query = query.filter(PublishSchedule.scheduled_time <= before)
        return query.order_by(PublishSchedule.scheduled_time).all()

    # ── 表现数据 ──

    def record_performance(
        self,
        draft_id: int,
        platform: str,
        views: int = 0,
        likes: int = 0,
        comments: int = 0,
        shares: int = 0,
    ) -> ContentPerformance:
        session = db.session
        perf = ContentPerformance(
            draft_id=draft_id,
            platform=platform,
            views=views,
            likes=likes,
            comments=comments,
            shares=shares,
        )
        session.add(perf)
        session.commit()
        return perf


# 全局单例
content_repo = ContentRepository()
