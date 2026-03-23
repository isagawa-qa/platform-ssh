# Architecture

5-layer SSH testing.

| # | Layer | File |
|---|-------|------|
| 1 | Interface | ssh_interface.py |
| 2 | Validator | validators/*.py |
| 3 | Task | tasks/run_ssh_command.py |
| 4 | Role | roles/ssh_batch_executor.py |
| 5 | Test | tests/test_ssh_batch.py |
