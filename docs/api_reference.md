# 🔌 SentinelX Trust AI — REST API Reference Guide

**Version:** 5.0.0 (API v1)  
**Base URL:** `http://localhost:8000/api/v1`  
**Envelope Format:** Standardized `APIResponse[T]`  

---

## 📐 Unified API Response Envelope

Every endpoint returns JSON wrapped in a standard `APIResponse` structure:

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": { ... }
}
```

In the event of an error, `success` is `false`, `data` is `null`, and `message` describes the issue:

```json
{
  "success": false,
  "message": "Resource not found for platform 'unknown_site'.",
  "data": null
}
```

---

## 🔑 Authentication & Headers

Protected endpoints require a Bearer JWT Token passed in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Seeded Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@sentinelx.com` | `AdminPassword123` |
| **Analyst** | `analyst@sentinelx.com` | `AnalystPassword123` |
| **Reader** | `reader@sentinelx.com` | `ReaderPassword123` |

---

## 📋 Endpoint Directory

### 🏥 1. System Health (`/health`)

#### `GET /api/v1/health`
Checks platform availability, uptime telemetry, and PostgreSQL database connectivity.

- **Access Level:** Public
- **Response Example (200 OK):**
```json
{
  "success": true,
  "message": "System is healthy and operational.",
  "data": {
    "status": "healthy",
    "timestamp": "2026-07-29T21:45:00.000000",
    "version": "5.0.0",
    "database": "connected",
    "uptime_seconds": 3600.42
  }
}
```

---

### 🔑 2. Authentication (`/auth`)

#### `POST /api/v1/auth/login`
Authenticates email and password credentials, returning a JWT access token.

- **Access Level:** Public
- **Request Body:**
```json
{
  "email": "analyst@sentinelx.com",
  "password": "AnalystPassword123"
}
```
- **Response Example (200 OK):**
```json
{
  "success": true,
  "message": "Authentication successful.",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "email": "analyst@sentinelx.com",
      "role": "analyst"
    }
  }
}
```

#### `GET /api/v1/auth/me`
Retrieves the currently authenticated user's active session profile.

- **Access Level:** Authenticated (`Bearer Token`)

---

### 🏆 3. Gold Layer Analytics (`/gold`)

#### `GET /api/v1/gold/platforms`
Retrieves pre-computed Gold platform analytics with pagination and filters.

- **Query Parameters:**
  - `q`: Free text query
  - `site`: Platform domain filter (e.g. `melbet`)
  - `risk_level`: Filter by risk tier (`LOW`, `MEDIUM`, `HIGH`)
  - `min_trust_score` / `max_trust_score`: Score range filter (0–100)
  - `page` (default 1), `size` (default 20)
- **Response Example (200 OK):**
```json
{
  "success": true,
  "message": "Retrieved 1 Gold platform analytics record(s) out of 1 total match(es).",
  "data": {
    "total": 1,
    "page": 1,
    "size": 20,
    "pages": 1,
    "items": [
      {
        "site": "melbet",
        "trust_score": 88.5,
        "trust_level": "HIGH",
        "confidence_score": 0.90,
        "total_payment_methods": 12,
        "active_payment_methods": 10,
        "supported_countries": ["IN", "BR"],
        "top_payment_methods": ["Paytm", "UPI", "Bitcoin"],
        "risk_summary": "High platform trust score based on diverse payment methods.",
        "risk_flags": [],
        "last_scraped_at": "2026-07-29T12:00:00.000000",
        "updated_at": "2026-07-29T12:05:00.000000"
      }
    ]
  }
}
```

#### `GET /api/v1/gold/platforms/{site}`
Retrieves pre-computed Gold trust analytics for a specific platform domain.

#### `GET /api/v1/gold/insights`
Retrieves pre-computed payment method reliability insights across platforms.

---

### 🔎 4. Multi-Criteria Search (`/search`)

#### `GET /api/v1/search`
Searches payment records supporting free text, platform, country, currency, trust score range, and risk level filtering.

- **Query Parameters:** `q`, `site`, `payment_name`, `payment_type`, `country`, `currency`, `min_trust_score`, `max_trust_score`, `risk_level`, `page`, `size`.

---

### 🧠 5. AI Intelligence (`/trust-score`, `/analyze`, `/rag/query`)

#### `POST /api/v1/trust-score`
Computes Trust Score (0-100), risk tier, confidence score, and individual rule breakdown.

- **Access Level:** Analyst / Admin
- **Request Body:**
```json
{
  "site": "melbet"
}
```
- **Response Example (200 OK):**
```json
{
  "success": true,
  "message": "Trust Score calculated successfully for platform 'melbet'.",
  "data": {
    "site": "melbet",
    "trust_score": 88.5,
    "trust_level": "HIGH",
    "confidence_score": 0.90,
    "score_explanation": "Platform 'melbet' achieved a Trust Score of 88.5/100 (HIGH). Data confidence: 90%.",
    "rule_evaluations": [
      {
        "rule_name": "Rule 1: Data Completeness",
        "passed": true,
        "score_contribution": 25.0,
        "max_weight": 25.0,
        "description": "High data completeness with 12 records."
      }
    ],
    "risk_flags": [],
    "evaluated_at": "2026-07-29T21:45:00.000000"
  }
}
```

#### `POST /api/v1/analyze`
Generates structured AI risk analysis report and payment method reliability breakdowns.

#### `POST /api/v1/rag/query`
Executes provider-agnostic RAG natural language search against platform documents.

- **Request Body:**
```json
{
  "query": "What payment methods are supported on Melbet in India?",
  "top_k": 3,
  "filter_site": "melbet"
}
```

---

### 📊 6. Telemetry (`/metrics`)

#### `GET /metrics`
Exposes Prometheus metric counters, status codes, and latency histograms.

- **Access Level:** Public / Monitor
- **Response Format:** Plain text Prometheus exposition format.

---

## 💻 Runnable cURL Examples

### 1. Authenticate and Obtain JWT Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "analyst@sentinelx.com", "password": "AnalystPassword123"}'
```

### 2. Search Gold Platform Analytics
```bash
curl -X GET "http://localhost:8000/api/v1/gold/platforms?min_trust_score=70&risk_level=HIGH" \
     -H "Accept: application/json"
```

### 3. Compute Live Trust Score
```bash
curl -X POST "http://localhost:8000/api/v1/trust-score" \
     -H "Authorization: Bearer <your_jwt_token>" \
     -H "Content-Type: application/json" \
     -d '{"site": "melbet"}'
```
