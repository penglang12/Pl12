#!/usr/bin/env python3
"""数据采集脚本 - 定时收集已发布内容的表现数据。

每小时运行一次，由 GitHub Actions cron 触发。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.db import db
from core.logger import logger, setup_logging
from core.models import ContentDraft, ContentPerformance


def main() -> None:
    setup_logging()
    logger.info("开始采集内容表现数据")

    db.connect()

    session = db.session
    published = (
        session.query(ContentDraft)
        .filter(ContentDraft.status == "published")
        .all()
    )

    for draft in published:
        # TODO: 调用平台 API 获取实际数据
        perf = ContentPerformance(
            draft_id=draft.id,
            platform=draft.platform,
        )
        session.add(perf)

    session.commit()
    logger.info(f"已采集 {len(published)} 条内容的表现数据")


if __name__ == "__main__":
    main()
