<template>
  <footer>
    <FlagAccent />
    <p>&copy; 2026 Szamma Mia. Wszystkie prawa zastrzeżone.</p>
  </footer>
</template>

<script setup>
import FlagAccent from './FlagAccent.vue'
</script>

<style scoped>
footer {
  background: var(--dark);
  color: var(--white);
  text-align: center;
  padding: 2rem;
}

footer :deep(.flag-accent) {
  justify-content: center;
  margin-bottom: 1rem;
}
</style>
