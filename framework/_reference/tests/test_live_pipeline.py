"""Live pipeline tests: real SSH target, no mocks.

Run with a target named by SSH_TEST_* env vars (see conftest.py). The
per-rule correctness test also needs SSH_TEST_SSHD_CONFIG: the path to the
sshd_config the target is running (tests/target/sshd_config for the bundled
Docker target). It computes each rule's expected verdict from that file
independently of the validator and asserts every one of the 88 rules agrees.
"""
import json
import os
import re
from pathlib import Path

import pytest

from roles.ssh_batch_executor import SSHBatchExecutor
from tasks.run_ssh_command import run_ssh_command
from validators.compliance_validator import ComplianceValidator

pytestmark = pytest.mark.live

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
RULE_FILES = sorted(FIXTURES.glob("*_rules.json"))
# Packages and services the bundled target provides (every package/service rule in the fixtures).
TARGET_PACKAGES = {"openssh-server"}
TARGET_SERVICES = {"sshd": "active"}


def make_validator(ssh, path):
    stem = path.stem.replace("_rules", "")
    cls = type(f"{stem.upper()}Validator", (ComplianceValidator,), {"FRAMEWORK": stem, "FRAMEWORK_ID": stem})
    return cls(ssh, json.loads(path.read_text(encoding="utf-8")))


def expected_verdict(rule, config_text):
    """Independent oracle: what the rule's verdict must be for this sshd_config."""
    kind = rule["check_type"]
    if kind == "config_value":
        for line in config_text.splitlines():
            parts = line.split()
            if parts and parts[0].lower() == rule["directive"].lower():
                return len(parts) > 1 and parts[1].lower() == rule["expected"].lower()
        return False
    if kind == "config_absent":
        # The validator runs `grep -i '<directive>'`: the directive is a regex
        # (e.g. "Ciphers.*chacha20"), matched case-insensitively per line.
        pattern = re.compile(rule["directive"], re.IGNORECASE)
        return not any(pattern.search(line) for line in config_text.splitlines())
    if kind == "package_installed":
        return rule["package"] in TARGET_PACKAGES
    if kind == "service_status":
        return TARGET_SERVICES.get(rule["service"]) == rule["expected_status"]
    raise AssertionError(f"oracle has no rule for check_type {kind}")


@pytest.fixture(scope="module")
def target_config():
    path = os.environ.get("SSH_TEST_SSHD_CONFIG")
    if not path or not Path(path).is_file():
        msg = "SSH_TEST_SSHD_CONFIG not set to the target's sshd_config; per-rule oracle unavailable"
        if os.environ.get("SSH_LIVE_REQUIRED") == "1":
            pytest.fail(msg, pytrace=False)
        pytest.skip(msg)
    return Path(path).read_text(encoding="utf-8")


def test_interface_executes_and_reports_exit_code(live_ssh):
    ok = live_ssh.execute("echo isagawa-live")
    assert ok["exit_code"] == 0 and ok["passed"] is True
    assert ok["stdout"] == "isagawa-live"
    bad = live_ssh.execute("exit 3")
    assert bad["exit_code"] == 3 and bad["passed"] is False


def test_run_ssh_command_honors_expected_exit(live_ssh):
    assert run_ssh_command(live_ssh, "test -f /etc/ssh/sshd_config")["passed"] is True
    assert run_ssh_command(live_ssh, "test -f /nonexistent", expected_exit=1)["passed"] is True


def test_batch_executor_covers_all_frameworks(live_ssh):
    assert len(RULE_FILES) == 8
    executor = SSHBatchExecutor(live_ssh, [make_validator(live_ssh, p) for p in RULE_FILES])
    executor.execute_all()
    summary = executor.get_results()
    assert summary["total"] == 88
    assert len(summary["by_framework"]) == 8
    assert summary["passed"] + summary["failed"] == 88
    assert all("evidence" in r and r["evidence"] != "" for r in summary["details"])


def test_every_rule_matches_the_oracle(live_ssh, target_config):
    mismatches, passed, failed, total = [], 0, 0, 0
    for path in RULE_FILES:
        rules = json.loads(path.read_text(encoding="utf-8"))
        results = make_validator(live_ssh, path).validate()
        assert len(results) == len(rules)
        for rule, result in zip(rules, results):
            total += 1
            want = expected_verdict(rule, target_config)
            passed += result["passed"]
            failed += not result["passed"]
            if result["passed"] != want:
                mismatches.append(f"{rule['rule_id']}: validator={result['passed']} oracle={want} "
                                  f"actual={result['actual']!r} evidence={result['evidence']!r}")
    print(f"live rules: {total} total, {passed} pass, {failed} fail, {len(mismatches)} oracle mismatches")
    assert total == 88
    assert passed > 0 and failed > 0, "target must exercise both verdicts"
    assert not mismatches, "\n".join(mismatches)
