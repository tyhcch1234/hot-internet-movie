# Hot Internet Movie · 每日熱片庫

每日最新興嘅影片／熱話，一日一版，持續累積。

- 網站：<https://tyhcch1234.github.io/hot-internet-movie/>
- 內容：Netflix 官方 Top 10、YouTube 熱片、香港網絡熱搜
- 累積方式：所有條目存在 `data/videos.json`，新日子直接加，舊資料永不覆蓋
- 自動化：GitHub Actions 每日香港時間 10:00 抓 Google Trends 香港熱搜

## 目錄

```
index.html              # 單頁網站（自動讀 data/videos.json）
data/videos.json        # 唯一資料來源，逐日累積
scripts/fetch_trends.py # 抓 Google Trends HK → 追加條目
scripts/validate.py     # 資料驗證（CI 會跑，唔過就唔會 commit）
.github/workflows/daily.yml  # 每日 10:00 HKT 定時任務
archive/YYYY-MM-DD.md   # 每日文字版存檔（可選）
```

## 自動更新

`.github/workflows/daily.yml` 每日 `0 2 * * *`（UTC）= **香港時間 10:00** 執行：

1. `fetch_trends.py` 抓 Google Trends 香港即時熱搜（最多 10 條，自動去重）
2. `validate.py` 驗證格式同資料原則
3. 有變動才 commit + push，Pages 約一分鐘後更新

注意：香港時間 10:00 是 cron 的預定時間，GitHub 排隊通常有數分鐘延遲；
同一日已有「網絡／熱搜」條目時會自動跳過，唔會重複加。

手動觸發：repo → Actions → **Daily trending update** → Run workflow。

本機試跑：

```bash
python3 scripts/fetch_trends.py --dry-run   # 只印出抓到嘅話題
python3 scripts/fetch_trends.py             # 真正寫入（同日已有就跳過）
python3 scripts/validate.py                 # 檢查資料
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
  "metric_kind": "搜尋結果",
  "note": "一句話講下亮點。",
  "url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
  "source": "YouTube 搜尋：本週＋最多觀看"
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `date` | ✅ | `YYYY-MM-DD`，同日共用同一日期，網站自動分組 |
| `platform` | ✅ | `Netflix` / `YouTube` / `網絡`（決定標籤顏色同篩選） |
| `category` | ✅ | 例：劇集、電影、短片、熱搜 |
| `rank` | ✅ | 當日排名（1–50），同平台同類別內排序 |
| `title` | ✅ | 片名／話題名 |
| `metric` | ✅ | 觀看數／榜位；熱搜話題一律寫「熱搜話題」 |
| `metric_kind` | ✅ | 只可 `官方榜` / `搜尋結果` / `搜尋熱度` |
| `note` | ➖ | 一句話賣點 |
| `url` | ✅ | 可驗證的 https 原始連結 |
| `source` | ✅ | 數字／排名的出處同統計期間 |

## 資料原則（`validate.py` 會強制）

1. **每個數字都要有出處**：Netflix 用 Tudum 官方榜（每週更新，統計上一個完整週）；熱搜用 Google Trends；YouTube 用搜尋結果顯示的觀看數。
2. **`metric_kind` 講清楚數字類型**：
   - `官方榜` — 平台官方排行榜數字（例：Netflix 7.7M 觀看／週）
   - `搜尋結果` — 自己搜尋／抓取所見（例：YouTube 觀看數）
   - `搜尋熱度` — Google Trends 熱度，**不是**觀看次數，`metric` 必須寫「熱搜話題」
3. **YouTube 沒有公開 Shorts 熱門榜**（官方 Trending 頁已下線），所以 YouTube 條目 `source` 一定要寫明取數方法，例如：
   - `YouTube 搜尋：本週＋最多觀看`
   - `YouTube 官方頻道：上載 24 小時`
   - `YouTube Shorts：頻道頁面`
   驗證器見到 YouTube 條目冇「搜尋／官方／頻道／Shorts」字眼就會 fail。
4. **重複條目**：同一節目連續上榜可以逐日再收錄（`date` 不同），但 `note` 要更新為當日情況。

## 本機預覽

```bash
cd hot-internet-movie
python3 -m http.server 8000
# 開 http://localhost:8000
```

直接開 `index.html`（file://）會因為瀏覽器安全限制讀不到 JSON，所以要起本地 server。
