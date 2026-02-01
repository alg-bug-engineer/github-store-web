<template>
  <div class="space-y-8">
    <div>
      <h1 class="text-2xl font-semibold text-text-primary">Charts</h1>
      <p class="text-sm text-text-secondary">Desktop-grade rankings based on stars and momentum.</p>
    </div>

    <div v-if="loading" class="space-y-6">
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div v-for="i in 3" :key="i" class="skeleton h-48 rounded-2xl"></div>
      </div>
      <div class="skeleton h-64 rounded-2xl"></div>
    </div>

    <div v-else-if="error" class="flash flash-error">
      <p class="font-medium">{{ error }}</p>
      <button @click="fetchCharts" class="mt-2 text-sm underline">Retry</button>
    </div>

    <div v-else class="space-y-6">
      <!-- Top 3 -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <router-link
          v-for="(repo, index) in topThree"
          :key="repo.id"
          :to="`/repo/${repo.owner}/${repo.name}`"
          class="bg-bg-secondary border border-border-default rounded-2xl p-5 flex flex-col gap-4 hover:border-accent-tertiary hover:shadow-lg transition-all cursor-pointer group"
        >
          <div class="flex items-center justify-between text-xs text-text-tertiary">
            <span class="uppercase tracking-widest">Rank #{{ index + 1 }}</span>
            <span class="flex items-center gap-1 text-green-400">
              + {{ trendValue(repo) }}
            </span>
          </div>
          <div class="flex items-center gap-3">
            <img
              :src="repo.avatar_url || `https://github.com/${repo.owner}.png`"
              :alt="repo.owner"
              class="w-12 h-12 rounded-xl bg-bg-tertiary object-cover"
            />
            <div class="min-w-0">
              <h3 class="text-lg font-semibold text-text-primary truncate group-hover:text-accent-tertiary transition-colors">{{ repo.name }}</h3>
              <p class="text-sm text-text-secondary truncate">{{ repo.description }}</p>
            </div>
          </div>
          <div class="flex items-center justify-between text-xs text-text-secondary">
            <span>Stars {{ formatNumber(repo.stars) }}</span>
            <span class="capitalize">{{ repo.primary_category || repo.category || 'other' }}</span>
          </div>
          <div class="h-1 rounded-full bg-bg-tertiary">
            <div class="h-1 rounded-full bg-green-500" :style="{ width: trendWidth(repo) }"></div>
          </div>
          <span class="text-xs text-accent-tertiary group-hover:underline">View details →</span>
        </router-link>
      </div>

      <!-- Rankings Table -->
      <div class="bg-bg-secondary border border-border-default rounded-2xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-text-primary">Top 100</h2>
          <span class="text-xs text-text-tertiary">Updated with latest stars</span>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="text-left text-text-tertiary border-b border-border-default">
                <th class="py-2 pr-4">Rank</th>
                <th class="py-2 pr-4">App</th>
                <th class="py-2 pr-4">Category</th>
                <th class="py-2 pr-4">Stars</th>
                <th class="py-2 pr-4">Trend</th>
                <th class="py-2">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(repo, index) in restOfChart"
                :key="repo.id"
                class="border-b border-border-default last:border-b-0 hover:bg-bg-tertiary/50 cursor-pointer transition-colors"
                @click="$router.push(`/repo/${repo.owner}/${repo.name}`)"
              >
                <td class="py-3 pr-4 text-text-secondary">#{{ index + 4 }}</td>
                <td class="py-3 pr-4">
                  <div class="flex items-center gap-3">
                    <img
                      :src="repo.avatar_url || `https://github.com/${repo.owner}.png`"
                      :alt="repo.owner"
                      class="w-8 h-8 rounded-lg bg-bg-tertiary object-cover"
                    />
                    <div class="min-w-0">
                      <p class="font-medium text-text-primary truncate">{{ repo.name }}</p>
                      <p class="text-xs text-text-secondary truncate">{{ repo.full_name }}</p>
                    </div>
                  </div>
                </td>
                <td class="py-3 pr-4 text-text-secondary capitalize">{{ repo.primary_category || repo.category || 'other' }}</td>
                <td class="py-3 pr-4 text-text-secondary">{{ formatNumber(repo.stars) }}</td>
                <td class="py-3 pr-4">
                  <span class="inline-flex items-center gap-1 text-green-400">
                    + {{ trendValue(repo) }}
                  </span>
                </td>
                <td class="py-3">
                  <span class="text-xs text-accent-tertiary">View →</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { repositoriesAPI } from '../services/api';

const loading = ref(true);
const error = ref(null);
const repos = ref([]);

const topThree = computed(() => repos.value.slice(0, 3));
const restOfChart = computed(() => repos.value.slice(3));

const fetchCharts = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await repositoriesAPI.search({
      sort: 'stars',
      view: 'all',
      page: 1,
      per_page: 100,
    });
    const data = response.data || response;
    repos.value = data.items || [];
  } catch (err) {
    console.error('Failed to load charts:', err);
    error.value = err.message || 'Unable to load chart data.';
  }

  loading.value = false;
};

const trendValue = (repo) => {
  if (!repo) return 0;
  if (repo.total_downloads) return Math.max(1, Math.round(repo.total_downloads / 1000));
  return Math.max(1, Math.round(repo.stars / 1000));
};

const trendWidth = (repo) => {
  const value = trendValue(repo);
  const width = Math.min(100, value * 4);
  return `${width}%`;
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
};

onMounted(fetchCharts);
</script>
