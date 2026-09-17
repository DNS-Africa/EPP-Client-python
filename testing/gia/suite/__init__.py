"""End-to-end test suite for the .de zone.

Exercises the full software chain:

    this suite (EPP client) -> DAMSR -> rEngin -> multiplexer -> DENIC OTE

Basic EPP operations first, then advanced DNSSEC (secDNS-1.1) operations.
Every run updates a persistent checklist (checklist.json + CHECKLIST.md)
that records which tests pass, fail, or are blocked, and which error is
currently blocking the remaining tests.
"""

__version__ = "1.0"
