# bencode

Strict, dependency-free [BitTorrent bencode][1] encoder and decoder for
Python 3.10+. Round-trips are exact: the decoder rejects every
non-canonical encoding (leading zeros, `i-0e`, dict keys out of order or
duplicated, trailing data after a value), and the encoder emits dict
keys sorted lexicographically by raw bytes.

[1]: https://www.bittorrent.org/beps/bep_0003.html#bencoding

## Install

```bash
python -m pip install -e .
```

Or from a clone:

```bash
pip install -e .
```

## Quick start

```python
from bencode import encode, decode

torrent = {
    b"announce": b"http://tracker.example/announce",
    b"info": {
        b"length": 12345,
        b"name": b"file.iso",
        b"piece length": 16384,
        b"pieces": b"\x00" * 40,
    },
}

raw = encode(torrent)
assert decode(raw) == torrent
```

The four bencode types map to Python types one-to-one:

| Bencode             | Python                              |
| ------------------- | ----------------------------------- |
| `i<n>e`             | `int`                               |
| `<len>:<bytes>`     | `bytes`                             |
| `l<...>e`           | `list`                              |
| `d<key><value>...e` | `dict[bytes, ...]` (keys are bytes) |

## API reference

### `encode(value) -> bytes`

Encode a value to canonical bencode bytes.

* Accepts `int`, `bytes`/`bytearray`/`memoryview`, `list`/`tuple`, and
  `dict` with `bytes` keys.
* Rejects `bool` (would silently encode as `int`), `str`, `float`,
  `None`, sets, and any other type with `EncodeError`.
* Dict keys must be `bytes`. The encoder sorts them lexicographically by
  raw bytes — the canonical bencode requirement.

```python
encode(0)              # b'i0e'
encode(-7)             # b'i-7e'
encode(b"spam")        # b'4:spam'
encode([])             # b'le'
encode({})             # b'de'
encode({b"b": 1, b"a": 2})  # b'd1:ai2e1:bi1ee'
```

### `decode(data) -> Any`

Decode a single complete bencode value. Raises `TrailingDataError` if
extra bytes remain after it.

```python
decode(b"i42e")              # 42
decode(b"4:spam")            # b'spam'
decode(b"l4:spami42ee")      # [b'spam', 42]
decode(b"d1:ai1ee")          # {b'a': 1}
```

### `decode_partial(data, *, offset=0) -> tuple[Any, int]`

Decode a single value starting at `offset` and return `(value, end)`,
where `end` is the position immediately after the consumed value.
Useful for hand-rolling concatenated-value parsers.

```python
data = b"i7e0:"
value, end = decode_partial(data)        # (7, 3)
value, end = decode_partial(data, offset=end)  # (b'', 5)
```

### `iter_decode(data) -> Iterator[Any]`

Yield each bencode value in `data` until the input is exhausted.
Raises immediately on the first malformed value.

```python
list(iter_decode(b"i1e0:le"))   # [1, b'', []]
```

## Errors

All errors descend from `BencodeError`, which subclasses `ValueError`,
so `except ValueError` will catch them all.

| Class                  | Raised when                                          |
| ---------------------- | ---------------------------------------------------- |
| `EncodeError`          | `encode` got an unsupported value or dict-key type.  |
| `DecodeError`          | Base class for decode errors. Carries `.offset`.     |
| `TruncatedError`       | Input ended mid-token.                               |
| `InvalidIntegerError`  | Bad integer body (`ie`, `i01e`, `i-0e`, ...).        |
| `InvalidStringError`   | Bad string length prefix or truncated body.          |
| `InvalidDictError`     | Non-bytes key, or keys not strictly increasing.      |
| `TrailingDataError`    | `decode` saw bytes after the first complete value.   |

`EncodeError.path` is a tuple describing where in the input structure
the bad value lives, e.g. `(b"info", "name", 3)` for the fourth element
of `value[b"info"]["name"]`.

## Why the strict rules?

Bencode is a *canonical* format: the same Python value must round-trip
to exactly the same bytes, and the same bytes must decode to exactly
the same value, on every implementation. Strict validation makes that
invariant detectable at decode time:

* Leading zeros (`i01e`, `02:ab`) and `i-0e` are not legal — they would
  give two encodings for one number.
* Dict keys must be sorted ascending byte-strings — otherwise the same
  dict can encode in any of *n!* orders.
* `bool` is rejected on encode because `True == 1`, so `encode(True)`
  could silently produce `i1e` and round-trip to `1` — easy to miss.

If you want a forgiving parser, this isn't it.

## Running tests

```bash
pip install -e ".[dev]"
ruff check .
mypy --strict src/bencode
pytest --cov=bencode --cov-branch --cov-report=term-missing --cov-fail-under=100
```

The bundled suite has 106 tests: 100% line + 100% branch coverage on
all four source modules.

## Quality bar

`bencode` is held to the strict path because malformed torrent metadata
can change hashes, break interoperability, or waste client time.

- CI runs on Python 3.10, 3.11, and 3.12.
- `ruff check .` is blocking.
- `mypy --strict src/bencode` is blocking.
- `pytest --cov=bencode --cov-branch --cov-report=term-missing --cov-fail-under=100`
  is blocking.
- Package builds are smoke-tested before release.
- The repository includes [QUALITY.md](QUALITY.md), [CONTRIBUTING.md](CONTRIBUTING.md),
  and [SECURITY.md](SECURITY.md) so users can inspect the maintenance bar.

## License

MIT — see `LICENSE`.
