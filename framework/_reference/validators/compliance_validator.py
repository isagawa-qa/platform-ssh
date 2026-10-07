"""
ComplianceValidator: Abstract Base Class

All framework-specific validators (STIG, CIS, NIST, etc.) inherit from this base class.
Rules are data-driven: each rule specifies a check_type, and validate() dispatches to the
corresponding check_* method to produce an enhanced result dict.
"""

import re
from abc import ABC
from typing import List, Dict, Any, Optional


class ComplianceValidator(ABC):
    """Abstract base class for compliance validators."""

    FRAMEWORK = ""
    FRAMEWORK_ID = ""

    def __init__(self, ssh, rules: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize the validator.

        Args:
            ssh: SSH client (or mock) with execute(cmd) method
            rules: List of rule dicts. If None, loads from default_rules()
        """
        self.ssh = ssh
        self.rules = rules if rules is not None else self.default_rules()

    def default_rules(self) -> List[Dict[str, Any]]:
        """
        Load default rules from fixture file.
        Subclasses should override or provide fixture path.
        """
        return []

    def check_config_value(
        self,
        file: str,
        directive: str,
        expected: str,
        rule_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        """
        Check that a config file directive has the expected value.

        Args:
            file: Path to config file (e.g., /etc/ssh/sshd_config)
            directive: Directive name (e.g., PermitRootLogin)
            expected: Expected value (e.g., "no")
            rule_id: Rule ID for result
            severity: Severity level

        Returns:
            Enhanced result dict
        """
        try:
            result = self.ssh.execute(f"grep -i '^{directive}' {file}")
            if result.get("exit_code") != 0:
                actual = "not found"
                passed = False
                evidence = f"Directive '{directive}' not found in {file}"
            else:
                output = result.get("stdout", "").strip()
                # Parse: "PermitRootLogin yes" -> "yes"
                match = re.search(rf"^{directive}\s+(.+?)(?:\s|$)", output, re.IGNORECASE)
                actual = match.group(1).strip() if match else "unparseable"
                passed = actual.lower() == expected.lower()
                evidence = output

            return self.make_result(
                rule_id=rule_id,
                check="config_value",
                passed=passed,
                expected=expected,
                actual=actual,
                evidence=evidence,
                severity=severity,
                remediation=f"Set {directive} {expected} in {file}",
            )
        except Exception as e:
            return self.make_result(
                rule_id=rule_id,
                check="config_value",
                passed=False,
                expected=expected,
                actual="error",
                evidence=str(e),
                severity=severity,
                remediation=f"Set {directive} {expected} in {file}",
            )

    def check_config_absent(
        self,
        file: str,
        directive: str,
        rule_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        """
        Check that a config file directive is NOT present.

        Args:
            file: Path to config file
            directive: Directive pattern (e.g., "PermitEmptyPasswords yes")
            rule_id: Rule ID for result
            severity: Severity level

        Returns:
            Enhanced result dict
        """
        try:
            result = self.ssh.execute(f"grep -i '{directive}' {file}")
            passed = result.get("exit_code") != 0
            if passed:
                actual = "absent"
                evidence = f"Directive pattern '{directive}' not found"
            else:
                actual = "present"
                evidence = f"Found: {result.get('stdout', '').strip()}"

            return self.make_result(
                rule_id=rule_id,
                check="config_absent",
                passed=passed,
                expected="absent",
                actual=actual,
                evidence=evidence,
                severity=severity,
                remediation=f"Remove '{directive}' from {file}",
            )
        except Exception as e:
            return self.make_result(
                rule_id=rule_id,
                check="config_absent",
                passed=False,
                expected="absent",
                actual="error",
                evidence=str(e),
                severity=severity,
                remediation=f"Remove '{directive}' from {file}",
            )

    def check_package_installed(
        self,
        package: str,
        rule_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        """
        Check that a package is installed via rpm -q.

        Args:
            package: Package name (e.g., openssh-server)
            rule_id: Rule ID for result
            severity: Severity level

        Returns:
            Enhanced result dict
        """
        try:
            result = self.ssh.execute(f"rpm -q {package}")
            passed = result.get("exit_code") == 0
            actual = "installed" if passed else "not installed"
            evidence = result.get("stdout", "").strip() if passed else "Package not found"

            return self.make_result(
                rule_id=rule_id,
                check="package_installed",
                passed=passed,
                expected="installed",
                actual=actual,
                evidence=evidence,
                severity=severity,
                remediation=f"Install {package}",
            )
        except Exception as e:
            return self.make_result(
                rule_id=rule_id,
                check="package_installed",
                passed=False,
                expected="installed",
                actual="error",
                evidence=str(e),
                severity=severity,
                remediation=f"Install {package}",
            )

    def check_service_status(
        self,
        service: str,
        expected_status: str,
        rule_id: str,
        severity: str,
    ) -> Dict[str, Any]:
        """
        Check that a service has the expected status.
        Uses systemctl first, falls back to pgrep.

        Args:
            service: Service name (e.g., sshd)
            expected_status: Expected status (e.g., active, running)
            rule_id: Rule ID for result
            severity: Severity level

        Returns:
            Enhanced result dict
        """
        try:
            # Try systemctl first
            result = self.ssh.execute(f"systemctl is-active {service}")
            if result.get("exit_code") == 0:
                actual = result.get("stdout", "").strip()
                passed = actual.lower() == expected_status.lower()
                evidence = f"systemctl is-active: {actual}"
            else:
                # Fallback to pgrep (hosts without systemd, e.g. containers).
                # Report in systemctl vocabulary, which is what the rules expect.
                result = self.ssh.execute(f"pgrep -f {service}")
                found = result.get("exit_code") == 0
                actual = "active" if found else "inactive"
                passed = actual.lower() == expected_status.lower()
                evidence = f"pgrep: process {'found' if found else 'not found'} ({actual})"

            return self.make_result(
                rule_id=rule_id,
                check="service_status",
                passed=passed,
                expected=expected_status,
                actual=actual,
                evidence=evidence,
                severity=severity,
                remediation=f"Start {service} service",
            )
        except Exception as e:
            return self.make_result(
                rule_id=rule_id,
                check="service_status",
                passed=False,
                expected=expected_status,
                actual="error",
                evidence=str(e),
                severity=severity,
                remediation=f"Start {service} service",
            )

    def make_result(
        self,
        rule_id: str,
        check: str,
        passed: bool,
        expected: str,
        actual: str,
        evidence: str,
        severity: str,
        remediation: str,
    ) -> Dict[str, Any]:
        """
        Produce an enhanced result dict.

        Args:
            rule_id: Unique rule identifier (e.g., STIG-001)
            check: Check type (e.g., config_value, package_installed)
            passed: Whether the check passed
            expected: Expected value/state
            actual: Actual value/state
            evidence: Evidence string (output, error, etc.)
            severity: Severity level (high, medium, low, critical)
            remediation: Remediation guidance

        Returns:
            Enhanced result dict with framework, check, and structured data
        """
        return {
            "rule_id": rule_id,
            "framework": self.FRAMEWORK,
            "framework_id": self.FRAMEWORK_ID,
            "check": check,
            "passed": passed,
            "expected": expected,
            "actual": actual,
            "evidence": evidence,
            "severity": severity,
            "remediation": remediation,
        }

    def validate(self) -> List[Dict[str, Any]]:
        """
        Run all rules and return a list of results.

        Iterates over self.rules, dispatches each rule to the correct check_*
        method based on the rule's check_type field.

        Returns:
            List of enhanced result dicts
        """
        results = []
        for rule in self.rules:
            check_type = rule.get("check_type")
            rule_id = rule.get("rule_id", "UNKNOWN")
            severity = rule.get("severity", "medium")

            try:
                if check_type == "config_value":
                    result = self.check_config_value(
                        file=rule.get("file"),
                        directive=rule.get("directive"),
                        expected=rule.get("expected"),
                        rule_id=rule_id,
                        severity=severity,
                    )
                elif check_type == "config_absent":
                    result = self.check_config_absent(
                        file=rule.get("file"),
                        directive=rule.get("directive"),
                        rule_id=rule_id,
                        severity=severity,
                    )
                elif check_type == "package_installed":
                    result = self.check_package_installed(
                        package=rule.get("package"),
                        rule_id=rule_id,
                        severity=severity,
                    )
                elif check_type == "service_status":
                    result = self.check_service_status(
                        service=rule.get("service"),
                        expected_status=rule.get("expected_status"),
                        rule_id=rule_id,
                        severity=severity,
                    )
                else:
                    result = self.make_result(
                        rule_id=rule_id,
                        check="unknown",
                        passed=False,
                        expected="unknown",
                        actual="unknown",
                        evidence=f"Unknown check_type: {check_type}",
                        severity=severity,
                        remediation="Check rule configuration",
                    )
                results.append(result)
            except Exception as e:
                result = self.make_result(
                    rule_id=rule_id,
                    check=check_type or "unknown",
                    passed=False,
                    expected="no error",
                    actual="error",
                    evidence=str(e),
                    severity=severity,
                    remediation="Check rule configuration",
                )
                results.append(result)

        return results
