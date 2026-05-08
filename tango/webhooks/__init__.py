"""Tango webhooks: signature helpers and developer tooling.

The signing helpers (:func:`verify_signature`, :func:`generate_signature`,
:func:`parse_signature_header`) are pure stdlib and importable from a default
``pip install tango``. The CLI (``tango webhooks ...``) and the in-process
:class:`~tango.webhooks.receiver.WebhookReceiver` ship with the
``tango[webhooks]`` extra.
"""

from tango.webhooks.signing import (
    SIGNATURE_HEADER,
    SIGNATURE_PREFIX,
    generate_signature,
    parse_signature_header,
    verify_signature,
)
from tango.webhooks.simulate import SignedRequest, sign

__all__ = [
    "SIGNATURE_HEADER",
    "SIGNATURE_PREFIX",
    "SignedRequest",
    "generate_signature",
    "parse_signature_header",
    "sign",
    "verify_signature",
]
