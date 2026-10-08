"""Unit tests for ComplianceValidator check semantics.

The fake SSH below returns exactly what SSHInterface.execute() returns
(command, stdout, stderr, exit_code, passed) and nothing else, so these
tests fail if the validator reads a key the real interface never sets.
"""
import json
from pathlib import Path

import pytest

from validators.compliance_validator import ComplianceValidator

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
CHECK_TYPES = {"config_value", "config_absent", "package_installed", "service_status"}


class FakeSSH:
    """Answers commands by prefix with (exit_code, stdout), like SSHInterface.execute()."""

    def __init__(self, responses):
        self.responses = responses
        self.commands = []

    def execute(self, cmd):
        self.commands.append(cmd)
        for prefix, (code, out) in self.responses.items():
            if cmd.startswith(prefix):
                return {"command": cmd, "stdout": out, "stderr": "", "exit_code": code, "passed": code == 0}
        return {"command": cmd, "stdout": "", "stderr": "not found", "exit_code": 1, "passed": False}


class SampleValidator(ComplianceValidator):
    FRAMEWORK = "Sample"
    FRAMEWORK_ID = "sample"


def run(responses, rule):
    return SampleValidator(FakeSSH(responses), [rule]).validate()[0]


def config_rule(directive, expected):
    return {"rule_id": "T-001", "check_type": "config_value", "file": "/etc/ssh/sshd_config",
            "directive": directive, "expected": expected, "severity": "high"}


def test_config_value_match_passes():
    r = run({"grep -i '^PermitRootLogin'": (0, "PermitRootLogin no")}, config_rule("PermitRootLogin", "no"))
    assert r["passed"] is True
    assert r["actual"] == "no"


def test_config_value_mismatch_fails_with_actual_value():
    r = run({"grep -i '^PermitRootLogin'": (0, "PermitRootLogin yes")}, config_rule("PermitRootLogin", "no"))
    assert r["passed"] is False
    assert r["actual"] == "yes"


def test_config_value_is_case_insensitive():
    r = run({"grep -i '^LogLevel'": (0, "LogLevel verbose")}, config_rule("LogLevel", "VERBOSE"))
    assert r["passed"] is True


def test_config_value_missing_directive_fails():
    r = run({}, config_rule("MaxAuthTries", "4"))
    assert r["passed"] is False
    assert r["actual"] == "not found"


def test_config_absent_passes_when_grep_finds_nothing():
    rule = {"rule_id": "T-002", "check_type": "config_absent", "file": "/etc/ssh/sshd_config",
            "directive": "PermitUserEnvironment yes", "severity": "high"}
    r = run({}, rule)
    assert r["passed"] is True
    assert r["actual"] == "absent"


def test_config_absent_fails_when_present():
    rule = {"rule_id": "T-002", "check_type": "config_absent", "file": "/etc/ssh/sshd_config",
            "directive": "PermitUserEnvironment yes", "severity": "high"}
    r = run({"grep -i 'PermitUserEnvironment yes'": (0, "PermitUserEnvironment yes")}, rule)
    assert r["passed"] is False
    assert r["actual"] == "present"


def test_package_installed_passes():
    rule = {"rule_id": "T-003", "check_type": "package_installed", "package": "openssh-server", "severity": "high"}
    r = run({"rpm -q openssh-server": (0, "openssh-server-8.7p1-38.el9.x86_64")}, rule)
    assert r["passed"] is True
    assert r["actual"] == "installed"


def test_package_missing_fails():
    rule = {"rule_id": "T-003", "check_type": "package_installed", "package": "openssh-server", "severity": "high"}
    r = run({"rpm -q openssh-server": (1, "package openssh-server is not installed")}, rule)
    assert r["passed"] is False
    assert r["actual"] == "not installed"


SERVICE_RULE = {"rule_id": "T-004", "check_type": "service_status", "service": "sshd",
                "expected_status": "active", "severity": "high"}


def test_service_via_systemctl():
    r = run({"systemctl is-active sshd": (0, "active")}, SERVICE_RULE)
    assert r["passed"] is True
    assert r["evidence"].startswith("systemctl")


def test_service_pgrep_fallback_reports_active():
    r = run({"systemctl is-active sshd": (1, ""), "pgrep -f sshd": (0, "1")}, SERVICE_RULE)
    assert r["passed"] is True
    assert r["actual"] == "active"
    assert r["evidence"].startswith("pgrep")


def test_service_pgrep_fallback_not_running_fails():
    r = run({"systemctl is-active sshd": (1, ""), "pgrep -f sshd": (1, "")}, SERVICE_RULE)
    assert r["passed"] is False
    assert r["actual"] == "inactive"


def test_unknown_check_type_fails_closed():
    r = run({}, {"rule_id": "T-005", "check_type": "bogus", "severity": "low"})
    assert r["passed"] is False
    assert r["check"] == "unknown"


def test_result_carries_framework_fields():
    r = run({"grep -i '^PermitRootLogin'": (0, "PermitRootLogin no")}, config_rule("PermitRootLogin", "no"))
    for key in ("rule_id", "framework", "framework_id", "check", "passed", "expected",
                "actual", "evidence", "severity", "remediation"):
        assert key in r
    assert r["framework"] == "Sample"


RULE_FILES = sorted(FIXTURES.glob("*_rules.json"))


def test_all_eight_rule_fixtures_present():
    assert len(RULE_FILES) == 8


@pytest.mark.parametrize("path", RULE_FILES, ids=lambda p: p.stem)
def test_fixture_rules_dispatch_to_known_checks(path):
    rules = json.loads(path.read_text(encoding="utf-8"))
    assert rules, f"{path.name} is empty"
    assert {r["check_type"] for r in rules} <= CHECK_TYPES
    results = SampleValidator(FakeSSH({}), rules).validate()
    assert len(results) == len(rules)
    assert all(r["check"] != "unknown" for r in results)
