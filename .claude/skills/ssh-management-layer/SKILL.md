---
name: SSH Management Layer
type: prescriptive
domain: ssh-image-testing
---

# SSH Management Layer — Skill

**Type:** Prescriptive
**Domain:** SSH Image Testing for CIQ Rocky Linux

## Identity

Automated SSH-based validation of enterprise Linux images. Connects to target hosts, runs validators against packages/kernel/services/configs, and produces test reports.

## Vocabulary

| Term | Meaning |
|------|---------|
| Host config | Target host definition (IP, variant, expected packages) |
| Variant | Image type: rlc-pro, rlc-pro-ai, rocky-standard |
| Validator | Module checking one aspect (packages, kernel, services, configs) |
| Batch executor | Orchestrator running validators in sequence |
| Scope | Test scope: full, quick, compliance |

## Steps

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Accept input | → [[references/step-01.md]] |
| 2 | Preflight checks | → [[references/step-02.md]] |
| 3 | Plan validators | → [[references/step-03.md]] |
| 4 | Execute tests | → [[references/step-04.md]] |
| 5 | Compile report | → [[references/step-05.md]] |

## Rules

- All SSH operations go through SSHInterface (never raw paramiko)
- Validators are stateless — results come from the host, not local state
- Every validator check produces evidence (command output)
- Fail-fast on connection errors; continue on individual check failures
