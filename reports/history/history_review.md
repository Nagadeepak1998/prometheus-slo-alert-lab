# SLO History Review

Decision: **PAGE**

## Release Windows

| Window | Deploy | Minutes Since Deploy | Decision | Triggered Policies | Max Burn | Page Policy |
|---|---|---:|---|---:|---:|---|
| baseline deploy verification | checkout-2026.07.08-1 | 10 | ok | 0 | 0.1 | - |
| canary expansion watch | checkout-2026.07.08-2 | 25 | ticket | 1 | 9.0 | - |
| post-expansion incident review | checkout-2026.07.08-3 | 40 | page | 2 | 22.0 | fast-page |

## Summary

- Windows evaluated: 3
- Page windows: 1
- Ticket windows: 1
- Worst window: post-expansion incident review
- Max burn rate: 22.0

## Recommendations

- First page-worthy history window is post-expansion incident review for deploy checkout-2026.07.08-3.
- Block promotion until rollback, mitigation, or an explicit incident owner is recorded.
