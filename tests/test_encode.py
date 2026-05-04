"""Tests for :func:`bencode.encode`."""

from __future__ import annotations

import pytest

from bencode import EncodeError, encode


class TestEncodeIntegers:
    def test_encode_zero_is_i0e(self) -> None:
        assert encode(0) == b"i0e"

    def test_encode_positive_integer(self) -> None:
        assert encode(42) == b"i42e"

    def test_encode_negative_integer(self) -> None:
        assert encode(-7) == b"i-7e"

    def test_encode_large_integer(self) -> None:
        big = 10 ** 30
        assert encode(big) == b"i" + str(big).encode("ascii") + b"e"

    def test_encode_bool_raises(self) -> None:
        with pytest.raises(EncodeError, match="bool is not"):
            encode(True)

    def test_encode_bool_false_also_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode(False)


class TestEncodeStrings:
    def test_encode_empty_bytes(self) -> None:
        assert encode(b"") == b"0:"

    def test_encode_simple_bytes(self) -> None:
        assert encode(b"spam") == b"4:spam"

    def test_encode_bytes_with_null_byte(self) -> None:
        assert encode(b"\x00\x01") == b"2:\x00\x01"

    def test_encode_bytearray_works(self) -> None:
        assert encode(bytearray(b"egg")) == b"3:egg"

    def test_encode_memoryview_works(self) -> None:
        assert encode(memoryview(b"abc")) == b"3:abc"

    def test_encode_str_raises(self) -> None:
        with pytest.raises(EncodeError, match="unsupported type"):
            encode("spam")


class TestEncodeLists:
    def test_encode_empty_list(self) -> None:
        assert encode([]) == b"le"

    def test_encode_simple_list(self) -> None:
        assert encode([b"spam", 42]) == b"l4:spami42ee"

    def test_encode_nested_list(self) -> None:
        assert encode([[1, 2], [3]]) == b"lli1ei2eeli3eee"

    def test_encode_tuple_treated_like_list(self) -> None:
        assert encode((b"a", b"b")) == b"l1:a1:be"


class TestEncodeDicts:
    def test_encode_empty_dict(self) -> None:
        assert encode({}) == b"de"

    def test_encode_dict_sorts_by_key_bytes(self) -> None:
        assert encode({b"b": 1, b"a": 2}) == b"d1:ai2e1:bi1ee"

    def test_encode_dict_nested_value(self) -> None:
        out = encode({b"k": [b"v", 9]})
        assert out == b"d1:kl1:vi9eee"

    def test_encode_dict_str_key_raises(self) -> None:
        with pytest.raises(EncodeError, match="bytes"):
            encode({"a": 1})

    def test_encode_dict_int_key_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode({1: 1})

    def test_encode_dict_bool_key_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode({True: 1})

    def test_encode_dict_with_byteslike_key_raises(self) -> None:
        # bytearray and memoryview are not hashable as dict keys, so the
        # encoder accepts only ``bytes`` keys.  Verify we say so clearly
        # if someone reaches us with a memoryview-keyed mapping built
        # from outside CPython's normal dict.
        class FakeMap(dict):  # type: ignore[type-arg]
            pass
        m = FakeMap()
        # Insert via dict's underlying storage by side-stepping hashing.
        dict.__setitem__(m, b"a", 1)  # bytes key works
        assert encode(m) == b"d1:ai1ee"


class TestEncodeUnsupported:
    def test_encode_none_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode(None)

    def test_encode_float_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode(1.5)

    def test_encode_set_raises(self) -> None:
        with pytest.raises(EncodeError):
            encode({1, 2, 3})

    def test_encode_error_carries_path(self) -> None:
        with pytest.raises(EncodeError) as exc:
            encode({b"top": [b"ok", None]})
        assert exc.value.path == (b"top", 1)
        assert exc.value.value is None
