# pochao_profile

This is a portfolio showcasing my work in data analysis and data engineering.

## data_analysis

**Project Name:** game_data_analysis
**Description:**
針對亞洲手遊的轉蛋機制進行數據分析。透過分析玩家的消費金額、抽獎次數與獲獎價值，來識別高價值玩家群體、優化行銷預算分配，並解讀整體市場趨勢。
Data analysis focusing on gacha mechanics in Asian mobile games. By analyzing player spending, draw counts, and prize values, it identifies high-value player segments, optimizes marketing budget allocation, and interprets overall market trends.

**Project Name:** Japanese_Passport_Data_Analysis
**Description:**
探討日本人護照持有率議題的分析專案。使用 Python 串接 E-Stat API 獲取人口數據，整合清洗外務省護照統計與匯率資料，最後透過 Tableau Dashboard 進行視覺化呈現。
An analysis project investigating Japan's passport ownership rates. It uses Python to fetch population data via the E-Stat API, integrates and cleans MOFA passport statistics and exchange rates, and visualizes the results using a Tableau Dashboard.

**Project Name:** Amazon_Delivery_Dataset_Analysis
**Description:**
基於 Amazon 最後一哩路物流數據的分析。探討天氣、交通狀況、配送時段及城市類型如何影響配送效率與物流人員評分，旨在找出優化物流營運與客戶體驗的關鍵因素。
Analysis based on Amazon's last-mile logistics data. It explores how weather, traffic, delivery windows, and city types impact delivery efficiency and agent ratings, aiming to identify key factors for optimizing logistics operations and customer experience.

## data_engineering

**Project Name:** f1News-scraper
**Description:**
全自動化的 F1 新聞聚合系統。使用爬蟲抓取海外新聞，透過 Gemini AI 進行翻譯與潤飾，並整合 Backend (FastAPI) 與 Frontend (React) 呈現給使用者，解決跨語言閱讀賽事資訊的痛點。
An automated F1 news aggregation system. It scrapes overseas news, uses Gemini AI for translation and editing, and integrates a FastAPI backend with a React frontend to solve cross-language reading barriers.

**Project Name:** taipei_taxi_kafka_project
**Description:**
一個結合 Kafka 與 Spark 的實驗性數據工程專案。旨在實作即時數據串流處理，並將數據整合至 AWS 儲存，最後透過 BI 工具進行視覺化分析。
An experimental data engineering project combining Kafka and Spark. It implements real-time data streaming, integrates with AWS storage, and provides data for BI visualization.

**Project Name:** lalae-data-platform
**Description:**
專為行銷人員打造的數據中台 (基於 GCP)。能自動串接 Google Ads、Facebook Ads 與 Google Sheets 數據至 BigQuery，提供數據清洗、SQL 轉換及自動化輸出功能，大幅節省人工處理時間。
A data platform built on GCP for marketers. It automatically connects Google Ads, Facebook Ads, and Google Sheets data to BigQuery, offering data cleaning, SQL transformation, and automated exports to save manual processing time.

**Project Name:** aws-data-pipeline-ml-platform
**Description:**
基於 AWS 最佳實踐的端到端雲端數據平台。使用 Terraform (IaC) 部署，涵蓋從資料攝取 (ETL)、Redshift 倉儲、SageMaker 用戶分群預測，到自動同步回 Salesforce 的完整閉環流程。
An end-to-end cloud data platform following AWS best practices. Deployed via Terraform (IaC), it covers the full lifecycle from data ingestion (ETL), Redshift warehousing, and SageMaker user segmentation, to syncing results back to Salesforce.

**Project Name:** highway_traffic_streaming_datapipeline
**Description:**
整合電腦視覺與大數據串流技術的工程平台。利用 YOLO 進行即時車輛偵測，透過 Kafka 與 Spark Streaming 處理數據，並結合 dbt 與 PostgreSQL 建立數據倉儲模型。
An engineering platform integrating computer vision and big data streaming. It uses YOLO for real-time vehicle detection, processes data via Kafka and Spark Streaming, and builds data warehouse models using dbt and PostgreSQL.

**Project Name:** Secure-E-commerce-Customer-360-Platform
**Description:**
採用現代數據技術棧 (MDS) 建構的端到端專案。整合 Airflow、dbt 與 BigQuery，特別強調個資安全防護 (PII Masking)、數據合約 (Data Contracts) 與 CI/CD 自動化流程的實踐。
An end-to-end project built with the Modern Data Stack (MDS). It integrates Airflow, dbt, and BigQuery, emphasizing PII masking, Data Contracts, and automated CI/CD workflows.