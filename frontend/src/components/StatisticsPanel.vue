<template>
  <div class="statistics-panel flex items-center justify-center space-x-8">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="stats" class="flex items-center space-x-8">
      <div class="stat-item">
        <div class="stat-value">{{ stats.repositories_count }}</div>
        <div class="stat-label">Repositories</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.releases_count }}</div>
        <div class="stat-label">Releases</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ formatDownloads(stats.total_downloads) }}</div>
        <div class="stat-label">Downloads</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ stats.categories_count }}</div>
        <div class="stat-label">Categories</div>
      </div>
    </div>
  </div>
</template>
...
<style scoped>
.statistics-panel {
  padding: 0.5rem 1rem;
  background-color: transparent;
  border-radius: 8px;
  margin-bottom: 1rem;
}
.stat-item {
  text-align: center;
}
.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
}
.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}
</style>
