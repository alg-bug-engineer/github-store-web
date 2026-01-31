<template>
  <div class="platform-icons flex gap-1">
    <template v-for="platform in platforms" :key="platform">
      <div class="relative group">
        <component :is="getIconComponent(platform)" class="w-4 h-4 text-text-secondary" />
        <span
          class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-bg-tertiary text-text-secondary text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap"
        >
          {{ getPlatformName(platform) }}
        </span>
      </div>
    </template>
    <div v-if="platforms.length === 0" class="relative group">
      <!-- Generic download icon if no platforms detected -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="w-4 h-4 text-text-tertiary"
      >
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-bg-tertiary text-text-secondary text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap"
      >
        Platform N/A
      </span>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';
import IconAndroid from './icons/IconAndroid.vue';
import IconWindows from './icons/IconWindows.vue';
import IconMac from './icons/IconMac.vue';
import IconLinux from './icons/IconLinux.vue';

const props = defineProps({
  platforms: {
    type: Array,
    default: () => [], // e.g., ['windows', 'mac', 'linux', 'android']
  },
});

const getIconComponent = (platform) => {
  switch (platform) {
    case 'windows':
      return IconWindows;
    case 'mac':
      return IconMac;
    case 'linux':
      return IconLinux;
    case 'android':
      return IconAndroid;
    default:
      return null; // Should not happen if platforms array is clean
  }
};

const getPlatformName = (platform) => {
  switch (platform) {
    case 'windows':
      return 'Windows';
    case 'mac':
      return 'Mac';
    case 'linux':
      return 'Linux';
    case 'android':
      return 'Android';
    default:
      return platform; // Fallback
  }
};
</script>

<style scoped>
/* Tooltip styles handled by Tailwind classes */
</style>
