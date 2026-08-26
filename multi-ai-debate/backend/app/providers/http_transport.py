"""
Shared HTTPS transport for every outbound provider call.

Why this module exists
----------------------
Consumer security suites (Avast/AVG "Web Shield", Kaspersky, ESET, and most corporate
proxies) terminate TLS locally and re-sign every certificate with their own root CA. That
root is installed in the Windows certificate store, so browsers and curl (Schannel) work
fine - but Python/OpenSSL does not use the Windows store, so every httpx request fails with:

    [SSL: CERTIFICATE_VERIFY_FAILED] unable to get local issuer certificate

On this project that failure was invisible: the model-discovery `/models` listing swallowed
it in a bare `except Exception: pass` and silently fell back to the small curated model
list, so the setup wizard could never show a provider's full catalogue.

Loading the Windows roots alone is still not enough, because Avast's shield root marks its
Basic Constraints extension non-critical, which OpenSSL's strict mode rejects:

    [SSL: CERTIFICATE_VERIFY_FAILED] Basic Constraints of CA cert not marked critical

So the context below trusts certifi's bundle *plus* the OS root store, and clears only
`VERIFY_X509_STRICT` - the RFC-pedantry flag. Chain building, signature checks, expiry and
hostname verification all stay on. This is not `verify=False`.
"""

import ssl
import sys
from typing import Optional

import certifi
import httpx

_SSL_CONTEXT: Optional[ssl.SSLContext] = None
_OS_ROOT_PEMS: Optional[str] = None
_CONTEXT_LOGGED = False


def _os_root_store_pems() -> str:
    """
    Every root the OS trusts, as concatenated PEM. Empty string off Windows.

    Memoized: enumerating and DER->PEM converting ~100 certificates is CPU-blocking, and this
    is reached from request handlers (/health diagnostics) on the event loop.
    """
    global _OS_ROOT_PEMS
    if _OS_ROOT_PEMS is not None:
        return _OS_ROOT_PEMS
    if not hasattr(ssl, "enum_certificates"):
        _OS_ROOT_PEMS = ""
        return _OS_ROOT_PEMS
    chunks = []
    for store in ("ROOT", "CA"):
        try:
            entries = ssl.enum_certificates(store)
        except Exception:
            continue
        for der, encoding, _trust in entries:
            if encoding != "x509_asn":
                continue
            try:
                chunks.append(ssl.DER_cert_to_PEM_cert(der))
            except Exception:
                continue  # a single malformed store entry must not sink the whole bundle
    _OS_ROOT_PEMS = "\n".join(chunks)
    return _OS_ROOT_PEMS


def provider_ssl_context() -> ssl.SSLContext:
    """
    Build (once) the verifying SSL context used for all provider traffic.

    Falls back to the stock certifi context if the OS store cannot be read, so behaviour on
    Linux/macOS is unchanged.
    """
    global _SSL_CONTEXT, _CONTEXT_LOGGED
    if _SSL_CONTEXT is not None:
        return _SSL_CONTEXT

    context = ssl.create_default_context(cafile=certifi.where())
    added_os_roots = False
    os_roots = _os_root_store_pems()
    if os_roots:
        try:
            context.load_verify_locations(cadata=os_roots)
            added_os_roots = True
        except Exception as e:
            print(f"[transport] Could not merge the OS root store, using certifi only: {e}")

    # Locally-generated interception roots are frequently non-compliant in ways that only
    # strict mode cares about. Keep chain/hostname/expiry verification; drop the pedantry.
    context.verify_flags &= ~ssl.VERIFY_X509_STRICT

    _SSL_CONTEXT = context
    if not _CONTEXT_LOGGED:
        _CONTEXT_LOGGED = True
        source = "certifi + OS root store" if added_os_roots else "certifi"
        print(f"[transport] HTTPS verification enabled ({source}, non-strict X509).")
    return context


def build_async_client(**kwargs) -> httpx.AsyncClient:
    """Drop-in replacement for httpx.AsyncClient(...) for outbound provider calls."""
    kwargs.setdefault("verify", provider_ssl_context())
    return httpx.AsyncClient(**kwargs)


def transport_diagnostics() -> dict:
    """Small summary for /health style reporting."""
    context = provider_ssl_context()
    return {
        "platform": sys.platform,
        "certifi_bundle": certifi.where(),
        "os_root_store_merged": bool(_os_root_store_pems()),
        "strict_x509": bool(context.verify_flags & ssl.VERIFY_X509_STRICT),
        "verify_enabled": context.verify_mode != ssl.CERT_NONE,
    }
