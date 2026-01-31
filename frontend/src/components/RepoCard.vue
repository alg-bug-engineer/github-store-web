<template>
  <div class="bg-bg-secondary border border-border-default rounded-lg p-4 hover:border-accent-primary transition-all duration-200 hover:shadow-lg hover:shadow-black/10">
    <div class="flex items-start gap-3">
      <!-- Developer Avatar with fallback -->
      <img
        :src="ownerAvatarUrl"
        :alt="repo.owner"
        class="w-10 h-10 rounded-lg flex-shrink-0 bg-bg-tertiary object-cover"
        @error="handleAvatarError"
      />
      <div class="flex-1 min-w-0">
        <router-link
          :to="`/repo/${repo.owner}/${repo.name}`"
          class="text-accent-tertiary hover:underline font-semibold text-base block truncate"
        >
          {{ repo.full_name }}
        </router-link>
        <p class="text-text-secondary text-sm mt-1 line-clamp-2">
          {{ repo.description || 'No description available' }}
        </p>
      </div>
    </div>

    <!-- Topics -->
    <div v-if="repo.topics && repo.topics.length" class="flex flex-wrap gap-1.5 mt-3">
      <span
        v-for="topic in repo.topics.slice(0, 4)"
        :key="topic"
        class="px-2 py-0.5 rounded-md text-xs font-medium bg-bg-tertiary text-text-secondary border border-border-default"
      >
        {{ topic }}
      </span>
      <span v-if="repo.topics.length > 4" class="text-text-tertiary text-xs leading-6">
        +{{ repo.topics.length - 4 }}
      </span>
    </div>

    <!-- Stats -->
    <div class="flex items-center gap-4 mt-3 text-xs text-text-secondary">
      <span v-if="repo.language" class="flex items-center gap-1">
        <span class="w-3 h-3 rounded-full" :style="{ backgroundColor: languageColor(repo.language) }"></span>
        {{ repo.language }}
      </span>

      <span class="flex items-center gap-1">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
        </svg>
        {{ formatNumber(repo.stars) }}
      </span>

      <span class="flex items-center gap-1">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
          <path d="M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"></path>
        </svg>
        {{ formatNumber(repo.forks) }}
      </span>

      <span v-if="repo.category" class="px-2 py-0.5 rounded-md text-xs font-medium bg-bg-tertiary text-text-secondary border border-border-default">
        {{ repo.category }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  repo: {
    type: Object,
    required: true
  }
});

// 计算属性：获取开发者头像 URL
const ownerAvatarUrl = computed(() => {
  // 优先使用 avatar_url 字段
  if (props.repo.avatar_url) {
    return props.repo.avatar_url;
  }
  // 如果有 owner_avatar_url 字段
  if (props.repo.owner_avatar_url) {
    return props.repo.owner_avatar_url;
  }
  // 如果有 owner 字段，构造 GitHub 头像 URL
  if (props.repo.owner) {
    return `https://github.com/${props.repo.owner}.png`;
  }
  // 最后使用默认头像
  return 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
});

// 处理头像加载失败
const handleAvatarError = (event) => {
  event.target.src = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'm';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k';
  }
  return num.toString();
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
  'Objective-C': '#438eff',
  Scala: '#c22d40',
  Elixir: '#6e4a7e',
};

const languageColor = (lang) => {
  return languageColors[lang] || '#6e7681';
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
