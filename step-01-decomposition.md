# SSH Image Testing — Domain Decomposition

## Spec Type
**BUILD** — produces an executable test framework for SSH-based image validation.

## Domain
SSH-based testing of CIQ Rocky Linux enterprise images (RLC Pro, RLC Pro AI, standard Rocky).

## Core Components

1. **SSH Interface** — paramiko-based connection management with retry and auth
2. **Validators** — package, kernel, service, and config validation modules
3. **Test Runner** — batch executor that orchestrates validators against target hosts
4. **Fixtures** — host configuration files with CIQ-specific image data
5. **Reporting** — test result compilation with failure analysis and recommendations

## 5-Layer Architecture Mapping

| Layer | SSH Adaptation | File |
|-------|---------------|------|
| 1. Interface | SSHInterface (paramiko wrapper) | `framework/_reference/ssh_interface.py` |
| 2. Validator | PackageValidator, KernelValidator, ServiceValidator, ConfigValidator | `framework/_reference/validators/*.py` |
| 3. Task | run_ssh_command (atomic SSH operation) | `framework/_reference/tasks/run_ssh_command.py` |
| 4. Role | SSHBatchExecutor (orchestrates validators) | `framework/_reference/roles/ssh_batch_executor.py` |
| 5. Test | test_ssh_batch (pytest suite with mocked SSH) | `framework/_reference/tests/test_ssh_batch.py` |

## Actors

- **QA Engineer** — runs validation suites, reviews results
- **DevOps Engineer** — configures host targets, manages SSH keys
- **Image Builder** — builds CIQ images, triggers validation after build

## Platform

- **paramiko** — SSH2 protocol library for Python
- **Rocky Linux** — base OS for all CIQ images
- **CIQ** — enterprise Linux vendor (RLC Pro, RLC Pro AI packages)
- **pytest** — test execution framework

## Workflow (5-step pipeline)

1. **Input** — target host, image variant, test scope
2. **Preflight** — SSH connectivity, paramiko availability, config validation
3. **Plan** — select validators and thresholds based on variant
4. **Execute** — run test suite via SSHBatchExecutor
5. **Report** — compile results, flag failures, recommend fixes
