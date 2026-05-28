"""内容生成器 - 调用 AI 模型生成新媒体内容。"""

import json
import re
from typing import Any, Dict, List, Optional

from .ai_client import ai_client
from .config import config
from .errors import ValidationError
from .logger import logger
from .prompts import (
    COMMENT_REPLY,
    CONTENT_STRATEGY,
    IMAGE_TEXT_POST,
    SHORT_VIDEO_SCRIPT,
)
from .schemas import GeneratePostInput, GenerateScriptInput


class ContentGenerator:
    """AI 内容生成器，支持多种内容类型。"""

    # 提取 JSON 块的模式
    JSON_PATTERN = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)

    def generate_script(
        self,
        theme: str,
        audience: str = "大众用户",
        duration: int = 60,
        style: str = "轻松有趣",
    ) -> Dict[str, Any]:
        """生成短视频脚本（入口处 Pydantic 验证）。"""
        # validate at entry point — be-best-practices rule
        input_data = GenerateScriptInput(
            theme=theme, audience=audience, duration=duration, style=style
        )
        prompt = SHORT_VIDEO_SCRIPT.format(
            theme=input_data.theme,
            audience=input_data.audience,
            duration=input_data.duration,
            style=input_data.style,
        )
        return self._call_and_parse(prompt, "短视频脚本")

    def generate_post(
        self,
        theme: str,
        word_count: int = 800,
    ) -> Dict[str, Any]:
        """生成图文笔记。"""
        prompt = IMAGE_TEXT_POST.format(theme=theme, word_count=word_count)
        return self._call_and_parse(prompt, "图文笔记")

    def generate_comment_reply(
        self,
        comment: str,
        topic: str,
        strategy: str = "友好回应并引导互动",
    ) -> str:
        """生成评论回复。"""
        prompt = COMMENT_REPLY.format(comment=comment, topic=topic, strategy=strategy)
        result = ai_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=config().get("models", "chat", "model_id", default="deepseek-chat"),
        )
        return result.strip()

    def generate_content_plan(
        self,
        nich: str,
        trending_topics: str = "暂无",
        top_performing: str = "暂无",
    ) -> str:
        """生成内容策略规划。"""
        prompt = CONTENT_STRATEGY.format(
            nich=nich, trending_topics=trending_topics, top_performing=top_performing
        )
        result = ai_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=config().get("models", "reasoning", "model_id", default="deepseek-reasoner"),
        )
        return result.strip()

    def _call_and_parse(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """调用 AI 并解析 JSON 响应。"""
        raw = ai_client.chat(
            messages=[{"role": "user", "content": prompt}],
            model=config().get("models", "chat", "model_id", default="deepseek-chat"),
        )

        # 尝试从 markdown 代码块中提取 JSON
        match = self.JSON_PATTERN.search(raw)
        json_str = match.group(1) if match else raw

        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning(f"{content_type} JSON 解析失败，返回原始文本")
            return {"raw": raw, "_parse_error": True}


# 全局单例
generator = ContentGenerator()
