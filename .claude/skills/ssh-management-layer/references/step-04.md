# Step 4: Execute

Run test suite via SSHBatchExecutor.

## Flow

1. Initialize SSHBatchExecutor with host config + selected validators
2. Execute validators in order: package, kernel, service, config
3. Collect per-validator results (pass/fail/error + evidence)
4. Handle connection failures (retry 3x with backoff)
5. Report progress during execution

## Error Handling

- Connection lost mid-test: retry from failed validator
- Command timeout: skip check, mark as error
- All validators complete regardless of individual failures
