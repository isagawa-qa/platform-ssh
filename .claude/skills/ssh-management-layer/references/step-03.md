# Step 3: Plan

Select validators and thresholds based on image variant.

## Validator Selection Matrix

| Validator | full | quick | compliance |
|-----------|------|-------|-----------|
| Package | yes | yes | no |
| Kernel | yes | no | no |
| Service | yes | yes | no |
| Config | yes | no | yes |

## Thresholds by Variant

- rlc-pro: package_match >= 95%, all services running
- rlc-pro-ai: same + CUDA/PyTorch packages present
- rocky-standard: relaxed (90% package match)
