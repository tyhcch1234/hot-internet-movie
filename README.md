# Hot Internet Movie · 每日熱片庫

每日最新興嘅影片／熱話，一日一版，持續累積。

- 網站：<https://tyhcch1234.github.io/hot-internet-movie/>
- 內容：Netflix 官方 Top 10、YouTube 熱片、香港網絡熱搜
- 累積方式：所有條目存在 `data/videos.json`，新日子直接加，舊資料永不覆蓋

## 目錄

```
index.html            # 單頁網站（自動讀 data/videos.json）
data/videos.json      # 唯一資料來源，逐日累積
archive/YYYY-MM-DD.md # 每日文字版存檔（可選）
```

## 每日新增一條片

在 `data/videos.json` 的 `items` 陣列最前面加一個物件，再更新 `updated`：

```json
{
  "date": "2026-10-31",
  "platform": "YouTube",
  "category": "短片",
  "rank": 1,
  "title": "片名",
  "metric": "1.2M 觀看（48 小時）",
  "note": "一句話講下亮點。",
  "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
  "source": "YouTube 搜尋「本週最多觀看」"
}
```

欄位規則：

| 欄位 | 必填 | 說明 |
|------|------|------|
| `date` | ✅ | `YYYY-MM-DD`，同一日共用同一個日期，網站會自動分組 |
| `platform` | ✅ | `Netflix` / `YouTube` / `網絡`（決定標籤顏色同篩選） |
| `category` | ✅ | 例：劇集、電影、短片、熱搜 |
| `rank` | ✅ | 當日排名，同平台同類別內排序 |
| `title` | ✅ | 片名／話題名 |
| `metric` | ➖ | 觀看數、榜單位置等；**冇可靠數字就留空或寫「熱搜話題」，不要估** |
| `note` | ➖ | 一句話賣點 |
| `url` | ✅ | 可驗證的原始連結 |
| `source` | ✅ | 數字／排名的出處同統計期間 |

## 資料原則

1. **每個數字都要有出處**：Netflix 用 Tudum 官方榜（每週一更新，統計上一個完整週）；熱搜用 Google Trends；YouTube 用搜尋結果顯示的觀看數。
2. **區分「觀看次數」同「熱度」**：Google Trends 只代表搜尋熱度，不可寫成觀看量。
3. **YouTube 沒有公開 Shorts 熱門榜**（官方 Trending 頁已下線），所以 YouTube 條目一律註明取數方法，例如「YouTube 搜尋：本週＋最多觀看」。
4. **重複條目**：同一節目連續上榜可以逐日再收錄（`date` 不同），但 `note` 要更新為當日情況。

## 本機預覽

```bash
cd hot-internet-movie
python3 -m http.server 8000
# 開 http://localhost:8000
```

直接開 `index.html`（file://）會因為瀏覽器安全限制讀不到 JSON，所以要起本地 server。
