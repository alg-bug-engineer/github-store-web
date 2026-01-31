<template>
  <div class="space-y-6">
    <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-text-primary">Browse Apps</h1>
        <p class="text-sm text-text-secondary">Find open-source software across platforms and topics.</p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="selectedSort"
          class="px-3 py-2 text-sm bg-bg-secondary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
        >
          <option value="stars">Trending</option>
          <option value="updated">Recently Updated</option>
          <option value="created">Newest</option>
          <option value="downloads">Most Downloads</option>
        </select>
        <button @click="applyFilters" class="btn-primary px-4 py-2">Apply</button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)] gap-6">
      <!-- Filters -->
      <aside class="space-y-6 bg-bg-secondary border border-border-default rounded-2xl p-5 lg:sticky lg:top-24 h-fit">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-text-primary">Filters</h2>
          <button @click="clearFilters" class="text-xs text-text-tertiary hover:text-text-primary">Reset</button>
        </div>

        <div class="space-y-3">
          <p class="text-xs uppercase tracking-widest text-text-tertiary">Platform</p>
          <div class="space-y-2">
            <label v-for="option in platformOptions" :key="option.value" class="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                :value="option.value"
                v-model="selectedPlatforms"
                class="h-4 w-4 rounded border-border-default bg-bg-tertiary text-accent-primary focus:ring-accent-tertiary"
              />
              <span>{{ option.label }}</span>
            </label>
          </div>
        </div>

        <div class="space-y-3">
          <p class="text-xs uppercase tracking-widest text-text-tertiary">Topics</p>
          <div class="space-y-2">
            <label v-for="option in topicOptions" :key="option.topic" class="flex items-center justify-between text-sm">
               <span class="flex items-center gap-2">
                <input
                  type="checkbox"
                  :value="option.topic"
                  v-model="selectedTopics"
                  class="h-4 w-4 rounded border-border-default bg-bg-tertiary text-accent-primary focus:ring-accent-tertiary"
                />
                {{ option.topic }}
              </span>
              <span class="text-xs text-text-tertiary">{{ option.count }}</span>
            </label>
          </div>
        </div>
      </aside>

      <!-- Results -->
      <section class="space-y-4">
        <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div class="relative flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search for applications, tools, extensions..."
              class="w-full px-4 py-3 text-sm bg-bg-secondary text-text-primary placeholder-text-secondary border border-border-default rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
              @keyup.enter="applyFilters"
            />
            <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div class="text-sm text-text-secondary">
            <span v-if="total">{{ total }} results</span>
          </div>
        </div>

        <div v-if="activeFilters.length" class="flex flex-wrap gap-2 text-xs">
          <button
            v-for="filter in activeFilters"
            :key="filter.key"
            class="flex items-center gap-2 rounded-full border border-border-default bg-bg-tertiary px-3 py-1 text-text-secondary hover:text-text-primary"
            @click="removeFilter(filter)"
          >
            {{ filter.label }}
            <span class="text-text-tertiary">x</span>
          </button>
        </div>

        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
          <div v-for="i in 8" :key="i" class="skeleton h-40 rounded-2xl"></div>
        </div>

        <div v-else>
          <div v-if="results.length" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4">
            <AppCard v-for="repo in results" :key="repo.id" :repository="repo" />
          </div>

          <div v-else class="blankslate">
            <div class="blankslate-icon">
              <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 class="blankslate-heading">No results found</h3>
            <p class="blankslate-description">Try adjusting your search query or filters.</p>
          </div>

          <div v-if="totalPages > 1" class="flex justify-center gap-1 mt-8">
            <button
              @click="goToPage(page - 1)"
              :disabled="page === 1"
              class="px-3 py-1.5 text-sm border border-border-default rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-bg-tertiary transition-colors"
            >
              Previous
            </button>

            <button
              v-for="p in visiblePages"
              :key="p"
              @click="goToPage(p)"
              :class="[
                'px-3 py-1.5 text-sm border rounded-md transition-colors',
                p === page
                  ? 'bg-accent-primary text-white border-accent-primary'
                  : 'border-border-default hover:bg-bg-tertiary'
              ]"
            >
              {{ p }}
            </button>

            <button
              @click="goToPage(page + 1)"
              :disabled="page === totalPages"
              class="px-3 py-1.5 text-sm border border-border-default rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-bg-tertiary transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { repositoriesAPI } from '../services/api';
import AppCard from '../components/AppCard.vue';

const route = useRoute();
const router = useRouter();

const searchQuery = ref('');
const selectedPlatforms = ref([]);
const selectedTopics = ref([]);
const selectedSort = ref('stars');
const viewMode = ref('apps');
const results = ref([]);
const loading = ref(false);
const page = ref(1);
const perPage = ref(20);
const total = ref(0);

const platformOptions = [
  { label: 'Windows', value: 'windows' },
  { label: 'macOS', value: 'mac' },
  { label: 'Linux', value: 'linux' },
  { label: 'Android', value: 'android' },
];

const topicOptions = ref([]);

const totalPages = computed(() => Math.ceil(total.value / perPage.value));

const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, page.value - 2);
  const end = Math.min(totalPages.value, page.value + 2);
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  return pages;
});

const activeFilters = computed(() => {
  const filters = [];
  selectedPlatforms.value.forEach((value) => {
    const label = platformOptions.find((opt) => opt.value === value)?.label || value;
    filters.push({ key: `platform-${value}`, type: 'platform', value, label });
  });
  selectedTopics.value.forEach((value) => {
    filters.push({ key: `topic-${value}`, type: 'topic', value, label: value });
  });
  return filters;
});

const parseQueryList = (value) => {
  if (!value) return [];
  if (Array.isArray(value)) return value;
  return value.split(',').map((item) => item.trim()).filter(Boolean);
};

const buildQuery = () => ({
  q: searchQuery.value || undefined,
  platform: selectedPlatforms.value.length ? selectedPlatforms.value.join(',') : undefined,
  topics: selectedTopics.value.length ? selectedTopics.value.join(',') : undefined, // Changed from category
  sort: selectedSort.value !== 'stars' ? selectedSort.value : undefined,
  view: viewMode.value !== 'apps' ? viewMode.value : undefined,
  page: page.value !== 1 ? page.value : undefined,
});

const applyFilters = () => {
  page.value = 1;
  router.push({ path: '/search', query: buildQuery() });
};

const clearFilters = () => {
  selectedPlatforms.value = [];
  selectedTopics.value = [];
  selectedSort.value = 'stars';
  searchQuery.value = '';
  page.value = 1;
  router.push({ path: '/search', query: { view: viewMode.value !== 'apps' ? viewMode.value : undefined } });
};

const removeFilter = (filter) => {
  if (filter.type === 'platform') {
    selectedPlatforms.value = selectedPlatforms.value.filter((item) => item !== filter.value);
  } else if (filter.type === 'topic') {
    selectedTopics.value = selectedTopics.value.filter((item) => item !== filter.value);
  }
  applyFilters();
};

const goToPage = (newPage) => {
  if (newPage < 1 || newPage > totalPages.value) return;
  page.value = newPage;
  router.push({ path: '/search', query: buildQuery() });
};

const fetchResults = async () => {
  loading.value = true;
  try {
    const response = await repositoriesAPI.search({
      q: searchQuery.value,
      view: viewMode.value,
      platform: selectedPlatforms.value.length ? selectedPlatforms.value.join(',') : undefined,
      topics: selectedTopics.value.length ? selectedTopics.value.join(',') : undefined, // Changed from category
      sort: selectedSort.value,
      page: page.value,
      per_page: perPage.value,
    });
    const data = response.data || response;
    results.value = data.items || [];
    total.value = data.total || 0;
  } catch (error) {
    console.error('Search failed:', error);
    results.value = [];
    total.value = 0;
  }
  loading.value = false;
};

const fetchTopics = async () => {
  try {
    const response = await repositoriesAPI.getTopics({ limit: 50 });
    topicOptions.value = response.data || response;
  } catch (error) {
    console.error('Failed to fetch topics:', error);
  }
};

const syncFromQuery = (query) => {
  searchQuery.value = query.q || '';
  selectedPlatforms.value = parseQueryList(query.platform);
  selectedTopics.value = parseQueryList(query.topics); // Changed from category
  selectedSort.value = query.sort || 'stars';
  viewMode.value = query.view || 'apps';
  page.value = query.page ? Number(query.page) : 1;
};

onMounted(() => {
  syncFromQuery(route.query);
  fetchResults();
  fetchTopics();
});

watch(
  () => route.query,
  (newQuery, oldQuery) => {
    syncFromQuery(newQuery);
    if (JSON.stringify(newQuery) !== JSON.stringify(oldQuery)) {
      fetchResults();
    }
  },
  { deep: true }
);
</script>
