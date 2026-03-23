# Step 1: User Input

Accept target host, image variant, test scope, and credentials.

## Parameters

- **host** (required): IP address or hostname of target
- **variant** (required): rlc-pro, rlc-pro-ai, or rocky-standard
- **scope** (optional, default: full): full, quick, or compliance
- **credentials**: SSH key path or password

## Validation

- Host must be reachable (basic ping or TCP check)
- Variant must be one of the known types
- Scope determines which validators run
- Credentials must be provided (no passwordless default)
