import { ref } from 'vue'
import { api } from './useApi'

// Convert URL-safe base64 → Uint8Array (required by pushManager.subscribe)
function urlBase64ToUint8Array(base64) {
  const padding = '='.repeat((4 - (base64.length % 4)) % 4)
  const b64 = (base64 + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(b64)
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)))
}

// Synthesize a two-tone "ding" using the Web Audio API.
// Plays when a push arrives and the app is in the foreground.
function playNotificationSound() {
  try {
    const ctx = new AudioContext()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.frequency.setValueAtTime(880, ctx.currentTime)          // A5
    osc.frequency.setValueAtTime(1100, ctx.currentTime + 0.12)  // C#6
    gain.gain.setValueAtTime(0.35, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.7)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + 0.7)
  } catch {
    // AudioContext not available (e.g. SSR / test env) — silent fail
  }
}

const isSubscribed = ref(false)
const isSupported = ref(
  typeof window !== 'undefined' &&
  'serviceWorker' in navigator &&
  'PushManager' in window
)

let _vapidKey = null
async function fetchVapidKey() {
  if (_vapidKey) return _vapidKey
  const res = await api.get('/push/vapid-key')
  _vapidKey = res.data.public_key
  return _vapidKey
}

async function getRegistration() {
  return navigator.serviceWorker.register('/sw.js', { scope: '/' })
}

/**
 * Subscribe this device to push.
 * Idempotent — safe to call on every admin login.
 * Silently no-ops if push is unsupported or permission denied.
 */
async function subscribe() {
  if (!isSupported.value) return

  const reg = await getRegistration()

  // If the browser already holds a subscription, sync it to the backend
  // (handles the case where the DB was wiped) then return early.
  const existing = await reg.pushManager.getSubscription()
  if (existing) {
    isSubscribed.value = true
    try {
      const s = existing.toJSON()
      await api.post('/push/subscribe', { endpoint: s.endpoint, p256dh: s.keys.p256dh, auth: s.keys.auth })
    } catch { /* ignore — backend may already have it */ }
    return
  }

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return

  try {
    const key = await fetchVapidKey()
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(key),
    })
    const s = sub.toJSON()
    await api.post('/push/subscribe', { endpoint: s.endpoint, p256dh: s.keys.p256dh, auth: s.keys.auth })
    isSubscribed.value = true
  } catch (err) {
    console.warn('[push] subscribe failed:', err)
  }
}

/** Unsubscribe this device. */
async function unsubscribe() {
  if (!isSupported.value) return
  const reg = await navigator.serviceWorker.getRegistration('/sw.js')
  if (!reg) return
  const sub = await reg.pushManager.getSubscription()
  if (!sub) { isSubscribed.value = false; return }

  try {
    await api.post('/push/unsubscribe', { endpoint: sub.toJSON().endpoint })
  } catch { /* ignore */ }
  await sub.unsubscribe()
  isSubscribed.value = false
}

/** Check whether this device is already subscribed. */
async function checkSubscriptionStatus() {
  if (!isSupported.value) return
  const reg = await navigator.serviceWorker.getRegistration('/sw.js')
  if (!reg) return
  const sub = await reg.pushManager.getSubscription()
  isSubscribed.value = !!sub
}

/**
 * Listen for push messages forwarded by the service worker to open windows.
 * Plays a sound and calls the optional callback with the push payload.
 * Call once from App.vue for admin users.
 */
function listenForForegroundPush(onPush) {
  if (!('serviceWorker' in navigator)) return
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data?.type === 'PUSH_RECEIVED') {
      playNotificationSound()
      onPush?.(event.data.data)
    }
  })
}

export function usePushNotifications() {
  return {
    isSubscribed,
    isSupported,
    subscribe,
    unsubscribe,
    checkSubscriptionStatus,
    listenForForegroundPush,
    playNotificationSound,
  }
}
