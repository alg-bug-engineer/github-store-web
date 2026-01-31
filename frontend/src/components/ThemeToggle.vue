<template>
  <button @click="toggleTheme" class="theme-toggle">
    <IconMoon v-if="currentTheme === 'light'" class="w-6 h-6" />
    <IconSun v-else class="w-6 h-6" />
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import IconSun from './icons/IconSun.vue';
import IconMoon from './icons/IconMoon.vue';

const currentTheme = ref('light'); // Default theme

const toggleTheme = () => {
  const nextTheme = currentTheme.value === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', nextTheme);
  localStorage.setItem('theme', nextTheme);
  currentTheme.value = nextTheme;
};

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    currentTheme.value = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
  } else {
    // If no theme is saved, check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      currentTheme.value = 'dark';
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      currentTheme.value = 'light';
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
    }
  }
});
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px; /* Adjust size as needed */
  height: 40px; /* Adjust size as needed */
  border-radius: 50%; /* Make it circular */
  background-color: var(--bg-tertiary); /* Use theme variable */
  color: var(--text-primary); /* Use theme variable */
  border: 1px solid var(--border-default);
  cursor: pointer;
  transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out, border-color 0.2s ease-in-out, transform 0.2s ease-in-out;
  padding: 0;
}

.theme-toggle:hover {
  background-color: var(--bg-secondary);
  border-color: var(--accent-primary);
  transform: scale(1.05);
}

.theme-toggle svg {
  transition: transform 0.2s ease-in-out;
}
</style>
