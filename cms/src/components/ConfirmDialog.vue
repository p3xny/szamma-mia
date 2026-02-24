<script setup>
defineProps({
  title: { type: String, default: 'Potwierdź' },
  message: { type: String, required: true },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('cancel')">
    <div class="modal">
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <div class="modal-actions">
        <button class="btn btn-secondary" @click="emit('cancel')">Anuluj</button>
        <button class="btn btn-danger" @click="emit('confirm')">Usuń</button>
      </div>
    </div>
  </div>
</template>
