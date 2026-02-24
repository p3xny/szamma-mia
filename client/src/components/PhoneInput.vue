<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  required:   { type: Boolean, default: false },
  placeholder:{ type: String, default: '600 123 456' },
})
const emit = defineEmits(['update:modelValue'])

const COUNTRIES = [
  { flag: '🇵🇱', dial: '+48',  name: 'Polska' },
  { flag: '🇩🇪', dial: '+49',  name: 'Niemcy' },
  { flag: '🇨🇿', dial: '+420', name: 'Czechy' },
  { flag: '🇸🇰', dial: '+421', name: 'Słowacja' },
  { flag: '🇺🇦', dial: '+380', name: 'Ukraina' },
  { flag: '🇧🇾', dial: '+375', name: 'Białoruś' },
  { flag: '🇬🇧', dial: '+44',  name: 'Wielka Brytania' },
  { flag: '🇫🇷', dial: '+33',  name: 'Francja' },
  { flag: '🇮🇹', dial: '+39',  name: 'Włochy' },
  { flag: '🇪🇸', dial: '+34',  name: 'Hiszpania' },
  { flag: '🇳🇱', dial: '+31',  name: 'Holandia' },
  { flag: '🇧🇪', dial: '+32',  name: 'Belgia' },
  { flag: '🇦🇹', dial: '+43',  name: 'Austria' },
  { flag: '🇨🇭', dial: '+41',  name: 'Szwajcaria' },
  { flag: '🇸🇪', dial: '+46',  name: 'Szwecja' },
  { flag: '🇳🇴', dial: '+47',  name: 'Norwegia' },
  { flag: '🇩🇰', dial: '+45',  name: 'Dania' },
  { flag: '🇫🇮', dial: '+358', name: 'Finlandia' },
  { flag: '🇷🇺', dial: '+7',   name: 'Rosja' },
  { flag: '🇺🇸', dial: '+1',   name: 'USA / Kanada' },
]

const selected = ref(COUNTRIES[0])
const localNumber = ref('')
const open = ref(false)
const focused = ref(false)
const wrapperRef = ref(null)

// ── Parse initial / external value ────────────────────────────────────────

function parse(val) {
  if (!val) { localNumber.value = ''; return }
  // Match longest dial code first (e.g. +420 before +42)
  const sorted = [...COUNTRIES].sort((a, b) => b.dial.length - a.dial.length)
  const match = sorted.find(c => val.startsWith(c.dial))
  if (match) {
    selected.value = match
    localNumber.value = val.slice(match.dial.length).trimStart()
  } else {
    localNumber.value = val
  }
}

parse(props.modelValue)

watch(() => props.modelValue, (val) => {
  const current = (selected.value.dial + ' ' + localNumber.value).trim()
  if (val !== current) parse(val)
})

// ── Emit ──────────────────────────────────────────────────────────────────

function emitFull() {
  const num = localNumber.value.trim()
  emit('update:modelValue', num ? `${selected.value.dial} ${num}` : '')
}

function pickCountry(c) {
  selected.value = c
  open.value = false
  focused.value = false
  emitFull()
}

// ── Click-outside ─────────────────────────────────────────────────────────

function onOutside(e) {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) {
    open.value = false
  }
}
onMounted(() => document.addEventListener('mousedown', onOutside))
onUnmounted(() => document.removeEventListener('mousedown', onOutside))
</script>

<template>
  <div class="pi-wrap" :class="{ 'pi-open': open, 'pi-focused': focused || open }" ref="wrapperRef">

    <!-- Country trigger -->
    <button
      type="button"
      class="pi-trigger"
      @click="open = !open"
      :aria-expanded="open"
      aria-label="Wybierz kierunkowy"
    >
      <span class="pi-flag">{{ selected.flag }}</span>
      <span class="pi-dial">{{ selected.dial }}</span>
      <svg class="pi-chevron" :class="{ rotated: open }" width="12" height="12"
        viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
        stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <!-- Divider -->
    <span class="pi-divider" aria-hidden="true"></span>

    <!-- Number input -->
    <input
      v-model="localNumber"
      type="tel"
      class="pi-input"
      :placeholder="placeholder"
      :required="required"
      autocomplete="tel-national"
      @input="emitFull"
      @focus="focused = true"
      @blur="focused = false"
    />

    <!-- Dropdown -->
    <Transition name="pi-drop">
      <ul v-if="open" class="pi-dropdown" role="listbox">
        <li
          v-for="c in COUNTRIES"
          :key="c.dial + c.name"
          class="pi-option"
          :class="{ active: c.dial === selected.dial && c.name === selected.name }"
          role="option"
          :aria-selected="c.dial === selected.dial && c.name === selected.name"
          @mousedown.prevent="pickCountry(c)"
        >
          <span class="pi-opt-flag">{{ c.flag }}</span>
          <span class="pi-opt-name">{{ c.name }}</span>
          <span class="pi-opt-dial">{{ c.dial }}</span>
        </li>
      </ul>
    </Transition>

  </div>
</template>

<style scoped>
/* ── Outer wrapper looks like a single input ─────────────────────────────── */
.pi-wrap {
  position: relative;
  display: flex;
  align-items: stretch;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  background: #fff;
  transition: border-color 0.2s;
}

.pi-focused {
  border-color: var(--green);
}

/* ── Country trigger ─────────────────────────────────────────────────────── */
.pi-trigger {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0.7rem 10px 0.7rem 12px;
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 6px 0 0 6px;
  flex-shrink: 0;
  transition: background 0.15s;
  color: var(--dark);
}

.pi-trigger:hover {
  background: rgba(0, 0, 0, 0.04);
}

.pi-flag {
  font-size: 1.2rem;
  line-height: 1;
}

.pi-dial {
  font-size: 0.88rem;
  font-weight: 600;
  color: #444;
  letter-spacing: 0.01em;
}

.pi-chevron {
  color: #999;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.pi-chevron.rotated {
  transform: rotate(180deg);
}

/* ── Divider ─────────────────────────────────────────────────────────────── */
.pi-divider {
  width: 1px;
  background: #ddd;
  flex-shrink: 0;
  align-self: stretch;
}

/* ── Number input ────────────────────────────────────────────────────────── */
.pi-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 0.7rem 0.75rem;
  font-size: 0.95rem;
  font-family: inherit;
  color: var(--dark);
  min-width: 0;
}

.pi-input::placeholder {
  color: #bbb;
}

/* ── Dropdown ────────────────────────────────────────────────────────────── */
.pi-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 200;
  background: #fff;
  border: 1.5px solid #e5e5e5;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  list-style: none;
  margin: 0;
  padding: 4px 0;
  min-width: 220px;
  max-height: 260px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.pi-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.12s;
}

.pi-option:hover,
.pi-option.active {
  background: rgba(0, 146, 70, 0.07);
}

.pi-option.active .pi-opt-name {
  color: var(--green);
  font-weight: 700;
}

.pi-opt-flag {
  font-size: 1.15rem;
  flex-shrink: 0;
}

.pi-opt-name {
  flex: 1;
  font-size: 0.88rem;
  color: var(--dark);
}

.pi-opt-dial {
  font-size: 0.82rem;
  color: #999;
  font-weight: 600;
  flex-shrink: 0;
}

/* ── Dropdown transition ─────────────────────────────────────────────────── */
.pi-drop-enter-active,
.pi-drop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.pi-drop-enter-from,
.pi-drop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
