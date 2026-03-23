# SSH Image Testing — Domain Audit

## CIQ Products

### RLC Pro (Rocky Linux Commercial)
Enterprise Rocky Linux with commercial support, extended lifecycle, and compliance tooling.
- Base packages: rocky-release, rocky-repos, rocky-gpg-keys
- Security: CIS hardening profiles, STIG compliance scripts
- Services: cloud-init, sshd, chronyd, firewalld

### RLC Pro AI
RLC Pro plus AI/ML stack:
- CUDA toolkit (nvidia-cuda-toolkit)
- PyTorch, TensorFlow (via CIQ AI repo)
- NVIDIA drivers (kmod-nvidia)
- ML monitoring services

### CLK Packages
CIQ-specific configuration packages:
- clk-config (base configuration)
- clk-security (hardening)
- clk-monitoring (metrics collection)

## Standards & Frameworks

### CIS Benchmarks
- CIS Rocky Linux 9 Benchmark v1.0
- Covers: filesystem, services, network, audit, authentication
- Scoring: Level 1 (basic), Level 2 (hardened)

### STIG (Security Technical Implementation Guide)
- DISA STIG for RHEL/Rocky Linux
- Required for FedRAMP, DoD environments
- Machine-readable format (XCCDF, OVAL)

### FedRAMP
- Federal Risk and Authorization Management Program
- Requires STIG compliance + continuous monitoring
- Relevant for CIQ government clients

## Tools & Platforms

1. **paramiko** — Python SSH2 library, primary interface for remote execution
2. **fabric** — Higher-level SSH automation (built on paramiko)
3. **ansible** — Configuration management with SSH transport
4. **InSpec** — Compliance testing framework (Chef)
5. **Lynis** — Unix security auditing tool
6. **OpenSCAP** — SCAP compliance checker

## Pain Points

1. **Manual image validation** — no automated SSH-based testing pipeline; QA checks images by hand
2. **Variant drift** — RLC Pro and RLC Pro AI diverge in package lists; no single validator handles both
3. **Compliance verification lag** — CIS/STIG checks run separately from functional tests; results not integrated
4. **No regression detection** — image updates can break existing package versions; no diff-based validation
5. **Key management complexity** — SSH keys for different environments managed ad hoc

## Workflows

1. **Image build → validate** — builder produces image, triggers SSH test suite
2. **Compliance audit** — periodic CIS/STIG scan via SSH against running instances
3. **Regression test** — compare current image packages/services against known-good baseline
4. **Multi-variant test** — same test suite, different thresholds per image variant

## Domain Vocabulary

| Term | Definition |
|------|-----------|
| Host config | JSON describing target: IP, port, username, key path, variant |
| Variant | Image type: rlc-pro, rlc-pro-ai, rocky-standard |
| Validator | Module that checks one aspect (packages, kernel, services, configs) |
| Threshold | Pass/fail criteria per validator per variant |
| Test scope | full (all validators), quick (structural only), compliance (CIS/STIG) |
| Batch executor | Orchestrator that runs validators in sequence against a host |
| Evidence | Command output captured as proof of pass/fail |
| Preflight | Pre-test connectivity and config checks |
| Host config schema | Expected JSON structure for host_config files |
| Image manifest | Expected package list per variant |
| Baseline | Known-good state to compare against |
