"""Round-trip property tests for encode/decode."""

from __future__ import annotations

from typing import Any

import pytest

from bencode import decode, encode

_PRIMITIVES: list[Any] = [
    0,
    1,
    -1,
    42,
    -42,
    10 ** 18,
    -(10 ** 18),
    b"",
    b"spam",
    b"\x00\x01\x02\xff",
    b"a" * 1024,
]

_CONTAINERS: list[Any] = [
    [],
    [1, 2, 3],
    [b"a", [b"b", [b"c", []]]],
    {},
    {b"a": 1, b"b": [b"x", b"y"]},
    {b"nested": {b"deeper": {b"x": [1, 2]}}},
    [{b"k": 1}, {b"k": 2}],
]


@pytest.mark.parametrize("value", _PRIMITIVES + _CONTAINERS)
def test_roundtrip_value(value: Any) -> None:
    assert decode(encode(value)) == value


def test_roundtrip_torrent_like_structure() -> None:
    info = {
        b"length": 12345,
        b"name": b"file.iso",
        b"piece length": 16384,
        b"pieces": b"\x00" * 40,
    }
    torrent = {
        b"announce": b"http://tracker.example/announce",
        b"comment": b"a comment",
        b"created by": b"bencode tests",
        b"creation date": 1_700_000_000,
        b"info": info,
    }
    assert decode(encode(torrent)) == torrent


def test_dict_key_order_is_canonical_after_roundtrip() -> None:
    raw = {b"z": 1, b"a": 1, b"m": 1}
    encoded = encode(raw)
    assert encoded.index(b"1:a") < encoded.index(b"1:m") < encoded.index(b"1:z")
    decoded = decode(encoded)
    assert list(decoded) == [b"a", b"m", b"z"]
