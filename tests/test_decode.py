"""Tests for :func:`bencode.decode` (and ``decode_partial`` / ``iter_decode``)."""

from __future__ import annotations

import pytest

from bencode import (
    DecodeError,
    InvalidDictError,
    InvalidIntegerError,
    InvalidStringError,
    TrailingDataError,
    TruncatedError,
    decode,
    decode_partial,
    iter_decode,
)


class TestDecodeIntegers:
    def test_decode_zero(self) -> None:
        assert decode(b"i0e") == 0

    def test_decode_positive(self) -> None:
        assert decode(b"i42e") == 42

    def test_decode_negative(self) -> None:
        assert decode(b"i-7e") == -7

    def test_decode_large(self) -> None:
        big = b"i" + b"9" * 50 + b"e"
        assert decode(big) == int(b"9" * 50)

    def test_decode_empty_integer_raises(self) -> None:
        with pytest.raises(InvalidIntegerError):
            decode(b"ie")

    def test_decode_negative_zero_raises(self) -> None:
        with pytest.raises(InvalidIntegerError, match="-0"):
            decode(b"i-0e")

    def test_decode_leading_zero_raises(self) -> None:
        with pytest.raises(InvalidIntegerError, match="leading zero"):
            decode(b"i01e")

    def test_decode_double_negative_raises(self) -> None:
        with pytest.raises(InvalidIntegerError):
            decode(b"i--1e")

    def test_decode_just_dash_raises(self) -> None:
        with pytest.raises(InvalidIntegerError):
            decode(b"i-e")

    def test_decode_unterminated_integer_raises(self) -> None:
        with pytest.raises(TruncatedError):
            decode(b"i42")

    def test_decode_non_digit_in_integer_raises(self) -> None:
        with pytest.raises(InvalidIntegerError):
            decode(b"i4xe")


class TestDecodeStrings:
    def test_decode_empty_string(self) -> None:
        assert decode(b"0:") == b""

    def test_decode_simple_string(self) -> None:
        assert decode(b"4:spam") == b"spam"

    def test_decode_binary_string(self) -> None:
        assert decode(b"3:\x00\x01\x02") == b"\x00\x01\x02"

    def test_decode_truncated_body_raises(self) -> None:
        with pytest.raises(TruncatedError, match="truncated"):
            decode(b"5:abc")

    def test_decode_missing_colon_raises(self) -> None:
        with pytest.raises(InvalidStringError):
            decode(b"5abc")

    def test_decode_leading_zero_length_raises(self) -> None:
        with pytest.raises(InvalidStringError, match="leading zero"):
            decode(b"01:a")

    def test_decode_zero_then_data_is_trailing(self) -> None:
        with pytest.raises(TrailingDataError):
            decode(b"0:hi")


class TestDecodeLists:
    def test_decode_empty_list(self) -> None:
        assert decode(b"le") == []

    def test_decode_simple_list(self) -> None:
        assert decode(b"l4:spami42ee") == [b"spam", 42]

    def test_decode_nested_list(self) -> None:
        assert decode(b"lli1ei2eeli3eee") == [[1, 2], [3]]

    def test_decode_unterminated_list_raises(self) -> None:
        with pytest.raises(TruncatedError, match="list"):
            decode(b"li1e")

    def test_decode_list_with_bad_inner_propagates(self) -> None:
        with pytest.raises(InvalidIntegerError):
            decode(b"li-0ee")


class TestDecodeDicts:
    def test_decode_empty_dict(self) -> None:
        assert decode(b"de") == {}

    def test_decode_simple_dict(self) -> None:
        assert decode(b"d1:ai1e1:bi2ee") == {b"a": 1, b"b": 2}

    def test_decode_dict_keys_must_be_strings(self) -> None:
        with pytest.raises(InvalidDictError, match="byte string"):
            decode(b"di1ei2ee")

    def test_decode_dict_keys_must_be_increasing(self) -> None:
        with pytest.raises(InvalidDictError, match="increasing"):
            decode(b"d1:bi1e1:ai2ee")

    def test_decode_dict_duplicate_keys_raises(self) -> None:
        with pytest.raises(InvalidDictError, match="increasing"):
            decode(b"d1:ai1e1:ai2ee")

    def test_decode_dict_truncated_raises(self) -> None:
        with pytest.raises(TruncatedError, match="dict"):
            decode(b"d1:ai1e")

    def test_decode_dict_nested_value(self) -> None:
        assert decode(b"d1:kl1:vi9eee") == {b"k": [b"v", 9]}


class TestDecodeMisc:
    def test_decode_unknown_byte_raises(self) -> None:
        with pytest.raises(DecodeError, match="unexpected"):
            decode(b"x")

    def test_decode_trailing_bytes_raises(self) -> None:
        with pytest.raises(TrailingDataError):
            decode(b"i1ei2e")

    def test_decode_empty_input_raises(self) -> None:
        with pytest.raises(TruncatedError):
            decode(b"")

    def test_decode_accepts_bytearray(self) -> None:
        assert decode(bytearray(b"i7e")) == 7

    def test_decode_accepts_memoryview(self) -> None:
        assert decode(memoryview(b"i7e")) == 7

    def test_decode_rejects_non_bytes(self) -> None:
        with pytest.raises(DecodeError, match="bytes-like"):
            decode("i1e")  # type: ignore[arg-type]

    def test_decode_error_offset_attribute(self) -> None:
        with pytest.raises(InvalidIntegerError) as exc:
            decode(b"i01e")
        assert exc.value.offset == 0


class TestDecodePartial:
    def test_decode_partial_returns_consumed_offset(self) -> None:
        value, end = decode_partial(b"i7e0:")
        assert value == 7
        assert end == 3

    def test_decode_partial_continues_from_offset(self) -> None:
        data = b"i7e0:"
        first, mid = decode_partial(data)
        second, end = decode_partial(data, offset=mid)
        assert first == 7
        assert second == b""
        assert end == len(data)

    def test_decode_partial_negative_offset_raises(self) -> None:
        with pytest.raises(DecodeError):
            decode_partial(b"i1e", offset=-1)

    def test_decode_partial_offset_past_end_raises(self) -> None:
        with pytest.raises(DecodeError):
            decode_partial(b"i1e", offset=99)


class TestIterDecode:
    def test_iter_decode_empty_input_yields_nothing(self) -> None:
        assert list(iter_decode(b"")) == []

    def test_iter_decode_single_value(self) -> None:
        assert list(iter_decode(b"i1e")) == [1]

    def test_iter_decode_multiple_values(self) -> None:
        assert list(iter_decode(b"i1e0:le")) == [1, b"", []]

    def test_iter_decode_propagates_error(self) -> None:
        it = iter_decode(b"i1ei0")
        assert next(it) == 1
        with pytest.raises(TruncatedError):
            next(it)
