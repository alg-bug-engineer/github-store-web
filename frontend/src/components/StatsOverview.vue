<template>
  <div class="stats-overview grid grid-cols-2 md:grid-cols-4 gap-4 bg-bg-secondary p-4 rounded-lg border border-border-default">
    <div class="stat-item flex flex-col items-center justify-center p-3">
      <div class="text-3xl font-bold text-accent-primary mb-1">
        <StatsCounter :target="stats.repositories_count" />
      </div>
      <div class="text-sm text-text-secondary">Repositories</div>
    </div>
    <div class="stat-item flex flex-col items-center justify-center p-3">
      <div class="text-3xl font-bold text-accent-primary mb-1">
        <StatsCounter :target="stats.releases_count" />
      </div>
      <div class="text-sm text-text-secondary">Releases</div>
    </div>
    <div class="stat-item flex flex-col items-center justify-center p-3">
      <div class="text-3xl font-bold text-accent-primary mb-1">
        <StatsCounter :target="stats.total_downloads" />
      </div>
      <div class="text-sm text-text-secondary">Downloads</div>
    </div>
    <div class="stat-item flex flex-col items-center justify-center p-3">
      <div class="text-3xl font-bold text-accent-primary mb-1">
        <StatsCounter :target="stats.categories_count" />
      </div>
      <div class="text-sm text-text-secondary">Categories</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { repositoriesAPI } from '../services/api';
import StatsCounter from './StatsCounter.vue';

const stats = ref({
  repositories_count: 0,
  releases_count: 0,
  total_downloads: 0,
  categories_count: 0,
});

const fetchStats = async () => {
  try {
    const response = await repositoriesAPI.getStatsOverview();
    const data = response.data || response;
    stats.value = data;
  } catch (error) {
    console.error('Error fetching stats overview:', error);
  }
};

onMounted(fetchStats);
</script>

<style scoped>
/* Scoped styles mostly handled by Tailwind classes and theme variables */
</style>
