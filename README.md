# Po-Chao Wang | Portfolio & Selected Projects

[English](README.md) | [繁體中文](README.zh-TW.md)

Welcome to my portfolio repository. This space highlights selected production-grade projects spanning **Data Engineering**, **Data Analytics**, **Machine Learning / Predictive Modeling**, and **AI Agents**.

---

## 🌟 Featured Projects

### 1. [Ecommerce Customer Intelligence & Predictive Growth Suite](Ecommerce-Customer-Intelligence-Predictive-Growth-Suite)
> **Full-Stack Data Engineering, Predictive ML, and C360 Decision System**

* **Tech Stack**: Apache Kafka, Apache Spark Streaming, Google BigQuery, dbt, BigQuery ML (XGBoost / Regression), Apache Airflow, Terraform, GKE, Lightdash
* **Highlights**:
  * **High-Throughput Streaming**: Handles real-time event streaming at **500 ~ 2,000+ EPS** (~43M ~ 170M+ daily events) with Kafka and Spark Structured Streaming.
  * **Predictive Decision Engine**: Transforms raw events into RFM customer segmentation and ML-driven Customer Lifetime Value (LTV) predictions for actionable CRM daily action plans.
  * **Enterprise CI/CD & IaC**: Implements Slim CI via GitHub Actions and GCP Workload Identity Federation, cutting BigQuery test compute costs by >90%. Full infrastructure automated with Terraform and GKE.
  * **Data Privacy (PII Protection)**: Irreversible SHA-256 email hashing at the Staging layer with fine-grained IAM dataset access controls.

---

### 2. [LaLaE Data Platform](lalae-data-platform)
> **Automated Multi-Channel ETL Platform for Marketing & Analytics Teams**

* **Tech Stack**: GCP Cloud Run, Google BigQuery, GCP Cloud Tasks, Cloud Scheduler, Terraform, Next.js 14, Django REST Framework
* **Highlights**:
  * **Automated Data Ingestion**: Seamlessly connects Google Ads, Meta (Facebook) Ads, and Google Sheets APIs with granular metric/dimension selection.
  * **In-Warehouse SQL Transformation**: Integrated SQL editor on BigQuery for cleaning, joining, and aggregating multi-channel marketing data.
  * **Scheduled Exports**: Automated cron scheduling to deliver processed datasets directly into downstream Google Sheets.
  * **100% Serverless & IaC**: Built entirely on GCP Serverless infrastructure provisioned via Terraform with a zero-backend-dependency mock demo mode.

---

### 3. [Amazon Delivery Operations Analysis](amazon_kaggle_data_analysis)
> **Business Operations Analytics, Hypothesis Testing & Diagnostic Modeling**

* **Tech Stack**: Python, Pandas, Statsmodels (OLS + HC3 Robust Errors), Seaborn, OpenSlide
* **Highlights**:
  * **From Business Problem to Metrics**: Deconstructs vague operational pain points into measurable KPIs (Median Delivery Time, IQR, P75 Long-Duration Rate) on 43,000+ logistics records.
  * **Multivariate Econometric Control**: Applies multivariate regression with HC3 robust standard errors to isolate true operational bottlenecks in Semi-Urban logistics (+102 mins delivery delay after controlling for traffic, distance, and weather).
  * **Executive Slide Deck**: Includes an interactive HTML presentation deck built with OpenSlide for stakeholder review.

---

### 4. [AI Ads Analyst Agent](digital-marketing-analyst-agent)
> **Autonomous AI Agent for Cross-Channel Advertising & GA4 Analytics**

* **Tech Stack**: Python, LLM Agent Workflow, Model Context Protocol (MCP), GA4 API, Google Ads API, Meta Ads API
* **Highlights**:
  * **Cross-Platform Ad Performance**: Automated multi-channel performance comparisons across CPA, ROAS, CTR, CVR, spend, and conversions.
  * **Transparent Analysis Trace**: Built-in environment gating, data source attribution, and explainable analysis traces to prevent black-box AI hallucinations.
  * **Flexible Ingestion**: Supports direct MCP tool connections as well as offline CSV dataset processing with automated Markdown/Sheets reporting.

---

## 🛠️ Technical Skills Overview

| Category | Technologies & Tools |
|---|---|
| **Data Engineering** | Apache Kafka, Apache Spark, Google BigQuery, dbt, Apache Airflow, PostgreSQL |
| **Cloud & Infrastructure** | Google Cloud Platform (GCP), AWS, Docker, Kubernetes (GKE), Terraform (IaC), GitHub Actions |
| **Data Science & Analytics** | Python (Pandas, NumPy, Scikit-Learn, Statsmodels), SQL, BigQuery ML, Tableau, Lightdash |
| **AI & LLM Systems** | Agentic Workflows, Model Context Protocol (MCP), Prompt Engineering, FastAPI, Django |