"""Exception hierarchy for the :mod:`bencode` package.

All errors raised by the public API descend from :class:`BencodeError`,
which is itself a :class:`ValueError`, so callers may catch either.
Decode errors carry the integer ``offset`` at which the error was
detected.  Encode errors carry the offending value verbatim so the
caller can inspect (or re-raise from) them.
"""

from __future__ import annotations

__all__ = [
    "BencodeError",
    "EncodeError",
    "DecodeError",
    "TruncatedError",
    "InvalidIntegerError",
    "InvalidStringError",
    "InvalidDictError",
    "TrailingDataError",
]


class BencodeError(ValueError):
    """Base class for every error raised by :mod:`bencode`."""


class EncodeError(BencodeError):
    """Raised when :func:`bencode.encode` is given an unsupported value.

    The offending value is stored on :attr:`value` and the path to it
    inside the original structure is stored on :attr:`path` (a tuple of
    ``int`` for list indices and ``bytes`` for dict keys).
    """

    def __init__(
        self,
        message: str,
        *,
        value: object,
        path: tuple[object, ...] = (),
    ) -> None:
        super().__init__(message)
        self.value = value
        self.path = path


class DecodeError(BencodeError):
    """Base class for decode errors.  Carries the byte ``offset``."""

    def __init__(self, message: str, *, offset: int) -> None:
        super().__init__(message)
        self.offset = offset


class TruncatedError(DecodeError):
    """Input ended before the current token was complete."""


class InvalidIntegerError(DecodeError):
    """Integer token was malformed (``i e``, ``i01e``, ``i-0e``, ...)."""


class InvalidStringError(DecodeError):
    """Length-prefixed string was malformed or its body truncated."""


class InvalidDictError(DecodeError):
    """Dict had a non-bytes key or keys not in strictly increasing order."""


class TrailingDataError(DecodeError):
    """:func:`decode` saw bytes after a complete top-level value."""
