"""调度器 - 编排定时内容发布、数据采集等周期性任务。"""

from .logger import logger
from .task_queue import queue


class Scheduler:
    """业务调度器，注册所有周期性任务。"""

    def __init__(self) -> None:
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        queue.start()
        self._register_scheduled_jobs()
        self._started = True
        logger.info("业务调度器已启动")

    def _register_scheduled_jobs(self) -> None:
        """注册所有周期性业务任务。"""
        # ── 内容发布任务 ──
        # 每 30 分钟检查待发布的草稿
        queue.register("publish_content", self._handle_publish)
        queue.schedule_cron("publish_content", "*/30 * * * *")

        # ── 数据采集任务 ──
        # 每小时检查已发布内容的表现
        queue.register("collect_performance", self._handle_collect_performance)
        queue.schedule_cron("collect_performance", "0 * * * *")

        # ── 评论回复检查 ──
        # 每 15 分钟检查新评论
        queue.register("check_comments", self._handle_check_comments)
        queue.schedule_cron("check_comments", "*/15 * * * *")

        # ── 内容策略生成 ──
        # 每天早上 8 点生成今日内容建议
        queue.register("generate_content_plan", self._handle_generate_plan)
        queue.schedule_cron("generate_content_plan", "0 8 * * *")

        logger.info("所有周期性任务已注册")

    # ── 任务处理函数（占位，后续 Phase 实现） ──

    def _handle_publish(self, args: str) -> None:
        logger.info(f"发布任务执行: {args}")

    def _handle_collect_performance(self, args: str) -> None:
        logger.info(f"采集表现数据: {args}")

    def _handle_check_comments(self, args: str) -> None:
        logger.info(f"检查评论: {args}")

    def _handle_generate_plan(self, args: str) -> None:
        logger.info(f"生成内容计划: {args}")

    def shutdown(self) -> None:
        if self._started:
            queue.shutdown()
            self._started = False
            logger.info("业务调度器已关闭")


# 全局单例
scheduler = Scheduler()
