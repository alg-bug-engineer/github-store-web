<template>
  <div
    :class="[
      'group relative rounded-2xl border border-border-default bg-bg-secondary/80 p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-accent-primary/50 hover:shadow-lg hover:shadow-black/15 cursor-pointer',
      isShelf ? 'w-64 shrink-0' : 'w-full'
    ]"
    @click="goToDetail"
  >
    <div class="flex items-start gap-3">
      <img
        :src="ownerAvatarUrl"
        :alt="repository.owner"
        class="w-12 h-12 rounded-xl flex-shrink-0 bg-bg-tertiary object-cover"
        @error="handleAvatarError"
        @click.stop
      />
      <div class="min-w-0 flex-1">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <h3 class="text-base font-semibold text-text-primary truncate">
              {{ repository.name }}
            </h3>
            <p class="text-xs text-text-secondary truncate">
              {{ repository.full_name || repository.owner }}
            </p>
          </div>
          <div class="flex items-center gap-1 text-xs text-text-secondary">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
            </svg>
            <span class="font-medium text-text-primary">{{ formatNumber(repository.stars) }}</span>
          </div>
        </div>
        <p class="mt-2 text-sm text-text-primary/70 line-clamp-2" :title="repository.description">
          {{ repository.description || 'No description provided.' }}
        </p>
      </div>
    </div>

    <div class="mt-4 flex flex-wrap items-center gap-2">
      <span
        v-if="repository.language"
        class="inline-flex items-center gap-1.5 rounded-full border border-border-default bg-bg-tertiary px-2.5 py-1 text-xs text-text-secondary"
      >
        <span class="h-2 w-2 rounded-full" :style="{ backgroundColor: getLanguageColor(repository.language) }"></span>
        {{ repository.language }}
      </span>
      <span
        v-for="topic in visibleTopics"
        :key="topic"
        class="rounded-full border border-border-default bg-bg-tertiary px-2.5 py-1 text-xs text-text-secondary"
      >
        {{ topic }}
      </span>
    </div>

    <div class="mt-4 flex items-center justify-between text-xs text-text-secondary">
      <span v-if="repository.latest_version" class="px-2 py-1 rounded-md bg-bg-tertiary border border-border-default text-text-primary/80">
        {{ repository.latest_version }}
      </span>
      <span v-else class="px-2 py-1 rounded-md bg-bg-tertiary border border-border-default text-text-primary/80">Open Source</span>
      <span v-if="lastUpdated" class="capitalize">{{ lastUpdated }}</span>
    </div>

    <div class="mt-4 flex items-center gap-2 lg:hidden">
      <button
        class="flex-1 px-3 py-2 text-xs font-medium bg-accent-secondary text-white rounded-lg"
        @click.stop="copyInstallCommand"
      >
        Copy Install
      </button>
      <button
        class="flex-1 px-3 py-2 text-xs font-medium border border-border-default rounded-lg"
        @click.stop="goToDetail"
      >
        Details
      </button>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  repository: {
    type: Object,
    required: true,
  },
  variant: {
    type: String,
    default: 'grid',
  },
});

const router = useRouter();

const isShelf = computed(() => props.variant === 'shelf');

const visibleTopics = computed(() => {
  if (!props.repository.topics || !props.repository.topics.length) return [];
  return props.repository.topics.slice(0, 3);
});

const timeAgo = (date) => {
  if (!date) return null;
  const now = new Date();
  const past = new Date(date);
  const diffInSeconds = Math.floor((now - past) / 1000);

  const units = [
    { name: 'year', seconds: 31536000 },
    { name: 'month', seconds: 2592000 },
    { name: 'week', seconds: 604800 },
    { name: 'day', seconds: 86400 },
    { name: 'hour', seconds: 3600 },
    { name: 'minute', seconds: 60 },
  ];

  for (const unit of units) {
    const interval = Math.floor(diffInSeconds / unit.seconds);
    if (interval >= 1) {
      return `Updated ${interval} ${unit.name}${interval > 1 ? 's' : ''} ago`;
    }
  }
  return 'Updated just now';
};

const lastUpdated = computed(() => {
    const dateToShow = props.repository.latest_release_date || props.repository.github_updated_at;
    return timeAgo(dateToShow);
});

const ownerAvatarUrl = computed(() => {
  if (props.repository.avatar_url) return props.repository.avatar_url;
  if (props.repository.owner_avatar_url) return props.repository.owner_avatar_url;
  if (props.repository.owner) return `https://github.com/${props.repository.owner}.png`;
  return 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
});

const installCommand = computed(() => {
  const owner = props.repository.owner || props.repository.full_name?.split('/')[0] || 'repo';
  const name = props.repository.name || props.repository.full_name?.split('/')[1] || 'app';
  return `git clone https://github.com/${owner}/${name}.git`;
});

const handleAvatarError = (event) => {
  event.target.src = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
};

const copyInstallCommand = async () => {
  try {
    await navigator.clipboard.writeText(installCommand.value);
  } catch (error) {
    console.error('Failed to copy command:', error);
  }
};

const goToDetail = () => {
  if (props.repository.owner && props.repository.name) {
    router.push(`/repo/${props.repository.owner}/${props.repository.name}`);
  } else if (props.repository.full_name) {
    const [owner, name] = props.repository.full_name.split('/');
    router.push(`/repo/${owner}/${name}`);
  }
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
};

const formatCategory = (value) => {
  if (!value) return '';
  return value.replace(/_/g, ' ');
};

const getLanguageColor = (language) => {
  const colors = {
    JavaScript: '#f1e05a',
    Python: '#3572A5',
    Java: '#b07219',
    'C#': '#178600',
    TypeScript: '#2b7489',
    Go: '#00ADD8',
    Rust: '#dea584',
    Vue: '#41b883',
    HTML: '#e34c26',
    CSS: '#563d7c',
    PHP: '#4F5D95',
    Ruby: '#701516',
    C: '#555555',
    'C++': '#f34b7d',
    Shell: '#89e051',
    Kotlin: '#F18E33',
    Swift: '#ffac45',
    Dart: '#00B4AB',
  };
  return colors[language] || '#cccccc';
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
