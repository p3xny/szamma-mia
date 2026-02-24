<script setup>
import { inject } from 'vue'
import HeroSection from '@/components/HeroSection.vue'
import AboutSection from '@/components/AboutSection.vue'
import EventBanner from '@/components/EventBanner.vue'
import MenuSection from '@/components/MenuSection.vue'
import LocationSection from '@/components/LocationSection.vue'
import InfoSection from '@/components/InfoSection.vue'
import FooterSection from '@/components/FooterSection.vue'

const openCart = inject('openCart')
</script>

<template>
  <HeroSection />
  <AboutSection />
  <EventBanner />
  <MenuSection @open-cart="openCart" />
  <LocationSection />
  <InfoSection />
  <FooterSection />
</template>
