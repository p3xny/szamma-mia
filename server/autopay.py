"""
AutoPay (Blue Media) payment gateway integration helpers.

Documentation: https://developers.autopay.pl/en
Hash algorithm: SHA256, pipe-separated fields + shared key at the end.

To use, set in .env:
    AUTOPAY_SERVICE_ID   – assigned by AutoPay during onboarding
    AUTOPAY_SHARED_KEY   – secret key from AutoPay merchant panel
    AUTOPAY_GATEWAY_URL  – https://testpay.autopay.eu/payment (test)
                           https://pay.autopay.eu/payment       (production)
    AUTOPAY_RETURN_URL   – base URL the customer lands on after payment
                           e.g. https://szamma-mia.pl/order-confirmation
    AUTOPAY_FAILURE_URL  – base URL on payment failure
                           e.g. https://szamma-mia.pl/payment-failed
"""

import hashlib
import os
from base64 import b64decode
from xml.etree import ElementTree as ET

AUTOPAY_SERVICE_ID = os.getenv("AUTOPAY_SERVICE_ID", "")
AUTOPAY_SHARED_KEY = os.getenv("AUTOPAY_SHARED_KEY", "")
AUTOPAY_GATEWAY_URL = os.getenv(
    "AUTOPAY_GATEWAY_URL", "https://testpay.autopay.eu/payment"
)
AUTOPAY_RETURN_URL = os.getenv(
    "AUTOPAY_RETURN_URL", "http://localhost:5173/order-confirmation"
)
AUTOPAY_FAILURE_URL = os.getenv(
    "AUTOPAY_FAILURE_URL", "http://localhost:5173/payment-failed"
)

# Payment methods that require online payment via AutoPay
ONLINE_PAYMENT_METHODS = {"blik", "card-online", "transfer"}


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _sha256(*parts: str) -> str:
    """SHA256 of all parts joined with '|' separator."""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def compute_hash(*fields: str) -> str:
    """
    Compute AutoPay hash for arbitrary fields.
    Appends AUTOPAY_SHARED_KEY as the last element before hashing.

    Hash formula (from AutoPay docs):
        SHA256(field1|field2|...|fieldN|SharedKey)
    """
    return _sha256(*fields, AUTOPAY_SHARED_KEY)


# ---------------------------------------------------------------------------
# Payment initiation
# ---------------------------------------------------------------------------


def build_payment_params(order_id: int, amount: str) -> dict:
    """
    Build the POST parameters dict to submit to the AutoPay gateway.

    Required hash fields (in this order): ServiceID, OrderID, Amount, SharedKey
    Optional fields (Description, CustomerEmail, GatewayID, Currency, …) can be
    inserted between Amount and SharedKey in the hash when added here.

    Args:
        order_id: Internal order ID used as AutoPay's OrderID.
        amount:   Formatted amount string, e.g. "49.99".

    Returns:
        Dict ready to be submitted as HTML form fields.
    """
    service_id = AUTOPAY_SERVICE_ID
    order_id_str = str(order_id)

    # Hash: ServiceID | OrderID | Amount | SharedKey
    hash_val = compute_hash(service_id, order_id_str, amount)

    return {
        "ServiceID": service_id,
        "OrderID": order_id_str,
        "Amount": amount,
        "ReturnURL": f"{AUTOPAY_RETURN_URL}/{order_id}",
        "FailureURL": f"{AUTOPAY_FAILURE_URL}/{order_id}",
        "Hash": hash_val,
    }


# ---------------------------------------------------------------------------
# Return redirect verification
# ---------------------------------------------------------------------------


def verify_return_hash(service_id: str, order_id: str, hash_received: str) -> bool:
    """
    Verify the hash on the GET redirect AutoPay sends back to ReturnURL.

    Hash formula: SHA256(ServiceID|OrderID|SharedKey)
    """
    expected = compute_hash(service_id, order_id)
    return expected == hash_received


# ---------------------------------------------------------------------------
# ITN (Instant Transaction Notification) webhook
# ---------------------------------------------------------------------------


def parse_itn(raw_xml: str) -> dict:
    """
    Parse the ITN XML document AutoPay sends via POST (base64-encoded).

    Returns a flat dict with all transaction fields needed for hash verification.
    Raises ValueError if the XML is malformed or missing the transaction element.
    """
    root = ET.fromstring(raw_xml)
    tx = root.find("transactions/transaction")
    if tx is None:
        raise ValueError("No <transaction> element in ITN XML")

    def _text(tag: str) -> str:
        el = tx.find(tag)
        return (el.text or "") if el is not None else ""

    return {
        "service_id": root.findtext("serviceID") or "",
        "order_id": _text("orderID"),
        "remote_id": _text("remoteID"),
        "amount": _text("amount"),
        "currency": _text("currency"),
        "gateway_id": _text("gatewayID"),
        "payment_date": _text("paymentDate"),
        "payment_status": _text("paymentStatus"),
        "payment_status_details": _text("paymentStatusDetails"),
        "hash": root.findtext("hash") or "",
    }


def verify_itn_hash(tx: dict) -> bool:
    """
    Verify the hash in an ITN notification.

    Hash formula (from AutoPay docs):
        SHA256(serviceID|orderID|remoteID|amount|currency|gatewayID|
               paymentDate|paymentStatus|paymentStatusDetails|SharedKey)
    """
    expected = compute_hash(
        tx["service_id"],
        tx["order_id"],
        tx["remote_id"],
        tx["amount"],
        tx["currency"],
        tx["gateway_id"],
        tx["payment_date"],
        tx["payment_status"],
        tx["payment_status_details"],
    )
    return expected == tx["hash"]


# ---------------------------------------------------------------------------
# Confirmation response
# ---------------------------------------------------------------------------


def build_confirmation_xml(service_id: str, order_id: str, confirmed: bool) -> str:
    """
    Build the XML confirmation body that must be returned to AutoPay within
    the ITN webhook response (HTTP 200).

    Hash formula: SHA256(serviceID|orderID|confirmation|SharedKey)
    """
    confirmation = "CONFIRMED" if confirmed else "NOTCONFIRMED"
    hash_val = compute_hash(service_id, order_id, confirmation)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<confirmationList>"
        f"<serviceID>{service_id}</serviceID>"
        "<transactionsConfirmations>"
        "<transactionConfirmed>"
        f"<orderID>{order_id}</orderID>"
        f"<confirmation>{confirmation}</confirmation>"
        "</transactionConfirmed>"
        "</transactionsConfirmations>"
        f"<hash>{hash_val}</hash>"
        "</confirmationList>"
    )
