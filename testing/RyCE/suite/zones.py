"""Zone profile for the RyCE (.wien) EPP test suite.

The suite connects to a single EPP edge (``EPP_HOST`` / ``EPP_PORT`` /
``EPP_USER`` / ``EPP_PASSWORD`` from the env file). The zone profile drives:

* test-domain suffix (``.wien``),
* where the role contact handles come from (suite-created contacts for RyCE,
  since the registrar has no pre-mapped RyCE handles),
* nameserver pairs, the known-taken label, and contact test data
  (env-overridable, sensible .wien defaults otherwise).

secDNS (DNSSEC) support is auto-detected from the greeting at run time; when
the OTE does not advertise ``secDNS-1.1`` the DNSSEC phase cases are recorded
as SKIPPED, not FAILED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class Zone:
    key: str                    # "wien"
    tld: str                    # test-domain suffix, e.g. ".wien"
    registry: str               # OTE behind the EPP edge (display name)
    contact_source: str         # "env" | "create"
    env_prefix: str             # env-file key prefix, e.g. "W"
    taken_domain: str           # known-registered label for the taken-check
    role_defaults: Dict[str, str] = field(default_factory=dict)
    # OTE-wide EPP schema: contact:voice may match the dotted
    # '(\+[0-9]{1,3}\.[0-9]{1,14})?' pattern. Override with W_CONTACT_PHONE.
    phone_default: str = "+43.155500101"

    def role_env_key(self, role: str) -> str:
        return f"{self.env_prefix}_{role.upper()}"


_ZONES: Dict[str, Zone] = {
    "wien": Zone(
        key="wien",
        tld=".wien",
        registry="RyCE OTE",
        # RyCE .wien: the registrar (dnspty) has no pre-mapped RyCE handles,
        # so the suite creates its own contacts.
        contact_source="create",
        env_prefix="W",
        taken_domain="wiener.stadt",
    ),
}


def get_zone(key: str) -> Zone:
    try:
        return _ZONES[key]
    except KeyError:
        raise SystemExit(f"unknown zone {key!r} (choose from: {', '.join(_ZONES)})")


def all_zone_keys():
    return list(_ZONES)
