# Technical Requirements Document (TRD)

Version: 1.0
Status: Draft
Project: SentinelX AI – Multi-Agent Data Lakehouse Platform
Author: niraj
Last Updated:  June 
# 1. Purpose

The Technical Requirements Document (TRD) describes how SentinelX AI will be designed, developed, deployed, and maintained.

This document focuses on the technical architecture, software components, technology stack, implementation strategy, coding standards, and deployment plan.

Unlike the Product Requirements Document (PRD), which defines *what* the system should do, the TRD defines *how* the system will achieve those requirements.
# 2. Project Overview

SentinelX AI is a production-style, open-source Multi-Agent AI platform designed to collect, process, analyze, and visualize publicly available betting website data.

The platform integrates Web Scraping, Big Data Processing, Machine Learning, Retrieval-Augmented Generation (RAG), and Multi-Agent AI into a single intelligent system.

The project follows a modular architecture, allowing each component to be developed, tested, and deployed independently.
# 3. Technical Goals

The technical objectives of this project are:

- Build a scalable backend architecture.
- Automate data collection from public websites.
- Process data using Big Data technologies.
- Store structured datasets efficiently.
- Apply Machine Learning for analytics.
- Enable semantic search using vector embeddings.
- Build a Multi-Agent AI workflow.
- Deploy using Docker.
                    User
                      │
                      ▼
                 FastAPI API
                      │
                      ▼
             LangGraph Orchestrator
                      │
 ┌──────────────┬──────────────┬──────────────┐
 │              │              │              │
 ▼              ▼              ▼              ▼
Scraper     Validator      Analytics       RAG
 Agent         Agent          Agent        Agent
 │              │              │              │
 └──────────────┴──────┬───────┴──────────────┘
                        │
                        ▼
                  PostgreSQL
                        │
                        ▼
                  Spark Pipeline
                        │
                        ▼
              Iceberg + MinIO
                        │
                        ▼
                   Streamlit

# Updated Architecture
                React (Next.js)

                       │

                 REST API/WebSocket

                       │

                   FastAPI

                       │

                LangGraph Agents

                       │

     Scraper  ML  Kafka  Spark  RAG

                       │

                PostgreSQL

                       │

              Iceberg + MinIO    

# 5. Technology Stack

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Axios
- Recharts

---

## Backend

- Python 3.13+
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

---

## Database

- PostgreSQL

---

## Web Scraping

- Playwright
- Scrapy
- BeautifulSoup

---

## Streaming

- Apache Kafka

---

## Big Data

- Apache Spark (PySpark)

---

## Data Lakehouse

- Apache Iceberg
- MinIO

---

## AI & Machine Learning

- Scikit-Learn
- FAISS
- Sentence Transformers
- Ollama
- LangChain
- LangGraph

---

## DevOps

- Docker
- Docker Compose

---

## Monitoring

- Prometheus
- Grafana

---

## Version Control

- Git
- GitHub                             