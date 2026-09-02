# Po-Chao Wang | 個人作品集與精選專案

[English](README.md) | [繁體中文](README.zh-TW.md)

歡迎來到我的個人作品集倉庫。此處精選展示了橫跨 **數據工程（Data Engineering）**、**商業數據分析（Data Analytics）**、**機器學習與預測模型（Machine Learning / Predictive Modeling）** 以及 **AI Agent 系統** 的 4 個生產級專案。

---

## 🌟 精選核心專案

### 1. [Ecommerce Customer Intelligence & Predictive Growth Suite](Ecommerce-Customer-Intelligence-Predictive-Growth-Suite)
> **全棧數據工程、預測型機器學習與客戶 360 (C360) 商業決策系統**

* **技術棧**：Apache Kafka、Apache Spark Streaming、Google BigQuery、dbt、BigQuery ML (XGBoost / Regression)、Apache Airflow、Terraform、GKE、Lightdash
* **核心亮點與工程指標**：
  * **高吞吐即時數據串流**：以 Kafka 與 Spark Structured Streaming 支援 **500 ~ 2,000+ EPS**（每日處理約 4,300 萬至 1.7 億筆事件）的高並發即時數據流。
  * **預測型決策引擎**：結合 RFM 客戶分群與 BigQuery ML 預測顧客終身價值（LTV），自動化產出每日 CRM 優先行動方案（Daily Action Plan）。
  * **企業級 CI/CD 與 IaC**：透過 GitHub Actions、GCP Workload Identity Federation 與 Slim CI 機制，僅對變更的 dbt 模型執行測試，**大幅降低 BigQuery 節點運算成本超過 90%**；完整雲端架構以 Terraform 與 GKE 實現代碼化管理。
  * **資料安全合規（PII 保護）**：在 Staging 層以 SHA-256 進行不可逆 Email 去識別化遮蔽，搭配 Terraform 細粒度 IAM 資料集存取權限控制。

---

### 2. [LaLaE Data Platform](lalae-data-platform)
> **專為行銷與數據團隊打造的一站式自動化多通路 ETL 數據中台**

* **技術棧**：GCP Cloud Run、Google BigQuery、GCP Cloud Tasks、Cloud Scheduler、Terraform、Next.js 14、Django REST Framework
* **核心亮點與工程指標**：
  * **自動化跨通路 API 串接**：安全整合 Google Ads、Meta (Facebook) Ads 與 Google Sheets API，支援自訂指標、維度與層級拉取。
  * **倉內 SQL 清洗與轉換**：內建基於 BigQuery 的線上 SQL 編輯器，支援跨平台廣告數據的過濾、標準化與關聯運算。
  * **定時自動化同步匯出**：支援 Cron 定時排程，自動將 SQL 處理後的乾淨數據覆寫或追加至指定 Google Sheets。
  * **100% Serverless 與 IaC**：全架構基於 GCP Serverless 雲原生服務（Cloud Run / Cloud Tasks / Cloud Scheduler），透過 Terraform 部署維護；並提供零後端依賴的本機 Mock 體驗模式。

---

### 3. [Amazon Delivery Operations Analysis](amazon_kaggle_data_analysis)
> **最後一哩路物流營運數據分析、假設檢定與歸因診斷模型**

* **技術棧**：Python、Pandas、Statsmodels (OLS + HC3 穩健標準誤)、Seaborn、OpenSlide
* **核心亮點與工程指標**：
  * **將模糊業務痛點轉化為量化指標**：針對 43,000+ 筆物流紀錄，建立中位數配送時長、四分位距（IQR）與 P75 長時配送率等多維度 KPI 體系。
  * **計量經濟學多元回歸控制**：採用 OLS 多元回歸並搭配 HC3 穩健標準誤，在嚴格控制交通、距離與天候等干擾變數後，成功定位出半郊區（Semi-Urban）仍存在約 **+102 分鐘** 的結構性營運瓶頸。
  * **決策級簡報展示**：內建以 OpenSlide 打造的高互動性獨立 HTML 簡報，方便利害關係人快速瀏覽關鍵洞察與行動建議。

---

### 4. [AI Ads Analyst Agent](digital-marketing-analyst-agent)
> **多通路數位廣告與 GA4 數據分析自主型 AI Agent**

* **技術棧**：Python、LLM Agent Workflow、Model Context Protocol (MCP)、GA4 API、Google Ads API、Meta Ads API
* **核心亮點與工程指標**：
  * **跨平台廣告成效即時對比**：自動整合分析 Google Ads、Meta Ads 與 GA4 數據，產出 CPA、ROAS、CTR、CVR、花費與轉換等綜合指標。
  * **可解釋分析軌跡（Explainable Trace）**：內建環境閘門檢查、數據源標記與分析軌跡標註，杜絕 AI 黑箱臆測與數據幻覺。
  * **彈性接入與自動報告生成**：同時支援線上 MCP 工具即時調用與離線 CSV 手動匯入模式，可自動輸出標準化 Markdown 分析報告與 Google Sheets 排程計畫。

---

## 🛠️ 技術能力矩陣（Skills Overview）

| 領域 | 核心技術與工具 |
|---|---|
| **數據工程 (Data Engineering)** | Apache Kafka, Apache Spark, Google BigQuery, dbt, Apache Airflow, PostgreSQL |
| **雲端架構與維運 (Cloud & IaC)** | Google Cloud Platform (GCP), AWS, Docker, Kubernetes (GKE), Terraform (IaC), GitHub Actions |
| **數據科學與分析 (Data Science & Analytics)** | Python (Pandas, NumPy, Scikit-Learn, Statsmodels), SQL, BigQuery ML, Tableau, Lightdash |
| **AI 與 LLM 系統 (AI & LLMs)** | Agentic Workflows, Model Context Protocol (MCP), Prompt Engineering, FastAPI, Django |
