"""Tests for DISA STIG Validator."""
import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from validators.stig_validator import STIGValidator


class TestSTIGValidatorUnit:
    """Unit tests: no SSH connection needed."""

    def test_framework_attributes(self):
        mock_ssh = MagicMock()
        v = STIGValidator(mock_ssh)
        assert v.FRAMEWORK == "DISA STIG"
        assert v.FRAMEWORK_ID == "stig"

    def test_default_rules_loads_fixture(self):
        mock_ssh = MagicMock()
        v = STIGValidator(mock_ssh)
        rules = v.default_rules()
        assert isinstance(rules, list)
        assert len(rules) == 15

    def test_rule_ids_prefix(self):
        mock_ssh = MagicMock()
        v = STIGValidator(mock_ssh)
        rules = v.default_rules()
        for rule in rules:
            assert rule["rule_id"].startswith("STIG-"), f"Rule {rule['rule_id']} missing STIG- prefix"

    def test_validate_returns_results(self):
        mock_ssh = MagicMock()
        mock_ssh.execute.return_value = {
            "stdout": "PermitRootLogin no",
            "stderr": "",
            "exit_code": 0,
            "passed": True,
            "returncode": 0
        }
        v = STIGValidator(mock_ssh)
        results = v.validate()
        assert isinstance(results, list)
        assert len(results) == 15
        for r in results:
            assert "rule_id" in r
            assert "framework" in r
            assert r["framework"] == "DISA STIG"
            assert "severity" in r
            assert "passed" in r


class TestSTIGValidatorLive:
    """Live tests against Docker SSH target."""

    @pytest.fixture
    def ssh_connection(self, live_ssh):
        """Live target from conftest's live_ssh (SSH_TEST_* env vars)."""
        return live_ssh

    @pytest.mark.live
    def test_live_stig_validation(self, ssh_connection):
        v = STIGValidator(ssh_connection)
        results = v.validate()
        assert isinstance(results, list)
        assert len(results) == 15
        for r in results:
            assert "rule_id" in r
            assert "framework" in r
            assert "severity" in r
            assert "passed" in r
            assert "expected" in r
            assert "actual" in r
            assert "evidence" in r
            assert "remediation" in r

    @pytest.mark.live
    def test_live_stig_result_count(self, ssh_connection):
        v = STIGValidator(ssh_connection)
        results = v.validate()
        assert len(results) == 15
        stig_ids = [r["rule_id"] for r in results]
        assert all(rid.startswith("STIG-") for rid in stig_ids)
