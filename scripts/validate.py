#!/usr/bin/env python3
"""檢查 data/videos.json 結構同資料原則，CI 同本地都用得。

規則重點：
1. 精確數字必須有 source（出處 + 統計期間），metric_kind 講明數字係咩類型
2. Google Trends 熱度 ≠ 觀看次數，所以 metric_kind 一定要係「搜尋熱度」
3. YouTube 冇官方 Shorts 熱門榜 → source 必須寫明取數方法（搜尋／官方／頻道）
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "videos.json"

PLATFORMS = {"Netflix", "YouTube", "網絡"}
KINDS = {"官方榜", "搜尋結果", "搜尋熱度"}
REQUIRED = ["date", "platform", "category", "rank", "title", "metric_kind", "url", "source"]
YT_METHOD = ("搜尋", "官方", "頻道", "Shorts")


def fail(errors, msg):
    errors.append(msg)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    errors = []
    items = data.get("items") or []

    if not isinstance(items, list) or not items:
        fail(errors, "items 係空或唔係陣列")
        items = []

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get("updated", ""))):
        fail(errors, f"updated 格式錯：{data.get('updated')!r}")
    else:
        try:
            dt.date.fromisoformat(data["updated"])
        except ValueError:
            fail(errors, f"updated 唔係有效日期：{data['updated']}")

    seen_rank, seen_title = set(), set()
    for i, it in enumerate(items):
        tag = f"items[{i}] {it.get('title', '?')}"
        for k in REQUIRED:
            if not str(it.get(k, "")).strip():
                fail(errors, f"{tag}：缺少 {k}")
        if it.get("platform") not in PLATFORMS:
            fail(errors, f"{tag}：platform 唔合法（{it.get('platform')}）")
        if it.get("metric_kind") not in KINDS:
            fail(errors, f"{tag}：metric_kind 唔合法（{it.get('metric_kind')}），只可用 {sorted(KINDS)}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(it.get("date", ""))):
            fail(errors, f"{tag}：date 格式錯")
        if not isinstance(it.get("rank"), int) or not 1 <= it["rank"] <= 50:
            fail(errors, f"{tag}：rank 要係 1–50 嘅整數")
        if not re.match(r"^https://", str(it.get("url", ""))):
            fail(errors, f"{tag}：url 要係 https")

        if it.get("platform") == "YouTube" and not any(m in str(it.get("source", "")) for m in YT_METHOD):
            fail(errors, f"{tag}：YouTube 條目 source 要寫明取數方法（{ '/'.join(YT_METHOD) }）")
        if it.get("metric_kind") == "搜尋熱度" and str(it.get("metric", "")) != "熱搜話題":
            fail(errors, f"{tag}：搜尋熱度嘅 metric 應該係「熱搜話題」，唔好寫成觀看數")

        rk = (it.get("date"), it.get("platform"), it.get("category"), it.get("rank"))
        if rk in seen_rank:
            fail(errors, f"{tag}：同一日同平台同類別排名重複 {rk}")
        seen_rank.add(rk)

        tk = (it.get("date"), str(it.get("title", "")).strip())
        if tk in seen_title:
            fail(errors, f"{tag}：同一日標題重複")
        seen_title.add(tk)

    if items:
        latest = max(x["date"] for x in items)
        if data.get("updated") != latest:
            fail(errors, f"updated（{data.get('updated')}）應該等於最新日期（{latest}）")

    if errors:
        print(f"✗ 驗證失敗，{len(errors)} 個問題：", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        return 1

    days = len({x["date"] for x in items})
    print(f"✓ 驗證通過：{len(items)} 條 / {days} 日 / 最新 {data['updated']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
