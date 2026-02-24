"""
Web Push helper — sends push notifications to all stored admin subscriptions.

VAPID keys are read from environment variables:
  VAPID_PRIVATE_KEY  — PEM content, newlines encoded as \\n
  VAPID_PUBLIC_KEY   — URL-safe base64, uncompressed EC point (for the browser)
  VAPID_SUBJECT      — e.g.  mailto:admin@szamma-mia.pl

Run  python generate_vapid.py  once to generate these keys.
"""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@szamma-mia.pl")

_executor = ThreadPoolExecutor(max_workers=4)


def _send_one(endpoint: str, p256dh: str, auth: str, payload: dict) -> bool:
    """
    Send a single push notification (runs in a thread — pywebpush is sync).
    Returns True if the subscription is still valid, False if it should be deleted.
    """
    try:
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth},
            },
            data=json.dumps(payload, ensure_ascii=False),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
            ttl=300,
        )
        return True
    except WebPushException as exc:
        # 404 / 410 = subscription expired or explicitly unregistered by the browser
        if exc.response is not None and exc.response.status_code in (404, 410):
            return False
        # Other errors (network, temporary) — keep the subscription
        return True
    except Exception:
        return True


async def push_to_all(db: AsyncSession, payload: dict) -> None:
    """Send *payload* to every push subscription stored in the DB."""
    if not VAPID_PRIVATE_KEY or not VAPID_PUBLIC_KEY:
        return  # Not configured — skip silently

    from models import PushSubscription  # local import avoids circular deps

    result = await db.execute(select(PushSubscription))
    subs = result.scalars().all()
    if not subs:
        return

    loop = asyncio.get_running_loop()
    stale_ids = []

    for sub in subs:
        alive = await loop.run_in_executor(
            _executor, _send_one, sub.endpoint, sub.p256dh, sub.auth, payload
        )
        if not alive:
            stale_ids.append(sub.id)

    # Clean up dead subscriptions
    for sid in stale_ids:
        stale = await db.get(PushSubscription, sid)
        if stale:
            await db.delete(stale)
    if stale_ids:
        await db.commit()


async def push_to_all_bg(payload: dict) -> None:
    """
    Background-task wrapper — creates its own DB session so it is safe to call
    after the request's session has been closed.
    """
    from database import async_session  # local import

    async with async_session() as db:
        await push_to_all(db, payload)
