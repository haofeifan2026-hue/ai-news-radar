#!/usr/bin/env python3
"""Collect AI-related items from RSS, GitHub, Reddit, and optional X RSS bridges."""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import pathlib
import re
import sys
from typing import Any

import feedparser
import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG = ROOT / "config.yaml"


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def item_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def rss_items(name: str, url: str, limit: int) -> list[dict[str, str]]:
    parsed = feedparser.parse(url)
    out = []
    for entry in parsed.entries[:limit]:
        link = entry.get("link", "")
        if not link:
            continue
        out.append({"id": item_id(link), "source": name, "title": clean(entry.get("title", "")), "url": link, "summary": clean(entry.get("summary", ""))})
    return out


def github_items(cfg: dict[str, Any], limit: int) -> list[dict[str, str]]:
    headers = {"Accept": "application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    out = []
    for repo in cfg.get("repositories", []):
        data = requests.get(f"https://api.github.com/repos/{repo}/releases", headers=headers, timeout=20).json()
        for release in data[:limit]:
            url = release.get("html_url", "")
            out.append({"id": item_id(url), "source": f"GitHub: {repo}", "title": clean(release.get("name") or release.get("tag_name", "")), "url": url, "summary": clean(release.get("body", ""))})
    for query in cfg.get("searches", []):
        data = requests.get("https://api.github.com/search/repositories", params={"q": query, "sort": "updated", "per_page": limit}, headers=headers, timeout=20).json()
        for repo in data.get("items", []):
            url = repo.get("html_url", "")
            out.append({"id": item_id(url), "source": "GitHub Search", "title": clean(repo.get("full_name", "")), "url": url, "summary": clean(repo.get("description", ""))})
    return out


def reddit_items(cfg: dict[str, Any], limit: int) -> list[dict[str, str]]:
    out = []
    headers = {"User-Agent": "codex-ai-radar/1.0"}
    for subreddit in cfg.get("subreddits", []):
        data = requests.get(f"https://www.reddit.com/r/{subreddit}/new.json", params={"limit": limit}, headers=headers, timeout=20).json()
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            url = "https://www.reddit.com" + post.get("permalink", "")
            out.append({"id": item_id(url), "source": f"Reddit: r/{subreddit}", "title": clean(post.get("title", "")), "url": url, "summary": clean(post.get("selftext", ""))})
    return out


def render(items: list[dict[str, str]], output_dir: pathlib.Path) -> None:
    today = dt.datetime.now().strftime("%Y-%m-%d")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{today}.md"
    lines = [f"---\ndate: {today}\ntags: [ai-radar, codex, obsidian]\n---", "", f"# AI 资讯雷达 · {today}", "", "> 自动收集；发布前请人工核验来源、时间和结论。", ""]
    for entry in items:
        lines += [f"## {entry['title']}", f"- 来源：{entry['source']}", f"- 链接：[{entry['url']}]({entry['url']})", f"- 摘要：{entry['summary'][:600] or '暂无摘要'}", f"- 采集 ID：`{entry['id']}`", ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    limit = int(cfg.get("max_items_per_source", 20))
    items = []
    items += github_items(cfg.get("github", {}), limit)
    items += reddit_items(cfg.get("reddit", {}), limit)
    for feed in cfg.get("feeds", []):
        items += rss_items(feed["name"], feed["url"], limit)
    xcfg = cfg.get("x", {})
    if xcfg.get("enabled"):
        for url in xcfg.get("rss_urls", []):
            items += rss_items("X/Twitter", url, limit)
    deduped = {entry["id"]: entry for entry in items}
    render(list(deduped.values()), ROOT / cfg.get("output_dir", "inbox/ai-radar"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"collector failed: {exc}", file=sys.stderr)
        raise
