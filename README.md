# Po-Chao Wang | Data Engineering, Analytics & AI Portfolio

[English](README.md) | [繁體中文](README.zh-TW.md)

Hi, I'm **Po-Chao Wang**. Welcome to my portfolio!

Here you'll find **4 selected end-to-end projects** demonstrating my capabilities across **Data Engineering**, **Data Analytics**, **Machine Learning**, and **AI Agents** — turning raw data into automated pipelines, actionable business insights, and intelligent systems.

---

## ⚡ Quick Project Summary (At a Glance)

| Project | Primary Domain | Core Purpose (What it does & why it matters) | Key Tech Stack |
|---|---|---|---|
| 🛍️ **[Ecommerce Intelligence Suite](#1-ecommerce-customer-intelligence--predictive-growth-suite)** | Data Engineering & ML | Automated customer analytics system that predicts Customer Lifetime Value (LTV) and outputs daily targeted action plans for marketing & CRM. | Kafka, Spark, BigQuery ML, dbt, Airflow, Terraform |
| 🔄 **[LaLaE Data Platform](#2-lalae-data-platform)** | ETL Data Platform | Automated all-in-one data middle platform that connects Google Ads, Meta Ads, and Sheets, replacing hours of manual reporting with automated BigQuery pipelines. | GCP Cloud Run, BigQuery, Next.js, Django, Terraform |
| 📦 **[Amazon Delivery Operations Analysis](#3-amazon-delivery-operations-analysis)** | Business Data Analytics | In-depth operational analysis on 43,000+ logistics orders, using statistical modeling to identify the root causes of delivery bottlenecks and guide business decisions. | Python, Econometrics (OLS), Statsmodels, OpenSlide |
| 🤖 **[AI Ads Analyst Agent](#4-ai-ads-analyst-agent)** | Autonomous AI Agent | An AI analyst that automatically cross-examines Google Ads, Meta Ads, and GA4 data in natural language, producing audit-proof performance reports. | Python, AI Agent Workflows, MCP, Google/Meta APIs |

---

## 🌟 Featured Projects

### 1. [Ecommerce Customer Intelligence & Predictive Growth Suite](Ecommerce-Customer-Intelligence-Predictive-Growth-Suite)
> **Full-Stack Data Engineering, Predictive ML & Customer 360 Decision System**

* **🎯 Business Problem**: E-commerce companies often have fragmented user data across multiple channels. Marketing and CRM teams waste time guessing who to contact, when to reach out, and who is likely to churn.
* **💡 The Solution**: Built an end-to-end customer intelligence system combining high-throughput real-time data streaming, automated data warehousing, and machine learning to produce an automated **"Daily CRM Action Plan"**.
* **📈 Key Highlights & Impact**:
  * **Real-Time Scale**: Streams **500 ~ 2,000+ events/sec** (~43M ~ 170M+ events/day) using Kafka and Spark Structured Streaming.
  * **Predictive ML**: Built RFM segmentation + BigQuery ML models (LTV prediction) to identify high-value and churn-risk customers.
  * **Cost Optimization**: Implemented **Slim CI** in GitHub Actions, **reducing BigQuery compute costs by over 90%** during testing.
  * **Privacy Compliance**: Automatic irreversible SHA-256 PII masking for sensitive user emails at the staging layer.
* **🛠️ Tech Stack**: `Apache Kafka` `Apache Spark` `Google BigQuery` `dbt` `BigQuery ML` `Apache Airflow` `Terraform` `GKE (Kubernetes)` `Lightdash`

---

### 2. [LaLaE Data Platform](lalae-data-platform)
> **Automated Multi-Channel ETL Platform for Marketing & Analytics Teams**

* **🎯 Business Problem**: Digital marketers and data analysts spend countless hours every week manually downloading CSV reports from Google Ads and Facebook Ads, then copy-pasting them into spreadsheets.
* **💡 The Solution**: Developed a serverless, self-service ETL data platform that automatically syncs multi-channel ad data, enables in-warehouse SQL transformation, and delivers clean reports on schedule.
* **📈 Key Highlights & Impact**:
  * **End-to-End Automation**: Replaced manual data extraction with scheduled API syncs from Google Ads, Meta Ads, and Google Sheets.
  * **In-Warehouse SQL Editor**: Allows users to filter, standardize, and join cross-platform metrics directly on Google BigQuery.
  * **100% Serverless Architecture**: Built on GCP Cloud Run, Cloud Tasks, and Cloud Scheduler for zero-idle hosting costs and auto-scalability.
  * **Interactive Demo**: Live web demo available with zero-backend mock mode for instant exploration.
* **🛠️ Tech Stack**: `GCP Cloud Run` `Google BigQuery` `GCP Cloud Tasks` `Terraform (IaC)` `Next.js 14` `Django REST Framework`

---

### 3. [Amazon Delivery Operations Analysis](amazon_kaggle_data_analysis)
> **Logistics Operations Analytics, Statistical Hypothesis Testing & Diagnostic Modeling**

* **🎯 Business Problem**: Logistics operations noted that "certain deliveries take too long," but lacked clear data on where resources should be prioritized to fix the delays.
* **💡 The Solution**: Formulated a structured analytical framework on 43,000+ delivery records — transforming a vague complaint into rigorous KPI tracking, hypothesis testing, and multivariate statistical modeling.
* **📈 Key Highlights & Impact**:
  * **Root Cause Discovery**: Disproved assumptions about traffic/distance and isolated that Semi-Urban deliveries face a **+102-minute structural bottleneck** (controlled via OLS regression with HC3 robust standard errors).
  * **Actionable Recommendations**: Advised operations to focus on dispatch and pickup process diagnosis rather than inefficient driver hiring.
  * **Executive Presentation**: Packaged findings into an interactive HTML slide deck (OpenSlide) for non-technical leadership and stakeholders.
* **🛠️ Tech Stack**: `Python` `Pandas` `Statsmodels (Multivariate OLS)` `Seaborn / Matplotlib` `OpenSlide`

---

### 4. [AI Ads Analyst Agent](digital-marketing-analyst-agent)
> **Autonomous AI Agent for Cross-Channel Advertising & GA4 Analytics**

* **🎯 Business Problem**: Evaluating multi-platform advertising performance (Google Ads, Meta Ads, GA4) requires repetitive data collation, and non-technical stakeholders often struggle to interpret raw dashboard numbers.
* **💡 The Solution**: Created an AI Agent capable of querying real-time advertising APIs via the Model Context Protocol (MCP), analyzing cross-channel trends, and generating structured executive reports in natural language.
* **📈 Key Highlights & Impact**:
  * **Automated Cross-Channel Insights**: Compares CPA, ROAS, CTR, and conversions across platforms to surface what's working and what isn't.
  * **Audit-Proof & Transparent**: Every AI-generated conclusion is backed by explicit data citations, environment gating, and trace logs to prevent hallucinations.
  * **Dual Ingestion**: Supports direct live API connections or offline CSV file imports for flexible deployment.
* **🛠️ Tech Stack**: `Python` `AI Agent Workflows` `Model Context Protocol (MCP)` `Google Ads API` `Meta Ads API` `GA4 API`

---

## 🛠️ Technical Skills Summary

| Category | Skills & Tools |
|---|---|
| **Data Engineering** | Apache Kafka, Apache Spark Streaming, Google BigQuery, dbt, Apache Airflow, PostgreSQL |
| **Cloud & DevOps** | Google Cloud Platform (GCP), AWS, Docker, Kubernetes (GKE), Terraform (IaC), GitHub Actions (CI/CD) |
| **Data Science & Analytics** | Python (Pandas, Scikit-Learn, Statsmodels), SQL, BigQuery ML, Tableau, Lightdash |
| **AI & Software Engineering** | LLM Agents, Model Context Protocol (MCP), FastAPI, Django, Next.js / TypeScript |

---

## 📬 Contact & Links
* **GitHub**: [@Gibon4385](https://github.com/Gibon4385)
* **LinkedIn**: [Po-Chao Wang](https://www.linkedin.com/in/po-chao-wang/)