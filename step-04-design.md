# SSH Image Testing — Spec Design

## Domain Schema

### host_config
```json
{
  "host": "string (IP or hostname)",
  "port": 22,
  "username": "string",
  "key_path": "string (path to SSH private key)",
  "variant": "rlc-pro | rlc-pro-ai | rocky-standard",
  "expected_packages": ["string"],
  "expected_services": ["string"],
  "thresholds": {
    "package_match_pct": 95,
    "service_running_pct": 100
  }
}
```

### validator_config
```json
{
  "validator_name": "string",
  "enabled": true,
  "checks": [{"name": "string", "command": "string", "expected": "string"}]
}
```

## File Map

```
output/ssh-image-testing/
├── .claude/
│   └── skills/
│       └── ssh-management-layer/
│           ├── SKILL.md
│           ├── workflow.md
│           ├── gate-contract.md
│           └── references/
│               ├── step-01.md (input)
│               ├── step-02.md (preflight)
│               ├── step-03.md (plan)
│               ├── step-04.md (execute)
│               └── step-05.md (report)
├── framework/
│   ├── _reference/
│   │   ├── ssh_interface.py
│   │   ├── validators/
│   │   │   ├── package_validator.py
│   │   │   ├── kernel_validator.py
│   │   │   ├── service_validator.py
│   │   │   └── config_validator.py
│   │   ├── tasks/
│   │   │   └── run_ssh_command.py
│   │   ├── roles/
│   │   │   └── ssh_batch_executor.py
│   │   ├── tests/
│   │   │   ├── test_ssh_batch.py
│   │   │   └── conftest.py
│   │   └── fixtures/
│   │       └── host_configs.json
│   └── resources/
│       └── eval_config.py
├── references/
│   ├── architecture.md
│   └── validator-catalog.md
├── _test/
│   ├── fixtures/
│   └── expected/
├── requirements.txt
├── FRAMEWORK.md
├── README.md
└── CONTRIBUTING.md
```

## Workflow Steps

1. **Input** — accept host, variant, scope, credentials
2. **Preflight** — SSH connectivity, paramiko, config validation, key permissions
3. **Plan** — select validators + thresholds based on variant
4. **Execute** — SSHBatchExecutor runs validators in order
5. **Report** — compile results, failure analysis, recommendations

## 5-Layer Classes

| Layer | Class | Responsibility |
|-------|-------|---------------|
| Interface | SSHInterface | paramiko wrapper, retry, auth, context manager |
| Validator | PackageValidator | rpm -q checks, version comparison |
| Validator | KernelValidator | kernel version, modules, sysctl |
| Validator | ServiceValidator | systemd status, enabled state |
| Validator | ConfigValidator | file contents, permissions, CIS checks |
| Task | run_ssh_command | atomic SSH execution with exit code check |
| Role | SSHBatchExecutor | orchestrates validators, collects results |
| Test | test_ssh_batch | pytest suite with mocked SSH |
