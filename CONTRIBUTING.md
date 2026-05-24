# Contributing

Thanks for considering a contribution. `bencode` is intentionally small and
strict, so changes should preserve canonical byte-level behavior.

## Local setup

```bash
python -m pip install -e ".[dev]"
ruff check .
mypy --strict src/bencode
pytest --cov=bencode --cov-branch --cov-report=term-missing --cov-fail-under=100
```

## Contribution rules

- Add tests for every encode/decode behavior change.
- Keep decode errors precise and offset-bearing.
- Keep encoded output canonical and deterministic.
- Keep runtime dependencies at zero.
- Keep public API changes documented in `README.md`.
