"""End-to-end test suite for the RyCE OTE (.wien) zone.

Exercises the full software chain:

    this suite (EPP client) -> DAMSR -> rEngin -> RyCE OTE (.wien)

Every run updates a persistent checklist (checklists/checklist.json +
checklists/CHECKLIST.md) that records which tests pass, fail, or are
blocked, and which error is currently blocking the remaining tests.
"""

__version__ = "1.0"
