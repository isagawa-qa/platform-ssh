"""DISA STIG Validator for SSH hardening checks."""
import json
import os
from .compliance_validator import ComplianceValidator


class STIGValidator(ComplianceValidator):
    """Validates SSH configuration against DISA STIG requirements."""

    FRAMEWORK = "DISA STIG"
    FRAMEWORK_ID = "stig"

    def default_rules(self):
        fixture_path = os.path.join(
            os.path.dirname(__file__), '..', 'fixtures', 'stig_rules.json'
        )
        with open(fixture_path) as f:
            return json.load(f)
