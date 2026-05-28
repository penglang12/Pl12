#!/usr/bin/env python3
"""内容策略自动生成脚本 - 可被 GitHub Actions 定时触发。

每天 8:00 运行，生成当日内容建议并存入数据库。
"""

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import config
from core.content_generator import generator
from core.db import db
from core.logger import logger, setup_logging
from core.models import ContentDraft


def main() -> None:
    setup_logging()
    cfg = config()

    logger.info("开始生成今日内容计划")

    # 连接数据库
    db.connect()

    # 从配置或上次表现数据获取主题
    # TODO: 从数据库读取历史表现数据，优化选题
    topics = [
        {"theme": "职场效率提升技巧", "audience": "职场白领", "style": "干货分享"},
        {"theme": "AI 工具推荐与评测", "audience": "科技爱好者", "style": "评测解说"},
    ]

    for topic in topics:
        try:
            result = generator.generate_script(
                theme=topic["theme"],
                audience=topic["audience"],
                style=topic["style"],
            )
            logger.info(f"内容生成成功: {result.get('title', topic['theme'])}")

            # 保存为草稿
            session = db.session
            draft = ContentDraft(
                title=result.get("title", topic["theme"])[:256],
                content_type="短视频脚本",
                platform="wechat_video",
                script=str(result.get("script", "")),
                status="draft",
                review_status="pending",
                source="ai_generated",
            )
            session.add(draft)
            session.commit()
            logger.info(f"草稿已保存: id={draft.id}")

        except Exception as e:
            logger.error(f"内容生成失败: {topic['theme']}: {e}")

    logger.info("今日内容计划生成完毕")


if __name__ == "__main__":
    main()
