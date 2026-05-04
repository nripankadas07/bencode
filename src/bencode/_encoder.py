"""Bencode encoder.

The encoder accepts the canonical bencode value set:

* ``int``                 -> ``i<value>e``
* ``bytes`` / ``bytearray`` / ``memoryview``  -> ``<length>:<bytes>``
* ``list`` / ``tuple``    -> ``l<elements>e``
* ``dict[bytes, ...]``    -> ``d<key><value>...e`` with keys sorted
  lexicographically by raw bytes (the canonical bencode requirement)

``bool``, ``str``, ``float``, ``None`` and any other type raise
:class:`EncodeError`.  ``str`` keys are rejected explicitly so that no
caller can accidentally produce two different encodings for the same
logical structure.
"""

from __future__ import annotations

from typing import Any, Sequence, Union

from ._errors import EncodeError

__all__ = ["encode"]

_BytesLike = (bytes, bytearray, memoryview)
_PathPart = Union[int, bytes]


def encode(value: Any) -> bytes:
    """Encode ``value`` to a ``bytes`` object using the bencode format.

    >>> encode(42)
    b'i42e'
    >>> encode([b'spam', 42])
    b'l4:spami42ee'
    """
    parts: list[bytes] = []
    _encode_into(value, parts, ())
    return b"".join(parts)


def _encode_into(
    value: Any, parts: list[bytes], path: tuple[_PathPart, ...]
) -> None:
    if isinstance(value, bool):
        raise EncodeError(
            "bool is not a bencode type (would silently encode as int)",
            value=value,
            path=path,
        )
    if isinstance(value, int):
        parts.append(b"i" + str(value).encode("ascii") + b"e")
        return
    if isinstance(value, _BytesLike):
        body = bytes(value)
        parts.append(str(len(body)).encode("ascii") + b":" + body)
        return
    if isinstance(value, (list, tuple)):
        _encode_sequence(value, parts, path)
        return
    if isinstance(value, dict):
        _encode_mapping(value, parts, path)
        return
    raise EncodeError(
        f"unsupported type for bencode: {type(value).__name__}",
        value=value,
        path=path,
    )


def _encode_sequence(
    value: Sequence[Any], parts: list[bytes], path: tuple[_PathPart, ...]
) -> None:
    parts.append(b"l")
    for index, item in enumerate(value):
        _encode_into(item, parts, path + (index,))
    parts.append(b"e")


def _encode_mapping(
    value: dict[Any, Any], parts: list[bytes], path: tuple[_PathPart, ...]
) -> None:
    items = _sorted_dict_items(value, path)
    parts.append(b"d")
    for key, item in items:
        parts.append(str(len(key)).encode("ascii") + b":" + key)
        _encode_into(item, parts, path + (key,))
    parts.append(b"e")


def _sorted_dict_items(
    value: dict[Any, Any], path: tuple[_PathPart, ...]
) -> list[tuple[bytes, Any]]:
    items: list[tuple[bytes, Any]] = []
    for key, item in value.items():
        if isinstance(key, bool) or not isinstance(key, bytes):
            raise EncodeError(
                "dict keys must be bytes (got "
                f"{type(key).__name__})",
                value=key,
                path=path,
            )
        items.append((key, item))
    items.sort(key=lambda kv: kv[0])
    return items
