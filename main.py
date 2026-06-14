#!/usr/bin/env python3
"""AI News Monitor - 每日 AI 行业新闻 & 热门开源项目监控"""
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config_loader import load_config, get_output_dir
from src.github_crawler import GitHubCrawler
from src.news_crawler import NewsCrawler
from src.report_generator import ReportGenerator


def run_once(config: dict) -> Path:
    print("=" * 60)
    print(f"🤖 AI News Monitor 启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # 1. 抓取新闻
    print("=" * 40)
    news_crawler = NewsCrawler(config)
    news = news_crawler.collect_all()
    print()

    # 2. 抓取 GitHub 项目
    print("=" * 40)
    gh_crawler = GitHubCrawler(config)
    repos = gh_crawler.collect_all()
    print()

    # 3. 生成报告
    print("=" * 40)
    print("[Report] 生成 Markdown 报告...")
    output_dir = get_output_dir(config)
    generator = ReportGenerator(output_dir)
    content = generator.generate_markdown(news, repos)
    filepath = generator.save(content)
    generator.save_latest(content)
    print(f"  报告已保存到: {filepath}")
    print(f"  最新报告链接: {output_dir / 'LATEST.md'}")
    print()
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    return filepath


def run_scheduled(config: dict):
    import schedule
    run_time = config["schedule"]["run_time"]
    print(f"⏰ 已启动定时模式，每天 {run_time} 自动运行")
    print("按 Ctrl+C 退出")
    print()

    # 先运行一次
    run_once(config)

    schedule.every().day.at(run_time).do(run_once, config=config)

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 已退出")
            sys.exit(0)
        except Exception as e:
            print(f"❌ 运行出错: {e}")
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(description="AI News Monitor - 每日 AI 行业新闻监控")
    parser.add_argument(
        "--mode",
        choices=["once", "scheduled"],
        default="once",
        help="once: 立即运行一次; scheduled: 每天定时运行",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="配置文件路径 (默认 config.yaml)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.mode == "scheduled":
        run_scheduled(config)
    else:
        run_once(config)


if __name__ == "__main__":
    main()
