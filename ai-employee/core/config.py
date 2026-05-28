"""配置管理 - 加载 config.yaml 并提供全局配置对象。"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """分层配置：文件默认值 → 环境变量覆盖。"""

    _instance: Optional["Config"] = None

    def __init__(self, path: Optional[str] = None) -> None:
        self.data: Dict[str, Any] = {}
        if path:
            self.load(path)

    def load(self, path: str) -> None:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}

    def get(self, *keys: str, default: Any = None) -> Any:
        """嵌套 key 取值，如 config.get('database', 'sqlite_path')"""
        current = self.data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return default
            else:
                return default
        return current

    def get_api_key(self) -> str:
        """从环境变量读取 API Key。"""
        import os

        env_var = self.get("ai_touhaowanjia", "api_key_env", default="AI_TOUHAOWANJIA_API_KEY")
        key = os.getenv(env_var)
        if not key:
            raise ValueError(
                f"API Key 未设置。请在环境变量 {env_var} 中配置，"
                f"或前往 https://findanai.co 获取。"
            )
        return key

    @classmethod
    def global_(cls, path: Optional[str] = None) -> "Config":
        """全局单例。"""
        if cls._instance is None:
            cls._instance = cls(path or _default_path())
        return cls._instance


def _default_path() -> str:
    """自动查找项目根目录下的 config.yaml。"""
    candidates = [
        Path.cwd() / "config.yaml",
        Path(__file__).parent.parent / "config.yaml",
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return str(candidates[0])


# 便捷引用
config = Config.global_
