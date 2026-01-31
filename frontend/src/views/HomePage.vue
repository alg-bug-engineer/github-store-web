<template>
  <div>
    <!-- Hero Section -->
    <div class="hero-section bg-gradient-to-br from-bg-secondary via-bg-primary to-bg-inset border border-border-default text-text-primary rounded-xl p-8 mb-8 relative overflow-hidden">
      <div class="w-full">
        <h1 class="text-3xl md:text-4xl font-bold mb-4">
          Discover Open Source Applications
        </h1>
        <p class="text-text-secondary text-lg mb-6">
          Browse, discover, and download applications directly from GitHub Releases.
          All open source, transparent, and free.
        </p>

        <!-- Search Form -->
        <div class="bg-bg-secondary/50 border border-border-default rounded-lg p-4">
          <div class="flex flex-col md:flex-row gap-3">
            <div class="flex-1">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search for applications..."
                class="w-full px-4 py-3 text-text-primary bg-bg-tertiary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent focus:bg-bg-secondary"
                @keyup.enter="goToSearch"
              />
            </div>

            <select
              v-model="selectedPlatformType"
              class="px-3 py-3 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
            >
              <option value="all">All Platforms</option>
              <option value="android">Android</option>
              <option value="windows">Windows</option>
              <option value="mac">macOS</option>
              <option value="linux">Linux</option>
              <option value="cli">CLI Tools</option>
              <option value="web">Web</option>
            </select>

            <select
              v-model="selectedLanguage"
              class="px-3 py-3 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
            >
              <option value="all">All Languages</option>
              <option value="Python">Python</option>
              <option value="JavaScript">JavaScript</option>
              <option value="TypeScript">TypeScript</option>
              <option value="Java">Java</option>
              <option value="C#">C#</option>
              <option value="C++">C++</option>
              <option value="Go">Go</option>
              <option value="Rust">Rust</option>
              <option value="PHP">PHP</option>
              <option value="Ruby">Ruby</option>
              <option value="Swift">Swift</option>
              <option value="Kotlin">Kotlin</option>
              <option value="Dart">Dart</option>
              <option value="Vue">Vue</option>
            </select>

            <select
              v-model="selectedSort"
              class="px-3 py-3 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
            >
              <option value="stars">Most Stars</option>
              <option value="updated">Recently Updated</option>
              <option value="created">Recently Created</option>
            </select>

            <button
              @click="goToSearch"
              class="btn-primary px-6 py-3 whitespace-nowrap"
            >
              <svg class="w-5 h-5 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Search
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <StatsOverview class="mb-8" />

    <!-- Categories -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-text-secondary" fill="currentColor" viewBox="0 0 16 16">
          <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5Zm8 0A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5Zm-8 8A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5Zm8 0A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5Z"></path>
        </svg>
        Browse by Category
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link
          v-for="category in categories"
          :key="category.id"
          :to="`/search?category=${category.id}`"
          class="bg-bg-secondary border border-border-default rounded-md p-4 hover:border-accent-primary transition-all duration-200 hover:shadow-md hover:shadow-black/10 dark:hover:shadow-black/20 group"
        >
          <div class="text-3xl mb-2">{{ category.icon }}</div>
          <h3 class="font-semibold text-text-primary group-hover:text-accent-tertiary">{{ category.name }}</h3>
          <p class="text-sm text-text-secondary">{{ category.description }}</p>
        </router-link>
      </div>
    </div>

    <!-- Hot Repositories -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-text-primary flex items-center gap-2">
          <svg class="w-5 h-5 text-color-danger-fg" fill="currentColor" viewBox="0 0 16 16">
            <path d="M7.998.002A7.998 7.998 0 0 0 0 8c0 2.246.925 4.276 2.415 5.732.253.254.6.25.853-.003l.266-.269a.6.6 0 0 0-.002-.848 5.997 5.997 0 0 1 3.72-10.598V2a1 1 0 0 1 1.5-.866l3.294 1.902a1 1 0 0 1 0 1.732L8.75 6.668A1 1 0 0 1 7.25 5.8V3.999a5 5 0 0 0-3.72 8.584c.2.2.206.526.006.726l-.266.269c-.253.253-.6.25-.853-.003A8 8 0 0 1 7.998.002Z"></path>
          </svg>
          Trending Repositories
        </h2>
        <router-link to="/discover" class="text-sm text-accent-tertiary hover:underline">
          View all
        </router-link>
      </div>

      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="i in 6" :key="i" class="skeleton h-32 rounded-md"></div>
      </div>

      <div v-else-if="hotRecommendations.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <AppCard v-for="repo in hotRecommendations" :key="repo.id" :repository="repo" />
      </div>

      <div v-else class="blankslate">
        <div class="blankslate-icon">
          <svg class="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 16 16">
            <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"></path>
          </svg>
        </div>
        <h3 class="blankslate-heading">No repositories yet</h3>
        <p class="blankslate-description">Sync some data to get started.</p>
      </div>
    </div>

    <!-- Features -->
    <div class="bg-bg-secondary border border-border-default rounded-md p-6 mb-8">
      <h2 class="text-xl font-semibold text-text-primary mb-6 text-center">Why GitHub Releases Store?</h2>
      <div class="grid md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="w-12 h-12 bg-label-green-bg rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-label-green-text" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Zm9.78-2.22-4.5 4.5a.75.75 0 0 1-1.06 0l-2-2a.75.75 0 1 1 1.06-1.06l1.47 1.47 3.97-3.97a.75.75 0 0 1 1.06 1.06Z"></path>
            </svg>
          </div>
          <h3 class="font-semibold text-text-primary mb-2">Open Source & Safe</h3>
          <p class="text-sm text-text-secondary">All applications are open source with transparent code you can review.</p>
        </div>
        <div class="text-center">
          <div class="w-12 h-12 bg-label-blue-bg rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-label-blue-text" fill="currentColor" viewBox="0 0 16 16">
              <path d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"></path>
              <path d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.749.749 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06l1.97 1.969Z"></path>
            </svg>
          </div>
          <h3 class="font-semibold text-text-primary mb-2">Direct Downloads</h3>
          <p class="text-sm text-text-secondary">Download apps directly from GitHub releases without any middleman.</p>
        </div>
        <div class="text-center">
          <div class="w-12 h-12 bg-label-purple-bg rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-6 h-6 text-label-purple-text" fill="currentColor" viewBox="0 0 16 16">
              <path d="M4.75 7a.75.75 0 0 0 0 1.5h4.5a.75.75 0 0 0 0-1.5h-4.5ZM5 4.75A.75.75 0 0 1 5.75 4h5.5a.75.75 0 0 1 0 1.5h-5.5A.75.75 0 0 1 5 4.75ZM6.75 10a.75.75 0 0 0 0 1.5h4.5a.75.75 0 0 0 0-1.5h-4.5Z"></path>
              <path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16H1.75A1.75 1.75 0 0 1 0 14.25Zm1.75-.25a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25V1.75a.25.25 0 0 0-.25-.25Z"></path>
            </svg>
          </div>
          <h3 class="font-semibold text-text-primary mb-2">AI Assistant</h3>
          <p class="text-sm text-text-secondary">Get personalized recommendations from our AI assistant.</p>
        </div>
      </div>
    </div>

    <!-- AI Chat -->
    <AIChat />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { discoverAPI } from '../services/api';
import StatsOverview from '../components/StatsOverview.vue';
import AppCard from '../components/AppCard.vue';
import AIChat from '../components/AIChat.vue';

const router = useRouter();
const searchQuery = ref('');
const selectedPlatformType = ref('all');
const selectedLanguage = ref('all');
const selectedSort = ref('stars');
const loading = ref(true);
const hotRecommendations = ref([]);

const categories = [
  { id: 'android', name: 'Android', icon: '📱', description: 'Mobile apps' },
  { id: 'windows', name: 'Windows', icon: '🪟', description: 'Windows apps' },
  { id: 'macos', name: 'macOS', icon: '🍎', description: 'Mac apps' },
  { id: 'linux', name: 'Linux', icon: '🐧', description: 'Linux apps' },
  { id: 'cli', name: 'CLI Tools', icon: '⌨️', description: 'Command line' },
  { id: 'web', name: 'Web', icon: '🌐', description: 'Web apps' },
  { id: 'python', name: 'Python', icon: '🐍', description: 'Python apps' },
  { id: 'javascript', name: 'JavaScript', icon: '📜', description: 'JS apps' },
];

const goToSearch = () => {
  router.push({
    path: '/search',
    query: {
      q: searchQuery.value || undefined,
      platform: selectedPlatformType.value !== 'all' ? selectedPlatformType.value : undefined,
      language: selectedLanguage.value !== 'all' ? selectedLanguage.value : undefined,
      sort: selectedSort.value !== 'stars' ? selectedSort.value : undefined,
    }
  });
};

const fetchHotRecommendations = async () => {
  loading.value = true;
  try {
    const response = await discoverAPI.getHome();
    const data = response.data || response;
    hotRecommendations.value = (data.hot || []).slice(0, 6);
  } catch (error) {
    console.error('Failed to fetch hot recommendations:', error);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchHotRecommendations);
</script>
