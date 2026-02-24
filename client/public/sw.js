// Szamma Mia — Service Worker
// Handles push notifications for staff tablets.

self.addEventListener('install', () => self.skipWaiting())
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()))

// ── Push received ──────────────────────────────────────────────────────────

self.addEventListener('push', event => {
  if (!event.data) return

  let data
  try {
    data = event.data.json()
  } catch {
    data = { title: 'Szamma Mia', body: event.data.text(), type: 'generic', id: Date.now() }
  }

  const options = {
    body: data.body,
    icon: '/icon.png',
    badge: '/icon.png',
    tag: `${data.type}-${data.id}`,   // collapse duplicate same-type notifications
    renotify: true,                    // always vibrate/sound even if same tag
    vibrate: [200, 100, 200, 100, 400],
    requireInteraction: true,          // stay on screen until dismissed
    data: { url: data.url || '/' },
    actions: [
      { action: 'open', title: 'Otwórz' },
      { action: 'dismiss', title: 'Zamknij' },
    ],
  }

  event.waitUntil(
    Promise.all([
      self.registration.showNotification(data.title, options),
      // Tell any open windows to play a sound
      self.clients
        .matchAll({ type: 'window', includeUncontrolled: true })
        .then(clients => clients.forEach(c => c.postMessage({ type: 'PUSH_RECEIVED', data }))),
    ])
  )
})

// ── Notification click ─────────────────────────────────────────────────────

self.addEventListener('notificationclick', event => {
  event.notification.close()
  if (event.action === 'dismiss') return

  const url = event.notification.data?.url || '/'

  event.waitUntil(
    self.clients
      .matchAll({ type: 'window', includeUncontrolled: true })
      .then(clients => {
        const existing = clients.find(c => c.url.startsWith(self.location.origin))
        if (existing) return existing.focus()
        return self.clients.openWindow(url)
      })
  )
})
