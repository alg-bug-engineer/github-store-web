<template>
  <div class="max-w-4xl mx-auto">
    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-40 rounded-md"></div>
      <div class="skeleton h-60 rounded-md"></div>
    </div>

    <!-- Content -->
    <div v-else-if="user">
      <!-- Profile Header -->
      <div class="bg-bg-secondary border border-border-default rounded-md p-6 mb-6">
        <div class="flex items-start gap-6">
          <img
            :src="user.avatar_url || defaultAvatar"
            :alt="user.nickname || 'User'"
            class="w-20 h-20 rounded-full border-2 border-border-default"
          />
          <div class="flex-1">
            <h1 class="text-2xl font-semibold text-text-primary">{{ user.nickname || 'User' }}</h1>
            <p class="text-text-secondary mt-1">{{ maskPhone(user.phone) }}</p>

            <div class="flex gap-4 mt-4 text-sm text-text-secondary">
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                </svg>
                <span class="font-semibold text-text-primary">{{ favorites.length }}</span> favorites
              </span>
            </div>
          </div>

          <button
            @click="handleLogout"
            class="btn-danger px-4 py-2 text-sm"
          >
            Sign out
          </button>
        </div>
      </div>

      <!-- Favorites Section -->
      <div class="bg-bg-secondary border border-border-default rounded-md">
        <div class="p-4 border-b border-border-default">
          <h2 class="text-lg font-semibold text-text-primary flex items-center gap-2">
            <svg class="w-5 h-5 text-color-warning-fg" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
            </svg>
            Starred Repositories
          </h2>
        </div>

        <div v-if="favoritesLoading" class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="i in 4" :key="i" class="skeleton h-28 rounded-md"></div>
          </div>
        </div>

        <div v-else-if="favorites.length" class="p-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="fav in favorites"
              :key="fav.id"
              class="border border-border-default rounded-md p-4 hover:border-accent-primary transition-colors"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <router-link
                    :to="`/repo/${fav.repository.owner}/${fav.repository.name}`"
                    class="text-accent-tertiary hover:underline font-semibold block truncate"
                  >
                    {{ fav.repository.full_name }}
                  </router-link>
                  <p class="text-text-secondary text-sm mt-1 line-clamp-2">
                    {{ fav.repository.description || 'No description' }}
                  </p>
                  <div class="flex items-center gap-3 mt-2 text-xs text-text-secondary">
                    <span v-if="fav.repository.language" class="flex items-center gap-1">
                      <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: languageColor(fav.repository.language) }"></span>
                      {{ fav.repository.language }}
                    </span>
                    <span class="flex items-center gap-1">
                      <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                      </svg>
                      {{ formatNumber(fav.repository.stars) }}
                    </span>
                  </div>
                </div>
                <button
                  @click="removeFavorite(fav.repository.id)"
                  class="text-text-secondary hover:text-color-danger-fg p-1"
                  title="Remove from favorites"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="p-8">
          <div class="blankslate">
            <div class="blankslate-icon">
              <svg class="w-10 h-10 mx-auto" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
              </svg>
            </div>
            <h3 class="blankslate-heading">No starred repositories</h3>
            <p class="blankslate-description">Star repositories to keep track of projects you're interested in.</p>
            <router-link to="/discover" class="btn-primary mt-4 inline-block px-4 py-2">
              Explore repositories
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Not logged in -->
    <div v-else class="blankslate">
      <div class="blankslate-icon">
        <svg class="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 16 16">
          <path d="M10.561 8.073a6.005 6.005 0 0 1 3.432 5.142.75.75 0 1 1-1.498.07 4.5 4.5 0 0 0-8.99 0 .75.75 0 0 1-1.498-.07 6.004 6.004 0 0 1 3.431-5.142 3.999 3.999 0 1 1 5.123 0ZM10.5 5a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z"></path>
        </svg>
      </div>
      <h3 class="blankslate-heading">Sign in to view your profile</h3>
      <p class="blankslate-description">Access your starred repositories and personalized recommendations.</p>
      <router-link to="/login" class="btn-primary mt-4 inline-block px-4 py-2">
        Sign in
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authAPI, favoritesAPI } from '../services/api';
import { useAuth } from '../stores/auth';

const user = ref(null);
const favorites = ref([]);
const loading = ref(true);
const favoritesLoading = ref(true);
const router = useRouter();
const { isLoggedIn, logout: authLogout } = useAuth();

const defaultAvatar = 'https://avatars.githubusercontent.com/u/0?v=4';

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

const maskPhone = (phone) => {
  if (!phone) return '';
  if (phone.length > 7) {
    return phone.slice(0, 3) + '****' + phone.slice(-4);
  }
  return phone;
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'm';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
};

const fetchUserProfile = async () => {
  loading.value = true;

  // Check if logged in
  if (!isLoggedIn.value) {
    loading.value = false;
    return;
  }

  try {
    const response = await authAPI.getProfile();
    const data = response.data || response;
    user.value = data;

    // Store user data locally
    localStorage.setItem('user', JSON.stringify(data));
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    // If token is invalid, clear it
    if (error.message?.includes('401') || error.message?.includes('unauthorized')) {
      authLogout();
    }
  } finally {
    loading.value = false;
  }
};

const fetchFavorites = async () => {
  favoritesLoading.value = true;

  try {
    const response = await favoritesAPI.list();
    const data = response.data || response;
    favorites.value = data.items || data || [];
  } catch (error) {
    console.error('Failed to fetch favorites:', error);
    favorites.value = [];
  } finally {
    favoritesLoading.value = false;
  }
};

const removeFavorite = async (repoId) => {
  try {
    await favoritesAPI.remove(repoId);
    favorites.value = favorites.value.filter(f => f.repository.id !== repoId);
  } catch (error) {
    console.error('Failed to remove favorite:', error);
  }
};

const handleLogout = () => {
  authLogout();
  router.push('/');
};

onMounted(async () => {
  await fetchUserProfile();
  if (user.value) {
    await fetchFavorites();
  }
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
