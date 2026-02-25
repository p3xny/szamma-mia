<script setup>
import { ref, onMounted } from 'vue'

const sectionRef = ref(null)
const visible = ref(false)

const EVENT_TYPES = [
  {
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="14" width="20" height="7" rx="2"/><path d="M2 14q2.5 3 5 0q2.5 3 5 0q2.5 3 5 0q2.5 3 5 0"/><line x1="7" y1="9" x2="7" y2="14"/><line x1="12" y1="7" x2="12" y2="14"/><line x1="17" y1="9" x2="17" y2="14"/><path d="M7 9c1-1.2 1-3 0-3S6 7.8 7 9z"/><path d="M12 7c1-1.2 1-3 0-3S11 5.8 12 7z"/><path d="M17 9c1-1.2 1-3 0-3S16 7.8 17 9z"/></svg>`,
    title: 'Urodziny i&nbsp;rocznice',
    desc: 'Świętuj wyjątkowe chwile w kameralnym otoczeniu przy włoskiej kuchni i dobrym winie.',
  },
  {
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/><line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/></svg>`,
    title: 'Spotkania firmowe',
    desc: 'Kameralna sala idealna na firmowy lunch, kolację integracyjną lub spotkanie z klientem.',
  },
  {
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    title: 'Imprezy rodzinne',
    desc: 'Chrzciny, komunia, jubileusz — przyjmij bliskich przy suto zastawionym stole.',
  },
  {
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
    title: 'Eventy specjalne',
    desc: 'Wieczory degustacyjne, kolacje tematyczne, pokazy kulinarne — stworzymy event na miarę Twoich potrzeb.',
  },
]

onMounted(() => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        visible.value = true
        observer.disconnect()
      }
    },
    { threshold: 0.08, rootMargin: '0px 0px -10% 0px' }
  )
  if (sectionRef.value) observer.observe(sectionRef.value)
})
</script>

<template>
  <section ref="sectionRef" class="events-section" id="events">
    <div class="events-inner">

      <!-- Header -->
      <div class="events-header" :class="{ visible }">
        <span class="events-eyebrow">Szamma <span class="events-eyebrow-red">Mia</span></span>
        <h2 class="events-title">Eventy i&nbsp;Wydarzenia</h2>
        <p class="events-subtitle">
          Nasza restauracja to idealne miejsce na prywatne uroczystości.
          Zapewniamy kameralną atmosferę, wyśmienitą kuchnię i&nbsp;indywidualną obsługę.
        </p>
      </div>

      <!-- Event type cards -->
      <div class="events-grid">
        <div
          v-for="(item, idx) in EVENT_TYPES"
          :key="idx"
          class="event-card"
          :class="{ visible }"
          :style="{ transitionDelay: visible ? idx * 0.1 + 's' : '0s' }"
        >
          <div class="event-card-icon" v-html="item.icon"></div>
          <h3 class="event-card-title" v-html="item.title"></h3>
          <p class="event-card-desc">{{ item.desc }}</p>
        </div>
      </div>

      <!-- CTA -->
      <div class="events-cta" :class="{ visible }">
        <p class="events-cta-text">
          Chcesz zarezerwować salę lub omówić szczegóły imprezy?
        </p>
        <!-- <a href="/reservation" class="events-cta-btn events-cta-btn-primary">Zarezerwuj stolik</a> -->
         <!-- events-cta-btn-secondary   <- class for black button -->
        <a href="tel:+48123456789" class="events-cta-btn events-cta-btn-primary">Zadzwoń do nas</a>
      </div>

    </div>
  </section>
</template>

<style scoped>
.events-section {
  background: var(--dark);
  padding: 5.5rem 1.5rem;
}

.events-inner {
  max-width: 1100px;
  margin: 0 auto;
}

/* ── Header ──────────────────────────────────────────────────────────── */
.events-header {
  text-align: center;
  margin-bottom: 3.5rem;
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.events-header.visible {
  opacity: 1;
  transform: none;
}

.events-eyebrow {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: 0.55rem;
}

.events-eyebrow-red {
  color: var(--red);
}

.events-title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800;
  color: var(--white);
  margin: 0 0 0.8rem;
  line-height: 1.15;
}

.events-subtitle {
  font-size: 1rem;
  color: #aaa;
  max-width: 560px;
  margin: 0 auto;
  line-height: 1.65;
}

/* ── Grid ────────────────────────────────────────────────────────────── */
.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 1.25rem;
  margin-bottom: 3rem;
}

/* ── Card ────────────────────────────────────────────────────────────── */
.event-card {
  background: #1e1e1e;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  padding: 1.75rem 1.5rem;
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.5s ease, transform 0.5s ease, box-shadow 0.3s ease;
}

.event-card.visible {
  opacity: 1;
  transform: none;
}

.event-card:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
  border-color: rgba(0, 146, 70, 0.3);
}

.event-card-icon {
  color: var(--green);
  margin-bottom: 1rem;
  line-height: 1;
}

.event-card-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--white);
  margin: 0 0 0.5rem;
  line-height: 1.3;
}

.event-card-desc {
  font-size: 0.88rem;
  color: #aaa;
  line-height: 1.6;
  margin: 0;
}

/* ── CTA ──────────────────────────────────────────────────────────────── */
.events-cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
  text-align: center;
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease 0.45s, transform 0.6s ease 0.45s;
}

.events-cta.visible {
  opacity: 1;
  transform: none;
}

.events-cta-text {
  width: 100%;
  color: #bbb;
  font-size: 1rem;
  margin: 0 0 0.25rem;
}

.events-cta-btn {
  display: inline-block;
  padding: 0.75rem 1.75rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  font-family: inherit;
}

.events-cta-btn-primary {
  background: var(--green);
  color: var(--white);
  border: 2px solid var(--green);
}

.events-cta-btn-primary:hover {
  background: #007a3a;
  border-color: #007a3a;
}

.events-cta-btn-secondary {
  background: transparent;
  color: var(--white);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.events-cta-btn-secondary:hover {
  border-color: var(--white);
}

/* ── Mobile ──────────────────────────────────────────────────────────── */
@media (max-width: 600px) {
  .events-section {
    padding: 3.5rem 1rem;
  }

  .events-grid {
    grid-template-columns: 1fr 1fr;
  }

  .events-cta {
    flex-direction: column;
  }

  .events-cta-btn {
    width: 100%;
    text-align: center;
  }
}

@media (max-width: 400px) {
  .events-grid {
    grid-template-columns: 1fr;
  }
}
</style>
