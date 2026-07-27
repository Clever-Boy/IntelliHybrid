"""
IntelliHybrid — Test Suite
Tests config loading, DynamoDB provisioning, and sync engine.
Uses moto for mocking AWS services.
"""

import os
import pytest
import yaml
from unittest.mock import MagicMock, patch
from decimal import Decimal


# ------------------------------------------------------------------ #
#  Fixtures
# ------------------------------------------------------------------ #

SAMPLE_CONFIG = {
    "aws": {
        "region": "us-east-1",
        "account_id": "123456789012",
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    },
    "onprem": {
        "subnet_cidr": "192.168.0.0/16",
        "database": {
            "type": "mysql",
            "host": "192.168.1.100",
            "port": 3306,
            "name": "testdb",
            "username": "testuser",
            "password": "testpass",
            "ssl": False,
        },
        "vpn": {
            "type": "site-to-site",
            "customer_gateway_ip": "203.0.113.10",
            "bgp_asn": 65000,
        },
    },
    "dynamodb": {
        "tables": [
            {
                "name": "test-users",
                "partition_key": {"name": "userId", "type": "S"},
                "billing_mode": "PAY_PER_REQUEST",
                "encryption": False,
                "point_in_time_recovery": False,
            },
            {
                "name": "test-orders",
                "partition_key": {"name": "orderId", "type": "S"},
                "sort_key": {"name": "createdAt", "type": "N"},
                "billing_mode": "PAY_PER_REQUEST",
                "encryption": False,
                "point_in_time_recovery": False,
            },
        ]
    },
    "log_level": "DEBUG",
    "sync_interval_seconds": 10,
}


@pytest.fixture
def config_file(tmp_path):
    """Write sample config to a temp YAML file and return its path."""
    path = tmp_path / "config.yaml"
    with open(path, "w") as f:
        yaml.dump(SAMPLE_CONFIG, f)
    return str(path)


# ------------------------------------------------------------------ #
#  Config Loader Tests
# ------------------------------------------------------------------ #

class TestConfigLoader:
    def test_loads_successfully(self, config_file):
        from intellihybrid.core.config_loader import ConfigLoader
        cfg = ConfigLoader(config_file).load()
        assert cfg.aws.region == "us-east-1"
        assert cfg.onprem.database.type == "mysql"
        assert cfg.onprem.database.host == "192.168.1.100"
        assert len(cfg.dynamodb.tables) == 2

    def test_resolves_env_vars(self, tmp_path):
        from intellihybrid.core.config_loader import ConfigLoader
        os.environ["TEST_SECRET"] = "resolved_value"
        raw = dict(SAMPLE_CONFIG)
        raw["aws"] = dict(raw["aws"])
        raw["aws"]["secret_access_key"] = "${TEST_SECRET}"
        path = tmp_path / "config_env.yaml"
        with open(path, "w") as f:
            yaml.dump(raw, f)
        cfg = ConfigLoader(str(path)).load()
        assert cfg.aws.secret_access_key == "resolved_value"
        del os.environ["TEST_SECRET"]

    def test_raises_on_missing_env_var(self, tmp_path):
        from intellihybrid.core.config_loader import ConfigLoader
        raw = dict(SAMPLE_CONFIG)
        raw["aws"] = dict(raw["aws"])
        raw["aws"]["access_key_id"] = "${NONEXISTENT_VAR_12345}"
        path = tmp_path / "config_bad.yaml"
        with open(path, "w") as f:
            yaml.dump(raw, f)
        with pytest.raises(EnvironmentError, match="NONEXISTENT_VAR_12345"):
            ConfigLoader(str(path)).load()

    def test_invalid_db_type_raises(self, tmp_path):
        from intellihybrid.core.config_loader import ConfigLoader
        raw = dict(SAMPLE_CONFIG)
        raw["onprem"] = dict(raw["onprem"])
        raw["onprem"]["database"] = dict(raw["onprem"]["database"])
        raw["onprem"]["database"]["type"] = "mongodb"
        path = tmp_path / "config_baddb.yaml"
        with open(path, "w") as f:
            yaml.dump(raw, f)
        with pytest.raises(ValueError, match="Invalid database type"):
            ConfigLoader(str(path)).load()

    def test_file_not_found(self):
        from intellihybrid.core.config_loader import ConfigLoader
        with pytest.raises(FileNotFoundError):
            ConfigLoader("/nonexistent/path/config.yaml").load()

    def test_table_partition_key_validated(self, tmp_path):
        from intellihybrid.core.config_loader import ConfigLoader
        raw = dict(SAMPLE_CONFIG)
        raw["dynamodb"] = {
            "tables": [{
                "name": "bad-table",
                "partition_key": {"name": "id", "type": "X"},  # invalid type
            }]
        }
        path = tmp_path / "config_badkey.yaml"
        with open(path, "w") as f:
            yaml.dump(raw, f)
        with pytest.raises(ValueError, match="partition_key type"):
            ConfigLoader(str(path)).load()


# ------------------------------------------------------------------ #
#  DynamoDB Manager Tests (moto)
# ------------------------------------------------------------------ #

class TestDynamoDBManager:

    @pytest.fixture(autouse=True)
    def aws_mock(self):
        """Mock AWS credentials and use moto."""
        os.environ.update({
            "AWS_DEFAULT_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": "testing",
            "AWS_SECRET_ACCESS_KEY": "testing",
            "AWS_SECURITY_TOKEN": "testing",
            "AWS_SESSION_TOKEN": "testing",
        })

    def test_provision_creates_tables(self, config_file):
        try:
            from moto import mock_aws
        except ImportError:
            pytest.skip("moto not installed")

        from intellihybrid.core.config_loader import ConfigLoader
        from intellihybrid.aws.dynamodb import DynamoDBManager

        with mock_aws():
            cfg = ConfigLoader(config_file).load()
            mgr = DynamoDBManager(cfg)
            results = mgr.provision_all_tables()
            assert results["test-users"] == "CREATED"
            assert results["test-orders"] == "CREATED"

    def test_table_exists_not_recreated(self, config_file):
        try:
            from moto import mock_aws
        except ImportError:
            pytest.skip("moto not installed")

        from intellihybrid.core.config_loader import ConfigLoader
        from intellihybrid.aws.dynamodb import DynamoDBManager

        with mock_aws():
            cfg = ConfigLoader(config_file).load()
            mgr = DynamoDBManager(cfg)
            mgr.provision_all_tables()
            results = mgr.provision_all_tables()
            assert results["test-users"] == "EXISTS"

    def test_put_and_get_item(self, config_file):
        try:
            from moto import mock_aws
        except ImportError:
            pytest.skip("moto not installed")

        from intellihybrid.core.config_loader import ConfigLoader
        from intellihybrid.aws.dynamodb import DynamoDBManager

        with mock_aws():
            cfg = ConfigLoader(config_file).load()
            mgr = DynamoDBManager(cfg)
            mgr.provision_all_tables()

            item = {"userId": "user-1", "name": "Alice", "age": Decimal("30")}
            mgr.put_item("test-users", item)

            fetched = mgr.get_item("test-users", {"userId": "user-1"})
            assert fetched is not None
            assert fetched["name"] == "Alice"

    def test_batch_write(self, config_file):
        try:
            from moto import mock_aws
        except ImportError:
            pytest.skip("moto not installed")

        from intellihybrid.core.config_loader import ConfigLoader
        from intellihybrid.aws.dynamodb import DynamoDBManager

        with mock_aws():
            cfg = ConfigLoader(config_file).load()
            mgr = DynamoDBManager(cfg)
            mgr.provision_all_tables()

            items = [{"userId": f"user-{i}", "name": f"User {i}"} for i in range(10)]
            written = mgr.batch_write("test-users", items)
            assert written == 10


# ------------------------------------------------------------------ #
#  Serialization Tests
# ------------------------------------------------------------------ #

class TestSerialization:
    def test_float_to_decimal(self):
        from intellihybrid.bridge.sync import _serialize_for_dynamo
        result = _serialize_for_dynamo({"price": 9.99})
        assert isinstance(result["price"], Decimal)
        assert result["price"] == Decimal("9.99")

    def test_nested_dict(self):
        from intellihybrid.bridge.sync import _serialize_for_dynamo
        result = _serialize_for_dynamo({"outer": {"inner": 1.5}})
        assert isinstance(result["outer"]["inner"], Decimal)

    def test_list_items(self):
        from intellihybrid.bridge.sync import _serialize_for_dynamo
        result = _serialize_for_dynamo([1.1, 2.2, "hello"])
        assert isinstance(result[0], Decimal)
        assert result[2] == "hello"

    def test_row_fingerprint_deterministic(self):
        from intellihybrid.bridge.sync import _row_fingerprint
        row = {"id": 1, "name": "Alice", "value": 42.5}
        fp1 = _row_fingerprint(row)
        fp2 = _row_fingerprint(row)
        assert fp1 == fp2

    def test_row_fingerprint_changes_on_mutation(self):
        from intellihybrid.bridge.sync import _row_fingerprint
        row1 = {"id": 1, "name": "Alice"}
        row2 = {"id": 1, "name": "Bob"}
        assert _row_fingerprint(row1) != _row_fingerprint(row2)
