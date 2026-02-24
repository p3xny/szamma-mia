<template>
  <section id="location" class="location">
    <h2 class="section-title">Znajdź Nas</h2>
    <p class="section-subtitle">Odwiedź nas dla niezapomnianych doznań kulinarnych</p>
    <div class="map-container">
      <iframe
        src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2452.292310123521!2d21.025537176245173!3d52.07440847194769!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47192f508ccda599%3A0x6098b28055e3d738!2sSzamma%20mia!5e0!3m2!1sen!2spl!4v1769946708832!5m2!1sen!2spl"
        allowfullscreen="true"
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade"
      ></iframe>
    </div>
    <p class="address">Sierakowskiego 2, 05-500 Piaseczno, Polska</p>
  </section>
</template>

<style scoped>
.location {
  background: var(--white);
  padding: 4rem 5%;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--dark);
}

.section-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 3rem;
}

.map-container {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.map-container iframe {
  width: 100%;
  height: 400px;
  border: none;
}

.address {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}
</style>
