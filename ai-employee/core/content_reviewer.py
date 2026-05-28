"""内容审核 - AI 辅助审核 + 人工审核流程。"""

from typing import Optional

from .ai_client import ai_client
from .config import config
from .logger import logger
from .prompts import CONTENT_REVIEW


class ReviewResult:
    """审核结果。"""

    def __init__(
        self,
        passed: bool = False,
        risk_level: str = "medium",
        issues: Optional[list] = None,
        suggestions: Optional[list] = None,
        score: int = 0,
    ):
        self.passed = passed
        self.risk_level = risk_level
        self.issues = issues or []
        self.suggestions = suggestions or []
        self.score = score

    @property
    def needs_human_review(self) -> bool:
        return self.risk_level == "high" or (not self.passed and self.score < 60)

    def __repr__(self) -> str:
        return (
            f"ReviewResult(passed={self.passed}, risk={self.risk_level}, "
            f"score={self.score}, issues={len(self.issues)})"
        )


class ContentReviewer:
    """内容审核模块 - AI 初审 + 人工复审标记。"""

    def __init__(self) -> None:
        self._auto_approve_threshold = 85

    def review(self, content: str) -> ReviewResult:
        """对内容进行 AI 审核。"""
        prompt = CONTENT_REVIEW.format(content=content)
        try:
            result = ai_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model=config().get("models", "chat", "model_id", default="deepseek-chat"),
            )
            import json, re

            match = re.search(r"```json\s*\n(.*?)\n```", result, re.DOTALL)
            data = json.loads(match.group(1)) if match else json.loads(result)

            parsed = ReviewResult(
                passed=data.get("passed", False),
                risk_level=data.get("risk_level", "medium"),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
                score=data.get("score", 0),
            )
        except Exception as e:
            logger.warning(f"AI 审核解析失败，标记为人工审核: {e}")
            parsed = ReviewResult(passed=False, risk_level="high", issues=["审核解析错误"])

        # 高分自动通过
        if parsed.score >= self._auto_approve_threshold and parsed.passed:
            logger.info(f"内容自动通过审核 (score={parsed.score})")

        return parsed


# 全局单例
reviewer = ContentReviewer()
