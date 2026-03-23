# SSH Image Testing — Domain Score

## Scoring Model (8 dimensions, max 90)

| # | Dimension | Weight | Score | Evidence |
|---|-----------|--------|-------|----------|
| 1 | Revenue Potential | 3x | 8/10 | Enterprise clients ($15K-$50K implementations), CIQ has active sales pipeline |
| 2 | Pain Intensity | 3x | 9/10 | Manual image validation is error-prone, compliance-critical, blocks releases |
| 3 | Repetitive Patterns | 3x | 9/10 | Same checks on every image build — packages, services, configs, kernel |
| 4 | Buyer Accessibility | 2x | 7/10 | DevOps/QA engineers at CIQ clients, known buyer persona |
| 5 | Documentation | 2x | 8/10 | CIS benchmarks well-documented, Rocky Linux has community docs |
| 6 | Compliance/Regulatory | 2x | 8/10 | STIG, FedRAMP requirements drive purchases |
| 7 | Community Demand | 2x | 7/10 | Rocky Linux community growing, enterprise Linux market expanding |
| 8 | Existing Tooling (inverse) | 1x | 6/10 | InSpec/Lynis exist but no SSH-native spec-driven platform |

## Composite Score

```
(8*3) + (9*3) + (9*3) + (7*2) + (8*2) + (8*2) + (7*2) + (6*1)
= 24 + 27 + 27 + 14 + 16 + 16 + 14 + 6
= 144 / 180 * 90
= 72
```

**Composite: 72/90**

## Decision

**BUILD** (threshold: 70+)

The SSH Image Testing domain scores above the BUILD threshold. High pain intensity and repetitive patterns drive the score. CIQ client engagement provides immediate revenue opportunity.
