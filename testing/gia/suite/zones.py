"""Zone profiles for the multi-zone EPP test suite.

Every zone connects to the SAME EPP edge (``EPP_HOST`` / ``EPP_PORT`` /
``EPP_USER`` / ``EPP_PASSWORD`` from the env file). The multiplexer routes
each command to the registry OTE that owns the TLD in the domain name, so
the only per-zone differences are registry policy:

* which contact roles a ``domain:create`` must carry,
* where the role contact handles come from: pre-mapped registry handles in
  the env file (``de``), or contacts the suite creates itself (``com``,
  ``africa``),
* nameserver pairs, the known-taken label, and contact test data
  (env-overridable per zone, built-in defaults otherwise).

secDNS (DNSSEC) support is auto-detected from each zone's greeting at run
time; when a zone's OTE does not advertise ``secDNS-1.1`` the DNSSEC phase
cases are recorded as SKIPPED, not FAILED.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

# Roles a zone may require, in canonical domain:create element order
# (registrant first, then the typed <domain:contact> roles).
CANONICAL_ROLES = ("registrant", "admin", "tech", "billing")

# Short role codes for generated contact handles (EPP contact:id max 16 chars).
ROLE_SHORT = {"registrant": "reg", "admin": "adm", "tech": "tec", "billing": "bil"}


@dataclass(frozen=True)
class Zone:
    key: str                    # "de" | "com" | "africa"
    tld: str                    # test-domain suffix, e.g. ".de"
    registry: str               # OTE behind the multiplexer (display name)
    required_roles: Tuple[str, ...]
    contact_source: str         # "env" (pre-mapped handles) | "create"
    env_prefix: str             # env-file key prefix, e.g. "DE"
    taken_domain: str           # known-registered label for the taken-check
    role_defaults: Dict[str, str] = field(default_factory=dict)
    # OTE-wide EPP schema: contact:voice must match the dotted
    # '(\\+[0-9]{1,3}\\.[0-9]{1,14})?' pattern on every zone, so all zones
    # share the dotted default. Override per zone with <PREFIX>_CONTACT_PHONE.
    phone_default: str = "+27.215550101"
    # Registrar-onboarding cases (holder/contact/authInfo changes, renew,
    # transfer, restore, strict RFC response checks). Enabled per zone.
    onboarding: bool = False
    # RFC 5910 interface for DNSSEC: "ds" (dsData) or "key" (keyData, for
    # registries that store DNSKEYs, e.g. DENIC's dnsentry:DNSKEY).
    secdns_interface: str = "ds"

    def role_env_key(self, role: str) -> str:
        return f"{self.env_prefix}_{role.upper()}"


_ZONES: Dict[str, Zone] = {
    "de": Zone(
        key="de",
        tld=".de",
        registry="DENIC OTE",
        # DENIC policy: registrant + admin + tech + billing, all pre-mapped
        # to existing DENIC handles via zone_contact.
        required_roles=("registrant", "admin", "tech", "billing"),
        contact_source="env",
        env_prefix="DE",
        taken_domain="denic.de",
        role_defaults={
            "registrant": "C0003239",
            "admin": "C0003243",
            "tech": "C0003247",
            "billing": "courtney1",
        },
        onboarding=True,
        secdns_interface="key",
    ),
    "com": Zone(
        key="com",
        tld=".com",
        registry="Verisign OTE",
        # OTE policy (probed via 2306 reasons "Registrant required" /
        # "Billing contact required"): all four roles are mandatory; the suite
        # creates them itself (no pre-mapped handles for this registrar).
        required_roles=("registrant", "admin", "tech", "billing"),
        contact_source="create",
        env_prefix="COM",
        taken_domain="google.com",
    ),
    "africa": Zone(
        key="africa",
        tld=".africa",
        registry="Registry Africa (RA) OTE",
        # EPP-native registry: same four-role policy as .de (verified via the
        # OTE's 2306 probe responses); suite-created contacts.
        required_roles=("registrant", "admin", "tech", "billing"),
        contact_source="create",
        env_prefix="AFRICA",
        taken_domain="google.africa",
    ),
}


def get_zone(key: str) -> Zone:
    try:
        return _ZONES[key]
    except KeyError:
        raise SystemExit(
            f"unknown zone {key!r} (choose from: {', '.join(_ZONES)})"
        )


def all_zone_keys():
    return list(_ZONES)
