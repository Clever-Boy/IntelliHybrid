# 🔗 IntelliHybrid — Intelligent On-Premise ↔ AWS Cloud Connector

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19121004.svg)](https://doi.org/10.5281/zenodo.19121004)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-DynamoDB%20%7C%20VPC%20%7C%20IAM-orange)](https://aws.amazon.com)
[![GitHub Stars](https://img.shields.io/github/stars/Clever-Boy/IntelliHybrid?style=social)](https://github.com/Clever-Boy/IntelliHybrid/stargazers)
[![Downloads](https://img.shields.io/github/downloads/Clever-Boy/IntelliHybrid/total)](https://github.com/Clever-Boy/IntelliHybrid/releases)

> **IntelliHybrid** is a production-ready, configuration-driven framework that enables secure, seamless bidirectional communication between on-premise infrastructure and AWS cloud environments — with zero code changes after setup.

---

## 🚀 What This Does

IntelliHybrid bridges the gap between your on-premise data center and AWS cloud by:

- 🔐 **Establishing secure VPN tunnels** (Site-to-Site or OpenVPN) between on-prem and AWS VPC
- 🗄️ **Connecting on-prem databases** (MySQL, PostgreSQL, Oracle, SQL Server) to AWS
- ⚡ **Auto-provisioning DynamoDB tables** with your custom Partition Key (PK) and Sort Key (SK) definitions
- 🔄 **Bidirectional data synchronization** — on-prem → cloud and cloud → on-prem
- 🛡️ **Enterprise-grade security** — IAM roles, KMS encryption, Security Groups, TLS everywhere
- 📊 **Observability built-in** — CloudWatch metrics, structured logging, alerting

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐         ┌──────────────────────────────────┐
│       ON-PREMISE                │         │          AWS CLOUD               │
│                                 │         │                                  │
│  ┌─────────────┐                │◄───────►│  ┌──────────────────┐            │
│  │  Your DB    │                │  VPN /  │  │   DynamoDB       │            │
│  │  MySQL /    │   IntelliHybrid│  Direct │  │   Tables (auto-  │            │
│  │  Postgres / │◄──────────────►│ Connect │  │   provisioned)   │            │
│  │  Oracle     │                │         │  └──────────────────┘            │
│  └─────────────┘                │         │                                  │
│                                 │         │  ┌──────────────────┐            │
│  ┌─────────────┐                │         │  │  IAM + KMS +     │            │
│  │  App Server │                │         │  │  VPC + Security  │            │
│  │  (any lang) │                │         │  │  Groups          │            │
│  └─────────────┘                │         │  └──────────────────┘            │
└─────────────────────────────────┘         └──────────────────────────────────┘
                         ▲                              ▲
                         └──────── IntelliHybrid ───────┘
                              (config.yaml drives all)
```
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

Copy the template and fill in your values:

```bash
cp config/config.template.yaml config/config.yaml
```

```yaml
# config/config.yaml
aws:
  region: us-east-1
  account_id: "123456789012"
  access_key_id: "${AWS_ACCESS_KEY_ID}"      # use env vars - never hardcode
  secret_access_key: "${AWS_SECRET_ACCESS_KEY}"

onprem:
  database:
    type: mysql                               # mysql | postgres | oracle | mssql
    host: 192.168.1.100
    port: 3306
    name: production_db
    username: "${DB_USER}"
    password: "${DB_PASSWORD}"
  vpn:
    type: site-to-site                        # site-to-site | openvpn | direct-connect
    customer_gateway_ip: "203.0.113.10"      # your public IP

dynamodb:
  tables:
    - name: users-table
      partition_key: { name: userId, type: S }
      sort_key:      { name: createdAt, type: N }
      billing_mode: PAY_PER_REQUEST
    - name: orders-table
      partition_key: { name: orderId, type: S }
      sort_key:      { name: customerId, type: S }
```

### 3. Initialize

```bash
intellihybrid init --config config/config.yaml
```

This single command will:
- ✅ Validate all credentials
- ✅ Establish VPN tunnel
- ✅ Create DynamoDB tables with your PK/SK schema
- ✅ Set up IAM roles with least-privilege access
- ✅ Configure Security Groups
- ✅ Perform a connectivity health-check

### 4. Start Syncing

```bash
intellihybrid sync --mode bidirectional --interval 60
```

---

## 📦 Features In Detail

### 🔐 Security First
- All secrets loaded from environment variables or AWS Secrets Manager — **never** stored in config files
- KMS-encrypted data at rest in DynamoDB
- TLS 1.3 for all data in transit
- Least-privilege IAM roles auto-generated per table

### 🗄️ On-Premise Database Support

| Database     | Version    | Status |
|--------------|------------|--------|
| MySQL        | 5.7, 8.0+  | ✅ Full |
| PostgreSQL   | 12+        | ✅ Full |
| Oracle       | 19c+       | ✅ Full |
| SQL Server   | 2019+      | ✅ Full |
| MongoDB      | 5.0+       | 🔜 Coming |

### ⚡ DynamoDB Table Provisioning

```python
from intellihybrid.aws import DynamoDBManager

mgr = DynamoDBManager.from_config("config/config.yaml")

# Create a table with any PK/SK combination
mgr.create_table(
    name="inventory",
    partition_key={"name": "productId", "type": "S"},
    sort_key={"name": "warehouseId", "type": "S"},
    gsi=[
        {
            "name": "category-index",
            "partition_key": {"name": "category", "type": "S"},
            "sort_key": {"name": "updatedAt", "type": "N"},
        }
    ],
    billing_mode="PAY_PER_REQUEST",
    encryption=True,
)
```

### 🔄 Sync Modes

```bash
# One-time full sync
intellihybrid sync --mode full

# Continuous bidirectional (recommended for production)
intellihybrid sync --mode bidirectional --interval 30

# Only on-prem → AWS
intellihybrid sync --mode push

# Only AWS → on-prem
intellihybrid sync --mode pull
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 How-To-Use Booklet](docs/HOW_TO_USE.md) | Step-by-step guide for all user types |
| [🏗️ Architecture Guide](docs/ARCHITECTURE.md) | Deep dive into how it works |
| [🔐 Security Guide](docs/SECURITY.md) | Security best practices & hardening |
| [🔧 Configuration Reference](docs/CONFIGURATION.md) | All config options explained |
| [🌐 VPN Setup Guide](docs/VPN_SETUP.md) | VPN configuration walkthroughs |
| [❓ FAQ](docs/FAQ.md) | Common questions & troubleshooting |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

---

## 📄 Citation

If you use IntelliHybrid in your research or production systems, please cite:

```bibtex
@software{kadam_intellihybrid_2025,
  author    = {Kadam, Shailesh},
  title     = {IntelliHybrid: Intelligent On-Premise to AWS Cloud Connector},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.XXXXXXX},
  url       = {https://github.com/Clever-Boy/IntelliHybrid}
}
```

---

## 📊 Stats & Adoption

This project is tracked on [Zenodo](https://zenodo.org) for academic citation metrics and download tracking.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Shailesh Kadam**  
🌐 [GitHub @Clever-Boy](https://github.com/Clever-Boy)  
📍 Dallas, Texas  
💼 [LinkedIn](https://www.linkedin.com/in/shailesh-kadam)

---

<p align="center">
  <b>⭐ Star this repo if IntelliHybrid saves you time! ⭐</b><br>
  Your stars directly support open-source hybrid cloud tooling.
</p>
