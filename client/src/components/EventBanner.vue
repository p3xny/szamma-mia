<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const banners = ref([])

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/event-banners')
    banners.value = data
  } catch {
    // silent — no banners shown
  }
})
</script>

<template>
  <section v-if="banners.length > 0" class="event-banners">
    <div class="flag-bar"></div>
    <a
      v-for="banner in banners"
      :key="banner.id"
      :href="banner.link_url || undefined"
      class="event-banner"
      :class="{ clickable: banner.link_url }"
    >
      <img :src="banner.image_url" :alt="banner.title" class="banner-img" />
      <div class="banner-overlay">
        <h2 class="banner-title">{{ banner.title }}</h2>
        <p v-if="banner.subtitle" class="banner-subtitle">{{ banner.subtitle }}</p>
      </div>
    </a>
  </section>
</template>

<style scoped>
.event-banners {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.flag-bar {
  height: 9px;
  background: linear-gradient(to right, var(--green) 0%, var(--green) 33%, var(--white) 33%, var(--white) 66%, var(--red) 66%, var(--red) 100%);
  flex-shrink: 0;
}

.event-banner {
  position: relative;
  display: block;
  width: 100%;
  height: 280px;
  overflow: hidden;
  text-decoration: none;
  color: var(--white);
}

.event-banner.clickable {
  cursor: pointer;
}

.event-banner.clickable:hover .banner-img {
  transform: scale(1.03);
}

.banner-img {
  width: 100%;
  height: 100%;
  /* object-fit: cover; */
  transition: transform 0.6s ease;
}

.banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(transparent 30%, rgba(0, 0, 0, 0.6) 100%);
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 2rem 3rem;
}

.banner-title {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.banner-subtitle {
  font-size: 1.1rem;
  margin: 0.35rem 0 0;
  opacity: 0.9;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .event-banner {
    height: 200px;
  }

  .banner-overlay {
    padding: 1.25rem 1.5rem;
  }

  .banner-title {
    font-size: 1.4rem;
  }

  .banner-subtitle {
    font-size: 0.95rem;
  }
}
</style>
