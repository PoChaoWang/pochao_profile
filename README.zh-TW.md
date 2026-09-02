# Po-Chao Wang | 數據工程、商業分析與 AI 作品集

[English](README.md) | [繁體中文](README.zh-TW.md)

你好，我是 **王柏超**，歡迎瀏覽我的個人作品集！

這裡精選展示了 **4 個端到端的實戰專案**，涵蓋 **數據工程（Data Engineering）**、**商業數據分析（Data Analytics）**、**預測型機器學習（Machine Learning）** 與 **AI Agent 系統** —— 致力於將原始資料轉化為全自動化的數據管道、具商業決策價值的洞察與智慧化工具。

---

## 專案速覽表

| 專案名稱 | 領域分類 | 一句話簡介（解決什麼問題、有什麼功用） | 核心技術棧 |
|---|---|---|---|
| **[電商客戶決策與增長系統](#1-ecommerce-customer-intelligence--predictive-growth-suite)** | 數據工程 & 機器學習 | 全自動化的客戶分析系統，預測顧客終身價值（LTV）並產出「每日 CRM 行動清單」，直接告訴業務該聯絡誰、防範誰流失。 | Kafka, Spark, BigQuery ML, dbt, Airflow, Terraform |
| **[LaLaE 多通路數據中台](#2-lalae-data-platform)** | ETL 數據平台開發 | 一站式自動化數據中台，串接 Google / Meta 廣告與試算表至 BigQuery，取代人工下載 CSV 與手動做報表的繁瑣流程。 | GCP Cloud Run, BigQuery, Next.js, Django, Terraform |
| **[Amazon 物流營運數據分析](#3-amazon-delivery-operations-analysis)** | 商業數據分析 | 分析 4.3 萬筆外送物流數據，透過統計回歸模型找出配送延誤的根本原因，為營運團隊提供精準的優化決策。 | Python, 計量回歸 (OLS), Statsmodels, OpenSlide |
| **[AI 廣告分析助理 Agent](#4-ai-ads-analyst-agent)** | AI Agent 系統開發 | 能用自然語言對話的 AI 助手，自動跨平台比對 Google Ads、Meta 與 GA4 數據，快速產出無黑箱的行銷成效分析報告。 | Python, AI Agent, MCP, Google/Meta 廣告 API |

---

## 精選專案詳細介紹

### 1. [Ecommerce Customer Intelligence & Predictive Growth Suite](Ecommerce-Customer-Intelligence-Predictive-Growth-Suite)
> **全棧數據工程、預測型機器學習與客戶 360 (C360) 商業決策系統**

* **解決的商業痛點**：電商各通路的會員資料分散，行銷與 CRM 團隊往往只能憑感覺行銷，無法精準得知「今天該聯絡哪位顧客？該給什麼優惠？誰即將流失？」。
* **解決方案與功用**：建立一套結合即時數據串流、雲端數據倉儲與機器學習的端到端決策系統，每日自動化輸出精準的 **CRM 優先行動清單（Daily Action Plan）**。
* **關鍵成效與工程亮點**：
  1. **高並發即時數據流**：以 Kafka 與 Spark Streaming 支援 **500 ~ 2,000+ EPS**（每日處理 4,300 萬至 1.7 億筆事件）的高吞吐量。
  2. **AI/ML 預測決策**：結合 RFM 客戶分群與 BigQuery ML 預測顧客終身價值（LTV），自動標記高價值客戶與流失風險群體。
  3. **雲端成本最佳化**：導入 **Slim CI** 自動化測試機制，**降低 BigQuery 測試運算成本超過 90%**。
  4. **個資隱私防護 (PII)**：在資料分層的 Staging 層即以 SHA-256 對敏感 Email 進行不可逆遮蔽，確保合規安全。
* **核心技術**：`Apache Kafka` `Apache Spark` `Google BigQuery` `dbt` `BigQuery ML` `Apache Airflow` `Terraform` `GKE (Kubernetes)` `Lightdash`

---

### 2. [LaLaE Data Platform](lalae-data-platform)
> **專為行銷與數據團隊打造的一站式自動化多通路 ETL 數據中台**

* **解決的商業痛點**：行銷與數據人員每週需耗費數小時手動從 Google Ads、Facebook Ads 後台下載報表、手動整理至 Excel，既耗時又容易出錯。
* **解決方案與功用**：打造無伺服器架構的自服務數據中台，自動串接多通路廣告 API，並在線上直接透過 SQL 進行資料清洗，依排程自動產出乾淨數據至 Google Sheets。
* **關鍵成效與工程亮點**：
  1. **報表全自動化**：以排程取代人工抓取，支援 Google Ads、Meta Ads 與 Google Sheets 資料的一鍵定時同步。
  2. **倉內 SQL 編輯器**：內建基於 BigQuery 的線上 SQL 工具，方便跨通路廣告數據的即時過濾、標準化與對比。
  3. **100% Serverless 雲原生架構**：採用 GCP Cloud Run、Cloud Tasks 與 Cloud Scheduler，具備自動彈性擴展與零閒置成本優勢。
  4. **線上展示與 Mock 模式**：提供免後端依賴的本地 Mock 模式與線上 Live Demo，隨開即用。
* **核心技術**：`GCP Cloud Run` `Google BigQuery` `GCP Cloud Tasks` `Terraform (IaC)` `Next.js 14` `Django REST Framework`

---

### 3. [Amazon Delivery Operations Analysis](amazon_kaggle_data_analysis)
> **物流營運數據分析、統計假設檢定與歸因診斷模型**

* **解決的商業痛點**：營運團隊發現「部分訂單配送時間過長」，但面對有限的預算與資源，不清楚延誤的根本原因在哪裡、該從何處著手改善。
* **解決方案與功用**：將模糊的業務痛點拆解為具體的量化指標，針對 4.3 萬筆訂單進行數據清洗、探索性分析（EDA）與多元計量回歸模型診斷，找出影響效率的關鍵瓶頸。
* **關鍵成效與工程亮點**：
  1. **定位關鍵瓶頸**：打破「距離遠或塞車才慢」的直覺迷思，透過 OLS 多元回歸（搭配 HC3 穩健標準誤）控制干擾因素後，精確找出半郊區（Semi-Urban）仍存在 **+102 分鐘** 的結構性流程延遲。
  2. **提供可落地的營運建議**：建議營運團隊優先針對半郊區的備貨與派單流程進行診斷測試，避免盲目增派外送員浪費預算。
  3. **利害關係人簡報展示**：以 OpenSlide 製作高互動性獨立 HTML 簡報，方便非技術主管與決策者快速掌握核心洞察。
* **核心技術**：`Python` `Pandas` `Statsmodels (多元 OLS 回歸)` `Seaborn / Matplotlib` `OpenSlide 互動簡報`

---

### 4. [AI Ads Analyst Agent](digital-marketing-analyst-agent)
> **多通路數位廣告與 GA4 數據分析自主型 AI Agent**

* **解決的商業痛點**：跨平台（Google Ads、Meta Ads、GA4）廣告數據分散，且非技術背景人員難以快速從複雜的儀表板中看出成效好壞與調整方向。
* **解決方案與功用**：開發能理解自然語言指令的 AI 分析助手，透過標準協議（MCP）安全調用廣告 API，自動跨通路比對數據並產出具邏輯推理軌跡的分析報告。
* **關鍵成效與工程亮點**：
  1. **跨平台指標自動比對**：一鍵交叉對比各通路的 CPA、ROAS、CTR、CVR 與轉換成效，迅速找出高投報與低效廣告活動。
  2. **透明可追溯（無黑箱）**：內建環境閘門、數據來源標籤與分析軌跡標註，杜絕 AI 幻覺臆測，確保報告數據 100% 可信。
  3. **彈性運作模式**：支援即時 API 連線分析與離線 CSV 匯入分析，並可自動產出 Markdown 報告或排程規劃。
* **核心技術**：`Python` `AI Agent 工作流` `Model Context Protocol (MCP)` `Google Ads API` `Meta Ads API` `GA4 API`

---

## 技術能力矩陣（Skills Overview）

| 領域分類 | 核心技術與工具 |
|---|---|
| **數據工程 (Data Engineering)** | Apache Kafka, Apache Spark Streaming, Google BigQuery, dbt, Apache Airflow, PostgreSQL |
| **雲端架構與維運 (Cloud & DevOps)** | Google Cloud Platform (GCP), AWS, Docker, Kubernetes (GKE), Terraform (IaC), GitHub Actions (CI/CD) |
| **數據科學與分析 (Data Science & Analytics)** | Python (Pandas, Scikit-Learn, Statsmodels), SQL, BigQuery ML, Tableau, Lightdash |
| **AI 與軟體工程 (AI & Software)** | LLM Agents, Model Context Protocol (MCP), FastAPI, Django, Next.js / TypeScript |

---

## 聯絡方式與相關連結
* **GitHub**: [@Gibon4385](https://github.com/Gibon4385)
* **LinkedIn**: [Po-Chao Wang](https://www.linkedin.com/in/po-chao-wang/)
