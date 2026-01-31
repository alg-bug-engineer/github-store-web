<template>
  <div class="space-y-10">
    <!-- Loading State -->
    <div v-if="loading" class="space-y-8">
      <div class="skeleton h-64 rounded-2xl"></div>
      <div v-for="i in 3" :key="i" class="space-y-4">
        <div class="skeleton h-6 w-40 rounded"></div>
        <div class="flex gap-4 overflow-hidden">
          <div v-for="j in 4" :key="j" class="skeleton h-40 w-64 rounded-2xl"></div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flash flash-error">
      <p class="font-medium">{{ error }}</p>
      <button @click="fetchData" class="mt-2 text-sm underline">Retry</button>
    </div>

    <!-- Content -->
    <div v-else class="space-y-12">
      <!-- Hero Banner -->
      <section v-if="heroRepo" class="hero-banner relative overflow-hidden rounded-3xl border border-border-default bg-bg-secondary">
        <div
          class="absolute inset-0 bg-cover bg-center opacity-50 blur-2xl scale-110"
          :style="heroBackdropStyle"
        ></div>
        <div class="absolute inset-0 bg-gradient-to-r from-bg-primary/95 via-bg-primary/85 to-bg-primary/50"></div>

        <div class="relative z-10 grid grid-cols-1 xl:grid-cols-[1.3fr_1fr] gap-10 px-8 py-10">
          <div class="flex flex-col gap-6">
            <div class="flex items-center gap-4">
              <img
                :src="heroAvatarUrl"
                :alt="heroRepo.owner"
                class="w-16 h-16 rounded-2xl bg-bg-tertiary object-cover"
                @error="handleHeroAvatarError"
              />
              <div>
                <p class="hero-label text-xs uppercase tracking-widest">Featured</p>
                <h1 class="hero-title text-3xl font-semibold">
                  {{ heroRepo.name }}
                </h1>
                <p class="hero-subtitle text-sm">{{ heroRepo.full_name }}</p>
              </div>
            </div>

            <p class="hero-description text-lg max-w-2xl">
              {{ heroRepo.description || 'A standout open-source app selected by our editors this week.' }}
            </p>

            <div class="hero-meta flex flex-wrap items-center gap-4 text-sm">
              <span class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: languageColor(heroRepo.language) }"></span>
                {{ heroRepo.language || 'Multi-language' }}
              </span>
              <span class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                </svg>
                {{ formatNumber(heroRepo.stars) }} stars
              </span>
              <span v-if="heroRepo.latest_version" class="hero-version px-2 py-1 rounded-full border border-border-default">
                {{ heroRepo.latest_version }}
              </span>
            </div>
          </div>

          <div class="flex flex-col justify-between gap-6">
            <div class="hero-card rounded-2xl border border-border-default p-6">
              <p class="hero-card-label text-xs uppercase tracking-widest">Why it stands out</p>
              <ul class="hero-card-list mt-3 space-y-2 text-sm">
                <li>- Curated for desktop-grade workflows.</li>
                <li>- Active releases with reliable packaging.</li>
                <li>- Built by a fast-moving open-source team.</li>
              </ul>
            </div>
            <div class="flex flex-wrap gap-3">
              <router-link
                :to="heroDetailLink"
                class="btn-primary px-6 py-3 text-sm flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Install
              </router-link>
              <a
                :href="heroRepo.html_url"
                target="_blank"
                class="btn-secondary px-6 py-3 text-sm flex items-center gap-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                View Details
              </a>
            </div>
          </div>
        </div>
      </section>

      <!-- Swimlanes -->
      <template v-for="shelf in shelves" :key="shelf.id">
        <section v-if="shelf.items.length" class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-xl font-semibold text-text-primary">{{ shelf.title }}</h2>
              <p class="text-sm text-text-secondary">{{ shelf.subtitle }}</p>
            </div>
            <router-link
              to="/search"
              class="text-sm text-accent-tertiary hover:underline"
            >
              Explore all
            </router-link>
          </div>
          <div class="flex gap-4 overflow-x-auto pb-2">
            <AppCard
              v-for="repo in shelf.items"
              :key="repo.id"
              :repository="repo"
              variant="shelf"
            />
          </div>
        </section>
      </template>

      <!-- Personalized Recommendations -->
      <section v-if="isLoggedIn && personalizedRecommendations.length" class="space-y-4">
        <div>
          <h2 class="text-xl font-semibold text-text-primary">Personalized for You</h2>
          <p class="text-sm text-text-secondary">Based on your starred projects.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <AppCard
            v-for="repo in personalizedRecommendations"
            :key="repo.id"
            :repository="repo"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { discoverAPI } from '../services/api';
import AppCard from '../components/AppCard.vue';

const hotRecommendations = ref([]);
const newDiscoveries = ref([]);
const editorChoice = ref([]);
const personalizedRecommendations = ref([]);
const loading = ref(true);
const error = ref(null);

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access_token');
});

const combinedPool = computed(() => {
  return [...hotRecommendations.value, ...newDiscoveries.value, ...editorChoice.value];
});

const heroRepo = computed(() => {
  return editorChoice.value[0] || hotRecommendations.value[0] || newDiscoveries.value[0] || null;
});

const heroBackdropStyle = computed(() => {
  if (!heroRepo.value) return {};
  const fullName = heroRepo.value.full_name || `${heroRepo.value.owner}/${heroRepo.value.name}`;
  const imageUrl = heroRepo.value.social_preview_url || `https://opengraph.githubassets.com/1/${fullName}`;
  return { backgroundImage: `url(${imageUrl})` };
});

const heroAvatarUrl = computed(() => {
  if (!heroRepo.value) return 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
  return heroRepo.value.avatar_url || heroRepo.value.owner_avatar_url || `https://github.com/${heroRepo.value.owner}.png`;
});

const heroDetailLink = computed(() => {
  if (!heroRepo.value) return '/search';
  return `/repo/${heroRepo.value.owner}/${heroRepo.value.name}`;
});

const rustPicks = computed(() => {
  return combinedPool.value.filter((repo) => repo.language === 'Rust').slice(0, 8);
});

const shelves = computed(() => {
  return [
    {
      id: 'trending',
      title: 'Trending This Week',
      subtitle: 'Fast-rising open-source apps on GitHub.',
      items: hotRecommendations.value.slice(0, 10),
    },
    {
      id: 'editors',
      title: "Editor's Choice",
      subtitle: 'Curated picks from the GitHub Store team.',
      items: editorChoice.value.slice(0, 10),
    },
    {
      id: 'new',
      title: 'New & Noteworthy',
      subtitle: 'Fresh releases worth exploring.',
      items: newDiscoveries.value.slice(0, 10),
    },
    {
      id: 'rust',
      title: 'Written in Rust',
      subtitle: 'High-performance tools built in Rust.',
      items: rustPicks.value,
    },
  ];
});

const fetchData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await discoverAPI.getHome();
    const data = response.data || response;
    hotRecommendations.value = data.hot || [];
    newDiscoveries.value = data.new || [];
    editorChoice.value = data.editor_choice || [];
  } catch (err) {
    console.error('Error fetching home recommendations:', err);
    error.value = err.message || 'Failed to load recommendations. Please check if the backend is running.';
  }

  if (isLoggedIn.value) {
    try {
      const response = await discoverAPI.getPersonalized();
      const data = response.data || response;
      personalizedRecommendations.value = data || [];
    } catch (err) {
      console.error('Error fetching personalized recommendations:', err);
    }
  }

  loading.value = false;
};

const handleHeroAvatarError = (event) => {
  event.target.src = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
};

const languageColors = {
  JavaScript: '#f1e05a',
  TypeScript: '#3178c6',
  Python: '#3572A5',
  Java: '#b07219',
  Kotlin: '#A97BFF',
  Swift: '#F05138',
  Go: '#00ADD8',
  Rust: '#dea584',
  'C++': '#f34b7d',
  C: '#555555',
  'C#': '#178600',
  Ruby: '#701516',
  PHP: '#4F5D95',
  Shell: '#89e051',
  Vue: '#41b883',
  Dart: '#00B4AB',
};

const languageColor = (lang) => {
  return languageColors[lang] || '#6e7681';
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'm';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num;
};

onMounted(fetchData);
</script>

<style>
/* Light mode - default styles for hero banner */
.hero-label {
  color: var(--text-tertiary);
}

.hero-title {
  color: var(--text-primary);
}

.hero-subtitle {
  color: var(--text-secondary);
}

.hero-description {
  color: var(--text-secondary);
}

.hero-meta {
  color: var(--text-secondary);
}

.hero-version {
  background-color: var(--bg-tertiary);
}

.hero-card {
  background-color: var(--bg-secondary);
}

.hero-card-label {
  color: var(--text-tertiary);
}

.hero-card-list {
  color: var(--text-secondary);
}

/* Dark mode - white text for better contrast */
[data-theme="dark"] .hero-label {
  color: rgba(255, 255, 255, 0.6);
}

[data-theme="dark"] .hero-title {
  color: #ffffff;
}

[data-theme="dark"] .hero-subtitle {
  color: rgba(255, 255, 255, 0.7);
}

[data-theme="dark"] .hero-description {
  color: rgba(255, 255, 255, 0.85);
}

[data-theme="dark"] .hero-meta {
  color: rgba(255, 255, 255, 0.8);
}

[data-theme="dark"] .hero-version {
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

[data-theme="dark"] .hero-card {
  background-color: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(8px);
}

[data-theme="dark"] .hero-card-label {
  color: rgba(255, 255, 255, 0.6);
}

[data-theme="dark"] .hero-card-list {
  color: rgba(255, 255, 255, 0.85);
}
</style>
