# SSH Image Testing Platform

Automated SSH-based validation of CIQ Rocky Linux enterprise images.

## Install

```bash
pip install -r requirements.txt
```

## Setup

1. Edit `framework/_reference/fixtures/host_configs.json` with your target hosts
2. Ensure SSH key access to targets
3. Configure image variant (rlc-pro, rlc-pro-ai, rocky-standard)

## Usage

```bash
# Run test suite
pytest framework/_reference/tests/ -v

# With the Isagawa Kernel installed:
# /kernel/session-start → /kernel/anchor → invoke SSH workflow
```

## Architecture

5-layer pattern: Interface → Validator → Task → Role → Test

See `FRAMEWORK.md` for details.

## CIQ Context

Validates enterprise Linux images from CIQ (Rocky Linux Commercial):
- RLC Pro: standard enterprise packages + compliance
- RLC Pro AI: CUDA/PyTorch/ML stack + enterprise
- Rocky Standard: base Rocky Linux
