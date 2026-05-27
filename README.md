# Isagawa SSH Compliance Platform

[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Compliance Frameworks](https://img.shields.io/badge/Frameworks-8%20Standards-orange.svg)](#compliance-frameworks)

Automated SSH compliance validation across eight security frameworks. An AI agent connects to your infrastructure via SSH, runs checks against STIG, CIS, NIST, FIPS, PCI DSS, HIPAA, SOC 2, and ISO 27001 standards, and produces auditor-ready reports with captured evidence for every check.

Built on the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel). See the full product page at [isagawa.co/ssh-compliance](https://www.isagawa.co/ssh-compliance.html).

## How It Works

Define your targets in a JSON fixture. The AI agent reads the fixture, identifies the image variant, selects the appropriate validators, connects via SSH, and executes every check. Results come back structured by framework, with pass/fail status and the raw command output as evidence.

The agent operates under kernel enforcement. It cannot skip checks, bypass the framework architecture, or drift from the validation pattern. Every run is reproducible and auditable.

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

Every validation follows a five-layer separation of concerns:

```
Test Layer         Assertions and report generation
  └── Role Layer       Orchestrates validators into batch runs
       └── Validator Layer   One check category (packages, kernel, services, config)
            └── Task Layer       Single SSH command execution
                 └── Interface Layer   SSH connection, retry, timeout handling
```

Four validators ship out of the box:

| Validator | Checks | Command |
|-----------|--------|---------|
| PackageValidator | Installed packages | `rpm -q <package>` |
| KernelValidator | Kernel version and modules | `uname -r`, `lsmod` |
| ServiceValidator | Running services | `systemctl is-active <service>` |
| ConfigValidator | Configuration file patterns | `grep -q '<pattern>' <file>` |

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
| QA Platform (Playwright) | Browser | Modern web applications |
| Docker Platform | Docker CLI | Container images |

## Contact

For commercial licensing, pilot programs, or technical questions:

**Email:** [alain@isagawa.co](mailto:alain@isagawa.co)
**Web:** [isagawa.co](https://www.isagawa.co)

## License

Proprietary. Copyright (c) 2025 Isagawa. All rights reserved.

This repository is source-available for evaluation purposes. Production use requires a commercial license. See [LICENSE](LICENSE) for terms.
