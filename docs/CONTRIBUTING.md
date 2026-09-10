# Contributing

This is a research repository. Changes should preserve identification assumptions.

## Rules

1. Do not remove the one-month weather lag in any strategy that is presented as tradable.
2. Do not tune weights or thresholds on the same sample you report as "out of sample" without saying so.
3. Any new headline number needs a matching note in `results/` and an update to `docs/LIMITATIONS.md` if a new caveat appears.
4. Network-free unit tests must stay green (`pytest -q`).
5. Prefer adding a robustness cell over adding a new "best" specification.

## Suggested workflow

```bash
pip install -e ".[dev]"
pytest -q
```
