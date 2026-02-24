<script setup>
import { ref, onMounted } from 'vue'

const sectionRef = ref(null)
const textRef = ref(null)
const imageRef = ref(null)

onMounted(() => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        textRef.value?.classList.add('slide-in')
        imageRef.value?.classList.add('slide-in')
        observer.disconnect()
      }
    },
    { threshold: 0.1, rootMargin: '0px 0px -42% 0px' }
  )
  if (sectionRef.value) observer.observe(sectionRef.value)
})
</script>

<template>
  <section class="about" id="about" ref="sectionRef">
    <div class="about-inner">

      <div class="about-text" ref="textRef">
        <span class="about-label">Nasza historia</span>
        <h2 class="about-heading">Włoska kuchnia<br>w sercu Piaseczna</h2>
        <div class="about-accent"></div>
        <p class="about-paragraph">
          Szamma Mia to więcej niż restauracja — to miejsce, w którym włoska tradycja
          spotyka się z ciepłem domowej kuchni. Od lat serwujemy dania przygotowywane
          z najświeższych składników, sprowadzanych prosto z Włoch. Każdy talerz
          to hołd dla autentycznych smaków Toskanii, Sycylii i Kampanii.
        </p>
        <p class="about-paragraph">
          Ernest - nasz szef kuchni, zainspirowany latami spędzonymi w białostockich Choroszczy,
          dba o to, by każda wizyta u nas była prawdziwą podróżą kulinarną i nie tylko.
          Zapraszamy do stołu — czeka na Ciebie smak, którego nie zapomnisz.
        </p>
        <div class="about-stats">
          <div class="about-stat">
            <span class="stat-number">15+</span>
            <span class="stat-label">lat w Choroszczy</span>
          </div>
          <div class="about-stat">
            <span class="stat-number">40+</span>
            <span class="stat-label">dań w menu</span>
          </div>
          <div class="about-stat">
            <span class="stat-number">100%</span>
            <span class="stat-label">świeże składniki</span>
          </div>
        </div>
      </div>

      <div class="about-image-wrap" ref="imageRef">
        <div class="about-image-frame">
          <!-- <img
            src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=900&auto=format&fit=crop"
            alt="Wnętrze restauracji Szamma Mia"
            class="about-image"
          /> -->
          <img 
          src="https://scontent-waw2-1.cdninstagram.com/v/t39.30808-6/407285719_17902507523903229_8163332718714437713_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=109&ig_cache_key=MzI0ODI3MzIxMzI2NzIwNDU4Ng%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6InhwaWRzLjExMjR4MTQwNi5zZHIuQzMifQ%3D%3D&_nc_ohc=3qXZzLRLB6cQ7kNvwHzfQKn&_nc_oc=AdmfK2giOc2WYlOTGJD0hZUuLzAXo1shSoJVnEmJjYVjIz6LWiDBHevsneuNJda24xE&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-waw2-1.cdninstagram.com&_nc_gid=I51Wvk2p6CaqbwRw6kgM7A&oh=00_AfshcX-OoNBWes1QtTL0eZJDNHYa0ab7NtS3GSvVwYtTEg&oe=69A296C8"
          alt="Wnętrze restauracji Szamma Mia"
          class="about-image"
          >
        </div>
        <div class="about-image-badge">
          <span class="badge-line1">Autentyczna</span>
          <span class="badge-line2">Kuchnia Włoska</span>
        </div>
      </div>

    </div>
  </section>
</template>

<style scoped>
.about {
  background: var(--white);
  padding: 6rem 5%;

  font-family: 'Nocturne', serif;
}

.about-inner {
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5rem;
  align-items: center;
}

/* ── Text column ── */
.about-label {
  display: inline-block;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--green);
  margin-bottom: 1rem;
}

.about-heading {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--dark);
  margin-bottom: 1.25rem;
}

.about-accent {
  width: 52px;
  height: 4px;
  background: linear-gradient(to right, var(--green) 33%, var(--white) 33%, var(--white) 66%, var(--red) 66%);
  border-radius: 2px;
  margin-bottom: 1.75rem;
}

.about-paragraph {
  font-size: 1rem;
  color: #555;
  line-height: 1.8;
  margin-bottom: 1.1rem;
}

.about-stats {
  display: flex;
  gap: 2rem;
  margin-top: 2.25rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.about-stat {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--dark);
  line-height: 1;
}

.stat-label {
  font-size: 0.78rem;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── Image column ── */
.about-image-wrap {
  position: relative;
}

.about-image-frame {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.14);
  aspect-ratio: 4 / 5;
}

.about-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s ease;
}

.about-image-frame:hover .about-image {
  transform: scale(1.03);
}

.about-image-badge {
  position: absolute;
  bottom: -1.5rem;
  left: -1.5rem;
  background: var(--green);
  color: var(--white);
  padding: 1.1rem 1.4rem;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 146, 70, 0.35);
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.badge-line1 {
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.85;
  letter-spacing: 0.04em;
}

.badge-line2 {
  font-size: 1rem;
  font-weight: 800;
  letter-spacing: 0.01em;
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .about-inner {
    grid-template-columns: 1fr;
    gap: 3rem;
  }

  .about-image-wrap {
    order: -1;
  }

  .about-image-frame {
    aspect-ratio: 16 / 9;
  }

  .about-image-badge {
    bottom: -1.25rem;
    left: 1rem;
  }

  .about-heading {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .about {
    padding: 4rem 5%;
  }

  .about-stats {
    gap: 1.25rem;
  }

  .stat-number {
    font-size: 1.4rem;
  }
}

/* ── Slide-in animation (one-shot on first scroll into view) ── */
.about-text,
.about-image-wrap {
  opacity: 0;
  transition: opacity 0.7s ease, transform 0.7s ease;
}

.about-text {
  transform: translateX(-48px);
}

.about-image-wrap {
  transform: translateX(48px);
  transition-delay: 0.15s;
}

.about-text.slide-in,
.about-image-wrap.slide-in {
  opacity: 1;
  transform: translateX(0);
}
</style>
