"""Tests for the error hierarchy and attribute carriage."""

from __future__ import annotations

import pytest

from bencode import (
    BencodeError,
    DecodeError,
    EncodeError,
    InvalidDictError,
    InvalidIntegerError,
    InvalidStringError,
    TrailingDataError,
    TruncatedError,
    decode,
    encode,
)


def test_bencode_error_is_value_error() -> None:
    assert issubclass(BencodeError, ValueError)


def test_encode_error_is_bencode_error() -> None:
    assert issubclass(EncodeError, BencodeError)


def test_decode_subclasses_chain() -> None:
    for cls in (
        TruncatedError,
        InvalidIntegerError,
        InvalidStringError,
        InvalidDictError,
        TrailingDataError,
    ):
        assert issubclass(cls, DecodeError)
        assert issubclass(cls, BencodeError)


def test_decode_error_offset_attribute() -> None:
    # Leading-zero string length inside a list bubbles the offset
    # of the bad token (1, just inside the ``l``).
    with pytest.raises(InvalidStringError) as exc:
        decode(b"l01:ae")
    assert isinstance(exc.value.offset, int)
    assert exc.value.offset == 1


def test_decode_truncated_error_offset_attribute() -> None:
    with pytest.raises(TruncatedError) as exc:
        decode(b"l")
    assert exc.value.offset == 0


def test_trailing_data_error_offset() -> None:
    with pytest.raises(TrailingDataError) as exc:
        decode(b"i1ei2e")
    assert exc.value.offset == 3


def test_encode_error_path_root() -> None:
    with pytest.raises(EncodeError) as exc:
        encode(None)
    assert exc.value.path == ()
    assert exc.value.value is None


def test_encode_error_path_into_list() -> None:
    with pytest.raises(EncodeError) as exc:
        encode([1, 2, None])
    assert exc.value.path == (2,)


def test_encode_error_path_into_dict() -> None:
    with pytest.raises(EncodeError) as exc:
        encode({b"a": [1, None]})
    assert exc.value.path == (b"a", 1)


def test_value_error_alias_catches_everything() -> None:
    with pytest.raises(ValueError):
        encode(None)
    with pytest.raises(ValueError):
        decode(b"")
