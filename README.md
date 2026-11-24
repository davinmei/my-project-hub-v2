# My Project Hub 2.0｜個人專案作品展示平台

從生成式 AI 課程作品展示延伸的個人作品集。網站使用 **HTML、CSS、原生 JavaScript 與 JSON**，目前收錄五個課程作品，並可擴充個人專案、產學合作及研究專案。備援同步及資料維護工具使用 Python 標準函式庫。

- **V1 原始繳交版**：[my-project-hub](https://github.com/davinmei/my-project-hub)
- **V2 補交改良版**：[GitHub 儲存庫](https://github.com/davinmei/my-project-hub-v2) · [GitHub Pages](https://davinmei.github.io/my-project-hub-v2/)

V1 為原始繳交快照。V2 是持續維護版本，加入新版首頁、雙重篩選、LLM Wiki、個人資料頁及可離線執行的資料工具。

## 功能
- 首頁：從 JSON 計算作品、技術分類及專案類型數量，展示最新作品及前兩筆標為精選的作品。
- 作品總覽：即時搜尋可與專案類型和技術分類同時使用，支援三種排序、結果計數、清除條件及空狀態。
- 作品詳細頁：共用 `project.html?id=<id>` 模板，依資料顯示流程圖、多張截圖和相關連結。實際截圖可放大，並可用關閉按鈕或 Esc 返回。
- 關於我：依 `data/profile.json` 呈現個人簡介、學習背景、技術能力、興趣與發展方向、公開連結及網站介紹。
- 響應式版型與鍵盤操作支援
- 維護工具：同步作品與個人資料備援，離線檢查欄位、圖片、網址格式和備援一致性。

## 專案架構

| 路徑 | 用途 |
|---|---|
| `index.html`、`projects.html`、`project.html`、`about.html` | 首頁、作品總覽、共用作品詳細頁、關於我 |
| `css/style.css`、`js/` | 共用樣式、資料載入、導覽及各頁渲染 |
| `data/projects.json`、`data/profile.json` | 作品與個人資料的正式來源 |
| `data/projects-data.js`、`data/profile-data.js` | 從 JSON 產生的瀏覽器備援 |
| `assets/images/` | 封面、成果截圖與流程圖 |
| `scripts/`、`tests/` | Python 同步及驗證工具、隔離資料測試 |
| `AGENTS.md` | AI 協作、公開資料、測試及 Git 維護規範 |

## Phase 1 至 Phase 5

| 階段 | 成果 |
|---|---|
| Phase 1 | 簡約科技風首頁、統計、最新與精選作品 |
| Phase 2 | 即時搜尋、雙重分類、三種排序、共用詳細頁與可放大的成果截圖 |
| Phase 3 | 追加智慧家庭能源管理 LLM Wiki，驗證以資料和素材擴充作品 |
| Phase 4 | 新增關於我、個人資料 JSON 與四頁導覽 |
| Phase 5 | 備援同步、離線驗證、單元測試及完整 AI 維護流程 |

## 目前收錄作品（5 個課程作業）
- **AI 面試模擬系統｜林教練**：AI Suite + Groq + Gradio 面試練習
- **毛孩新手村｜AI 貓狗飼養顧問**：EmbeddingGemma 2、FAISS、Groq RAG 問答（RAG01 + RAG02）
- **AI 智慧行程規劃與反思助手**：Planner → Reviewer → Reviser 三階段行程規劃
- **出門準備檢查助手（Ready to Go）**：HTML、CSS、原生 JavaScript、localStorage、Canvas 與 SVG；情境模板、多清單、本機使用者分頁及準備進度（Web App）
- **智慧家庭能源管理 LLM Wiki**：第九週課程作業。依六份來源建立可追溯的 Wiki，並以九頁 HTML 互動簡報展示教學 Query、排程模擬及測驗。 [線上簡報](https://davinmei.github.io/smart-home-llm-wiki/slides/index.html) · [Wiki 知識索引](https://github.com/davinmei/smart-home-llm-wiki/blob/main/wiki/index.md)

五個作品均使用實際操作畫面作為封面。前四個作品的介紹根據 Notebook、Web App 原始碼與說明整理，未執行 Notebook 的 API 呼叫。這四個作品的線上展示及原始碼網址仍待提供。

第四個作品使用 `assets/images/packing-checklist.png`，詳細介紹位於 `project.html?id=packing-checklist`。來源檔案 `incoming-projects/packing-checklist/index.html` 保持原樣；清單資料僅保存於目前瀏覽器，不會同步至其他裝置。出門清單應用本身的完整操作、重新載入保存與手機版面驗收仍待進行，個人開發心得待補。

## 在電腦上預覽

**可以直接雙擊 `index.html` 或 `about.html` 開啟網站**。直接開啟時使用 `data/projects-data.js` 或 `data/profile-data.js` 的備援，透過 HTTP 預覽及 GitHub Pages 優先讀取相應的 JSON。

有 Python 時，在本專案資料夾執行：

```bash
python -m http.server 8000 --bind 127.0.0.1
```

再開啟 `http://localhost:8000/`。若啟動位置是專案的上一層，請開啟 `http://localhost:8000/my-project-hub-v2/`。

## 上傳 GitHub Pages

1. 確認目前位於 V2，並以 `git remote get-url origin` 及 `git remote get-url --push origin` 核對兩個遠端都指向 `my-project-hub-v2.git`。
2. 執行下方的備援同步、資料驗證與測試，再用模擬專案子路徑預覽。`incoming-projects/` 由 Git 忽略，僅供本機參考。
3. 取得使用者授權後才提交並推送至 V2 的 `main`。在 V2 的 **Settings → Pages** 選擇 **Deploy from a branch**，設定 `main` 和 `/ (root)`。
4. 等候部署完成後，在 Pages 設定頁開啟實際網址。確認首頁統計、精選、搜尋、分類、排序、詳細頁及關於我正常，再回報部署結果。

## 如何透過 AI 新增作品

先讀 [AGENTS.md](AGENTS.md)，提供 `.ipynb`、README、儲存庫或操作截圖。核對來源並整理草稿，由使用者確認公開內容後才新增至 `data/projects.json` 與 `assets/images/`。接著同步備援、執行資料驗證與相關瀏覽器檢查，回報結果。Git 提交與部署另待使用者授權。

### 第四個作品的擴充驗證

本次依 `AGENTS.md` 完成第四個作品的原始碼分析、資料草稿及使用者確認後，追加至相同 JSON 陣列，並由 JSON 重新產生本機備援資料。原本三個作品資料、圖片、HTML 版型及共用 CSS 保持不變；本次使用第四個作品驗證資料驅動的擴充流程。

### Phase 3 作品擴充

LLM Wiki 使用既有的 `systemDiagram`、`screenshots` 與 `links`，技術分類由 JSON 直接產生。首頁沿用精選區最多兩筆的規則，LLM Wiki 獨立顯示於最新作品區。

本次擴充新增五個素材、更新四個檔案：

| 用途 | 檔案 |
|---|---|
| 新作品與本機備援 | `data/projects.json`、`data/projects-data.js` |
| 新分類規範與擴充紀錄 | `AGENTS.md`、`README.md` |
| 封面 | `assets/images/smart-home-llm-wiki-cover.webp` |
| 成果截圖 | `assets/images/smart-home-llm-wiki-knowledge.webp`、`assets/images/smart-home-llm-wiki-simulation.webp`、`assets/images/smart-home-llm-wiki-quiz.webp` |
| 工作流程圖 | `assets/images/smart-home-llm-wiki-workflow.svg` |

首頁統計由 4 個作品、4 個技術分類、1 個專案類型變為 5、5、1。共用 HTML、CSS 與渲染程式逐檔比對一致。

## 安全與限制
- 不放 API 金鑰、憑證或私人資料；不要把含密鑰的原始 Notebook 直接公開。
- 目前網站為**靜態作品展示**，不是已上線的 AI 面試或 RAG 互動服務。
- 作品詳細頁依資料顯示已確認的 HTTPS 連結。

## 備援同步、資料驗證與測試

在 V2 根目錄使用 Python 3.10 以上執行，工具只用標準函式庫：

```powershell
python scripts/sync_data.py
python scripts/sync_data.py --check
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

- `sync_data.py` 先解析兩份正式 JSON，再產生或更新有差異的備援。透過暫存檔原子替換，重複執行時相同內容不會重新寫入。
- `sync_data.py --check` 為唯讀檢查。備援缺少或生成格式有差異時回傳非零，接受 LF 與 CRLF 換行。
- `validate_data.py` 檢查兩份 JSON 的結構、作品與個人欄位、圖片位置、網址格式和備援的解析後內容。驗證預設離線，資料錯誤回傳非零，警告不影響通過。HTTP 語法可通過格式檢查，但會提示網站只顯示 HTTPS。
- `unittest` 使用暫存資料測試有效與無效欄位、路徑、網址、備援和同步失敗。保留瀏覽器驗收，確認頁面行為、圖片解碼及 GitHub Pages 子路徑。

`data/projects.json` 與 `data/profile.json` 是各自的唯一編輯來源。備援格式分別為 `window.PROJECTS_FALLBACK = <JSON 陣列>;` 與 `window.PROFILE_FALLBACK = <JSON 物件>;`。由同步工具生成，勿手動編輯。

### Phase 2 選填欄位

| 欄位 | 用途 |
|---|---|
| `projectType` | 課程作業、個人專案、產學合作或研究專案 |
| `courseWeek` | 經確認的課程週次，使用正整數 |
| `projectDate` | 經確認的作品日期，使用 `YYYY-MM-DD` |
| `systemDiagram` | 流程圖，物件包含相對路徑 `src` 與替代文字 `alt` |
| `screenshots` | 額外成果截圖陣列，每筆包含 `src` 與 `alt` |
| `links` | 額外相關連結陣列，每筆包含 `label` 與完整 HTTPS 網址 `url` |

維持既有 `category`、`image`、`imageAlt`、`imageType`、`githubUrl` 與 `demoUrl`，技術分類、封面、GitHub 原始碼和線上展示繼續使用這些欄位。詳細頁隱藏缺少資料的區塊，也會略過格式無效或重複的連結。原有實際截圖封面可直接放大。

### 搜尋、篩選與排序

- 關鍵字比對名稱、摘要、詳細介紹、技術分類、技術標籤及專案類型。英文不分大小寫。
- 關鍵字、專案類型和技術分類同時套用。技術分類選項由 JSON 自動產生，缺少類型的舊資料仍可在「全部類型」瀏覽。清除條件會復原所有欄位及預設排序。
- 預設為最新加入優先，也可選最早加入或名稱排序。首頁最新與總覽加入順序共用 `addedOrder`。缺少時用原始陣列位置（從 1 起算），同值則按原始位置破同分，最新排序取較後者優先。名稱依繁體中文語系排序，英文不分大小寫。
- `addedOrder` 記錄網站收錄順序，`projectDate` 記錄作品日期。首頁統計實際存在的技術分類與專案類型。

## 關於我資料

`about.html` 的個人資料集中在 `data/profile.json`，由 `js/about.js` 渲染。`js/site-data.js` 提供關於我與作品頁共用的 JSON 和備援載入方式。

| 欄位 | 資料格式 |
|---|---|
| `intro` | 身分 `role`、英文身分 `roleEn` 與簡介 `description` |
| `education` | 學習背景陣列，每筆包含校名 `school`、系所 `program` 與學位或就讀狀態 `degree` |
| `skills` | 說明 `note` 與分類陣列 `groups`，每組含 `title` 及 `technologies` 字串陣列 |
| `interests` | 興趣與發展方向陣列，每筆含 `title` 及 `description` |
| `links` | 已確認的公開連結陣列，每筆含 `label` 及 HTTPS `url` |
| `site.paragraphs` | 網站介紹的文字段落陣列 |

修改本人同意公開的內容時，編輯 `data/profile.json`，使用上方指令同步與驗證，再透過 HTTP 或直接開啟 `about.html` 確認內容。

僅發布本人確認公開的資料。聯絡資訊、個人照片、學歷日期、研究細節、經歷或履歷連結須先確認，私人資料及合作機密不得放入公開 JSON 或備援。技術標籤用於呈現接觸或實作過的領域。

### 共用導覽

首頁、作品總覽、作品詳細與關於我共用同一組主要導覽及頁尾連結。頁尾提供「V2 原始碼」與「V1 原版參考」，分別連向各自的儲存庫。更新時同步檢查四頁的相對路徑、順序和選取狀態。首頁、作品總覽、關於我使用 `aria-current="page"` 標示當前頁面，作品詳細頁以 `aria-current="location"` 標示作品總覽區段。

## 網站最後更新

2026-11-24。首頁日期由 `js/site-update.js` 的 `SITE_LAST_UPDATED` 固定設定，僅在實際修改網站內容時更新。
