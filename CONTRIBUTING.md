# Contributing

## Architecture

Follow the 5-layer pattern:
1. Interface (ssh_interface.py) — all SSH goes through here
2. Validators (validators/*.py) — one module per check type
3. Tasks (tasks/*.py) — atomic operations
4. Roles (roles/*.py) — orchestration
5. Tests (tests/*.py) — pytest with mocks

## Adding Validators

1. Create `framework/_reference/validators/new_validator.py`
2. Implement `validate()` method returning list of check results
3. Register in SSHBatchExecutor
4. Add tests in `tests/test_ssh_batch.py`

## Testing

All changes must pass: `pytest framework/_reference/tests/ -v`
