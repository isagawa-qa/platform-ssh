# Gate Contract — SSH Management Layer

## Verification Methods
→ [[references/verification-methods.md]]

## Structural Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| BUILD-01 | ssh_interface.py exists | file_exists | `test -f framework/_reference/ssh_interface.py` | Create |
| BUILD-02 | SSHInterface class | grep | `grep -q 'class SSHInterface' ssh_interface.py` | Add class |
| BUILD-03 | Retry logic | grep | `grep -q 'retry' ssh_interface.py` | Add retry |
| BUILD-04 | 4 validator files | file_exists | `ls validators/*.py | wc -l` = 4 | Create |
| BUILD-05 | run_ssh_command.py | file_exists | `test -f tasks/run_ssh_command.py` | Create |
| BUILD-06 | ssh_batch_executor.py | file_exists | `test -f roles/ssh_batch_executor.py` | Create |
| BUILD-07 | test_ssh_batch.py | file_exists | `test -f tests/test_ssh_batch.py` | Create |
| BUILD-08 | conftest.py | file_exists | `test -f tests/conftest.py` | Create |
| BUILD-09 | host_configs.json | file_exists | `test -f fixtures/host_configs.json` | Create |
| BUILD-10 | requirements.txt | grep | `grep -q 'paramiko' requirements.txt` | Add dep |
| BUILD-11 | FRAMEWORK.md | file_exists | `test -f FRAMEWORK.md` | Create |
| BUILD-12 | SKILL.md | file_exists | `test -f .claude/skills/ssh-management-layer/SKILL.md` | Create |

## Functional Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| FUNC-01 | SSHInterface imports | run_code | `python -c "from ssh_interface import SSHInterface"` | Fix |
| FUNC-02 | PackageValidator imports | run_code | `python -c "from validators.package_validator import PackageValidator"` | Fix |
| FUNC-03 | Task imports | run_code | `python -c "from tasks.run_ssh_command import run_ssh_command"` | Fix |
| FUNC-04 | Role imports | run_code | `python -c "from roles.ssh_batch_executor import SSHBatchExecutor"` | Fix |
| FUNC-05 | host_configs.json valid | json_valid | `python -c "import json; json.load(open('fixtures/host_configs.json'))"` | Fix |
| TEST-01 | All unit tests pass | run_test | `pytest tests/ -v` exits 0 | Fix |

## Integration Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| INT-01 | Kernel domain-setup discovers spec | run_code | Protocol created | Fix SKILL.md |
| INT-02 | Hooks fire in workspace | run_code | actions_since_anchor increments | Fix hooks |
| INT-03 | Task completes under enforcement | run_code | completed_tasks has entry | Fix cycling |

## Documentation Gates

| ID | Check | Method | Pass Criteria | Fail Action |
|----|-------|--------|---------------|-------------|
| DOC-01 | README has install | grep | `grep -q 'install' README.md` | Add |
| DOC-02 | FRAMEWORK explains layers | grep | `grep -q 'Layer' FRAMEWORK.md` | Add |

## Summary
- Structural: 12, Functional: 6, Integration: 3, Documentation: 2
- **Total: 23 gates**
