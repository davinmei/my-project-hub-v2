# My Project Hub 2.0 — AI 開發與維護規範

## 1. 專案目的與工作原則

My Project Hub 2.0 源於生成式 AI 課程作業，現作為可長期擴充的個人作品集。網站集中展示 Web App、AI / LLM、RAG、AI Agent、LLM Wiki 等成果，未來可收錄課程作業、個人專案、產學合作與研究專案。訪客可搜尋、篩選並閱讀共用版型的作品介紹，或前往公開的原始碼及展示。

**最重要的設計原則：新作品以資料驅動方式新增，盡量不修改既有 HTML 版型。** AI 應先讀取此文件及現有資料，再進行任何更動；不得只憑專案名稱推測實際功能。

## 2. 技術與部署限制

- 網站使用 HTML、CSS、原生 JavaScript 與 JSON。維護工具使用 Python 3.10 以上及標準函式庫。除非使用者明確同意，不新增前端框架、後端、資料庫或付費服務。
- 以 GitHub Pages 作為預設部署環境；所有站內資源使用能在 GitHub Pages 專案子路徑運作的相對 URL，不假設部署在網域根目錄。
- 本版的儲存庫與部署子路徑使用 `my-project-hub-v2`。頁尾的「V2 原始碼」連到維護版儲存庫，「V1 原版參考」連到原始繳交儲存庫。V2 的 Pages 位址見 README。
- 不得把 API Key、密碼、Colab secrets、個人私密資訊或其他憑證寫入網站資料、程式碼、截圖或 Git 歷史。
- 網站文字以繁體中文為主；技術名稱保留官方英文名稱。
- 必須可在桌面與手機上閱讀，使用語意化 HTML，確保鍵盤可操作與圖片有替代文字。

## 3. 固定網站頁面

1. `index.html`：首頁。顯示站點介紹、作品數、技術分類數與專案類型數，以及從資料中選出的最新和精選作品。未填的類型不列入類型數。
2. `projects.html`：作品總覽。即時搜尋作品名稱、摘要、詳細介紹、技術分類、技術標籤與專案類型，英文不分大小寫。關鍵字、專案類型與技術分類為交集條件，技術分類由資料產生。可查看結果數量、切換排序或一鍵清除條件。
3. `project.html?id=<project-id>`：作品詳細頁。用同一模板呈現不同作品，不為每個作品各建一個 HTML 檔。
4. `about.html`：關於我。依 `data/profile.json` 呈現個人簡介、學習背景、技術領域、興趣、公開連結與網站介紹。

詳細頁依序呈現返回連結、標題與基本資訊、封面、專案動機、專案介紹、核心功能、系統流程圖、開發成果、成果截圖、使用技術、學習與反思及相關連結。缺資料的區塊自動隱藏，僅寫「待補充」的心得視為無內容。封面標為實際截圖時可點擊放大，額外截圖可逐張放大並用關閉按鈕或 Esc 返回。找不到指定 ID 時提供返回作品總覽的連結。

## 4. 檔案架構與責任分工

```text
my-project-hub-v2/
├── AGENTS.md                # AI 開發與維護規範（本檔）
├── README.md                # 人類讀者的專案介紹、執行及部署說明
├── index.html               # 首頁
├── projects.html            # 作品列表
├── project.html             # 共用作品詳細頁
├── about.html               # 關於我
├── css/
│   └── style.css            # 全站共用外觀、元件與響應式規則
├── js/
│   ├── site-data.js         # 共用 JSON 與備援資料載入
│   ├── main.js              # 共用導覽與首頁行為
│   ├── projects.js          # 專案資料讀取、搜尋、篩選、列表呈現
│   ├── project-detail.js    # 依 URL id 呈現詳細頁
│   └── about.js             # 渲染關於我
├── data/
│   ├── projects.json        # 全站唯一的作品編輯來源
│   ├── projects-data.js     # 作品資料的本機預覽備援
│   ├── profile.json         # 關於我的唯一編輯來源
│   └── profile-data.js      # 個人資料的本機預覽備援
├── assets/
│   └── images/             # 實際作品截圖或明確標示的預設圖
├── scripts/
│   ├── sync_data.py        # 從正式 JSON 同步備援
│   └── validate_data.py    # 離線驗證資料、路徑、網址格式及備援
└── tests/
    └── test_data_validation.py  # 使用暫存資料的單元測試
```

**`data/projects.json` 與 `data/profile.json` 分別是作品與個人資料的唯一正式來源。** 修改 JSON 後執行 `python scripts/sync_data.py`，從來源產生 `projects-data.js` 與 `profile-data.js`。備援由工具生成，禁止手動分別維護或反向覆蓋 JSON。

兩種資料共用 `js/site-data.js`。HTTP 和 GitHub Pages 優先透過 `fetch` 讀取 JSON，讀取或格式檢查失敗時使用備援。以 `file://` 直接開啟時，由一般 script 標籤載入備援。

單純新增作品時，修改 `data/projects.json`、同步備援並加入必要的圖片。依需要更新文件或網站日期。共用詳細頁維持資料驅動，避免為單一作品新增 HTML 或硬編碼渲染邏輯。

## 5. 介面風格與共用元件

- 整體風格：清爽、專業的科技藍白色系，白／淺灰背景、藍色強調色，卡片式作品展示。
- 導覽列、按鈕、卡片、標籤、字體層級、邊距與頁尾遵守共用 CSS，勿在單一新作品內任意加入另一套設計。
- 維護首頁、作品總覽、作品詳細與關於我四頁的導覽及頁尾時，同步更新相對連結與順序。主要導覽固定為「首頁、作品總覽、關於我」。對應頁使用 `aria-current="page"`，作品詳細頁的作品總覽連結使用 `aria-current="location"`。使用 `active` 樣式標示目前頁面或區段。
- 手機單欄、寬螢幕多欄的作品卡片排列；避免水平溢出。
- 卡片至少顯示封面、作品名稱、技術分類、簡短摘要與技術標籤。總覽卡片另顯示已填的專案類型與作業週次。已完成／開發中使用明確文字標示。
- 搜尋、篩選與詳細頁必須從同一份 JSON 產生，避免三個地方內容不一致。
- 保留足夠對比、可見的鍵盤焦點、合理的圖片比例及載入／失敗訊息。

## 6. 作品資料規格

`data/projects.json` 是 **JSON 陣列**，每個元素為一個作品物件。使用下列統一欄位：

| 欄位 | 型別 | 必填 | 規則 |
|---|---|---|---|
| `id` | string | 是 | 唯一，英數小寫與連字號，例如 `pet-rag-advisor`；建立後不隨意變更 |
| `title` | string | 是 | 確實存在的作品名稱 |
| `category` | string | 是 | 限 `Web App`、`AI / LLM`、`RAG`、`AI Agent`、`LLM Wiki`、`Other` |
| `summary` | string | 是 | 作品卡片使用的一至兩句簡介 |
| `description` | string | 是 | 作品詳細介紹 |
| `motivation` | string | 是 | 開發動機，僅寫有依據的內容 |
| `features` | string[] | 是 | 已實作的主要功能；未完成功能不得混入 |
| `technologies` | string[] | 是 | 程式碼或文件可支持的技術名稱 |
| `results` | string | 是 | 已實現的成果或目前進度，不虛構量化數據 |
| `lessonsLearned` | string | 是 | 有依據的心得；資料不足時可填 `待補充` |
| `image` | string | 是 | 相對路徑，例如 `assets/images/pet-rag-advisor.png`；無截圖用網站統一的預設圖片 |
| `imageAlt` | string | 是 | 描述圖片內容；預設圖需明確標示非實際截圖 |
| `demoUrl` | string | 是 | 完整 `https://` 網址或空字串；不得捏造 |
| `githubUrl` | string | 是 | 完整 `https://` 網址或空字串；不得捏造 |
| `status` | string | 是 | `completed` 或 `in-progress` |
| `featured` | boolean | 是 | 是否顯示於首頁精選區 |
| `addedOrder` | number | 否 | 收錄順序的正整數。新增作品時使用比目前最大值更大的順序 |
| `imageType` | string | 否 | 實際操作截圖使用 `screenshot`，已知佔位圖可標為 `placeholder` |
| `projectType` | string | 否 | `課程作業`、`個人專案`、`產學合作`、`研究專案` 之一 |
| `courseWeek` | number | 否 | 有來源確認的課程週次，填正整數 |
| `projectDate` | string | 否 | 有來源確認的作品日期，使用 `YYYY-MM-DD` |
| `systemDiagram` | object | 否 | 系統流程圖，使用相對圖片路徑 `src` 與替代文字 `alt` |
| `screenshots` | object[] | 否 | 額外成果截圖，各筆使用 `src` 與 `alt`，依陣列順序顯示 |
| `links` | object[] | 否 | 其他相關外部連結，各筆使用 `label` 與完整 `https://` 的 `url` |

首頁以最大 `addedOrder` 選出最新作品，總覽預設最新加入優先，另可選最早加入或作品名稱排序。缺少 `addedOrder` 時以原始陣列位置（從 1 起算）為準。同值時最新取陣列較後者優先，最早取陣列較前者優先。名稱依繁體中文語系排序，英文不分大小寫。`addedOrder` 是收錄順序，作品日期另填 `projectDate`。新增 `LLM Wiki` 技術分類時，總覽選項與首頁計數由 JSON 自動更新，既有作品的分類沿用原值。

舊資料可以省略所有選填欄位。未填 `projectType` 的作品仍出現在「全部類型」，只有已填的類型會計入首頁統計。已有封面繼續使用 `image` 與 `imageAlt`，`screenshots` 供額外截圖使用。GitHub 原始碼及線上展示沿用 `githubUrl`、`demoUrl`，Google Colab 等額外連結放在 `links`，同一網址只顯示一次。連結資料須核對可用性，網站版型顯示有標籤且格式有效的 HTTPS 網址。離線驗證接受完整的 HTTP 或 HTTPS 語法，HTTP 會提示目前頁面只顯示 HTTPS。驗證通過只代表格式有效，連線與頁面內容須另行確認。

所有欄位保留一致的大小寫，文件需為有效 UTF-8 JSON，避免註解、尾隨逗號、重複欄位及重複作品 ID。圖片使用專案內相對路徑與 `/`，大小寫須和實際檔案相同，禁止路徑逸出專案根目錄。新作品資訊不完整時，先整理可確認的部分並列出缺項，**不要為了填滿欄位捏造內容**。若有重要資料不足，應在正式寫入前向使用者確認。

### 關於我資料與隱私

`data/profile.json` 是單一 JSON 物件，包含 `intro`（`role`、`roleEn`、`description`）、`education`（`school`、`program`、`degree` 陣列）、`skills`（`note` 和 `groups`，每組有 `title` 與 `technologies`）、`interests`（`title`、`description` 陣列）、`links`（`label`、`url` 陣列）和 `site.paragraphs`（文字段落陣列）。詳見 [README 的關於我資料說明](README.md#關於我資料)。

更新前取得本人對新增或變更內容的公開確認。修改 `data/profile.json` 後執行 `python scripts/sync_data.py` 產生 `data/profile-data.js`，格式為 `window.PROFILE_FALLBACK = <JSON 物件>;`。執行資料驗證，再用 HTTP 與 `file://` 確認關於我頁面。個人資料集中於 JSON，避免重複寫入 HTML 或渲染程式。

僅使用本人明確同意公開的內容及完整 HTTPS 連結。勿納入手機號碼、個人住址、學號、未確認的電子郵件或經歷、未公開的論文內容、合作機密、未授權的照片及未確認的履歷連結。學歷日期、證照或熟練度須有依據與公開同意。

## 7. AI 整理新作品的標準流程

使用者可能提供 `.ipynb`、`.py`、`.html`、GitHub Repository、README、操作截圖或展示網址。每次新增作品依序執行：

1. **閱讀來源專案**。核對使用者提供的檔案、程式及說明，辨識同一作品的不同階段或版本。
2. **分析真實成果**。確認名稱、動機、技術、已實作功能、執行方式與狀態，區分程式已實作、來源文字描述和實際驗證結果。移除 API Key、token、私人網址、帳號與含憑證的輸出。
3. **整理展示草稿**。列出摘要、動機、功能、技術、成果、截圖、外部連結、缺項與預計的 JSON。優先使用獲准的實際畫面，若使用預設封面或示意圖，清楚標示。
4. **確認公開內容**。先由使用者確認介紹、素材與公開連結，有差異時修正草稿。
5. **新增資料及素材**。確認 ID 唯一後追加作品，沿用現有欄位與共用頁面。原始 Notebook 的完整內容留在來源專案。
6. **同步備援**。執行 `python scripts/sync_data.py`。
7. **執行資料驗證**。執行同步檢查與資料驗證。修改驗證器、同步工具或資料規則時，一併執行單元測試。
8. **執行瀏覽器測試**。依修改範圍檢查首頁、列表、搜尋分類、排序、詳細頁、錯誤 ID、圖片及連結，並測試必要的手機版面、GitHub Pages 子路徑與 `file://`。
9. **回報修改與實測結果**。列出修改檔案、通過項目、限制與待補資料，區分本機完成和網站已部署。
10. **確認後提交與部署**。取得使用者授權後，核對 V2 遠端，再執行 Git 提交、推送及部署。

## 8. 修改既有作品與網站的規則

- 修改某作品時，依現有 `id` 找到對應資料；除非明確要求，不更改 ID。
- 只更動需求相關的檔案與欄位，禁止無理由的大規模重構。
- 不刪除原有作品，不清空 JSON，不覆蓋無關截圖或連結。
- 不得捏造 GitHub、Colab、Gradio 或其他展示網址；無法確認可用性就註明「未驗證」。
- Notebook 使用 Gradio 的臨時 `share` 連結可能失效，不得當作永久公開服務；可保留程式碼連結及截圖，並清楚標示互動展示的狀態。
- 如果新增新分類、欄位或頁面，先說明對舊資料和既有頁面造成的影響，再同步更新本文件及 README。

### Git 與部署安全

- `my-project-hub` 是 V1 原始繳交版本，供參考；維護工作在 `my-project-hub-v2` 進行。LLM Wiki 等來源專案用於核對，修改來源需要獨立的使用者授權。
- 執行前檢查 `git status --short --branch` 與工作目錄，保留已有且尚未提交的成果。推送前以 `git remote get-url origin` 及 `git remote get-url --push origin` 核對 fetch、push 都指向 `my-project-hub-v2.git`。
- 提交、推送與部署須有使用者明確授權。禁止擅自執行會丟失工作樹或改寫歷史的命令，例如 `git reset --hard`、`git clean` 或強制推送。

## 9. 完成前的驗收清單

在 V2 根目錄執行：

```powershell
python scripts/sync_data.py
python scripts/sync_data.py --check
python scripts/validate_data.py
python -m unittest discover -s tests -v
```

同步檢查比對備援產出格式並接受 LF 與 CRLF，資料驗證比對解析後內容與欄位型態。驗證工具為唯讀且離線執行。資料錯誤使驗證回傳非零，僅有警告時仍可通過。單元測試的正反案例使用獨立暫存資料，正式資料仍需執行驗證。通過自動化驗證後，再依實際修改範圍進行瀏覽器驗收。

- [ ] 兩份 JSON 均可解析、作品 ID 唯一、欄位符合規格，兩份備援同步。
- [ ] 首頁與列表使用同一資料來源，作品總數／精選內容沒有硬編碼造成的錯誤。
- [ ] 搜尋與兩種分類可組合，三種排序、結果數量、清除條件與空狀態正確。詳細頁連結可運作，錯誤 ID 有返回連結。
- [ ] 圖片存在並有替代文字。選填的流程圖與截圖缺少資料時隱藏，截圖可透過鍵盤開啟和關閉。示意圖應清楚標示。
- [ ] 外部連結只在有網址時顯示，且沒有填入虛構的連結。
- [ ] 電腦和手機排版可讀；鍵盤可操作主要功能。
- [ ] 四頁的主要導覽及目前頁狀態正確，關於我在 HTTP 與 `file://` 均可從對應的資料來源正常顯示。
- [ ] 無 API Key、憑證、私密資料或敏感執行輸出。
- [ ] GitHub Pages 專案子路徑下可載入 CSS、JS、JSON、圖片及站內頁面。
- [ ] 更新 README 的作品與部署說明；回報實際驗證過的項目及尚未驗證項目。

## 10. 初始作品與示範擴充

首版預計收錄以下三個作品，實際內容須依來源檔案核對後整理：

1. `interview-coach`：AI 面試模擬系統（來源：`作業6.ipynb的副本`）。
2. `pet-rag-advisor`：毛孩新手村：AI 貓狗飼養顧問（RAG01、RAG02 為同一作品的建庫及問答階段，合併展示）。
3. `ai-trip-reflection`：AI 智慧行程規劃與反思助手（Reflection Agent：Planner、Reviewer、Reviser）。

**本週作業的可重複性驗證方式**：先建立兩個作品，再讓 AI 重新閱讀本文件，使用第三個 Notebook 走完「資料分析 → 展示草稿 → 使用者確認 → 寫入 JSON → 頁面驗證」流程。保留 Git commit 紀錄或操作前後畫面，作為 AGENTS.md 實際生效的證據。

## 網站更新日期規範

1. 網站首頁必須顯示「網站最後更新日期」。
2. 當 AI 新增作品、修改作品內容或更新網站功能時，
   必須同步更新 `js/site-update.js` 中的
   `SITE_LAST_UPDATED`。
3. 日期格式統一使用 YYYY-MM-DD。
4. 日期必須代表實際修改日期，不得使用瀏覽器當天日期
   自動冒充網站更新日期。
5. 只要沒有實際修改網站內容，就不得任意更新日期。
6. 修改完成後，必須確認首頁顯示的日期正確。
