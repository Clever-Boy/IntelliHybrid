"""
IntelliHybrid — Basic Setup Example
Run this script to see IntelliHybrid in action with a local DynamoDB (LocalStack or DynamoDB Local).

Prerequisites:
  pip install intellihybrid[all]
  # Start DynamoDB Local (optional, for local testing):
  docker run -p 8000:8000 amazon/dynamodb-local
"""

import os
import sys

# For local DynamoDB testing (remove in production):
os.environ.setdefault("AWS_ACCESS_KEY_ID", "local")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "local")
os.environ.setdefault("AWS_ACCOUNT_ID", "000000000000")
os.environ.setdefault("DB_USER", "testuser")
os.environ.setdefault("DB_PASSWORD", "testpassword")

from intellihybrid.core.config_loader import HybridConfig, AWSConfig, OnPremConfig
from intellihybrid.core.config_loader import DatabaseConfig, VPNConfig, DynamoDBConfig, DynamoTableConfig
from intellihybrid.aws.dynamodb import DynamoDBManager
from decimal import Decimal


def demo_dynamodb_operations():
    """Demonstrate DynamoDB table creation and CRUD operations."""
    print("\n" + "=" * 60)
    print("  IntelliHybrid — DynamoDB Demo")
    print("=" * 60 + "\n")

    # Build config programmatically (alternatively, use config.yaml)
    config = HybridConfig(
        aws=AWSConfig(
            region="us-east-1",
            account_id=os.environ["AWS_ACCOUNT_ID"],
            access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        ),
        onprem=OnPremConfig(
            database=DatabaseConfig(
                type="mysql",
                host="192.168.1.100",
                port=3306,
                name="testdb",
                username=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
            ),
            vpn=VPNConfig(
                type="site-to-site",
                customer_gateway_ip="203.0.113.10",
            ),
        ),
        dynamodb=DynamoDBConfig(tables=[
            DynamoTableConfig(
                name="demo-products",
                partition_key={"name": "productId", "type": "S"},
                sort_key={"name": "category", "type": "S"},
                billing_mode="PAY_PER_REQUEST",
                encryption=False,
                point_in_time_recovery=False,
                gsi=[
                    {
                        "name": "category-price-index",
                        "partition_key": {"name": "category", "type": "S"},
                        "sort_key": {"name": "price", "type": "N"},
                    }
                ],
                tags={"Environment": "demo", "Owner": "shailesh"},
            ),
            DynamoTableConfig(
                name="demo-orders",
                partition_key={"name": "orderId", "type": "S"},
                sort_key={"name": "customerId", "type": "S"},
                billing_mode="PAY_PER_REQUEST",
                encryption=False,
                point_in_time_recovery=False,
            ),
        ]),
    )

    dynamo = DynamoDBManager(config)

    # 1. Provision tables
    print("📦 Provisioning DynamoDB tables from config...")
    results = dynamo.provision_all_tables()
    for table, status in results.items():
        icon = "✅" if status in ("CREATED", "EXISTS") else "❌"
        print(f"   {icon} {table}: {status}")

    # 2. Insert items
    print("\n📝 Inserting sample products...")
    products = [
        {
            "productId": "prod-001",
            "category": "electronics",
            "name": "Wireless Headphones",
            "price": Decimal("79.99"),
            "stock": 150,
        },
        {
            "productId": "prod-002",
            "category": "electronics",
            "name": "USB-C Hub",
            "price": Decimal("34.99"),
            "stock": 300,
        },
        {
            "productId": "prod-003",
            "category": "office",
            "name": "Ergonomic Mouse",
            "price": Decimal("49.99"),
            "stock": 75,
        },
    ]
    written = dynamo.batch_write("demo-products", products)
    print(f"   ✅ Inserted {written} products")

    # 3. Fetch a single item
    print("\n🔍 Fetching product prod-001...")
    item = dynamo.get_item("demo-products", {"productId": "prod-001", "category": "electronics"})
    if item:
        print(f"   Found: {item['name']} — ${item['price']}")

    # 4. Scan
    print("\n📋 Scanning all products...")
    all_products = dynamo.scan_table("demo-products")
    for p in all_products:
        print(f"   [{p['category']}] {p['productId']}: {p['name']} — ${p['price']}")

    # 5. List all tables
    print("\n📚 All DynamoDB tables in account:")
    for t in dynamo.list_tables():
        print(f"   - {t}")

    print("\n✅ Demo complete! IntelliHybrid is working.\n")


if __name__ == "__main__":
    demo_dynamodb_operations()
