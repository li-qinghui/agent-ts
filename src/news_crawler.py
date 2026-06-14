import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import feedparser
from bs4 import BeautifulSoup


class NewsCrawler:
    def __init__(self, config: Dict):
        self.feeds = config["rss_feeds"]
        self.keywords = {}
        for cat, kws in config["keywords"].items():
            self.keywords[cat] = kws
        self.flat_keywords = []
        for cat, kws in self.keywords.items():
            self.flat_keywords.extend(kws)
        self.lookback_days = 2  # 只看最近2天的新闻

    def _parse_time(self, entry) -> datetime:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
        return datetime.now(timezone.utc)

    def _strip_html(self, text: str) -> str:
        if not text:
            return ""
        try:
            soup = BeautifulSoup(text, "lxml")
            return soup.get_text(separator=" ", strip=True)
        except:
            return text[:500]

    def _match_keywords(self, text: str) -> Dict[str, List[str]]:
        if not text:
            return {}
        text_lower = text.lower()
        result = {}
        for cat, kws in self.keywords.items():
            matched = []
            for kw in kws:
                if kw.lower() in text_lower:
                    matched.append(kw)
            if matched:
                result[cat] = matched
        return result

    def fetch_feed(self, feed_info: Dict) -> List[Dict]:
        name = feed_info["name"]
        url = feed_info["url"]
        category = feed_info.get("category", "general")
        language = feed_info.get("language", "en")
        print(f"  抓取 [{name}]...")
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"    失败: {e}")
            return []
        items = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.lookback_days)
        for entry in parsed.entries[:50]:
            title = getattr(entry, "title", "")
            link = getattr(entry, "link", "")
            summary = self._strip_html(getattr(entry, "summary", ""))
            pub_time = self._parse_time(entry)
            if pub_time < cutoff:
                continue
            text_for_match = f"{title} {summary}"
            matched = self._match_keywords(text_for_match)
            score = 0
            for cat, kws in matched.items():
                score += len(kws) * 10
            items.append({
                "title": title,
                "url": link,
                "summary": summary[:500],
                "source": name,
                "category": category,
                "language": language,
                "published": pub_time.strftime("%Y-%m-%d %H:%M UTC"),
                "matched_keywords": matched,
                "score": score,
            })
        print(f"    得到 {len(items)} 条有效新闻")
        return items

    def collect_all(self) -> Dict[str, List[Dict]]:
        print("[News] 正在从 RSS 源抓取新闻...")
        all_items = []
        for feed_info in self.feeds:
            items = self.fetch_feed(feed_info)
            all_items.extend(items)
            time.sleep(0.5)

        # 按标题去重
        seen = set()
        unique = []
        for item in all_items:
            key = item["title"][:60].lower()
            if key not in seen:
                seen.add(key)
                unique.append(item)

        # 分类：关键词匹配 >0 的优先
        by_category = {
            "matched": [],   # 有关键词匹配的
            "agent": [],     # Agent 相关
            "hardware": [],  # 硬件相关
            "general": [],   # 其他
        }
        for item in unique:
            matched = item["matched_keywords"]
            if matched:
                by_category["matched"].append(item)
                if "ai_agent" in matched:
                    by_category["agent"].append(item)
                if "ai_hardware" in matched:
                    by_category["hardware"].append(item)
            else:
                by_category["general"].append(item)

        # 按 score 排序
        for cat in by_category:
            by_category[cat].sort(key=lambda x: x["score"], reverse=True)

        total = sum(len(v) for v in by_category.values())
        print(f"  共获取 {total} 条新闻 (匹配关键词: {len(by_category['matched'])})")
        return by_category
