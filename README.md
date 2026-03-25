# Isagawa SSH Image Testing Platform

### AI Execution Management for Infrastructure Validation

> AI can generate validation scripts. But can you trust it to test your production images correctly?

The SSH Image Testing Platform connects to running Linux images via SSH, executes validation commands, and verifies the image meets expected configuration. The AI agent generates and runs the validation scripts — managed by the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel) to ensure it does it right every time.

Adaptable to any SSH-accessible infrastructure — enterprise Linux, cloud images, bare metal, containers.

---

## The Problem

Enterprise Linux images ship across AWS, GCP, Azure, and bare metal. Each image variant has specific requirements — correct packages, kernel version, running services, security configs. Manual validation doesn't scale. AI-generated scripts break when they don't follow the framework patterns.

**The cycle:** Generate validation script → misses a check → ship broken image → customer finds it → patch → repeat.

## The Solution

A **5-layer validation framework** managed by the Isagawa Kernel. The AI agent reads the framework, understands the target image variant, generates the right validators, and executes them — all under enforcement that prevents architectural drift.

---

## 5-Layer Architecture

Every validation follows a strict separation of concerns:

| Layer | Responsibility | File |
|-------|---------------|------|
| **Interface** | SSH connection, retry, timeout | `ssh_interface.py` |
| **Validator** | One check category (packages, kernel, services, config) | `validators/*.py` |
| **Task** | Atomic command execution | `tasks/run_ssh_command.py` |
| **Role** | Orchestrates validators into batch runs | `roles/ssh_batch_executor.py` |
| **Test** | Asserts results, produces reports | `tests/test_ssh_batch.py` |

```
Test (Arrange / Act / Assert)
  └─→ Role (batch executor, runs all validators)
       └─→ Validator (one check category)
            └─→ Task (single SSH command)
                 └─→ Interface (paramiko wrapper, retry, context manager)
```

### Four Validators

| Validator | What it checks | SSH command |
|-----------|---------------|-------------|
| **PackageValidator** | Expected packages installed | `rpm -q <package>` |
| **KernelValidator** | Kernel version + loaded modules | `uname -r`, `lsmod` |
| **ServiceValidator** | Expected services running | `systemctl is-active <service>` |
| **ConfigValidator** | Config file patterns present | `grep -q '<pattern>' <file>` |

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Claude Code](https://claude.ai/claude-code)
- SSH access to a target host (key-based authentication)

### 1. Install

```bash
git clone https://github.com/isagawa-qa/platform-ssh.git
cd platform-ssh
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure your target

Edit `framework/_reference/fixtures/host_configs.json`:

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

### 3. Set up the AI agent

```bash
claude                    # Start Claude Code in the project directory
```

On first run, the agent reads `CLAUDE.md`, discovers the SSH domain spec, and configures itself. It will ask you to restart to activate enforcement hooks.

```bash
claude                    # Restart
> continue                # Agent picks up — now under kernel enforcement
```

### 4. Run the SSH workflow

```bash
# Inside Claude Code:
/ssh-workflow
```

The agent follows the 5-step pipeline:

1. **Input** — Accept target host, variant, scope
2. **Preflight** — Verify SSH connectivity, paramiko installed, key permissions
3. **Plan** — Select validators based on image variant
4. **Execute** — Run SSHBatchExecutor against target
5. **Report** — Compile per-validator results with failure analysis

### 5. Run tests directly

```bash
# Unit tests (mocked SSH, no live target needed)
pytest framework/_reference/tests/ -v

# Production test (requires live SSH target)
# Use /kernel/prod-test for full L1/L2/L3 validation
```

---

## Supported Image Variants

| Variant | Description | Key packages |
|---------|-------------|-------------|
| **Enterprise** | Enterprise Linux with extended support + compliance | `rocky-release`, compliance tools, hardened configs |
| **AI/HPC** | GPU-first Linux for AI/HPC workloads | `nvidia-cuda-toolkit`, `python3-torch`, ML stack |
| **Standard** | Base Linux image | `bash`, `openssh-server`, core packages |

---

## Project Structure

```
platform-ssh/
├── .claude/
│   ├── commands/
│   │   └── ssh-workflow.md          # Invoke the 5-step pipeline
│   ├── skills/
│   │   └── ssh-management-layer/    # Domain spec
│   │       ├── SKILL.md             # Identity, vocabulary, step table
│   │       ├── workflow.md          # 5-step pipeline
│   │       ├── gate-contract.md     # 23 verification gates
│   │       └── references/          # Step-by-step specs
│   └── state/                       # Kernel state files
├── framework/
│   └── _reference/
│       ├── ssh_interface.py         # Layer 1: SSH connection wrapper
│       ├── validators/
│       │   ├── package_validator.py # Layer 2: Package checks
│       │   ├── kernel_validator.py  # Layer 2: Kernel checks
│       │   ├── service_validator.py # Layer 2: Service checks
│       │   └── config_validator.py  # Layer 2: Config checks
│       ├── tasks/
│       │   └── run_ssh_command.py   # Layer 3: Atomic execution
│       ├── roles/
│       │   └── ssh_batch_executor.py # Layer 4: Batch orchestrator
│       ├── tests/
│       │   ├── conftest.py          # Mock SSH fixtures
│       │   └── test_ssh_batch.py    # Layer 5: Unit tests
│       └── fixtures/
│           └── host_configs.json    # Target host definitions
├── _test/                           # Production test artifacts
├── CLAUDE.md                        # Kernel bootstrap
├── FRAMEWORK.md                     # Architecture overview
├── CONTRIBUTING.md                  # Development rules
├── requirements.txt                 # paramiko, pytest
└── README.md
```

---

## How It Works With the Kernel

The SSH platform includes a **domain spec** at `.claude/skills/ssh-management-layer/` that teaches the AI agent how to validate images. The Isagawa Kernel enforces:

- **Every SSH operation goes through SSHInterface** — never raw paramiko
- **Validators are stateless** — results come from the host, not local state
- **Every check produces evidence** — command output captured for inspection
- **Fail-fast on connection errors** — retry 3x with exponential backoff
- **Continue on check failures** — individual failures don't stop the batch

The agent learns from failures and updates its approach permanently.

---

## Production Testing

Use [`/kernel/prod-test`](https://github.com/isagawa-co/isagawa-kernel) for full production validation:

```bash
/kernel/prod-test /path/to/platform-ssh
```

This runs the complete test suite:

| Level | What | Gates |
|-------|------|-------|
| **L1 Structural** | Files exist, patterns present | 12 gates |
| **L2 Functional** | Imports work, unit tests pass | 6 gates |
| **L3 Production** | Framework runs against live SSH target | 6 gates |

Total: **23 gates** verified against a disposable test workspace with a Docker-based Rocky Linux target.

---

## The Bigger Picture

SSH image testing is one domain. The Isagawa Kernel supports **any** domain.

| Platform | Interface | What it validates |
|----------|-----------|------------------|
| [QA Platform (Selenium)](https://github.com/isagawa-qa/platform-selenium) | Browser | Web UI workflows |
| **SSH Platform** (this repo) | SSH | Linux image configuration |
| QA Platform (Playwright) | Browser | Modern web apps |
| Docker Platform | Docker CLI | Container images |

Same kernel, same enforcement, same 5-layer pattern — different interface layer.

---

## Services

We build AI-managed infrastructure validation platforms. The AI agent generates validation scripts, the kernel enforces correctness, and the framework ensures consistency across image variants and cloud providers.

**[alain@isagawa.co](mailto:alain@isagawa.co)** · **[DM on LinkedIn](https://www.linkedin.com/in/alain-ignacio-54b9823)**

---

## License

[MIT](LICENSE) — Copyright (c) 2025 Isagawa

---

<sub>Built with the [Isagawa Kernel](https://github.com/isagawa-co/isagawa-kernel) — self-building, self-improving, safety-first.</sub>
