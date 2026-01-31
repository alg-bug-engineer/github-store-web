<template>
  <div>
    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)] gap-6">
      <div class="skeleton h-80 rounded-2xl"></div>
      <div class="space-y-4">
        <div class="skeleton h-40 rounded-2xl"></div>
        <div class="skeleton h-64 rounded-2xl"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flash flash-error">
      <p class="font-medium">{{ error }}</p>
      <router-link to="/discover" class="text-accent-tertiary underline mt-2 inline-block">
        Back to Discover
      </router-link>
    </div>

    <!-- Content -->
    <div v-else-if="repository" class="grid grid-cols-1 lg:grid-cols-[320px_minmax(0,1fr)] gap-6">
      <!-- Left Column -->
      <aside class="space-y-6">
        <div class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <div class="flex items-start gap-4">
            <img
              :src="ownerAvatarUrl"
              :alt="repository.owner"
              class="w-16 h-16 rounded-2xl flex-shrink-0 bg-bg-tertiary object-cover"
              @error="handleAvatarError"
            />
            <div class="min-w-0">
              <h1 class="text-xl font-semibold text-text-primary truncate">{{ repository.name }}</h1>
              <p class="text-sm text-text-secondary truncate">{{ repository.full_name }}</p>
            </div>
          </div>

          <p class="mt-4 text-sm text-text-secondary">{{ repository.description }}</p>

          <div class="mt-4 flex flex-wrap gap-3 text-xs text-text-secondary">
            <span class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
              </svg>
              <span class="font-semibold text-text-primary">{{ formatNumber(repository.stars) }}</span> stars
            </span>
            <span class="flex items-center gap-1">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"></path>
              </svg>
              <span class="font-semibold text-text-primary">{{ repository.forks }}</span> forks
            </span>
            <span v-if="repository.language" class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full" :style="{ backgroundColor: languageColor(repository.language) }"></span>
              {{ repository.language }}
            </span>
          </div>

          <div class="mt-5 flex flex-col gap-2">
            <a
              v-if="latestAssets.length"
              :href="latestAssets[0].browser_download_url"
              class="btn-primary px-4 py-2 text-sm text-center"
            >
              Download Latest
            </a>
            <a
              v-if="repository.homepage"
              :href="repository.homepage"
              target="_blank"
              class="btn-secondary px-4 py-2 text-sm text-center"
            >
              Visit Website
            </a>
            <a
              :href="repository.html_url"
              target="_blank"
              class="btn-secondary px-4 py-2 text-sm text-center"
            >
              View on GitHub
            </a>
            <button
              v-if="isLoggedIn"
              @click="toggleFavorite"
              :class="['star-button w-full justify-center', isFavorited ? 'starred' : '']"
            >
              <svg class="w-4 h-4" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
              {{ isFavorited ? 'Starred' : 'Star' }}
            </button>
          </div>
        </div>

        <div class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <p class="text-xs uppercase tracking-widest text-text-tertiary">Install Commands</p>
          <div class="mt-3 flex flex-wrap gap-2">
            <button
              v-for="option in installOptions"
              :key="option.id"
              @click="selectedInstall = option.id"
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium border',
                selectedInstall === option.id
                  ? 'bg-accent-primary/10 text-accent-primary border-accent-primary/40'
                  : 'border-border-default text-text-secondary hover:text-text-primary'
              ]"
            >
              {{ option.label }}
            </button>
          </div>
          <div class="mt-3 rounded-lg border border-border-default bg-bg-tertiary px-3 py-2 font-mono text-xs text-text-secondary">
            {{ activeInstallCommand }}
          </div>
          <button
            class="mt-3 w-full px-3 py-2 text-xs font-medium border border-border-default rounded-md cursor-pointer hover:bg-bg-tertiary hover:text-text-primary transition-colors"
            @click="copyInstallCommand"
          >
            {{ copySuccess ? 'Copied!' : 'Copy Command' }}
          </button>
        </div>
      </aside>

      <!-- Right Column -->
      <section class="space-y-6">
        <div class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-text-primary">Overview</h2>
            <button v-if="!summary" @click="generateSummary" :disabled="summaryLoading" class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-2">
              <svg class="w-4 h-4" :class="{'animate-spin': summaryLoading}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ summaryLoading ? 'Generating...' : 'AI Summary' }}
            </button>
          </div>
          
          <div v-if="summary" class="mt-4 p-4 bg-bg-tertiary border-l-4 border-accent-primary text-text-secondary text-sm">
            <p class="font-mono">{{ summary }}</p>
          </div>
          <p v-else class="mt-3 text-sm text-text-secondary">
            {{ repository.description || 'This project does not have a description yet.' }}
          </p>

          <div v-if="summaryError" class="mt-3 text-xs text-red-500">{{ summaryError }}</div>

          <div v-if="repository.topics && repository.topics.length" class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="topic in repository.topics"
              :key="topic"
              class="topic-tag"
            >
              {{ topic }}
            </span>
          </div>
        </div>

        <div class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <h2 class="text-lg font-semibold text-text-primary">Screenshots</h2>
          <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              v-for="(image, index) in galleryImages"
              :key="index"
              class="h-32 rounded-xl border border-border-default bg-bg-tertiary bg-cover bg-center"
              :style="{ backgroundImage: `url(${image})` }"
            ></div>
          </div>
        </div>

        <div v-if="latestRelease" class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <h2 class="text-lg font-semibold text-text-primary">Latest Release</h2>
          <div class="mt-3 flex items-center gap-3 text-sm text-text-secondary">
            <span class="label label-green font-semibold">{{ latestRelease.tag_name }}</span>
            <span v-if="latestRelease.is_prerelease" class="label label-orange">Pre-release</span>
            <span>Released {{ formatDate(latestRelease.published_at) }}</span>
          </div>

          <!-- Platform Tabs -->
          <div v-if="latestAssets.length && platformTabs.length > 1" class="mt-4 flex flex-wrap gap-2">
            <button
              v-for="tab in platformTabs"
              :key="tab.id"
              @click="selectedPlatform = tab.id"
              :class="[
                'px-3 py-1.5 rounded-md text-xs font-medium border-2 cursor-pointer transition-all',
                selectedPlatform === tab.id
                  ? 'bg-accent-primary/15 text-accent-primary border-accent-primary font-semibold'
                  : 'border-transparent bg-bg-tertiary text-text-secondary hover:text-text-primary hover:border-border-default'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>

          <div v-if="filteredAssets.length" class="mt-4 space-y-2">
            <div
              v-for="asset in filteredAssets"
              :key="asset.id"
              class="flex items-center justify-between bg-bg-tertiary border border-border-default p-3 rounded-md"
            >
              <div class="flex items-center gap-3 min-w-0">
                <span class="text-lg">{{ getFileIcon(asset.file_type || asset.name) }}</span>
                <div class="min-w-0">
                  <p class="font-medium text-text-primary truncate">{{ asset.name }}</p>
                  <p class="text-xs text-text-secondary">
                    {{ formatBytes(asset.size) }}
                    <span v-if="asset.platform" class="ml-2 label label-gray">{{ asset.platform }}</span>
                  </p>
                </div>
              </div>
              <a
                :href="asset.browser_download_url"
                class="btn-primary px-3 py-1.5 text-xs"
              >
                Download
              </a>
            </div>
          </div>

          <div v-else-if="latestAssets.length && !filteredAssets.length" class="text-text-secondary text-sm italic mt-4">
            No assets available for this platform.
          </div>

          <div v-else class="text-text-secondary text-sm italic mt-4">
            No downloadable assets available for this release.
          </div>
        </div>

        <div v-if="releases.length > 1" class="bg-bg-secondary border border-border-default rounded-2xl p-6">
          <h2 class="text-lg font-semibold text-text-primary">Release History</h2>
          <div class="mt-4 divide-y divide-border-default">
            <div v-for="release in releases" :key="release.id" class="py-3 first:pt-0 last:pb-0">
              <div class="flex items-center gap-3">
                <span class="font-mono text-xs bg-bg-tertiary text-text-primary px-2 py-0.5 rounded border border-border-default">
                  {{ release.tag_name }}
                </span>
                <span v-if="release.is_prerelease" class="label label-orange text-xs">Pre-release</span>
                <span class="text-sm text-text-secondary">{{ formatDate(release.published_at) }}</span>
              </div>
              <p v-if="release.name && release.name !== release.tag_name" class="text-sm text-text-secondary mt-1">
                {{ release.name }}
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { repositoriesAPI, favoritesAPI } from '../services/api';
import { useAuth } from '../stores/auth';

const route = useRoute();
const owner = route.params.owner;
const repoName = route.params.repo;
const { isLoggedIn } = useAuth();

const loading = ref(true);
const error = ref(null);
const repository = ref(null);
const releases = ref([]);
const latestRelease = ref(null);
const latestAssets = ref([]);
const isFavorited = ref(false);
const selectedInstall = ref('brew');
const summary = ref('');
const summaryLoading = ref(false);
const summaryError = ref('');
const copySuccess = ref(false);
const selectedPlatform = ref('all');

const installOptions = computed(() => {
  const ownerName = repository.value?.owner || 'repo';
  const repo = repository.value?.name || 'app';
  return [
    { id: 'brew', label: 'Brew', command: `brew install ${repo}` },
    { id: 'winget', label: 'Winget', command: `winget install ${repo}` },
    { id: 'docker', label: 'Docker', command: `docker pull ghcr.io/${ownerName}/${repo}` },
  ];
});

const activeInstallCommand = computed(() => {
  return installOptions.value.find((opt) => opt.id === selectedInstall.value)?.command || '';
});

const platformTabs = computed(() => {
  const tabs = [{ id: 'all', label: 'All' }];
  const platforms = new Set();

  latestAssets.value.forEach(asset => {
    const name = asset.name?.toLowerCase() || '';
    if (name.includes('mac') || name.includes('darwin') || name.includes('.dmg') || name.includes('-osx')) {
      platforms.add('mac');
    }
    if (name.includes('win') || name.includes('.exe') || name.includes('.msi')) {
      platforms.add('windows');
    }
    if (name.includes('linux') || name.includes('.deb') || name.includes('.rpm') || name.includes('.appimage')) {
      platforms.add('linux');
    }
    if (name.includes('android') || name.includes('.apk') || name.includes('.aab')) {
      platforms.add('android');
    }
    if (name.includes('ios') || name.includes('.ipa') || name.includes('iphone') || name.includes('ipad')) {
      platforms.add('ios');
    }
  });

  if (platforms.has('mac')) tabs.push({ id: 'mac', label: 'macOS' });
  if (platforms.has('windows')) tabs.push({ id: 'windows', label: 'Windows' });
  if (platforms.has('linux')) tabs.push({ id: 'linux', label: 'Linux' });
  if (platforms.has('android')) tabs.push({ id: 'android', label: 'Android' });
  if (platforms.has('ios')) tabs.push({ id: 'ios', label: 'iOS' });

  return tabs;
});

const filteredAssets = computed(() => {
  if (selectedPlatform.value === 'all') return latestAssets.value;

  return latestAssets.value.filter(asset => {
    const name = asset.name?.toLowerCase() || '';
    switch (selectedPlatform.value) {
      case 'mac':
        return name.includes('mac') || name.includes('darwin') || name.includes('.dmg') || name.includes('-osx');
      case 'windows':
        return name.includes('win') || name.includes('.exe') || name.includes('.msi');
      case 'linux':
        return name.includes('linux') || name.includes('.deb') || name.includes('.rpm') || name.includes('.appimage');
      case 'android':
        return name.includes('android') || name.includes('.apk') || name.includes('.aab');
      case 'ios':
        return name.includes('ios') || name.includes('.ipa') || name.includes('iphone') || name.includes('ipad');
      default:
        return true;
    }
  });
});

const galleryImages = computed(() => {
  if (!repository.value) return [];
  const fullName = repository.value.full_name || `${repository.value.owner}/${repository.value.name}`;
  const ogImage = repository.value.social_preview_url || `https://opengraph.githubassets.com/1/${fullName}`;
  return [ogImage, ogImage, ogImage];
});

const ownerAvatarUrl = computed(() => {
  if (!repository.value) return 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
  if (repository.value.avatar_url) return repository.value.avatar_url;
  if (repository.value.owner_avatar_url) return repository.value.owner_avatar_url;
  if (repository.value.owner) return `https://github.com/${repository.value.owner}.png`;
  return 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
});

const handleAvatarError = (event) => {
  event.target.src = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
};

const fetchData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await repositoriesAPI.getDetail(owner, repoName);
    const data = response.data || response;

    repository.value = data.repository;
    releases.value = data.releases || [];
    latestRelease.value = data.latest_release;
    latestAssets.value = data.latest_assets || [];
    isFavorited.value = repository.value?.is_favorited || false;
  } catch (err) {
    console.error('Failed to fetch repository:', err);
    error.value = err.message || `Repository ${owner}/${repoName} not found`;
  }

  loading.value = false;
};

const toggleFavorite = async () => {
  if (!repository.value) return;

  try {
    if (isFavorited.value) {
      await favoritesAPI.remove(repository.value.id);
      isFavorited.value = false;
    } else {
      await favoritesAPI.add(repository.value.id);
      isFavorited.value = true;
    }
  } catch (err) {
    console.error('Failed to toggle favorite:', err);
  }
};

const generateSummary = async () => {
  if (!repository.value) return;
  summaryLoading.value = true;
  summaryError.value = '';
  try {
    const response = await repositoriesAPI.summarize(repository.value.id);
    summary.value = response.summary || response.data?.summary || 'AI summary could not be generated.';
  } catch (err) {
    console.error('Failed to generate AI summary:', err);
    summaryError.value = 'Failed to generate summary. The model may be overloaded.';
  } finally {
    summaryLoading.value = false;
  }
};

const copyInstallCommand = async () => {
  try {
    await navigator.clipboard.writeText(activeInstallCommand.value);
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy install command:', err);
  }
};

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'm';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num;
};

const formatBytes = (bytes) => {
  if (!bytes) return 'Unknown size';
  if (bytes >= 1073741824) return (bytes / 1073741824).toFixed(2) + ' GB';
  if (bytes >= 1048576) return (bytes / 1048576).toFixed(2) + ' MB';
  if (bytes >= 1024) return (bytes / 1024).toFixed(2) + ' KB';
  return bytes + ' B';
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

const getFileIcon = (fileType) => {
  const icons = {
    apk: 'apk',
    exe: 'win',
    msi: 'win',
    dmg: 'mac',
    pkg: 'mac',
    deb: 'linux',
    rpm: 'linux',
    appimage: 'linux',
    zip: 'zip',
    'tar.gz': 'zip',
  };

  if (typeof fileType === 'string') {
    const lowerType = fileType.toLowerCase();
    for (const [ext, icon] of Object.entries(icons)) {
      if (lowerType.includes(ext)) return icon;
    }
  }
  return 'file';
};

const languageColor = (lang) => {
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
  return languageColors[lang] || '#6e7681';
};

onMounted(fetchData);
</script>
