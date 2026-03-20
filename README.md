# 🔗 IntelliHybrid — Intelligent On-Premise ↔ AWS Cloud Connector

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19121004.svg)](https://doi.org/10.5281/zenodo.19121004)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-DynamoDB%20%7C%20VPC%20%7C%20IAM-orange)](https://aws.amazon.com)
[![AI Powered](https://img.shields.io/badge/AI-Claude%20Powered-blueviolet)](https://anthropic.com)
[![GitHub Stars](https://img.shields.io/github/stars/Clever-Boy/IntelliHybrid?style=social)](https://github.com/Clever-Boy/IntelliHybrid/stargazers)
[![Downloads](https://img.shields.io/github/downloads/Clever-Boy/IntelliHybrid/total)](https://github.com/Clever-Boy/IntelliHybrid/releases)

> **IntelliHybrid** is a production-ready, AI-powered framework that enables secure, seamless bidirectional communication between on-premise infrastructure and AWS cloud — with natural language querying, auto-generated schema documentation, and zero code changes after setup.

<p align="center">
  <a href="https://clever-boy.github.io/IntelliHybrid/ai-demo.html">
    <img src="https://img.shields.io/badge/🤖%20Live%20AI%20Demo-Try%20it%20now-blueviolet?style=for-the-badge" alt="Live AI Demo"/>
  </a>
  &nbsp;&nbsp;
  <a href="docs/HOW_TO_USE.md">
    <img src="https://img.shields.io/badge/📖%20How--To--Use-Read%20the%20guide-blue?style=for-the-badge" alt="How To Use"/>
  </a>
  &nbsp;&nbsp;
  <a href="docs/AI_FEATURES.md">
    <img src="https://img.shields.io/badge/🤖%20AI%20Features-Full%20docs-blueviolet?style=for-the-badge" alt="AI Features"/>
  </a>
</p>

---

## 🚀 What This Does

IntelliHybrid bridges the gap between your on-premise data center and AWS cloud by:

- 🔐 **Establishing secure VPN tunnels** (Site-to-Site, OpenVPN, or Direct Connect)
- 🗄️ **Connecting on-prem databases** (MySQL, PostgreSQL, Oracle, SQL Server) to AWS
- ⚡ **Auto-provisioning DynamoDB tables** with your custom Partition Key (PK) and Sort Key (SK)
- 🔄 **Bidirectional data synchronization** — on-prem → cloud and cloud → on-prem
- 🛡️ **Enterprise-grade security** — IAM roles, KMS encryption, TLS everywhere
- 🤖 **AI-powered data intelligence** — query in plain English, auto-generated column descriptions, instant data dictionaries

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│         ON-PREMISE              │         │           AWS CLOUD              │
│                                 │         │                                  │
│  ┌─────────────┐                │◄───────►│  ┌──────────────────┐            │
│  │  Your DB    │                │  VPN /  │  │   DynamoDB       │            │
│  │  MySQL /    │   IntelliHybrid│  Direct │  │   Tables (auto-  │            │
│  │  Postgres / │◄──────────────►│ Connect │  │   provisioned)   │            │
│  │  Oracle     │                │         │  └──────────────────┘            │
│  └─────────────┘                │         │                                  │
│                                 │         │  ┌──────────────────┐            │
│  ┌─────────────┐                │         │  │  AI Assistant    │            │
│  │  App Server │                │         │  │  NL Queries +    │            │
│  │  (any lang) │                │         │  │  Schema Intel    │            │
│  └─────────────┘                │         │  └──────────────────┘            │
└─────────────────────────────────┘         └──────────────────────────────────┘
                         ▲                              ▲
                         └──────── IntelliHybrid ───────┘
                           config.yaml + Claude AI drives all
```

---

## 🤖 AI Features — Ask Your Data Anything

> ### ▶ [Try the Live Interactive Demo](https://clever-boy.github.io/IntelliHybrid/ai-demo.html)
> Experience natural language queries, schema intelligence, and data dictionaries in your browser — no setup needed.

IntelliHybrid includes a full AI layer powered by Claude that understands your DynamoDB tables. No more writing queries — just ask.

---

### 💬 Natural Language Queries

Write questions the way you'd say them out loud. IntelliHybrid translates them into the correct DynamoDB operation and returns live data.

```python
from src.ai.assistant import AIAssistant

assistant = AIAssistant(config, anthropic_api_key="sk-ant-...")

result = await assistant.chat("Show me all orders from customer C-001")
result = await assistant.chat("How many products have stock below 10?")
result = await assistant.chat("Find users who signed up this month")
result = await assistant.chat("Add a new user: Jane Doe, email jane@example.com")
```

**Examples of questions that just work:**

| What you type | What runs |
|---|---|
| `"Show me all orders from customer C-001"` | `query` with KeyConditionExpression |
| `"How many products are low on stock?"` | `scan` with FilterExpression |
| `"Find the 5 most recent signups"` | `scan` with Limit + sort |
| `"Get order ORD-8821"` | `get_item` with exact key |
| `"Delete expired session sess-99"` | `delete_item` |

The AI also maintains conversation history, so follow-up questions like *"now filter those by electronics"* work naturally.

---

### 🧠 AI-Generated Column Descriptions

IntelliHybrid reads your table schema and a few sample rows, then generates clear business-friendly descriptions for every attribute — automatically.

```python
from src.ai.schema_intelligence import SchemaIntelligence

intel = SchemaIntelligence(config, anthropic_api_key="sk-ant-...")
description = await intel.describe_table("orders-table")
```

```json
{
  "table_description": "Stores customer order transactions with fulfillment status tracking",
  "attribute_descriptions": {
    "orderId":    "Unique identifier for each order transaction",
    "customerId": "References the placing customer — links to users-table PK",
    "status":     "Fulfillment state: processing, shipped, delivered, or cancelled",
    "total":      "Order value in USD cents",
    "createdAt":  "Unix timestamp when placed, used as sort key for date-range queries"
  },
  "access_patterns": [
    "Query all orders for a specific customer",
    "Get a single order by ID",
    "Filter orders by status for a fulfillment dashboard"
  ],
  "suggestions": [
    "Consider adding a GSI on status+createdAt for pipeline queries"
  ]
}
```

---

### 📖 Auto-Generated Data Dictionary

One call produces a fully formatted markdown data dictionary — ready for wikis, compliance documentation, or technical portfolios.

```python
dictionary = await intel.generate_data_dictionary("orders-table")
print(dictionary)
```

```markdown
# Data Dictionary: `orders-table`

**Purpose:** Stores all customer order transactions...

## Attributes

| Attribute          | Type | Description                                          |
|--------------------|------|------------------------------------------------------|
| `orderId` 🔑 PK    | S    | Unique identifier for each order transaction         |
| `customerId` 🔑 SK | S    | References the customer — links to users-table PK    |
| `status`           | S    | Fulfillment state: processing, shipped, delivered... |
| `total`            | N    | Order value in USD cents                             |
| `createdAt`        | N    | Unix timestamp, used for date-range queries          |

## Common Access Patterns

1. Query all orders for a specific customer
2. Get a single order by ID
3. Filter orders by status
```

---

### 🌐 AI REST API

Expose the entire AI layer over HTTP — connect any frontend, dashboard, or external tool.

```bash
pip install "intellihybrid[ai]"
export ANTHROPIC_API_KEY="sk-ant-..."
uvicorn src.ai.server:app --host 0.0.0.0 --port 8080
```

```bash
# Ask your data a question
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all orders from customer C-001"}'

# AI schema description for a table
curl http://localhost:8080/tables/orders-table

# Full data dictionary (markdown)
curl http://localhost:8080/tables/orders-table/dictionary

# Suggested example queries
curl http://localhost:8080/tables/orders-table/suggestions
```

> Interactive Swagger docs available at `http://localhost:8080/docs`

---

### 🖥️ AI Demo — Viewer Preview

The file [`docs/ai-demo.html`](docs/ai-demo.html) is a fully self-contained interactive demo of the AI Assistant. It runs entirely in the browser with no backend needed.

**To view it live**, enable GitHub Pages:
1. Go to **Settings → Pages** in this repo
2. Set Source to **`main` branch, `/docs` folder**
3. Click **Save**

Your demo will be live at:
```
https://clever-boy.github.io/IntelliHybrid/ai-demo.html
```

You can also open it locally — just double-click `docs/ai-demo.html` in your file browser. It shows:
- 💬 Chat interface with AI query responses and record cards
- 🗂️ Sidebar with connected tables and clickable example questions
- 📋 Query result display with per-row attribute cards
- 📖 AI-generated schema description view
- 📚 Auto-generated data dictionary output

---

## ⚡ Quick Start (5 Minutes)

### 1. Install

```bash
pip install intellihybrid
# or from source:
git clone https://github.com/Clever-Boy/IntelliHybrid.git
cd IntelliHybrid
pip install -e .
```

### 2. Configure

```bash
cp config/config.template.yaml config/config.yaml
```

```yaml
aws:
  region: us-east-1
  account_id: "123456789012"
  access_key_id: "${AWS_ACCESS_KEY_ID}"
  secret_access_key: "${AWS_SECRET_ACCESS_KEY}"

onprem:
  database:
    type: mysql                          # mysql | postgres | oracle | mssql
    host: 192.168.1.100
    port: 3306
    name: production_db
    username: "${DB_USER}"
    password: "${DB_PASSWORD}"
  vpn:
    type: site-to-site
    customer_gateway_ip: "203.0.113.10"

dynamodb:
  tables:
    - name: orders-table
      partition_key: { name: orderId, type: S }
      sort_key:      { name: customerId, type: S }
      billing_mode: PAY_PER_REQUEST
```

### 3. Initialize

```bash
intellihybrid init --config config/config.yaml
```

- ✅ Validates all credentials
- ✅ Establishes VPN tunnel
- ✅ Creates DynamoDB tables with your PK/SK schema
- ✅ Sets up least-privilege IAM roles
- ✅ Runs a connectivity health-check

### 4. Start Syncing

```bash
intellihybrid sync --mode bidirectional --interval 60
```

---

## 📦 Core Features

### 🔐 Security First
- All secrets via environment variables or AWS Secrets Manager — **never** in config files
- KMS-encrypted DynamoDB tables by default
- TLS 1.3 for all data in transit
- Least-privilege IAM roles auto-generated per table

### 🗄️ On-Premise Database Support

| Database   | Version   | Status    |
|------------|-----------|-----------|
| MySQL      | 5.7, 8.0+ | ✅ Full   |
| PostgreSQL | 12+       | ✅ Full   |
| Oracle     | 19c+      | ✅ Full   |
| SQL Server | 2019+     | ✅ Full   |
| MongoDB    | 5.0+      | 🔜 Coming |

### 🔄 Sync Modes

```bash
intellihybrid sync --mode full             # one-time complete sync
intellihybrid sync --mode bidirectional    # continuous, recommended
intellihybrid sync --mode push             # on-prem → DynamoDB only
intellihybrid sync --mode pull             # DynamoDB → on-prem only
intellihybrid sync --interval 30           # custom interval (seconds)
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 How-To-Use Booklet](docs/HOW_TO_USE.md) | Complete step-by-step setup guide |
| [🤖 AI Features Guide](docs/AI_FEATURES.md) | Full AI query engine & schema intelligence docs |
| [🔐 Security Guide](docs/SECURITY.md) | IAM, KMS, TLS hardening |
| [📦 Zenodo & Release Guide](docs/ZENODO_AND_RELEASE_GUIDE.md) | DOI, download metrics, EB-1A |
| [🤝 Contributing](CONTRIBUTING.md) | How to contribute |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Good first issues:**

| Feature | Difficulty |
|---|---|
| MongoDB connector | Medium |
| Terraform module | Medium |
| CDC real-time streaming | Hard |
| Web UI dashboard | Hard |

---

## 📄 Citation

If you use IntelliHybrid in your research or production systems, please cite:

```bibtex
@software{kadam_intellihybrid_2025,
  author    = {Kadam, Shailesh},
  title     = {IntelliHybrid: Intelligent On-Premise to AWS Cloud Connector},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19121004},
  url       = {https://github.com/Clever-Boy/IntelliHybrid}
}
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Shailesh Kadam**  
🌐 [GitHub @Clever-Boy](https://github.com/Clever-Boy)  
📍 Dallas, Texas  
💼 [LinkedIn](https://www.linkedin.com/in/sshaileshk)

---

<p align="center">
  <b>⭐ Star this repo if IntelliHybrid saves you time! ⭐</b><br>
  Your stars directly support open-source hybrid cloud tooling.
</p>
