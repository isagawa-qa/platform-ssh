# Step 5: Report

Compile test results into actionable report.

## Content

- Summary: host, variant, scope, overall pass/fail, timestamp
- Per-validator: name, status, evidence, duration
- Failure analysis: categorize (missing package, wrong version, stopped service, etc.)
- Recommendations: specific fix action per failure
- Compliance: CIS/STIG percentage if compliance scope

## Formats

- JSON (machine-readable): structured results for CI/CD integration
- Markdown (human-readable): formatted report for QA review
