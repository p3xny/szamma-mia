#!/usr/bin/env python3
"""
One-time VAPID key generator for Web Push.

Usage (from server/ with the venv activated):
    python generate_vapid.py

Copy the printed lines into server/.env, then restart uvicorn.
"""

from base64 import urlsafe_b64encode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

# Private key — PEM, newlines replaced with \n for single-line .env storage
private_pem = private_key.private_bytes(
    Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
).decode()
private_env = private_pem.strip().replace("\n", "\\n")

# Public key — URL-safe base64, uncompressed EC point (what browsers expect)
pub_bytes = private_key.public_key().public_bytes(
    Encoding.X962, PublicFormat.UncompressedPoint
)
public_b64 = urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()

print("\n=== VAPID Keys ===")
print("Add these three lines to  server/.env  then restart uvicorn:\n")
print(f'VAPID_PRIVATE_KEY="{private_env}"')
print(f"VAPID_PUBLIC_KEY={public_b64}")
print("VAPID_SUBJECT=mailto:admin@szamma-mia.pl")
print()
print("The VAPID_PUBLIC_KEY value is also the browser applicationServerKey.")
print("It is served automatically via GET /api/push/vapid-key.\n")
