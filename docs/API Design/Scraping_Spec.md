# SCRAPING_SPEC.md

# SentinelX Trust AI
## Web Scraping Specification Document
Version: 1.0
Status: Approved
Author: SentinelX Team
Last Updated: YYYY-MM-DD

---

# 1. Purpose

This document defines the official web scraping requirements for the SentinelX Trust AI project.

The objective is to collect only the required public information from supported betting platforms in a structured format for further processing through Kafka, Apache Flink, Spark, Machine Learning, RAG, and Multi-Agent systems.

This document acts as the contract between the Scraping Module and the Data Engineering Pipeline.

---

# 2. Project Scope

The scraping module is responsible for:

- Collecting public information
- Extracting supported payment methods
- Extracting currencies
- Extracting country availability
- Extracting bonus information (when publicly available)
- Extracting customer support information
- Producing standardized JSON output

The scraper MUST NOT collect unnecessary information.

---

# 3. Supported Websites

| Website | Priority | Spider Name | Status |
|----------|----------|-------------|--------|
| Melbet | High | melbet.py | Pending |
| 10Cric | High | tencric.py | Pending |
| 22XBet | High | twentytwoxbet.py | Pending |
| 22Crick | High | twentytwocrick.py | Pending |

---

# 4. Scraping Objectives

For every supported website, collect only the following information.

## Payment Information

- UPI
- Bank Transfer
- Net Banking
- Debit Card
- Credit Card
- Cryptocurrency
- E-Wallet
- Other Supported Payment Methods

---

## Country Information

- Supported Countries
- Restricted Countries (if publicly available)

---

## Currency Information

Examples

- INR
- USD
- EUR
- GBP
- BTC
- ETH

---

## Bonus Information

Publicly available

Examples

- Welcome Bonus
- Deposit Bonus
- Cashback
- Free Bet

---

## Customer Support

- Live Chat
- Email
- Telegram
- WhatsApp
- Phone Number
- Support URL

---

# 5. Data That MUST NOT Be Collected

The following information is outside project scope.

- Images
- Videos
- Advertisements
- JavaScript Files
- CSS Files
- Cookies
- Analytics Data
- User Personal Information
- Login Credentials
- User Accounts
- Betting History
- Financial Transactions
- Private APIs

---

# 6. Standard Output Schema

Every spider MUST generate the same schema.

```json
{
    "site": "",
    "page_type": "",
    "payment_type": "",
    "payment_name": "",
    "currency": "",
    "country": "",
    "bonus_name": "",
    "support_type": "",
    "support_value": "",
    "status": "",
    "source_url": "",
    "scraped_at": ""
}
```

---

# 7. Required Fields

Mandatory

- site
- source_url
- scraped_at

Optional

- payment_name
- bonus_name
- support_value

---

# 8. Validation Rules

The pipeline must validate:

- No empty site name
- Valid URL
- No duplicate records
- Timestamp available
- JSON format valid
- UTF-8 encoding

Invalid records should be rejected.

---

# 9. Folder Structure

```
sentinelx/

scraper/

    spiders/
        melbet.py
        tencric.py
        twentytwoxbet.py
        twentytwocrick.py

    items.py

    pipelines.py

    settings.py

    middlewares.py

    utils/

    exports/

docs/

SCRAPING_SPEC.md
```

---

# 10. Spider Workflow

```
Website

↓

Request

↓

Response

↓

Parser

↓

Item Extraction

↓

Validation

↓

JSON Output

↓

Export

↓

Kafka (Next Phase)
```

---

# 11. Output Location

All JSON files must be stored inside

```
scraper/exports/
```

Example

```
melbet.json

tencric.json

twentytwoxbet.json

twentytwocrick.json
```

---

# 12. Logging

Every spider must log

- Spider Started
- URL Requested
- Records Extracted
- Validation Passed
- Export Completed
- Errors

---

# 13. Error Handling

Spider should gracefully handle

- Timeout
- 404
- 403
- Connection Error
- Invalid HTML
- Empty Response

Spider should never crash.

---

# 14. Coding Standards

Each spider should

- Follow PEP-8
- Use reusable methods
- Avoid duplicate code
- Include comments
- Use type hints where possible

---

# 15. Ethical Guidelines

The scraper must

- Respect robots.txt where applicable
- Avoid excessive request rates
- Collect only publicly accessible information
- Never bypass authentication without authorization
- Never collect personal or sensitive user data

---

# 16. Future Integration

The JSON output produced by the scraping module will be consumed by

- Apache Kafka
- Apache Flink
- Data Lakehouse
- Apache Spark
- Machine Learning Pipeline
- Vector Database
- RAG System
- Multi-Agent Framework

No schema changes should be required in future phases.

---

# 17. Sprint Plan

## Sprint 1

- Project Setup
- Folder Structure
- Items
- Pipelines
- Settings

---

## Sprint 2

Melbet Spider

---

## Sprint 3

10Cric Spider

---

## Sprint 4

22XBet Spider

---

## Sprint 5

22Crick Spider

---

## Sprint 6

Validation

---

## Sprint 7

JSON Export

---

## Sprint 8

Kafka Integration

---

# 18. Definition of Done

The scraping module is considered complete when

- All four spiders work
- JSON schema is consistent
- Validation passes
- No duplicate records
- Logs generated
- Output exported successfully
- Ready for Kafka integration

---

# End of Document