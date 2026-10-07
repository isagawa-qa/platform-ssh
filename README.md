# Isagawa SSH Compliance Platform

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Compliance Frameworks](https://img.shields.io/badge/Frameworks-8%20Standards-orange.svg)](#compliance-frameworks)

Automated SSH compliance validation across eight security frameworks: STIG, CIS, NIST 800-171, FIPS 140-3, PCI DSS, HIPAA, SOC 2, and ISO 27001. An AI agent connects to your hosts over SSH, runs every check, and produces an auditor-ready report with captured evidence.

Built on the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel).

## The Problem

Enterprise Linux images ship across AWS, GCP, Azure, and bare metal. Each image variant has specific requirements: correct packages, kernel version, running services, and security configurations. Manual validation doesn't scale. AI-generated scripts break when they don't follow the framework patterns, and there's no enforcement to keep them on track.

The result is a cycle that repeats across organizations: generate a validation script, miss a check, ship a broken image, wait for a customer or auditor to find it, patch, and repeat.

## The Solution

An AI agent reads your target configuration, picks the checks for your image variant, connects over SSH, and runs them. The result is a report with pass or fail per rule, per framework, per host, with the raw command output captured as evidence. Hand it directly to an auditor. It works under guardrails from the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel).

## How It Works

Define your targets in a JSON fixture. The agent reads the fixture, identifies the image variant, selects the appropriate validators, connects via SSH, and executes every check.

The validation pipeline runs in five steps:

1. **Input.** Accept target host, variant, and scope.
2. **Preflight.** Verify SSH connectivity, confirm paramiko is installed, and check key permissions.
3. **Plan.** Select the checks for the image variant.
4. **Execute.** Run every check against the target host.
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

## Author

Built by Alain Ignacio, QA lead and test automation architect.
Portfolio: [alain-ignacio.github.io](https://alain-ignacio.github.io) · LinkedIn: [linkedin.com/in/alain-ignacio](https://www.linkedin.com/in/alain-ignacio)

## License

Proprietary. Copyright (c) 2025 Isagawa. All rights reserved. Source is available for evaluation only. See [LICENSE](LICENSE).
