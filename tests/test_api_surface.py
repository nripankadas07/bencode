"""Lock down the public API of the :mod:`bencode` package."""

from __future__ import annotations

import bencode

_EXPECTED = {
    "encode",
    "decode",
    "decode_partial",
    "iter_decode",
    "BencodeError",
    "EncodeError",
    "DecodeError",
    "TruncatedError",
    "InvalidIntegerError",
    "InvalidStringError",
    "InvalidDictError",
    "TrailingDataError",
}


def test_dunder_all_matches_expected() -> None:
    assert set(bencode.__all__) == _EXPECTED


def test_every_name_in_all_is_actually_exported() -> None:
    for name in bencode.__all__:
        assert hasattr(bencode, name), name


def test_no_unexpected_public_names() -> None:
    public = {
        name for name in dir(bencode)
        if not name.startswith("_") and name != "annotations"
    }
    extra = public - _EXPECTED
    assert extra == set(), f"unexpected public names: {extra}"


def test_version_is_a_string() -> None:
    assert isinstance(bencode.__version__, str)
    assert bencode.__version__.count(".") >= 1
