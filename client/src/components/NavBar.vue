<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCart } from '@/composables/useCart'
import { useAuth } from '@/composables/useAuth'

const emit = defineEmits(['open-cart'])
const router = useRouter()
const route = useRoute()
const { itemCount } = useCart()
const { isAuthenticated, user, logout } = useAuth()

const showPhoneDialog = ref(false)
const showUserMenu = ref(false)
const mobileMenuOpen = ref(false)
const phoneNumber = ref('+48 123 456 789')
const phoneHref = ref('tel:+48123456789')

onMounted(async () => {
  try {
    const res = await fetch('/api/site-config')
    if (res.ok) {
      const data = await res.json()
      if (data.phone) {
        phoneNumber.value = data.phone
        phoneHref.value = 'tel:' + data.phone.replace(/\s/g, '')
      }
    }
  } catch {
    // keep fallback
  }
})

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function handleLogout() {
  logout()
  showUserMenu.value = false
  closeMobileMenu()
  router.push('/')
}

function handleOrder() {
  closeMobileMenu()
  if (itemCount.value === 0) {
    showPhoneDialog.value = true
  } else {
    router.push('/cart-summary')
  }
}

function navigateHash(hash) {
  closeMobileMenu()
  if (route.path === '/') {
    const el = document.querySelector(hash)
    if (el) el.scrollIntoView({ behavior: 'smooth' })
  } else {
    router.push({ path: '/', hash })
  }
}

function goHome() {
  closeMobileMenu()
  if (route.path === '/') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    router.push('/')
  }
}

function openCartMobile() {
  closeMobileMenu()
  emit('open-cart')
}

// Close mobile menu on route change
watch(() => route.path, () => {
  closeMobileMenu()
})
</script>

<template>
  <nav :class="{ 'nav-menu-open': mobileMenuOpen }">
    <div class="logo">
      <!-- <a href="/" @click.prevent="goHome">Szamma <span>Mia</span></a> -->
      <img src="/src/assets/szamma-mia-logo.png" alt="Szamma Mia Logo" class="logo-img" @click.prevent="goHome" />
    </div>
    <ul class="nav-links">
      <li><a href="#about" @click.prevent="navigateHash('#about')">O nas</a></li>
      <li><a href="#menu" @click.prevent="navigateHash('#menu')">Menu</a></li>
      <li><router-link to="/reservation" @click="closeMobileMenu">Rezerwacja</router-link></li>
      <li><a href="#location" @click.prevent="navigateHash('#location')">Dojazd</a></li>
      <li><a href="#contact" @click.prevent="navigateHash('#contact')">Kontakt</a></li>
      <li v-if="!isAuthenticated">
        <router-link to="/login" class="nav-auth-link">Zaloguj się</router-link>
      </li>
      <li v-else class="user-menu-wrap">
        <button class="btn-user" @click="showUserMenu = !showUserMenu" aria-label="Konto">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </button>
        <Transition name="dropdown-fade">
          <div v-if="showUserMenu" class="user-dropdown" @click="showUserMenu = false">
            <span class="user-dropdown-name">{{ user?.first_name || 'Konto' }}</span>
            <router-link to="/account" class="user-dropdown-item">Moje konto</router-link>
            <button class="user-dropdown-item user-dropdown-logout" @click="handleLogout">Wyloguj się</button>
          </div>
        </Transition>
      </li>
      <li>
        <button class="btn-cart" @click="emit('open-cart')" aria-label="Koszyk">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
          </svg>
          <span v-if="itemCount > 0" class="cart-dot"></span>
        </button>
      </li>
      <li><button class="btn-order" @click="handleOrder">Zamów Teraz</button></li>
    </ul>

    <!-- Hamburger button (mobile only) -->
    <button class="btn-hamburger" @click="toggleMobileMenu" aria-label="Menu">
      <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="6" x2="21" y2="6"/>
        <line x1="3" y1="12" x2="21" y2="12"/>
        <line x1="3" y1="18" x2="21" y2="18"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
  </nav>

  <!-- Mobile menu overlay -->
  <Transition name="mobile-menu">
    <div v-if="mobileMenuOpen" class="mobile-menu">
      <a href="#about" class="mobile-menu-link" @click.prevent="navigateHash('#about')">O nas</a>
      <a href="#menu" class="mobile-menu-link" @click.prevent="navigateHash('#menu')">Menu</a>
      <router-link to="/reservation" class="mobile-menu-link" @click="closeMobileMenu">Rezerwacja</router-link>
      <a href="#location" class="mobile-menu-link" @click.prevent="navigateHash('#location')">Dojazd</a>
      <a href="#contact" class="mobile-menu-link" @click.prevent="navigateHash('#contact')">Kontakt</a>
      <template v-if="!isAuthenticated">
        <router-link to="/login" class="mobile-menu-link mobile-menu-auth" @click="closeMobileMenu">Zaloguj się</router-link>
      </template>
      <template v-else>
        <router-link to="/account" class="mobile-menu-link" @click="closeMobileMenu">Moje konto</router-link>
        <button class="mobile-menu-link mobile-menu-logout" @click="handleLogout">Wyloguj się</button>
      </template>
      <button class="mobile-menu-cart" @click="openCartMobile">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
        </svg>
        Koszyk
        <span v-if="itemCount > 0" class="mobile-cart-badge">{{ itemCount }}</span>
      </button>
      <button class="mobile-menu-order" @click="handleOrder">Zamów Teraz</button>
    </div>
  </Transition>

  <!-- Phone dialog for empty cart -->
  <Teleport to="body">
    <Transition name="phone-fade">
      <div v-if="showPhoneDialog" class="phone-backdrop" @click.self="showPhoneDialog = false">
        <div class="phone-dialog">
          <button class="phone-close" @click="showPhoneDialog = false">&times;</button>
          <h3 class="phone-title">Chcesz złożyć zamówienie telefonicznie?</h3>
          <p class="phone-number">{{ phoneNumber }}</p>
          <div class="phone-actions">
            <a :href="phoneHref" class="phone-btn-call">Zadzwoń</a>
            <button class="phone-btn-close" @click="showPhoneDialog = false">Zamknij</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
nav {
  position: fixed;
  top: 0;
  width: 100%;
  background: rgba(255,255,255,0.9);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;

  font-family: 'Nocturne', serif;
}
.nav-mobile {
  background: rgb(255,255,255);
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
}

.logo a {
  text-decoration: none;
  color: var(--green);
}

.logo-img {
  height: 40px;
  width: auto;
  display: block;
  cursor: pointer;
}

.logo span {
  color: var(--red);
}

.nav-links {
  display: flex;
  gap: 2rem;
  list-style: none;
  align-items: center;
}

.nav-links a {
  text-decoration: none;
  color: var(--dark);
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: var(--green);
}

.btn-order {
  background: var(--red);
  color: var(--white);
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.btn-order:hover {
  background: #b02530;
  transform: translateY(-2px);
}

.btn-cart {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--dark);
  padding: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
}

.btn-cart:hover {
  color: var(--green);
}

.cart-dot {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 9px;
  height: 9px;
  background: var(--green);
  border-radius: 50%;
  border: 2px solid var(--white);
}

/* Auth nav link */
.nav-auth-link {
  text-decoration: none;
  color: var(--green);
  font-weight: 600;
  font-size: 0.95rem;
  transition: opacity 0.2s;
}

.nav-auth-link:hover {
  opacity: 0.8;
}

/* User menu */
.user-menu-wrap {
  position: relative;
}

.btn-user {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--dark);
  padding: 0.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
}

.btn-user:hover {
  color: var(--green);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: var(--white);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  min-width: 180px;
  padding: 0.5rem 0;
  z-index: 1100;
  display: flex;
  flex-direction: column;
}

.user-dropdown-name {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--dark);
  border-bottom: 1px solid #eee;
}

.user-dropdown-item {
  display: block;
  padding: 0.6rem 1rem;
  font-size: 0.9rem;
  color: var(--dark);
  text-decoration: none;
  background: none;
  border: none;
  text-align: left;
  width: 100%;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.2s;
}

.user-dropdown-item:hover {
  background: var(--light-gray);
}

.user-dropdown-logout {
  color: var(--red);
  font-weight: 600;
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Phone dialog */
.phone-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phone-dialog {
  background: var(--white);
  border-radius: 12px;
  padding: 2rem;
  max-width: 380px;
  width: 90%;
  text-align: center;
  position: relative;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.phone-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.phone-close:hover {
  background: rgba(0, 0, 0, 0.08);
}

.phone-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 1rem;
}

.phone-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--green);
  margin-bottom: 1.5rem;
}

.phone-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.phone-btn-call {
  background: var(--green);
  color: var(--white);
  padding: 0.7rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.3s;
}

.phone-btn-call:hover {
  background: #007a3a;
}

.phone-btn-close {
  background: none;
  border: 1.5px solid #ccc;
  padding: 0.7rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  color: var(--dark);
  transition: border-color 0.3s;
}

.phone-btn-close:hover {
  border-color: var(--dark);
}

.phone-fade-enter-active,
.phone-fade-leave-active {
  transition: opacity 0.2s ease;
}

.phone-fade-enter-from,
.phone-fade-leave-to {
  opacity: 0;
}

/* Hamburger button — hidden on desktop */
.btn-hamburger {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--dark);
  padding: 0.4rem;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
}

.btn-hamburger:hover {
  color: var(--green);
}

/* Mobile menu — hidden on desktop */
.mobile-menu {
  display: none;
}

/* Mobile menu transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 768px) {
  nav.nav-menu-open {
    box-shadow: none;
    background: #fff;
  }

  .nav-links {
    display: none;
  }

  .btn-hamburger {
    display: flex;
  }

  .mobile-menu {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background: var(--white);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    z-index: 999;
    padding: 0.75rem 1.5rem 1.25rem;
    gap: 0.25rem;
  }

  .mobile-menu-link {
    display: flex;
    align-items: center;
    padding: 0.75rem 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--dark);
    text-decoration: none;
    border: none;
    background: none;
    cursor: pointer;
    font-family: inherit;
    border-radius: 6px;
    min-height: 44px;
    transition: background 0.2s;
  }

  .mobile-menu-link:hover {
    background: var(--light-gray);
  }

  .mobile-menu-auth {
    color: var(--green);
    font-weight: 600;
  }

  .mobile-menu-logout {
    color: var(--red);
    font-weight: 600;
    width: 100%;
    text-align: left;
  }

  .mobile-menu-cart {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 0.5rem;
    font-size: 1rem;
    font-weight: 500;
    color: var(--dark);
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    border-radius: 6px;
    min-height: 44px;
    transition: background 0.2s;
  }

  .mobile-menu-cart:hover {
    background: var(--light-gray);
  }

  .mobile-cart-badge {
    background: var(--green);
    color: var(--white);
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.1rem 0.45rem;
    border-radius: 10px;
    min-width: 1.2rem;
    text-align: center;
  }

  .mobile-menu-order {
    margin-top: 0.5rem;
    background: var(--red);
    color: var(--white);
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    min-height: 44px;
    transition: background 0.3s;
  }

  .mobile-menu-order:hover {
    background: #b02530;
  }
}
</style>
