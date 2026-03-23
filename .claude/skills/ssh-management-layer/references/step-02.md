# Step 2: Preflight Checks

Verify environment before running tests.

## Checks

1. SSH connectivity: paramiko connect with 10s timeout
2. paramiko available: import check
3. Host config JSON valid: schema validation
4. SSH key permissions: 0600 for private keys
5. Target OS detection: uname output

## Fail-Fast

Stop on first critical failure (connectivity, paramiko missing). Warnings for non-critical (key permissions, OS detection).
