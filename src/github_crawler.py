import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed


class GitHubCrawler:
    def __init__(self, config: Dict):
        self.topics = config["github"]["topics"]
        self.search_days = config["github"]["search_days"]
        self.top_n = config["github"]["top_n"]
        self.min_stars = config["github"]["min_stars"]
        self.token = config["github"].get("token", "")
        self.trending_url = config["github"]["trending_url"]
        self.all_keywords = []
        for cat, kws in config["keywords"].items():
            self.all_keywords.extend(kws)
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Mozilla/5.0",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def _api_request(self, url: str, params: Dict = None) -> Dict:
        resp = requests.get(url, headers=self.headers, params=params, timeout=30)
        if resp.status_code == 403:
            print(f"  [GitHub] API rate limit hit, trying trending page instead")
            return None
        if resp.status_code == 422:
            print(f"  [GitHub] API 422 error for {url}")
            return None
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def fetch_trending(self) -> List[Dict]:
        print("[GitHub] 抓取 Trending 页面...")
        resp = requests.get(self.trending_url, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        repos = []
        articles = soup.select("article.Box-row")
        for art in articles:
            link = art.select_one("h2 a")
            if not link:
                continue
            full_name = link.get_text(strip=True).replace(" ", "")
            href = "https://github.com/" + full_name
            desc_tag = art.select_one("p")
            description = desc_tag.get_text(strip=True) if desc_tag else ""
            stars_today_tag = art.select_one(".float-sm-right")
            stars_today = 0
            if stars_today_tag:
                text = stars_today_tag.get_text(strip=True)
                for w in text.split():
                    if w.isdigit() or w.replace(",", "").isdigit():
                        try:
                            stars_today = int(w.replace(",", ""))
                        except:
                            pass
            lang_tag = art.select_one('[itemprop="programmingLanguage"]')
            language = lang_tag.get_text(strip=True) if lang_tag else ""
            stars_link = art.select("a.Link--muted")
            total_stars = 0
            for l in stars_link:
                if "stargazers" in l.get("href", ""):
                    try:
                        total_stars = int(l.get_text(strip=True).replace(",", ""))
                    except:
                        pass
                    break
            repos.append({
                "name": full_name,
                "url": href,
                "description": description,
                "stars": total_stars,
                "stars_today": stars_today,
                "language": language,
                "source": "trending",
            })
        print(f"  从 Trending 获取 {len(repos)} 个项目")
        return repos

    def fetch_by_topic(self, topic: str, limit: int = 10) -> List[Dict]:
        since = (datetime.utcnow() - timedelta(days=self.search_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        repos = []
        try:
            # 方式1：通过 API 搜索
            query = f"topic:{topic} created:>{since}"
            url = "https://api.github.com/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": limit,
            }
            data = self._api_request(url, params)
            if data and "items" in data:
                for item in data["items"]:
                    repos.append({
                        "name": item["full_name"],
                        "url": item["html_url"],
                        "description": item.get("description") or "",
                        "stars": item["stargazers_count"],
                        "stars_today": 0,
                        "language": item.get("language") or "",
                        "source": f"topic:{topic}",
                    })
        except Exception as e:
            print(f"  [GitHub] API search failed for topic '{topic}': {e}")
            # 方式2：抓取话题页面
            try:
                topic_url = f"https://github.com/topics/{topic}?s=stars"
                resp = requests.get(topic_url, timeout=30)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    cards = soup.select("article.border-bottom")[:limit]
                    for card in cards[:limit]:
                        link = card.select_one("h3 a")
                        if not link:
                            continue
                        full_name = link.get("href", "").lstrip("/")
                        if not full_name:
                            continue
                        desc = card.select_one("p")
                        stars_tag = card.select_one("a[href*='/stargazers']")
                        try:
                            stars = 0
                            if stars_tag:
                                stars_text = stars_tag.get_text(strip=True).replace(",", "")
                                for w in stars_text.split():
                                    if w.isdigit():
                                        stars = int(w)
                                        break
                            lang_tag = card.select_one("span[itemprop='programmingLanguage']")
                            repos.append({
                                "name": full_name,
                                "url": f"https://github.com/{full_name}",
                                "description": desc.get_text(strip=True) if desc else "",
                                "stars": stars,
                                "stars_today": 0,
                                "language": lang_tag.get_text(strip=True) if lang_tag else "",
                                "source": f"topic:{topic}",
                            })
                        except:
                            pass
            except Exception as e2:
                print(f"  [GitHub] topic page fallback failed: {e2}")
        time.sleep(1)
        return repos

    def fetch_recent_popular(self) -> List[Dict]:
        print("[GitHub] 搜索近期热门 AI 项目 (近 {self.search_days} 天)...")
        since = (datetime.utcnow() - timedelta(days=self.search_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        repos = []
        try:
            url = "https://api.github.com/search/repositories"
            for query in [
                f"ai agent created:>{since}",
                f"llm agent created:>{since}",
                f"framework agent created:>{since}",
                f"multi-agent created:>{since}",
            ]:
                params = {
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 20,
                }
                data = self._api_request(url, params)
                if data and "items" in data:
                    for item in data["items"]:
                        repos.append({
                            "name": item["full_name"],
                            "url": item["html_url"],
                            "description": item.get("description") or "",
                            "stars": item["stargazers_count"],
                            "stars_today": 0,
                            "language": item.get("language") or "",
                            "source": f"search:{query.split(' created')[0]}",
                        })
                time.sleep(2)
        except Exception as e:
            print(f"  [GitHub] 搜索失败: {e}")
        print(f"  获取 {len(repos)} 个项目")
        return repos

    def collect_all(self) -> List[Dict]:
        all_repos = []
        seen = set()
        # 1) Trending
        try:
            all_repos.extend(self.fetch_trending())
        except Exception as e:
            print(f"  Trending 抓取失败: {e}")
        # 2) 近期热门搜索
        try:
            all_repos.extend(self.fetch_recent_popular())
        except Exception as e:
            print(f"  热门搜索失败: {e}")
        # 3) 按主题抓取
        for topic in self.topics[:5]:
            try:
                all_repos.extend(self.fetch_by_topic(topic, limit=8))
            except Exception as e:
                print(f"  Topic '{topic}' 失败: {e}")
        # 去重 + 过滤 + 排序
        unique = []
        for r in all_repos:
            key = r["name"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(r)
        # 关键词匹配
        for r in unique:
            text = f"{r['name']} {r['description']}"
            matched = []
            for kw in self.all_keywords:
                if kw.lower() in text.lower():
                    matched.append(kw)
            r["matched_keywords"] = matched
            r["score"] = (1 if matched else 0) * 10000 + r["stars"]
        # 过滤最少星数
        unique = [r for r in unique if r["stars"] >= self.min_stars]
        unique.sort(key=lambda x: x["score"], reverse=True)
        return unique[: self.top_n * 2]
