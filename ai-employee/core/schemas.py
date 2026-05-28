"""输入验证模式 - 对应 be-best-practices 的 Zod 层。

使用 Pydantic 在入口处验证，验证通过后信任数据类型往下传递。
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class GenerateScriptInput(BaseModel):
    theme: str = Field(..., min_length=2, max_length=200)
    audience: str = Field(default="大众用户", max_length=100)
    duration: int = Field(default=60, ge=15, le=600)
    style: str = Field(default="轻松有趣", max_length=50)


class GeneratePostInput(BaseModel):
    theme: str = Field(..., min_length=2, max_length=200)
    word_count: int = Field(default=800, ge=100, le=5000)


class ReviewContentInput(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)


class CreateDraftInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    content_type: str = Field(...)
    script: str = Field(..., min_length=1)
    platform: str = Field(default="wechat_video")
    image_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        valid = {"短视频脚本", "图文笔记", "直播话术"}
        if v not in valid:
            raise ValueError(f"content_type 必须是 {valid}")
        return v

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        valid = {"wechat_video", "douyin", "xiaohongshu", "kuaishou"}
        if v not in valid:
            raise ValueError(f"platform 必须是 {valid}")
        return v


class SchedulePublishInput(BaseModel):
    draft_id: int = Field(..., gt=0)
    publish_time: Optional[datetime] = None
