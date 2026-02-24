<template>
  <section class="info" id="contact">
    <!-- Top rule with flag colours -->
    <div class="info-flag-rule">
      <div class="rule-green"></div>
      <div class="rule-white"></div>
      <div class="rule-red"></div>
    </div>

    <div class="info-inner">

      <!-- Col 1: Brand -->
      <div class="info-col info-col-brand">
        <p class="brand-name">Szamma Mia</p>
        <p class="brand-tagline">Autentyczna kuchnia włoska<br>w sercu Piaseczna</p>
        <p class="brand-desc">
          Gotujemy z pasją, używając wyłącznie świeżych składników.
          Każde danie to historia — opowiedziana smakiem.
        </p>
      </div>

      <!-- Col 2: Contact -->
      <div class="info-col">
        <h3 class="col-heading">Kontakt</h3>
        <ul class="info-list">
          <li>
            <span class="info-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
              </svg>
            </span>
            <a
            href="https://www.google.com/maps?ll=52.074409,21.028112&z=16&t=m&hl=en&gl=PL&mapclient=embed&cid=6960509488367654712"
            target="_blank"
            >ul. Sierakowskiego 2<br>05-500 Piaseczno</a>
          </li>
          <li>
            <span class="info-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.27h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.84a16 16 0 0 0 5.92 5.92l.88-.88a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
              </svg>
            </span>
            <a href="tel:+48123456789">+48 123 456 789</a>
          </li>
          <li>
            <span class="info-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
              </svg>
            </span>
            <a href="mailto:kontakt@szammamia.pl">kontakt@szammamia.pl</a>
          </li>
        </ul>
      </div>

      <!-- Col 3: Hours -->
      <div class="info-col">
        <h3 class="col-heading">Godziny otwarcia</h3>
        <ul class="hours-list">
          <li>
            <span class="hours-day">Pon – Czw</span>
            <span class="hours-time">12:00 – 22:00</span>
          </li>
          <li>
            <span class="hours-day">Piątek</span>
            <span class="hours-time">12:00 – 23:00</span>
          </li>
          <li>
            <span class="hours-day">Sobota</span>
            <span class="hours-time">11:00 – 23:00</span>
          </li>
          <li class="hours-sunday">
            <span class="hours-day">Niedziela</span>
            <span class="hours-time">11:00 – 21:00</span>
          </li>
        </ul>
        <p class="hours-note">Kuchnia czynna do 30 min przed zamknięciem</p>
      </div>

      <!-- Col 4: Navigation -->
      <div class="info-col">
        <h3 class="col-heading">Odkryj nas</h3>
        <ul class="nav-list">
          <li><a href="#menu" @click.prevent="scrollTo('#menu')">Menu</a></li>
          <li><a href="#about" @click.prevent="scrollTo('#about')">O nas</a></li>
          <li><router-link to="/reservation">Rezerwacja stolika</router-link></li>
          <li><a href="#location" @click.prevent="scrollTo('#location')">Jak dojechać</a></li>
        </ul>
        <div class="social-row">
          <a href="https://www.facebook.com/profile.php?id=100088306341072" class="social-btn" aria-label="Facebook" target="_blank">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
            </svg>
          </a>
          <a href="https://www.instagram.com/szamma_mia_piaseczno" class="social-btn" aria-label="Instagram" target="_blank">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
            </svg>
          </a>
        </div>
      </div>

    </div>
  </section>
</template>

<script setup>
function scrollTo(hash) {
  const el = document.querySelector(hash)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.info {
  background: #141414;
  color: #ccc;

  font-family: 'Nocturne', serif;
}

.info-flag-rule {
  display: flex;
  height: 5px;
}

.rule-green  { flex: 1; background: var(--green); }
.rule-white  { flex: 1; background: rgba(255,255,255,0.25); }
.rule-red    { flex: 1; background: var(--red); }

.info-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 4rem 5% 3.5rem;
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr 1fr;
  gap: 3rem;
}

/* ── Col 1: Brand ── */
.info-col-brand {
  padding-right: 1.5rem;
  border-right: 1px solid rgba(255,255,255,0.07);
}

.brand-name {
  font-size: 1.9rem;
  font-weight: 800;
  color: var(--white);
  letter-spacing: -0.01em;
  margin-bottom: 0.4rem;
  font-style: italic;
}

.brand-tagline {
  font-size: 0.82rem;
  color: var(--green);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  line-height: 1.5;
  margin-bottom: 1.1rem;
}

.brand-desc {
  font-size: 0.88rem;
  color: #888;
  line-height: 1.75;
}

/* ── Column headings ── */
.col-heading {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--white);
  margin-bottom: 1.25rem;
  padding-bottom: 0.65rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* ── Contact list ── */
.info-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.info-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  font-size: 0.88rem;
  line-height: 1.5;
}

.info-icon {
  color: var(--green);
  flex-shrink: 0;
  margin-top: 1px;
}

.info-list a {
  color: #ccc;
  text-decoration: none;
  transition: color 0.2s;
}

.info-list a:hover {
  color: var(--white);
}

/* ── Hours ── */
.hours-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.hours-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  gap: 0.5rem;
}

.hours-day {
  color: #999;
}

.hours-time {
  color: var(--white);
  font-weight: 600;
  white-space: nowrap;
}

.hours-sunday .hours-day,
.hours-sunday .hours-time {
  color: rgba(255,255,255,0.45);
}

.hours-note {
  font-size: 0.75rem;
  color: #555;
  margin-top: 1rem;
  font-style: italic;
  line-height: 1.5;
}

/* ── Nav list ── */
.nav-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-bottom: 1.75rem;
}

.nav-list a {
  font-size: 0.88rem;
  color: #ccc;
  text-decoration: none;
  transition: color 0.2s, padding-left 0.2s;
  display: inline-block;
}

.nav-list a:hover {
  color: var(--white);
  padding-left: 4px;
}

/* ── Social ── */
.social-row {
  display: flex;
  gap: 0.6rem;
}

.social-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  text-decoration: none;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
}

.social-btn:hover {
  background: var(--green);
  border-color: var(--green);
  color: var(--white);
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .info-inner {
    grid-template-columns: 1fr 1fr;
    gap: 2.5rem;
  }

  .info-col-brand {
    border-right: none;
    padding-right: 0;
    grid-column: 1 / -1;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    padding-bottom: 2rem;
  }
}

@media (max-width: 560px) {
  .info-inner {
    grid-template-columns: 1fr;
    padding: 3rem 5% 2.5rem;
    gap: 2rem;
  }
}
</style>
