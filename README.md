# Isagawa SSH Compliance Platform

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Compliance Frameworks](https://img.shields.io/badge/Frameworks-8%20Standards-orange.svg)](#compliance-frameworks)

Automated SSH compliance validation across eight security frameworks. An AI agent connects to your infrastructure via SSH, runs checks against STIG, CIS, NIST, FIPS, PCI DSS, HIPAA, SOC 2, and ISO 27001 standards, and produces auditor-ready reports with captured evidence for every check.

Built on the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel). See the full product page at [isagawa.co/ssh-compliance](https://www.isagawa.co/ssh-compliance.html).

## The Problem

Enterprise Linux images ship across AWS, GCP, Azure, and bare metal. Each image variant has specific requirements: correct packages, kernel version, running services, and security configurations. Manual validation doesn't scale. AI-generated scripts break when they don't follow the framework patterns, and there's no enforcement to keep them on track.

The result is a cycle that repeats across organizations: generate a validation script, miss a check, ship a broken image, wait for a customer or auditor to find it, patch, and repeat.

## The Solution

The SSH Compliance Platform replaces that cycle with a structured, repeatable validation framework. An AI agent reads your target configuration, selects the right validators for your image variant, connects via SSH, and runs every check. The agent operates under kernel enforcement, which means it cannot skip checks, bypass the framework architecture, or drift from the validation pattern. Every run is reproducible and auditable.

The output is a structured report with pass/fail status per rule, per framework, per host, with the raw command output captured as evidence. Hand it directly to an auditor.

## How It Works

Define your targets in a JSON fixture. The agent reads the fixture, identifies the image variant, selects the appropriate validators, connects via SSH, and executes every check.

The validation pipeline runs in five steps:

1. **Input.** Accept target host, variant, and scope.
2. **Preflight.** Verify SSH connectivity, confirm paramiko is installed, and check key permissions.
3. **Plan.** Select validators based on the image variant.
4. **Execute.** Run the batch executor against the target host.
5. **Report.** Compile per-validator results with failure analysis and captured evidence.

```
Target: 192.168.1.100 (enterprise variant)
Frameworks: STIG, CIS, NIST 800-171, FIPS 140-3

STIG-001  PermitRootLogin .......... PASS  (no)
STIG-002  Protocol ................. PASS  (2)
STIG-003  MaxAuthTries ............. PASS  (4)
CIS-001   LogLevel ................. PASS  (INFO)
CIS-002   X11Forwarding ............ PASS  (no)
NIST-001  LoginGraceTime ........... PASS  (60)
NIST-002  PermitEmptyPasswords ..... PASS  (no)
NIST-003  Ciphers .................. FAIL  (aes128-cbc not allowed)
FIPS-001  KexAlgorithms ............ PASS  (ecdh-sha2-nistp256)
FIPS-002  MACs ..................... PASS  (hmac-sha2-256)

Passed: 9/10 (90.0%)
Failed: 1  [NIST-003: non-FIPS cipher detected]
```

## Compliance Frameworks

| Framework | Domain | Use Case |
|-----------|--------|----------|
| DISA STIG | Government | Required for DoD networks |
| CIS Benchmarks | Industry | Consensus-based hardening baseline |
| NIST 800-171 | Federal | Controlled Unclassified Information, CMMC |
| FIPS 140-3 | Cryptography | Cipher, key exchange, and MAC validation |
| PCI DSS | Payment | SSH hardening for cardholder data environments |
| HIPAA | Healthcare | Technical safeguards for PHI access controls |
| SOC 2 | Audit | Trust service criteria for security and availability |
| ISO 27001 | International | Annex A information security controls |

## Architecture

Every validation follows a five-layer separation of concerns. Each layer has a single responsibility, and the agent is enforced to follow this structure on every run.

| Layer | Responsibility | File |
|-------|---------------|------|
| Interface | SSH connection management, retry logic, timeout handling | `ssh_interface.py` |
| Validator | One check category (packages, kernel, services, or config) | `validators/*.py` |
| Task | Single SSH command execution | `tasks/run_ssh_command.py` |
| Role | Orchestrates validators into batch runs | `roles/ssh_batch_executor.py` |
| Test | Assertions against results, report generation | `tests/test_ssh_batch.py` |

```
Test Layer         Assertions and report generation
  └── Role Layer       Orchestrates validators into batch runs
       └── Validator Layer   One check category (packages, kernel, services, config)
            └── Task Layer       Single SSH command execution
                 └── Interface Layer   SSH connection, retry, timeout handling
```

Six validators ship out of the box:

| Validator | Checks | Command |
|-----------|--------|---------|
| PackageValidator | Expected packages are installed | `rpm -q <package>` |
| KernelValidator | Kernel version and loaded modules | `uname -r`, `lsmod` |
| ServiceValidator | Expected services are running | `systemctl is-active <service>` |
| ConfigValidator | Configuration file patterns are present | `grep -q '<pattern>' <file>` |
| STIGValidator | DISA STIG rule compliance | Framework-specific checks |
| ComplianceValidator | Multi-framework rule evaluation | Cross-framework rule engine |

## Kernel Enforcement

The SSH platform includes a domain spec that teaches the AI agent how to validate images. The Isagawa Kernel enforces these rules at runtime:

- Every SSH operation goes through the SSHInterface. The agent never calls paramiko directly.
- Validators are stateless. Results come from the host, not from local state.
- Every check produces evidence. The raw command output is captured and included in the report.
- Connection errors trigger fail-fast behavior with retry (3 attempts, exponential backoff).
- Individual check failures do not stop the batch. The full suite runs and all results are reported.

The agent learns from failures and updates its validation approach permanently through the kernel's lesson system.

## Quick Start

### Prerequisites

Python 3.10 or later, [Claude Code](https://claude.ai/claude-code), and SSH access to a target host with key-based authentication.

### Install

```bash
git clone https://github.com/isagawa-qa/platform-ssh.git
cd platform-ssh
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure

Add your target hosts to `framework/_reference/fixtures/host_configs.json`:

```json
{
  "my_server": {
    "host": "192.168.1.100",
    "port": 22,
    "username": "admin",
    "key_path": "/path/to/ssh/key",
    "variant": "enterprise",
    "expected_packages": ["bash", "openssh-server", "rocky-release"],
    "expected_services": ["sshd", "chronyd"]
  }
}
```

### Run

```bash
claude         # Start Claude Code in the project directory
/ssh-workflow  # Run the compliance validation pipeline
```

The agent handles the rest: preflight connectivity checks, validator selection based on your image variant, execution, and structured reporting.

### Tests

```bash
pytest framework/_reference/tests/ -v
```

Unit tests run with mocked SSH connections and do not require a live target.

## Supported Image Variants

| Variant | Description |
|---------|-------------|
| Enterprise | Enterprise Linux with extended support and compliance tooling |
| AI/HPC | GPU-optimized Linux for AI and high-performance computing workloads |
| Standard | Base Linux image with core packages |

## Project Structure

```
platform-ssh/
├── .claude/
│   ├── commands/
│   │   └── ssh-workflow.md             # Validation pipeline command
│   ├── skills/
│   │   └── ssh-management-layer/       # Domain spec for SSH validation
│   │       ├── SKILL.md                # Identity and step table
│   │       ├── workflow.md             # Five-step pipeline definition
│   │       ├── gate-contract.md        # Verification gates
│   │       └── references/             # Step-by-step specifications
│   └── state/                          # Runtime state
├── framework/
│   ├── resources/
│   │   └── eval_config.py              # Evaluation configuration
│   └── _reference/
│       ├── ssh_interface.py            # Layer 1: SSH connection wrapper
│       ├── validators/
│       │   ├── compliance_validator.py # Layer 2: Framework compliance checks
│       │   ├── config_validator.py     # Layer 2: Config file checks
│       │   ├── kernel_validator.py     # Layer 2: Kernel checks
│       │   ├── package_validator.py    # Layer 2: Package checks
│       │   ├── service_validator.py    # Layer 2: Service checks
│       │   └── stig_validator.py       # Layer 2: STIG-specific checks
│       ├── tasks/
│       │   └── run_ssh_command.py      # Layer 3: Atomic command execution
│       ├── roles/
│       │   └── ssh_batch_executor.py   # Layer 4: Batch orchestrator
│       ├── tests/
│       │   ├── conftest.py             # Mock SSH fixtures
│       │   └── test_ssh_batch.py       # Layer 5: Unit tests
│       └── fixtures/
│           ├── host_configs.json       # Target host definitions
│           ├── stig_rules.json         # DISA STIG rules
│           ├── cis_l1_rules.json       # CIS Level 1 rules
│           ├── nist_rules.json         # NIST 800-171 rules
│           ├── fips_rules.json         # FIPS 140-3 rules
│           ├── pci_dss_rules.json      # PCI DSS rules
│           ├── hipaa_rules.json        # HIPAA rules
│           ├── soc2_rules.json         # SOC 2 rules
│           └── iso27001_rules.json     # ISO 27001 rules
├── requirements.txt                    # Dependencies (paramiko, pytest)
└── README.md
```

## Other Platforms

SSH compliance is one domain. The Isagawa Kernel supports any domain that can be validated through a structured interface.

| Platform | Interface | Validates |
|----------|-----------|-----------|
| [QA Platform (Selenium)](https://github.com/isagawa-qa/platform-selenium) | Browser | Web UI workflows |
| SSH Compliance (this repo) | SSH | Linux image configuration |
| [QA Platform (Playwright)](https://github.com/isagawa-qa/platform-playwright) | Browser | Modern web applications |
| [QA Platform (Docker)](https://github.com/isagawa-qa/platform-docker) | Docker CLI | Container images |
| [QA Platform (DeepEval)](https://github.com/isagawa-qa/platform-deepeval) | Python | LLM output quality |
| [QA Platform (API)](https://github.com/isagawa-qa/platform-api) | HTTP | REST/GraphQL endpoints |
| [Vibe Coder Agent](https://github.com/isagawa-co/vibe-coder-agent) | AI Agent | AI-assisted code generation |

## Contact

For commercial licensing, pilot programs, or technical questions:

**Email:** [alain@isagawa.co](mailto:alain@isagawa.co)
**Web:** [isagawa.co](https://www.isagawa.co)

## License

Proprietary. Copyright (c) 2025 Isagawa. All rights reserved.

This repository is source-available for evaluation purposes. Production use requires a commercial license. See [LICENSE](LICENSE) for terms.
