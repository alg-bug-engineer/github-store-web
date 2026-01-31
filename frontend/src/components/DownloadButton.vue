<template>
  <div class="relative inline-block text-left">
    <template v-if="assets && assets.length > 0">
      <!-- Button for single or multiple assets -->
      <button
        type="button"
        @click="handleButtonClick"
        class="inline-flex items-center justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-accent-secondary text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        id="download-button"
        aria-haspopup="true"
        :aria-expanded="isOpen"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="w-5 h-5 mr-2"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Download
        <svg
          v-if="assets.length > 1"
          class="-mr-1 ml-2 h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>

      <!-- Dropdown menu for multiple assets -->
      <div
        v-if="isOpen && assets.length > 1"
        class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-bg-secondary ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
        role="menu"
        aria-orientation="vertical"
        aria-labelledby="download-button"
        tabindex="-1"
      >
        <div class="py-1" role="none">
          <a
            v-for="asset in assets"
            :key="asset.github_asset_id"
            :href="asset.browser_download_url"
            target="_blank"
            class="flex justify-between items-center px-4 py-2 text-sm text-text-primary hover:bg-bg-tertiary"
            role="menuitem"
            tabindex="-1"
          >
            {{ asset.name }}
            <span class="text-text-tertiary text-xs">{{ formatBytes(asset.size) }}</span>
          </a>
        </div>
      </div>
    </template>

    <template v-else>
      <!-- Button for no releases (View Source) -->
      <a
        :href="repositoryHtmlUrl"
        target="_blank"
        class="inline-flex items-center justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-accent-primary text-base font-medium text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="w-5 h-5 mr-2"
        >
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        View Source
      </a>
    </template>
  </div>
</template>

<script setup>
import { ref, defineProps, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  assets: {
    type: Array,
    default: () => [], // Array of ReleaseAsset objects
  },
  repositoryHtmlUrl: {
    type: String,
    required: true,
  },
});

const isOpen = ref(false);

const handleButtonClick = () => {
  if (props.assets.length === 1) {
    // Direct download for single asset
    window.open(props.assets[0].browser_download_url, '_blank');
  } else if (props.assets.length > 1) {
    // Toggle dropdown for multiple assets
    isOpen.value = !isOpen.value;
  }
};

const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

// Close dropdown when clicking outside
const handleClickOutside = (event) => {
  if (isOpen.value && !event.target.closest('.relative')) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
/* Scoped styles mostly handled by Tailwind classes and theme variables */
</style>
