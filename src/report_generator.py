from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ReportGenerator:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _format_stars(self, n: int) -> str:
        if n >= 1000:
            return f"{n/1000:.1f}k"
        return str(n)

    def generate_markdown(
        self,
        news: Dict[str, List[Dict]],
        repos: List[Dict],
    ) -> str:
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = []
        lines.append(f"# 🤖 AI 每日情报 ({today})")
        lines.append("")
        lines.append(f"> 自动生成于 {today} · 涵盖 GitHub 热门项目 & 行业新闻")
        lines.append("")
        lines.append("---")
        lines.append("")

        # ===== 摘要 =====
        total_news = sum(len(v) for v in news.values())
        matched_news = len(news.get("matched", []))
        agent_news = len(news.get("agent", []))
        hardware_news = len(news.get("hardware", []))
        lines.append("## 📊 今日概览")
        lines.append("")
        lines.append(f"- **新闻总数**: {total_news} 条")
        lines.append(f"- **关键词匹配**: {matched_news} 条")
        lines.append(f"- **Agent 相关**: {agent_news} 条")
        lines.append(f"- **硬件相关**: {hardware_news} 条")
        lines.append(f"- **热门开源项目**: {len(repos)} 个")
        lines.append("")
        lines.append("---")
        lines.append("")

        # ===== 硬件相关新闻 =====
        hw_news = news.get("hardware", [])
        if hw_news:
            lines.append(f"## 🔬 硬件进展 (NVIDIA / 台积电 / 华为 / DeepSeek 等)")
            lines.append("")
            for i, item in enumerate(hw_news[:10], 1):
                kws_text = ""
                for cat, kws in item["matched_keywords"].items():
                    kws_text += " ".join(f"`{k}`" for k in kws)
                lines.append(f"### {i}. {item['title']}")
                lines.append(f"- **来源**: {item['source']} · **时间**: {item['published']}")
                lines.append(f"- **链接**: {item['url']}")
                if item["summary"]:
                    lines.append(f"- **摘要**: {item['summary']}")
                if kws_text:
                    lines.append(f"- **关键词**: {kws_text}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # ===== Agent / 开发相关新闻 =====
        agent_news_list = news.get("agent", [])
        if agent_news_list:
            lines.append(f"## 🚀 AI Agent 开发动向")
            lines.append("")
            for i, item in enumerate(agent_news_list[:10], 1):
                kws_text = ""
                for cat, kws in item["matched_keywords"].items():
                    kws_text += " ".join(f"`{k}`" for k in kws)
                lines.append(f"### {i}. {item['title']}")
                lines.append(f"- **来源**: {item['source']} · **时间**: {item['published']}")
                lines.append(f"- **链接**: {item['url']}")
                if item["summary"]:
                    lines.append(f"- **摘要**: {item['summary']}")
                if kws_text:
                    lines.append(f"- **关键词**: {kws_text}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # ===== 其他关键词匹配新闻 =====
        matched = news.get("matched", [])
        shown = set()
        for item in hw_news + agent_news_list:
            shown.add(item["title"][:60].lower())
        other_matched = [item for item in matched if item["title"][:60].lower() not in shown]
        if other_matched:
            lines.append(f"## 🔥 其他关键词匹配新闻")
            lines.append("")
            for i, item in enumerate(other_matched[:15], 1):
                kws_text = ""
                for cat, kws in item["matched_keywords"].items():
                    kws_text += " ".join(f"`{k}`" for k in kws)
                lines.append(f"### {i}. {item['title']}")
                lines.append(f"- **来源**: {item['source']} · **时间**: {item['published']}")
                lines.append(f"- **链接**: {item['url']}")
                if item["summary"]:
                    lines.append(f"- **摘要**: {item['summary']}")
                if kws_text:
                    lines.append(f"- **关键词**: {kws_text}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # ===== 通用新闻 =====
        general = news.get("general", [])
        if general:
            lines.append(f"## 📰 其他行业新闻 ({len(general)} 条)")
            lines.append("")
            for i, item in enumerate(general[:20], 1):
                lines.append(f"{i}. **{item['title']}**")
                lines.append(f"   - 来源: {item['source']} · 时间: {item['published']}")
                lines.append(f"   - {item['url']}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # ===== GitHub 热门项目 =====
        if repos:
            lines.append(f"## ⭐ GitHub 热门 AI 开源项目")
            lines.append("")
            lines.append("> 按 stars 数量与关键词匹配度排序")
            lines.append("")
            for i, r in enumerate(repos[:20], 1):
                stars_line = f"⭐ {self._format_stars(r['stars'])}"
                if r.get("stars_today"):
                    stars_line += f" (+{r['stars_today']} today)"
                lang_line = f" · {r['language']}" if r["language"] else ""
                kws_text = ""
                if r.get("matched_keywords"):
                    kws_text = " · " + " ".join(f"`{k}`" for k in r["matched_keywords"][:5])
                lines.append(f"### {i}. [{r['name']}]({r['url']})")
                lines.append(f"- {stars_line}{lang_line} · 来源: `{r.get('source', '')}`{kws_text}")
                if r["description"]:
                    lines.append(f"- **简介**: {r['description']}")
                lines.append("")

        # 底部信息
        lines.append("")
        lines.append("---")
        lines.append(f"<sub>本报告由 AI News Monitor 自动生成于 {today}</sub>")
        lines.append("")
        return "\n".join(lines)

    def save(self, content: str) -> Path:
        filename = f"ai_news_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath

    def save_latest(self, content: str) -> Path:
        filepath = self.output_dir / "LATEST.md"
        filepath.write_text(content, encoding="utf-8")
        return filepath
