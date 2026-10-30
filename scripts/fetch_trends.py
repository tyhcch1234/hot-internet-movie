#!/usr/bin/env python3
"""每日抓 Google Trends（香港）即時熱搜，追加到 data/videos.json。

設計原則：
- 只寫入 data/videos.json，永不覆蓋舊日子
- 同一日已有「網絡／熱搜」條目就跳過（避免每日 workflow 重複加）
- 抓唔到嘢就靜靜退出（exit 0），唔好令 workflow 變紅
- 每條都寫明 source，數字類型寫入 metric_kind

用法：
    python3 scripts/fetch_trends.py            # 正式寫入
    python3 scripts/fetch_trends.py --dry-run  # 只印出抓到的話題
    python3 scripts/fetch_trends.py --max 10   # 每日最多幾條（預設 10）
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "videos.json"

FEED = "https://trends.google.com/trending/rss?geo=HK"
UA = "Mozilla/5.0 (compatible; hot-internet-movie/1.0)"
NS = "{https://trends.google.com/trending/rss}"
HT = NS + "news_item"
HKT = dt.timezone(dt.timedelta(hours=8))


def fetch(url=FEED, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-HK,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse(raw, limit):
    root = ET.fromstring(raw)
    out = []
    for item in root.iter("item"):
        title_el = item.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue
        news = item.find(HT)
        headline, link = "", ""
        if news is not None:
            # 子元素同樣帶 namespace，必須用 NS 前綴搵
            t = news.find(NS + "news_item_title")
            u = news.find(NS + "news_item_url")
            headline = (t.text or "").strip() if t is not None else ""
            link = (u.text or "").strip() if u is not None else ""
        if not link:
            # 退一步：部分話題冇新聞連結，用 Google Trends 該話題頁
            link = f"https://trends.google.com/trends/explore?geo=HK&q={urllib.parse.quote(title)}"
        if not link:
            continue
        note = re.sub(r"\s+", " ", headline)[:90] or "Google Trends 香港即時熱搜話題。"
        out.append({
            "date": dt.datetime.now(HKT).strftime("%Y-%m-%d"),
            "platform": "網絡",
            "category": "熱搜",
            "rank": len(out) + 1,
            "title": title,
            "metric": "熱搜話題",
            "metric_kind": "搜尋熱度",
            "note": note,
            "url": link,
            "source": "Google Trends HK 即時熱搜（自動抓取）",
        })
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max", type=int, default=10)
    args = ap.parse_args()

    today = dt.datetime.now(HKT).strftime("%Y-%m-%d")
    try:
        items = parse(fetch(), args.max)
    except Exception as e:  # 網絡／格式問題：唔應該中斷整個 workflow
        print(f"[skip] 抓取失敗：{e}", file=sys.stderr)
        return 0

    if not items:
        print("[skip] 今日 feed 冇內容")
        return 0

    print(f"[ok] 抓到 {len(items)} 個熱搜話題（{today}）")
    for i in items:
        print(f"  #{i['rank']} {i['title']}")

    if args.dry_run:
        return 0

    data = json.loads(DATA.read_text(encoding="utf-8"))
    existing = {(x["date"], x["platform"], x["category"]) for x in data["items"]}
    if (today, "網絡", "熱搜") in existing:
        print("[skip] 今日已經有熱搜條目，唔重複加")
        return 0

    taken = {x["title"] for x in data["items"] if x["date"] >= (
        dt.datetime.now(HKT) - dt.timedelta(days=7)).strftime("%Y-%m-%d")}
    new = [i for i in items if i["title"] not in taken]
    for n, i in enumerate(new, 1):
        i["rank"] = n

    data["items"] = new + data["items"]
    data["updated"] = max([data.get("updated", today), today])
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[done] 新增 {len(new)} 條，總數 {len(data['items'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
