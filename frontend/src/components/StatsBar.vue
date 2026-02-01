<template>
  <div class="stats-bar overflow-x-auto scrollbar-hide">
    <div class="flex items-center gap-6 min-w-max px-1 py-2">
      <!-- Apps count -->
      <div class="stat-item" @click="$emit('filter', 'apps')">
        <div class="stat-icon apps">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatNumber(stats.total?.apps || 0) }}</span>
          <span class="stat-label">Apps</span>
        </div>
      </div>

      <!-- All repos count -->
      <div class="stat-item" @click="$emit('filter', 'all')">
        <div class="stat-icon all">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatNumber(stats.total?.all || 0) }}</span>
          <span class="stat-label">All</span>
        </div>
      </div>

      <!-- Divider -->
      <div class="h-8 w-px bg-border-default"></div>

      <!-- Downloads -->
      <div class="stat-item" @click="$emit('sort', 'downloads')">
        <div class="stat-icon downloads">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatNumber(stats.total?.downloads || 0) }}</span>
          <span class="stat-label">Downloads</span>
        </div>
      </div>

      <!-- Divider -->
      <div class="h-8 w-px bg-border-default"></div>

      <!-- Platform stats -->
      <div class="stat-item platform" @click="$emit('platform', 'windows')">
        <div class="stat-icon windows">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.platforms?.windows || 0 }}</span>
          <span class="stat-label">Windows</span>
        </div>
      </div>

      <div class="stat-item platform" @click="$emit('platform', 'mac')">
        <div class="stat-icon macos">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.platforms?.macos || 0 }}</span>
          <span class="stat-label">macOS</span>
        </div>
      </div>

      <div class="stat-item platform" @click="$emit('platform', 'linux')">
        <div class="stat-icon linux">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.504 0c-.155 0-.315.008-.48.021-4.226.333-3.105 4.807-3.17 6.298-.076 1.092-.3 1.953-1.05 3.02-.885 1.051-2.127 2.75-2.716 4.521-.278.832-.41 1.684-.287 2.489a.424.424 0 00-.11.135c-.26.268-.45.6-.663.839-.199.199-.485.267-.797.4-.313.136-.658.269-.864.68-.09.189-.136.394-.132.602 0 .199.027.4.055.536.058.399.116.728.04.97-.249.68-.28 1.145-.106 1.484.174.334.535.47.94.601.81.2 1.91.135 2.774.6.926.466 1.866.67 2.616.47.526-.116.97-.464 1.208-.946.587-.003 1.23-.269 2.26-.334.699-.058 1.574.267 2.577.2.025.134.063.198.114.333l.003.003c.391.778 1.113 1.132 1.884 1.071.771-.06 1.592-.536 2.257-1.306.631-.765 1.683-1.084 2.378-1.503.348-.199.629-.469.649-.853.023-.4-.2-.811-.714-1.376v-.097l-.003-.003c-.17-.2-.25-.535-.338-.926-.085-.401-.182-.786-.492-1.046h-.003c-.059-.054-.123-.067-.188-.135a.357.357 0 00-.19-.064c.431-1.278.264-2.55-.173-3.694-.533-1.41-1.465-2.638-2.175-3.483-.796-1.005-1.576-1.957-1.56-3.368.026-2.152.236-6.133-3.544-6.139zm.529 3.405h.013c.213 0 .396.062.584.198.19.135.33.332.438.533.105.259.158.459.166.724 0-.02.006-.04.006-.06v.105a.086.086 0 01-.004-.021l-.004-.024a1.807 1.807 0 01-.15.706.953.953 0 01-.213.335.71.71 0 00-.088-.042c-.104-.045-.198-.064-.284-.133a1.312 1.312 0 00-.22-.066c.05-.06.146-.133.183-.198.053-.128.082-.264.088-.402v-.02a1.21 1.21 0 00-.061-.4c-.045-.134-.101-.2-.183-.333-.084-.066-.167-.132-.267-.132h-.016c-.093 0-.176.03-.262.132a.8.8 0 00-.205.334 1.18 1.18 0 00-.09.468v.02c.002.134.017.267.051.4.03.132.068.2.118.333.024.066.06.132.108.198a.96.96 0 00-.21.065 2.613 2.613 0 01-.065-.2 1.452 1.452 0 01-.102-.4v-.067l-.005-.027v-.064a1.69 1.69 0 01.095-.566c.047-.134.1-.2.183-.333.084-.135.21-.2.366-.267.136 0 .267-.028.374-.028zm-2.092.456c.015 0 .04.003.077.003.106 0 .212.035.318.132.107.066.178.135.243.267.065.132.107.2.107.4 0 .066-.003.133-.01.267a.896.896 0 01-.05.2c-.026.066-.052.132-.09.265l-.007.003c-.003-.003-.007-.007-.01-.01a.96.96 0 00-.04.066v.003c-.037.07-.063.133-.09.2l-.02.064c0-.003-.003-.003-.003-.006l-.003.003-.045-.132c-.021-.066-.038-.2-.038-.333 0-.066.005-.132.016-.2.01-.065.027-.132.055-.198l.007-.024c.032-.066.06-.133.093-.2a.62.62 0 00-.093-.2 1.021 1.021 0 00-.183-.135.482.482 0 00-.262-.066c-.107 0-.19.033-.262.066a1.017 1.017 0 00-.183.135c-.066.067-.093.133-.093.2.027.066.055.133.087.2.018.03.036.064.055.097l.003.006.008.018c.025.065.042.133.052.198.01.068.016.134.016.2 0 .133-.017.267-.038.333l-.045.132-.003-.003c0 .003-.003.006-.003.006l-.02-.064a1.25 1.25 0 01-.09-.2v-.003c-.013-.023-.027-.044-.04-.066-.003.003-.007.007-.01.01l-.007-.003a.896.896 0 01-.09-.265 1.097 1.097 0 01-.05-.2c-.007-.134-.01-.201-.01-.267 0-.2.042-.268.107-.4.065-.132.136-.201.243-.267.106-.097.212-.132.318-.132.037 0 .062-.003.077-.003z"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.platforms?.linux || 0 }}</span>
          <span class="stat-label">Linux</span>
        </div>
      </div>

      <div class="stat-item platform" @click="$emit('platform', 'android')">
        <div class="stat-icon android">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4483.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.2439 13.8533 7.8508 12 7.8508s-3.5902.3931-5.1367 1.0989L4.841 5.4467a.4161.4161 0 00-.5677-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3435-4.1021-2.6892-7.5743-6.1185-9.4396"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.platforms?.android || 0 }}</span>
          <span class="stat-label">Android</span>
        </div>
      </div>

      <!-- Divider -->
      <div class="h-8 w-px bg-border-default"></div>

      <!-- Stars -->
      <div class="stat-item" @click="$emit('sort', 'stars')">
        <div class="stat-icon stars">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 .587l3.668 7.568 8.332 1.151-6.064 5.828 1.48 8.279-7.416-3.967-7.417 3.967 1.481-8.279-6.064-5.828 8.332-1.151z"/>
          </svg>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatNumber(stats.total?.stars || 0) }}</span>
          <span class="stat-label">Stars</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { statsAPI } from '../services/api';

const emit = defineEmits(['filter', 'platform', 'sort']);

const stats = ref({
  total: {},
  platforms: {},
});
const loading = ref(true);
let refreshInterval = null;

const fetchStats = async () => {
  try {
    const response = await statsAPI.getDetailed();
    const data = response.data || response;
    stats.value = data;
  } catch (error) {
    console.error('Failed to fetch stats:', error);
  }
  loading.value = false;
};

const formatNumber = (num) => {
  if (!num) return '0';
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
};

onMounted(() => {
  fetchStats();
  // 每 60 秒刷新一次
  refreshInterval = setInterval(fetchStats, 60000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>

<style scoped>
.stats-bar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.stats-bar::-webkit-scrollbar {
  display: none;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  cursor: pointer;
}

.stat-item:hover {
  background-color: var(--bg-tertiary, #161b22);
}

.stat-item.platform:hover .stat-icon {
  transform: scale(1.1);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  transition: transform 0.2s;
}

.stat-icon.apps {
  background-color: rgba(56, 139, 253, 0.15);
  color: #58a6ff;
}

.stat-icon.all {
  background-color: rgba(163, 113, 247, 0.15);
  color: #a371f7;
}

.stat-icon.downloads {
  background-color: rgba(63, 185, 80, 0.15);
  color: #3fb950;
}

.stat-icon.windows {
  background-color: rgba(0, 120, 212, 0.15);
  color: #0078d4;
}

.stat-icon.macos {
  background-color: rgba(142, 142, 147, 0.15);
  color: #8e8e93;
}

.stat-icon.linux {
  background-color: rgba(255, 204, 0, 0.15);
  color: #ffcc00;
}

.stat-icon.android {
  background-color: rgba(61, 220, 132, 0.15);
  color: #3ddc84;
}

.stat-icon.stars {
  background-color: rgba(210, 153, 34, 0.15);
  color: #d29922;
}

.stat-content {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary, #e6edf3);
}

.stat-label {
  font-size: 0.625rem;
  color: var(--text-tertiary, #8b949e);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
</style>
