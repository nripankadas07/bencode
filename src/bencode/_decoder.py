"""Bencode decoder.

Strict decoder — every malformed input raises a subclass of
:class:`DecodeError` carrying the byte offset at which the problem was
detected.  No silent recovery, no best-effort parsing.
"""

from __future__ import annotations

from typing import Any, Iterator, Tuple, Union

from ._errors import (
    DecodeError,
    InvalidDictError,
    InvalidIntegerError,
    InvalidStringError,
    TrailingDataError,
    TruncatedError,
)

__all__ = ["decode", "decode_partial", "iter_decode"]

_BytesIn = Union[bytes, bytearray, memoryview]


def decode(data: _BytesIn) -> Any:
    """Decode ``data`` and return the single bencode value it contains.

    Raises :class:`TrailingDataError` if the input contains additional
    bytes after the first complete value.
    """
    buf = _coerce(data)
    value, end = _decode_at(buf, 0)
    if end != len(buf):
        raise TrailingDataError(
            f"unexpected trailing bytes after value at offset {end}",
            offset=end,
        )
    return value


def decode_partial(data: _BytesIn, *, offset: int = 0) -> Tuple[Any, int]:
    """Decode one value starting at ``offset``; return ``(value, end)``.

    ``end`` is the position immediately after the consumed value, so
    callers can chain the calls (or simply pass it as the next
    ``offset``).  Raises :class:`DecodeError` (or a subclass) on any
    malformed input — the input is *not* required to end at ``end``.
    """
    buf = _coerce(data)
    if offset < 0 or offset > len(buf):
        raise DecodeError(
            f"offset {offset} is outside data of length {len(buf)}",
            offset=offset,
        )
    return _decode_at(buf, offset)


def iter_decode(data: _BytesIn) -> Iterator[Any]:
    """Yield each bencode value in ``data`` until the input is exhausted.

    Useful for streams of concatenated values (e.g. multiple torrent
    handshake messages).  Each malformed value raises immediately.
    """
    buf = _coerce(data)
    pos = 0
    while pos < len(buf):
        value, pos = _decode_at(buf, pos)
        yield value


def _coerce(data: _BytesIn) -> bytes:
    if isinstance(data, (bytearray, memoryview)):
        return bytes(data)
    if isinstance(data, bytes):
        return data
    raise DecodeError(
        f"data must be bytes-like, got {type(data).__name__}",
        offset=0,
    )


def _decode_at(buf: bytes, offset: int) -> Tuple[Any, int]:
    if offset >= len(buf):
        raise TruncatedError("unexpected end of input", offset=offset)
    head = buf[offset:offset + 1]
    if head == b"i":
        return _decode_integer(buf, offset)
    if head == b"l":
        return _decode_list(buf, offset)
    if head == b"d":
        return _decode_dict(buf, offset)
    if head.isdigit():
        return _decode_string(buf, offset)
    raise DecodeError(
        f"unexpected byte {head!r} at offset {offset}", offset=offset
    )


def _decode_integer(buf: bytes, offset: int) -> Tuple[int, int]:
    end = buf.find(b"e", offset + 1)
    if end == -1:
        raise TruncatedError(
            "integer token missing terminator 'e'", offset=offset
        )
    body = buf[offset + 1:end]
    _validate_integer_body(body, offset)
    return int(body), end + 1


def _validate_integer_body(body: bytes, offset: int) -> None:
    if not body:
        raise InvalidIntegerError(
            "empty integer token 'ie'", offset=offset
        )
    if body == b"-0":
        raise InvalidIntegerError(
            "negative zero 'i-0e' is not allowed", offset=offset
        )
    digits = body[1:] if body.startswith(b"-") else body
    if not digits or not digits.isdigit():
        raise InvalidIntegerError(
            f"invalid integer body {body!r}", offset=offset
        )
    if len(digits) > 1 and digits.startswith(b"0"):
        raise InvalidIntegerError(
            f"leading zero in integer body {body!r}", offset=offset
        )


def _decode_string(buf: bytes, offset: int) -> Tuple[bytes, int]:
    colon = buf.find(b":", offset)
    if colon == -1:
        raise InvalidStringError(
            "string length missing ':' separator", offset=offset
        )
    length_bytes = buf[offset:colon]
    length = _parse_string_length(length_bytes, offset)
    start = colon + 1
    end = start + length
    if end > len(buf):
        raise TruncatedError(
            f"string body truncated: need {length} bytes, "
            f"have {len(buf) - start}",
            offset=offset,
        )
    return buf[start:end], end


def _parse_string_length(length_bytes: bytes, offset: int) -> int:
    # ``_decode_at`` only routes here when the head byte is a digit, so
    # ``length_bytes`` is non-empty by construction; no need to handle
    # the empty case explicitly.
    if len(length_bytes) > 1 and length_bytes.startswith(b"0"):
        raise InvalidStringError(
            f"leading zero in string length {length_bytes!r}",
            offset=offset,
        )
    return int(length_bytes)


def _decode_list(buf: bytes, offset: int) -> Tuple[list[Any], int]:
    pos = offset + 1
    items: list[Any] = []
    while True:
        if pos >= len(buf):
            raise TruncatedError(
                "list missing terminator 'e'", offset=offset
            )
        if buf[pos:pos + 1] == b"e":
            return items, pos + 1
        item, pos = _decode_at(buf, pos)
        items.append(item)


def _decode_dict(buf: bytes, offset: int) -> Tuple[dict[bytes, Any], int]:
    pos = offset + 1
    out: dict[bytes, Any] = {}
    last_key: bytes | None = None
    while True:
        if pos >= len(buf):
            raise TruncatedError(
                "dict missing terminator 'e'", offset=offset
            )
        if buf[pos:pos + 1] == b"e":
            return out, pos + 1
        last_key, pos = _read_dict_pair(buf, pos, last_key, out)


def _read_dict_pair(
    buf: bytes,
    pos: int,
    last_key: bytes | None,
    out: dict[bytes, Any],
) -> Tuple[bytes, int]:
    if not buf[pos:pos + 1].isdigit():
        raise InvalidDictError(
            f"dict key must be a byte string, got {buf[pos:pos + 1]!r}",
            offset=pos,
        )
    key, pos = _decode_string(buf, pos)
    if last_key is not None and key <= last_key:
        raise InvalidDictError(
            f"dict keys not strictly increasing: {last_key!r} >= {key!r}",
            offset=pos,
        )
    value, pos = _decode_at(buf, pos)
    out[key] = value
    return key, pos
