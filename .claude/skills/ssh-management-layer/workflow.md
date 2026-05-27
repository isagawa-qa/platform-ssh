# SSH Testing Workflow

5-step pipeline for SSH-based image validation.

## Pipeline

```
Input → Preflight → Plan → Execute → Report
```

## Step 1: Input
→ [[references/step-01.md]]
Accept: target host, image variant, test scope, credentials.

## Step 2: Preflight
→ [[references/step-02.md]]
Verify: SSH connectivity, paramiko, host config, key permissions.

## Step 3: Plan
→ [[references/step-03.md]]
Select: validators + thresholds based on variant and scope. Select compliance validators (STIG, CIS, NIST, FIPS, PCI, HIPAA, SOC2, ISO27001) based on host frameworks config.

## Step 4: Execute
→ [[references/step-04.md]]
Run: SSHBatchExecutor processes all validators against target host. Compliance validators run via ComplianceValidator.validate(). Results grouped by framework.

## Step 5: Report
→ [[references/step-05.md]]
Compile: per-validator results, failure analysis, recommendations. Includes per-framework compliance status with by_framework grouping.

## Key Classes

- **SSHInterface** — Layer 1, paramiko wrapper
- **PackageValidator, KernelValidator, ServiceValidator, ConfigValidator** — Layer 2
- **run_ssh_command** — Layer 3, atomic execution
- **SSHBatchExecutor** — Layer 4, orchestrator
- **ComplianceValidator** — Abstract base class for framework-specific validators
- **STIGValidator** — DISA STIG baseline validator (example pattern for agent generation)
