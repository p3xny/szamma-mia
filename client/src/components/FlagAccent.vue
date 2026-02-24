<template>
  <div class="flag-accent">
    <div class="flag-green"></div>
    <div class="flag-white"></div>
    <div class="flag-red"></div>
  </div>
</template>

<style scoped>
.flag-accent {
  display: flex;
  gap: 0;
}

.flag-accent div {
  width: 40px;
  height: 6px;
}

.flag-green { background: var(--green); }
.flag-white { background: var(--white); }
.flag-red { background: var(--red); }
</style>
