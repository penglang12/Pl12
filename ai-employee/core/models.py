"""数据模型 - SQLAlchemy ORM 定义。"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    JSON,
    Enum as SAEnum,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── 账号管理 ──────────────────────────────────────────────


class Account(Base):
    """社交媒体账号绑定信息。"""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    platform: Mapped[str] = mapped_column(String(32), comment="微信视频号/抖音/小红书/快手")
    nickname: Mapped[Optional[str]] = mapped_column(String(128))
    account_id: Mapped[str] = mapped_column(String(256), unique=True)
    cookies_json: Mapped[Optional[str]] = mapped_column(Text, comment="序列化 cookie")
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )


# ── 内容管理 ──────────────────────────────────────────────


class ContentDraft(Base):
    """内容草稿。"""

    __tablename__ = "content_drafts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    content_type: Mapped[str] = mapped_column(
        String(32), comment="短视频脚本/图文笔记/直播话术"
    )
    platform: Mapped[str] = mapped_column(String(32), default="wechat_video")
    script: Mapped[str] = mapped_column(Text, comment="文案脚本")
    image_prompt: Mapped[Optional[str]] = mapped_column(Text, comment="配图生成提示词")
    image_urls: Mapped[Optional[str]] = mapped_column(
        Text, comment="图片 URL 列表，逗号分隔"
    )
    video_url: Mapped[Optional[str]] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(
        String(16), default="draft", comment="draft/published/failed"
    )
    review_status: Mapped[str] = mapped_column(
        String(16), default="pending", comment="pending/approved/rejected"
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(64), comment="来源：manual/ai_generated/repurposed"
    )
    tags: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    published_at: Mapped[Optional[datetime]] = mapped_column()
    scheduled_at: Mapped[Optional[datetime]] = mapped_column()


class ContentPerformance(Base):
    """内容发布后的表现数据。"""

    __tablename__ = "content_performance"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("content_drafts.id"))
    platform: Mapped[str] = mapped_column(String(32))
    external_id: Mapped[Optional[str]] = mapped_column(
        String(256), comment="平台侧的 ID"
    )
    views: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    shares: Mapped[int] = mapped_column(default=0)
    collected_at: Mapped[datetime] = mapped_column(default=datetime.now)

    draft = relationship("ContentDraft", backref="performance_records")


# ── 任务记录 ──────────────────────────────────────────────


class TaskRecord(Base):
    """自动化任务执行记录。"""

    __tablename__ = "task_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[str] = mapped_column(
        String(64), index=True, comment="publish_content/collect_comments/check_performance"
    )
    status: Mapped[str] = mapped_column(
        String(16), default="running", comment="running/success/failed"
    )
    target_id: Mapped[Optional[int]] = mapped_column(
        Integer, comment="关联的 draft_id 等"
    )
    result: Mapped[Optional[str]] = mapped_column(Text, comment="执行结果 JSON")
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(default=datetime.now)
    finished_at: Mapped[Optional[datetime]] = mapped_column()


# ── 排期表 ──────────────────────────────────────────────


class PublishSchedule(Base):
    """发布排期。"""

    __tablename__ = "publish_schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("content_drafts.id"))
    platform: Mapped[str] = mapped_column(String(32))
    scheduled_time: Mapped[datetime] = mapped_column()
    status: Mapped[str] = mapped_column(
        String(16), default="pending", comment="pending/publishing/done/failed"
    )
    retry_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    draft = relationship("ContentDraft", backref="schedules")
