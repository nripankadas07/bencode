# Security policy

## Supported versions

The `main` branch is the supported development line.

## Reporting a vulnerability

Please report parser denial-of-service concerns, dependency issues, or malformed
input crashes through GitHub's private vulnerability reporting when available,
or by opening a minimal public issue without exploit payloads.

For untrusted bencoded input, limit document size before parsing. This package
parses complete byte strings in memory and intentionally leaves torrent
schema-level validation to callers.
