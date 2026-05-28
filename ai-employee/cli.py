#!/usr/bin/env python3
"""AI Employee CLI - 新媒体运营自动化命令行工具。

用法:
  python cli.py generate script --theme "AI 工具推荐" --style "干货分享"
  python cli.py generate post --theme "职场效率" --words 500
  python cli.py publish draft <id> [--time "2025-01-01 10:00"]
  python cli.py login wechat
  python cli.py review list
  python cli.py review run <id>
  python cli.py schedule list
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))


def cmd_generate_script(args):
    from core.content_generator import generator
    from core.logger import setup_logging
    setup_logging()
    result = generator.generate_script(
        theme=args.theme,
        audience=args.audience,
        duration=args.duration,
        style=args.style,
    )
    print(f"\n标题: {result.get('title', 'N/A')}")
    print(f"描述: {result.get('description', 'N/A')}")
    print(f"标签: {', '.join(result.get('hashtags', []))}")
    script = result.get("script", [])
    if script:
        print(f"\n脚本段落 ({len(script)}):")
        for seg in script:
            print(f"  [{seg.get('time','')}] {seg.get('narration','')[:80]}...")
    print(f"\n拍摄建议: {result.get('shooting_notes', 'N/A')}")


def cmd_generate_post(args):
    from core.content_generator import generator
    from core.logger import setup_logging
    setup_logging()
    result = generator.generate_post(
        theme=args.theme,
        word_count=args.words,
    )
    print(f"\n标题: {result.get('title', 'N/A')}")
    print(f"\n正文 ({len(result.get('body', ''))} 字):")
    print(result.get("body", "")[:500] + ("..." if len(result.get("body", "")) > 500 else ""))


def cmd_login(args):
    from core.logger import setup_logging
    setup_logging()
    if args.platform == "wechat":
        from core.browser import browser
        from adapters.wechat_video import WeChatVideoAdapter
        browser.start()
        adapter = WeChatVideoAdapter()
        if adapter.login():
            print("微信视频号登录成功")
        else:
            print("登录失败或超时")
            sys.exit(1)
    else:
        print(f"不支持的平台: {args.platform}")
        sys.exit(1)


def cmd_publish_draft(args):
    from core.db import db
    from core.logger import setup_logging
    from core.publish_pipeline import pipeline
    from core.schemas import CreateDraftInput, SchedulePublishInput
    setup_logging()
    db.connect()
    try:
        if args.action == "review":
            result = pipeline.review_draft(args.draft_id)
            status = result.get("review_status", "unknown")
            score = result.get("result", {}).get("score", 0)
            issues = result.get("result", {}).get("issues", [])
            print(f"草稿 #{args.draft_id} 审核: {status} (得分: {score})")
            if issues:
                print(f"问题: {'; '.join(issues)}")
        elif args.action == "schedule":
            from core.publish_pipeline import pipeline
            schedule = pipeline.schedule_publish(
                draft_id=args.draft_id,
                publish_time=args.time,
            )
            print(f"排期已创建: #{schedule.id} → {schedule.scheduled_time}")
        elif args.action == "go":
            from core.publish_pipeline import pipeline
            pipeline._execute_publish(f'{{"draft_id": {args.draft_id}}}')
            print(f"发布命令已执行: 草稿 #{args.draft_id}")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


def cmd_review(args):
    from core.db import db
    from core.logger import setup_logging
    setup_logging()
    db.connect()
    if args.action == "list":
        from core.models import ContentDraft
        from core.db import db
        session = db.session
        drafts = session.query(ContentDraft).filter(
            ContentDraft.review_status == "pending",
            ContentDraft.status == "draft",
        ).all()
        if not drafts:
            print("没有待审核的草稿")
            return
        print(f"待审核草稿 ({len(drafts)}):")
        for d in drafts:
            print(f"  #{d.id:04d} | {d.title[:40]:40s} | {d.content_type}")
    elif args.action == "run":
        from core.publish_pipeline import pipeline
        result = pipeline.review_draft(args.draft_id)
        print(f"草稿 #{args.draft_id}: {result['review_status']} (得分: {result['result']['score']})")


def cmd_schedule(args):
    from core.db import db
    from core.logger import setup_logging
    setup_logging()
    db.connect()
    if args.action == "list":
        from core.publish_pipeline import pipeline
        schedules = pipeline.get_schedule_today()
        if not schedules:
            print("今日无排期")
            return
        print(f"今日排期 ({len(schedules)}):")
        for s in schedules:
            print(f"  #{s.id:04d} | 草稿 #{s.draft_id:04d} | {s.scheduled_time} | {s.status}")


def cmd_strategy(args):
    from core.db import db
    from core.logger import setup_logging
    setup_logging()
    if args.action == "daily":
        from core.strategy_workflow import strategy
        report = strategy.run_daily()
        print(f"\n每日工作流完成:")
        print(f"  生成: {report['generated']} 篇")
        print(f"  审核通过: {report['approved']} 篇")
        print(f"  已排期: {report['scheduled']} 篇")
        if report["errors"]:
            print(f"  错误 ({len(report['errors'])}):")
            for e in report["errors"][:5]:
                print(f"    - {e}")
    elif args.action == "batch":
        from core.strategy_workflow import strategy
        report = strategy.run_batch(theme=args.theme, count=args.count)
        print(f"\n批量生成完成:")
        print(f"  生成: {report['generated']} 篇")
        print(f"  审核通过: {report['approved']} 篇")
        if report["errors"]:
            print(f"  错误: {len(report['errors'])}")


def cmd_server(args):
    """启动常驻服务"""
    from core.server import server
    server.start()


def main():
    parser = argparse.ArgumentParser(
        description="AI Employee - 新媒体运营自动化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # generate script
    gen = sub.add_parser("generate", help="AI 生成内容")
    gen_sub = gen.add_subparsers(dest="action")
    gs = gen_sub.add_parser("script", help="生成短视频脚本")
    gs.add_argument("--theme", required=True)
    gs.add_argument("--audience", default="大众用户")
    gs.add_argument("--duration", type=int, default=60)
    gs.add_argument("--style", default="轻松有趣")
    gp = gen_sub.add_parser("post", help="生成图文笔记")
    gp.add_argument("--theme", required=True)
    gp.add_argument("--words", type=int, default=800)

    # login
    login = sub.add_parser("login", help="登录社交媒体平台")
    login.add_argument("platform", choices=["wechat", "douyin", "xiaohongshu"])

    # publish
    pub = sub.add_parser("publish", help="管理内容发布")
    pub_sub = pub.add_subparsers(dest="action")
    pr = pub_sub.add_parser("review", help="AI 审核草稿")
    pr.add_argument("draft_id", type=int)
    ps = pub_sub.add_parser("schedule", help="创建发布排期")
    ps.add_argument("draft_id", type=int)
    ps.add_argument("--time", help="发布时间 (YYYY-MM-DD HH:MM)")
    pg = pub_sub.add_parser("go", help="立即发布草稿")
    pg.add_argument("draft_id", type=int)

    # review
    rv = sub.add_parser("review", help="内容审核管理")
    rv_sub = rv.add_subparsers(dest="action")
    rv_sub.add_parser("list", help="列出待审核草稿")
    rr = rv_sub.add_parser("run", help="执行 AI 审核")
    rr.add_argument("draft_id", type=int)

    # schedule
    sc = sub.add_parser("schedule", help="排期管理")
    sc_sub = sc.add_subparsers(dest="action")
    sc_sub.add_parser("list", help="今日排期")

    # server
    sub.add_parser("server", help="启动常驻服务")

    # strategy
    strat = sub.add_parser("strategy", help="自动化运营工作流")
    strat_sub = strat.add_subparsers(dest="action")
    strat_sub.add_parser("daily", help="执行每日内容运营流程")
    sb = strat_sub.add_parser("batch", help="批量生成同主题内容")
    sb.add_argument("--theme", required=True)
    sb.add_argument("--count", type=int, default=5)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route commands
    if args.command == "generate":
        if args.action == "script":
            cmd_generate_script(args)
        elif args.action == "post":
            cmd_generate_post(args)
        else:
            print("请指定 generate 子命令: script | post")
    elif args.command == "login":
        cmd_login(args)
    elif args.command == "publish":
        if args.action in ("review", "schedule", "go"):
            cmd_publish_draft(args)
        else:
            print("请指定 publish 子命令: review | schedule | go")
    elif args.command == "review":
        cmd_review(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "strategy":
        if args.action in ("daily", "batch"):
            cmd_strategy(args)
        else:
            print("请指定 strategy 子命令: daily | batch")
    elif args.command == "server":
        cmd_server(args)


if __name__ == "__main__":
    main()
