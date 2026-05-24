# bencode quality bar

This project is held to a strict codec quality bar: malformed data must fail
predictably, canonical encodings must be stable, and packaging must install the
same code that the tests exercise.

## Required checks

- `ruff check .` must pass with no ignored failures.
- `mypy --strict src/bencode` must pass.
- `pytest --cov=bencode --cov-branch --cov-report=term-missing --cov-fail-under=100`
  must pass.
- A built wheel must import successfully and round-trip a representative value.
- Decode behavior must keep enforcing BEP 3 canonical rules: no leading-zero
  integers, no negative zero, no unsorted or duplicate dictionary keys, and no
  trailing bytes for `decode`.

## Scope promises

`bencode` is a byte-oriented encoder/decoder. It does not interpret torrent
metainfo fields, validate tracker URLs, or coerce text encodings. Callers own
schema-level validation above the bencode layer.

## Release checklist

- Run the required checks locally.
- Confirm the README examples still match the public API.
- Confirm GitHub Actions is green on every Python version in the matrix.
- Confirm Dependabot and secret scanning have no open alerts.
