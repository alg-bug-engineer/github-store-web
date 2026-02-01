<template>
  <div class="space-y-4">
    <!-- Stats Bar -->
    <StatsBar @filter="handleViewFilter" @platform="handlePlatformFilter" @sort="handleSortFilter" />

    <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-semibold text-text-primary">Browse Apps</h1>
        <span v-if="selectedCategory" class="px-2 py-0.5 text-xs bg-accent-primary/10 text-accent-primary rounded-full">
          {{ getCategoryLabel(selectedCategory) }}
        </span>
      </div>
      <select
        v-model="selectedSort"
        class="px-3 py-1.5 text-sm bg-bg-secondary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
      >
        <option value="stars">Trending</option>
        <option value="updated">Recently Updated</option>
        <option value="created">Newest</option>
        <option value="downloads">Most Downloads</option>
      </select>
    </div>

    <div class="relative">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search for applications, tools, extensions..."
        class="w-full px-4 py-2.5 text-sm bg-bg-secondary text-text-primary placeholder-text-secondary border border-border-default rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
        @keyup.enter="applyFilters"
      />
      <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[260px_minmax(0,1fr)] gap-5">
      <!-- Filters -->
      <aside class="space-y-4 bg-bg-secondary border border-border-default rounded-xl p-4 lg:sticky lg:top-20 h-fit">
        <div class="flex items-center justify-between">
          <h2 class="text-sm font-semibold text-text-primary">Filters</h2>
          <button @click="clearFilters" class="text-xs text-text-tertiary hover:text-text-primary">Reset</button>
        </div>

        <div class="space-y-2">
          <p class="text-xs uppercase tracking-widest text-text-tertiary">Platform</p>
          <div class="space-y-1.5">
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

        <div class="space-y-2">
          <p class="text-xs uppercase tracking-widest text-text-tertiary">Topics</p>
          <div class="max-h-48 overflow-y-auto space-y-1.5">
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
        <!-- Active filters and result count -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm text-text-secondary">
            {{ total }} {{ total === 1 ? 'result' : 'results' }}
          </span>
          <template v-if="activeFilters.length">
            <span class="text-text-tertiary">|</span>
            <button
              v-for="filter in activeFilters"
              :key="filter.key"
              @click="removeFilter(filter)"
              class="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-bg-tertiary text-text-secondary rounded-full hover:bg-bg-secondary transition-colors"
            >
              {{ filter.label }}
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </template>
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
import { repositoriesAPI, categoriesAPI } from '../services/api';
import AppCard from '../components/AppCard.vue';
import StatsBar from '../components/StatsBar.vue';

const route = useRoute();
const router = useRouter();

const searchQuery = ref('');
const selectedPlatforms = ref([]);
const selectedTopics = ref([]);
const selectedCategory = ref('');
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

// 动态加载的分类标签映射
const categoryLabels = ref({});

const getCategoryLabel = (value) => categoryLabels.value[value] || value;

const topicOptions = ref([]);

// 加载分类配置
const loadCategoryLabels = async () => {
  try {
    const response = await categoriesAPI.getAll();
    const data = response.data || response;
    const labels = {};
    (data.categories || []).forEach(cat => {
      labels[cat.id] = cat.label;
    });
    categoryLabels.value = labels;
  } catch (error) {
    console.error('Failed to load category labels:', error);
    // 使用默认标签
    categoryLabels.value = {
      developer_tools: 'Dev Tools',
      productivity: 'Productivity',
      media: 'Media',
      utilities: 'System',
    };
  }
};

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
  if (selectedCategory.value) {
    filters.push({
      key: `category-${selectedCategory.value}`,
      type: 'category',
      value: selectedCategory.value,
      label: getCategoryLabel(selectedCategory.value)
    });
  }
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
  topics: selectedTopics.value.length ? selectedTopics.value.join(',') : undefined,
  category: selectedCategory.value || undefined,
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
  selectedCategory.value = '';
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
  } else if (filter.type === 'category') {
    selectedCategory.value = '';
  }
  applyFilters();
};

// StatsBar handlers
const handleViewFilter = (view) => {
  viewMode.value = view;
  applyFilters();
};

const handlePlatformFilter = (platform) => {
  if (!selectedPlatforms.value.includes(platform)) {
    selectedPlatforms.value = [platform];
  }
  applyFilters();
};

const handleSortFilter = (sort) => {
  selectedSort.value = sort;
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
      topics: selectedTopics.value.length ? selectedTopics.value.join(',') : undefined,
      category: selectedCategory.value || undefined,
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
  selectedTopics.value = parseQueryList(query.topics);
  selectedCategory.value = query.category || '';
  selectedSort.value = query.sort || 'stars';
  viewMode.value = query.view || 'apps';
  page.value = query.page ? Number(query.page) : 1;
};

onMounted(() => {
  loadCategoryLabels();
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

watch([selectedPlatforms, selectedTopics, selectedSort], () => {
  applyFilters();
}, { deep: true });

// Don't auto-apply when category changes from URL (handled by syncFromQuery)
</script>
