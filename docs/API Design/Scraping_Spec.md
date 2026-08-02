# SentinelX Trust AI – Web Scraping & Data Acquisition Specification

**Version:** 2.0  
**Status:** Approved  
**Author:** Rayri Sharma (Senior Data Acquisition Engineer)  
**Last Updated:** 2026-07-29  

---

## 1. Purpose

This document defines the official design, structure, schemas, and verification rules for the SentinelX Trust AI web scraping and data acquisition engine. 

The goal of the Data Acquisition module is to reliably scrape public payment gateway details (supported providers, transaction limits, processing latency, fees) from digital platform cashiers and structure them into a normalized Pydantic model format matching schema version 1.1 for downstream processing (ETL, lakehouse tiers, AI engine, and APIs).

---

## 2. Platform Architecture & Adapter Hierarchy

The acquisition engine relies on a unified Playwright browser execution context. It uses a factory pattern to resolve target-specific handlers dynamically at runtime:

```mermaid
classDiagram
    class BaseAdapter {
        <<Abstract>>
        +page: Page
        +context: BrowserContext
        +selectors: Dict
        +login_if_required()
        +navigate_to_deposit()
        +discover_payment_methods()
        +extract_payment_details()
    }
    class OneXBetAdapter {
        +login_if_required()
        +navigate_to_deposit()
    }
    class MelbetAdapter {
        +login_if_required()
        +navigate_to_deposit()
    }
    class TenCricAdapter {
        +login_if_required()
        +navigate_to_deposit()
    }
    class TwentyTwoXBetAdapter {
        +login_if_required()
        +navigate_to_deposit()
    }

    BaseAdapter <|-- OneXBetAdapter
    BaseAdapter <|-- MelbetAdapter
    BaseAdapter <|-- TenCricAdapter
    BaseAdapter <|-- TwentyTwoXBetAdapter
```

### 📋 Platform Mappings and Registry Aliases
All concrete adapters are registered inside the centralized `AdapterFactory` mapping registry:
* `"onexbet"`, `"1xbet"`: `OneXBetAdapter`
* `"melbet"`: `MelbetAdapter`
* `"10cric"`, `"tencric"`: `TencricAdapter` (pointing to `TenCricAdapter`)
* `"22xbet"`, `"twentytwobet"`: `TwentyTwoBetAdapter` (pointing to `TwentyTwoXBetAdapter`)

---

## 3. Data Acquisition Workflow

The scraping loop utilizes nested sub-managers to complete authentication, cashier navigation, lazy-load scanning, and detail extraction loops:

```mermaid
sequenceDiagram
    participant Main as main.py (Runner)
    participant Browser as BrowserManager
    participant Session as SessionManager
    participant Adapter as Site Adapter
    participant Discovery as PaymentDiscovery

    Main->>Browser: start_browser()
    Main->>Session: check_session(site)
    Session-->>Main: Return Session State (if active)
    Main->>Adapter: Instantiate Adapter(page, context)
    Adapter->>Session: verify_session_cookies(context)
    Note over Session: If cookies expired, clear state
    Adapter->>Adapter: login_if_required()
    Adapter->>Adapter: navigate_to_deposit()
    Adapter->>Discovery: discover_methods(selectors, site)
    
    loop Scrape Payments Loop
        Discovery->>Discovery: Click payment item
        Discovery->>Discovery: Capture screenshots & outer HTML
        Discovery->>Discovery: Scrape modal (limits, payee, etc.)
        Discovery->>Discovery: Parse fee & latency (heuristics)
    end
    
    Discovery-->>Adapter: Return PaymentRecord dicts
    Adapter->>Main: Validate & Save raw output JSON
```

---

## 4. Standard Output Schema (Version 1.1)

All scraped options must comply with the `PaymentRecord` schema. Extra metadata elements (processing delays, commissions, payee info) are captured inside the `extracted_data` dictionary block:

```json
{
    "schema_version": "1.1",
    "scraper_version": "1.0.0",
    "source_platform": "onexbet",
    "extraction_status": "success",
    "extraction_method": "playwright_sync",
    "site": "onexbet",
    "page_type": "deposit_page",
    "payment_type": "upi",
    "payment_name": "UPI Fast",
    "currency": "INR",
    "country": "IN",
    "bonus_name": null,
    "support_type": "live_chat",
    "support_value": null,
    "status": "active",
    "source_url": "https://1xlite-12947.pro/en/office/recharge/",
    "scraped_at": "2026-07-29T15:08:35Z",
    "extracted_data": {
        "upi_id": "merchant@bank",
        "bank_account": null,
        "ifsc_code": null,
        "payee_name": "SentinelX Labs Payee",
        "min_deposit": "500",
        "max_deposit": "50000",
        "limit_info": "Min: 500 INR / Max: 50000 INR",
        "processing_time": "Instant",
        "transaction_fee": "Free"
    }
}
```

---

## 5. Ingestion & Validation Standards

The pipeline validation layers enforce the following quality audits prior to Data Lake raw export:
1. **UTF-8 Charset Encoding:** Console logs and JSON dumps must strip non-ascii emoji characters to prevent encoding exceptions on Windows shells.
2. **Schema Compliance:** The exporter verifies records via the `PaymentRecord` Pydantic model. Invalid records fail validation and are skipped.
3. **Data Lake Organization:** Verified outputs are exported directly to historical directories: `data/raw/YYYY-MM-DD/HH-MM/`.