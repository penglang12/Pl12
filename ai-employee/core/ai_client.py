"""Ai头号玩家 API 客户端 - 统一 AI 模型调用层。"""

import json
from typing import Any, Dict, List, Optional, Tuple

import httpx

from .config import config
from .errors import ApiError, AuthError
from .logger import logger


class AIClient:
    """Ai头号玩家 API 封装。

    支持多模型路由、自动重试、超时控制。
    """

    def __init__(self) -> None:
        cfg = config()
        self.base_url = cfg.get("ai_touhaowanjia", "base_url", default="https://api.lk888.ai/api")
        self.timeout = cfg.get("ai_touhaowanjia", "timeout", default=60)
        self.max_retries = cfg.get("ai_touhaowanjia", "max_retries", default=3)
        self._api_key: Optional[str] = None
        self._client: Optional[httpx.Client] = None

    def _ensure_client(self) -> httpx.Client:
        if not self._client:
            self._api_key = config().get_api_key()
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str:
        """标准对话补全。"""
        cfg = config()
        payload: Dict[str, Any] = {
            "model": model or cfg.get("models", "chat", "model_id", default="deepseek-chat"),
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if stream:
            payload["stream"] = True

        return self._call("chat", payload)

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """流式对话。"""
        cfg = config()
        payload: Dict[str, Any] = {
            "model": model or cfg.get("models", "chat", "model_id", default="deepseek-chat"),
            "messages": messages,
            "stream": True,
        }
        if temperature is not None:
            payload["temperature"] = temperature

        client = self._ensure_client()
        with client.stream("POST", "/chat", json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    yield json.loads(data)

    def _call(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """带重试的 API 调用。"""
        client = self._ensure_client()
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                resp = client.post(f"/v1/{endpoint}", json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code in (401, 403):
                    raise AuthError("Ai头号玩家 API 鉴权失败，请检查 API Key")
                logger.warning(f"API 调用失败 (attempt {attempt}/{self.max_retries}): {e}")
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"网络错误 (attempt {attempt}/{self.max_retries}): {e}")

        raise ApiError(
            f"API 调用失败，已重试 {self.max_retries} 次",
            provider="ai_touhaowanjia",
            status_code=502,
        )

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None


# 全局单例
ai_client = AIClient()
