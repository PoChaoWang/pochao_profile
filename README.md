# Po-Chao Wang | Data Engineering, Analytics & AI Portfolio

[English](README.md) | [繁體中文](README.zh-TW.md)

Hi, I'm **Po-Chao Wang**. Welcome to my portfolio!

Here you will find **4 selected end-to-end projects** demonstrating my work across **Data Engineering**, **Data Analytics**, **Machine Learning**, and **AI Agents** — focusing on automated data pipelines, business decision systems, and intelligent tools.

---

## Projects Summary

| Project | Domain | Core Purpose (What it does & why it matters) | Key Tech Stack |
|---|---|---|---|
| **[Ecommerce Intelligence & Growth Suite](#1-ecommerce-customer-intelligence--predictive-growth-suite)** | Data Engineering & ML | Automated customer analytics system that predicts Customer Lifetime Value (LTV) and generates daily action plans for marketing and CRM teams. | Kafka, Spark, BigQuery ML, dbt, Airflow, Terraform |
| **[LaLaE Data Platform](#2-lalae-data-platform)** | ETL Data Platform | Automated data platform connecting Google Ads, Meta Ads, and Google Sheets to BigQuery, eliminating manual CSV exports and report generation. | GCP Cloud Run, BigQuery, Next.js, Django, Terraform |
| **[Amazon Delivery Operations Analysis](#3-amazon-delivery-operations-analysis)** | Business Data Analytics | Operational data analysis on 43,000+ logistics orders, using statistical modeling to identify delivery delay bottlenecks and guide operations strategy. | Python, Econometrics (OLS), Statsmodels, OpenSlide |
| **[AI Ads Analyst Agent](#4-ai-ads-analyst-agent)** | AI Agent System | Conversational AI analyst that queries Google Ads, Meta Ads, and GA4 data in natural language, generating explainable performance reports. | Python, AI Agents, MCP, Google/Meta Ad APIs |

---

## Featured Projects

### 1. [Ecommerce Customer Intelligence & Predictive Growth Suite](Ecommerce-Customer-Intelligence-Predictive-Growth-Suite)
> **Full-Stack Data Engineering, Predictive ML & Customer 360 Decision System**

* **Business Problem**: E-commerce customer data is fragmented across channels. Marketing and CRM teams often lack clear guidance on which customers to contact, which offers to provide, and who is at risk of churn.
* **Solution & Functionality**: Built an end-to-end decision system integrating real-time streaming, cloud warehousing, and machine learning to automatically generate a **Daily CRM Action Plan**.
* **Key Highlights & Engineering Metrics**:
  1. **High-Throughput Streaming**: Handles real-time event ingestion at **500 ~ 2,000+ EPS** (~43M ~ 170M+ events daily) with Kafka and Spark Structured Streaming.
  2. **Predictive ML Decisioning**: Integrates RFM customer segmentation with BigQuery ML models (LTV prediction) to flag high-value users and churn risks.
  3. **Cloud Cost Optimization**: Implemented **Slim CI** via GitHub Actions, **reducing BigQuery test compute costs by over 90%**.
  4. **PII Data Protection**: Irreversible SHA-256 masking for sensitive customer emails at the Staging layer with fine-grained IAM controls.
* **Tech Stack**: `Apache Kafka` `Apache Spark` `Google BigQuery` `dbt` `BigQuery ML` `Apache Airflow` `Terraform` `GKE (Kubernetes)` `Lightdash`

---

### 2. [LaLaE Data Platform](lalae-data-platform)
> **Automated Multi-Channel ETL Platform for Marketing & Analytics Teams**

* **Business Problem**: Marketing and data teams spend hours each week manually downloading reports from Google Ads and Facebook Ads, then copy-pasting data into spreadsheets.
* **Solution & Functionality**: Developed a serverless, self-service ETL platform that automatically syncs multi-channel ad data, enables in-warehouse SQL transformations, and schedules clean exports to Google Sheets.
* **Key Highlights & Engineering Metrics**:
  1. **Automated Pipelines**: Replaced manual data extraction with scheduled API syncs across Google Ads, Meta Ads, and Google Sheets.
  2. **In-Warehouse SQL Editor**: Allows users to filter, standardize, and join cross-platform metrics directly within Google BigQuery.
  3. **100% Serverless Architecture**: Built on GCP Cloud Run, Cloud Tasks, and Cloud Scheduler for zero-idle hosting costs and auto-scaling.
  4. **Live Demo & Mock Mode**: Includes an interactive web demo and a zero-backend mock mode for instant evaluation.
* **Tech Stack**: `GCP Cloud Run` `Google BigQuery` `GCP Cloud Tasks` `Terraform (IaC)` `Next.js 14` `Django REST Framework`

---

### 3. [Amazon Delivery Operations Analysis](amazon_kaggle_data_analysis)
> **Logistics Operations Analytics, Statistical Hypothesis Testing & Diagnostic Modeling**

* **Business Problem**: Operations observed that certain deliveries take too long, but lacked data-driven clarity on where resources should be allocated to resolve delays.
* **Solution & Functionality**: Deconstructed the problem into concrete KPI tracking across 43,000+ delivery records, using exploratory analysis and econometric regression modeling to identify operational bottlenecks.
* **Key Highlights & Engineering Metrics**:
  1. **Root Cause Identification**: Disproved common assumptions about traffic and distance, isolating that Semi-Urban deliveries face a **+102-minute structural delay** (controlled via OLS regression with HC3 robust standard errors).
  2. **Actionable Operations Strategy**: Advised operations to focus on dispatch and pickup process diagnosis rather than unnecessary driver hiring.
  3. **Executive Presentation Deck**: Packaged findings into an interactive HTML slide deck (OpenSlide) for non-technical leadership review.
* **Tech Stack**: `Python` `Pandas` `Statsmodels (Multivariate OLS)` `Seaborn / Matplotlib` `OpenSlide`

---

### 4. [AI Ads Analyst Agent](digital-marketing-analyst-agent)
> **Autonomous AI Agent for Cross-Channel Advertising & GA4 Analytics**

* **Business Problem**: Multi-channel ad data (Google Ads, Meta Ads, GA4) is fragmented, making it tedious and time-consuming for non-technical stakeholders to interpret complex dashboards.
* **Solution & Functionality**: Built an AI analysis agent that queries ad APIs via standard protocols (MCP), cross-evaluates campaign metrics in natural language, and produces structured reports with clear reasoning traces.
* **Key Highlights & Engineering Metrics**:
  1. **Cross-Channel Performance Comparison**: Automated cross-platform evaluation across CPA, ROAS, CTR, CVR, spend, and conversions.
  2. **Transparent & Audit-Proof**: Built-in environment gates, source citations, and analysis traces to prevent AI hallucinations.
  3. **Flexible Operating Modes**: Supports live API connectivity as well as offline CSV analysis with automated Markdown and Google Sheets reporting.
* **Tech Stack**: `Python` `AI Agent Workflows` `Model Context Protocol (MCP)` `Google Ads API` `Meta Ads API` `GA4 API`

---

## Technical Skills Summary

| Category | Core Technologies & Tools |
|---|---|
| **Data Engineering** | Apache Kafka, Apache Spark Streaming, Google BigQuery, dbt, Apache Airflow, PostgreSQL |
| **Cloud & DevOps** | Google Cloud Platform (GCP), AWS, Docker, Kubernetes (GKE), Terraform (IaC), GitHub Actions (CI/CD) |
| **Data Science & Analytics** | Python (Pandas, Scikit-Learn, Statsmodels), SQL, BigQuery ML, Tableau, Lightdash |
| **AI & Software Engineering** | LLM Agents, Model Context Protocol (MCP), FastAPI, Django, Next.js / TypeScript |

---

## Contact & Links
* **GitHub**: [@Gibon4385](https://github.com/Gibon4385)
* **LinkedIn**: [Po-Chao Wang](https://www.linkedin.com/in/po-chao-wang/)