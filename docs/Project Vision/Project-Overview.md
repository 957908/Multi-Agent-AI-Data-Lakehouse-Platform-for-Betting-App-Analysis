# PROJECT_OVERVIEW.md

# SentinelX Trust AI
## Multi-Agent Fraud Intelligence, Trust Scoring & Risk Analytics Platform

Version: 1.0
Status: Approved
Project Type: Academic + Industry Portfolio
Technology Stack: Big Data, AI, Machine Learning

---

# 1. Project Overview

SentinelX Trust AI is a Big Data and Artificial Intelligence platform designed to collect, process, analyze, and visualize publicly available information from online betting platforms.

The system combines Web Scraping, Streaming Analytics, Data Lakehouse, Machine Learning, Retrieval-Augmented Generation (RAG), and Multi-Agent AI to generate trust scores and risk insights for betting platforms.

---

# 2. Problem Statement

Users often struggle to determine whether an online betting platform is trustworthy.

Important information such as:

- Payment methods
- Bonus policies
- Customer support
- Country availability
- Complaints
- Reviews
- Regulatory information

is scattered across multiple sources.

There is no centralized intelligence platform that provides structured trust analysis.

---

# 3. Project Goal

The primary goal of SentinelX Trust AI is to:

- Collect public data
- Standardize data
- Stream data in real time
- Store data efficiently
- Perform advanced analytics
- Generate Trust Scores
- Detect Risk Indicators
- Provide AI-powered insights

---

# 4. Objectives

The project aims to:

- Build an automated web scraping pipeline
- Process streaming data using Kafka
- Analyze data using Apache Spark
- Store structured data in a Lakehouse
- Build ML-based trust prediction
- Build a RAG chatbot
- Coordinate AI Agents
- Visualize insights through dashboards

---

# 5. End Users

Primary Users

- Researchers
- Data Analysts
- Cybersecurity Professionals
- Risk Analysts
- Compliance Teams

Secondary Users

- Students
- Big Data Learners
- AI Researchers

---

# 6. Target Websites

Current Version

- Melbet
- 10Cric
- 22XBet
- 22Crick

Future Versions

- Stake
- Mostbet
- 1xBet
- Parimatch

---

# 7. High-Level Architecture

```
Website

↓

Web Scraping

↓

Kafka

↓

Apache Flink

↓

Lakehouse

↓

Apache Spark

↓

Machine Learning

↓

Vector Database

↓

RAG

↓

Multi-Agent AI

↓

Dashboard
```

---

# 8. Technology Stack

Programming

- Python

Backend

- FastAPI

Web Scraping

- Scrapy
- Playwright

Streaming

- Apache Kafka

Real-Time Processing

- Apache Flink

Storage

- PostgreSQL
- Parquet
- Delta Lake

Analytics

- Apache Spark

Machine Learning

- Scikit-learn
- XGBoost

Vector Search

- FAISS

AI

- Ollama
- LangChain

Visualization

- Streamlit

Monitoring

- Prometheus
- Grafana

Deployment

- Docker

---

# 9. Project Phases

Phase 1

Data Acquisition

Phase 2

Streaming

Phase 3

Lakehouse

Phase 4

Machine Learning

Phase 5

Vector Search

Phase 6

RAG

Phase 7

Multi-Agent AI

Phase 8

Deployment

---

# 10. Expected Output

The platform should provide

- Clean structured datasets
- Trust Scores
- Risk Scores
- Interactive Dashboards
- AI-generated Reports
- Searchable Knowledge Base

---

# 11. Success Criteria

The project will be considered successful when:

- All websites are scraped successfully
- Data flows through Kafka
- Spark analytics execute successfully
- ML model predicts trust score
- RAG answers user queries
- AI Agents collaborate
- Dashboard displays analytics

---

# 12. Future Scope

Future enhancements may include:

- Additional betting platforms
- Social media sentiment analysis
- News intelligence
- Cloud deployment
- Mobile application
- Real-time alerting
- LLM fine-tuning

---

# Document Status

Approved for Development
