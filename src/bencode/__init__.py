"""bencode — strict, dependency-free BitTorrent bencode encoder/decoder.

Public API::

    from bencode import (
        encode,
        decode,
        decode_partial,
        iter_decode,
        BencodeError,
        EncodeError,
        DecodeError,
        TruncatedError,
        InvalidIntegerError,
        InvalidStringError,
        InvalidDictError,
        TrailingDataError,
    )

Bencode is the wire format used by the BitTorrent protocol.  This
package implements the canonical four-type subset:

* signed integers (``i<n>e``)
* length-prefixed byte strings (``<len>:<bytes>``)
* lists (``l<...>e``)
* dictionaries (``d<key><value>...e``) with bytes keys in strictly
  increasing lexicographic order.

The encoder rejects ``bool`` (so ``True == 1`` cannot silently encode
as an integer) and any non-bytes dict key.  The decoder rejects every
non-canonical encoding — leading zeros in integer or length prefixes,
``i-0e``, dict keys out of order or duplicated — so that round-tripping
is exact.
"""

from ._decoder import decode, decode_partial, iter_decode
from ._encoder import encode
from ._errors import (
    BencodeError,
    DecodeError,
    EncodeError,
    InvalidDictError,
    InvalidIntegerError,
    InvalidStringError,
    TrailingDataError,
    TruncatedError,
)

__all__ = [
    "BencodeError",
    "DecodeError",
    "EncodeError",
    "InvalidDictError",
    "InvalidIntegerError",
    "InvalidStringError",
    "TrailingDataError",
    "TruncatedError",
    "decode",
    "decode_partial",
    "encode",
    "iter_decode",
]

__version__ = "0.1.0"
