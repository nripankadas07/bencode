        # Project Brief

        bencode exists to solve a narrow, inspectable developer-tooling problem:
        Strict, dependency-free BitTorrent-style bencode encoder/decoder. Round-trips are exact: rejects every non-canonical encoding.

        ## Portfolio Role

        This repository is part of the local-first engineering portfolio around
        agentic AI infrastructure, evaluation, parsing, safety boundaries, and
        small tools that can be understood from a fresh source checkout. It is not
        here to inflate repository count; it should either provide a reusable
        primitive, a benchmark surface, or a concrete local workflow.

        Topics: bencode, bittorrent, decoder, encoder, python, release-track, zero-dependencies

        ## Current Gates

        - Latest completed CI: success
        - Source files counted by audit: 4
        - Test files counted by audit: 8
        - Latest release: v0.1.0
        - License: MIT

        ## Upgrade Path

        - Add adversarial conformance fixtures and malformed-input cases.
- Generate metamorphic tests with SpecMutate for round-trip, idempotence, and normalization invariants.
- Document resource limits, error taxonomy, and any intentionally unsupported parts of the format.

        ## Reviewer Contract

        A serious reviewer should be able to clone the repository, read the
        README and this brief, run the tests, and understand exactly what is
        claimed. Future work should prefer deeper correctness, better fixtures,
        clearer limits, and stronger local demos over broad feature lists.
