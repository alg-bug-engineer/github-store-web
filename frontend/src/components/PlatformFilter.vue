<template>
  <div class="platform-filter flex flex-wrap gap-2">
    <button
      v-for="platformOption in platformOptions"
      :key="platformOption.value"
      @click="selectPlatform(platformOption.value)"
      class="flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-full transition-colors duration-200"
      :class="{
        'bg-accent-primary text-white': modelValue === platformOption.value,
        'bg-bg-secondary text-text-primary hover:bg-bg-tertiary border border-border-default': modelValue !== platformOption.value,
      }"
    >
      <component :is="platformOption.icon" v-if="platformOption.icon" class="w-4 h-4" />
      <span>{{ platformOption.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
import IconAndroid from './icons/IconAndroid.vue';
import IconWindows from './icons/IconWindows.vue';
import IconMac from './icons/IconMac.vue';
import IconLinux from './icons/IconLinux.vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: 'all', // 'android', 'windows', 'mac', 'linux', 'all'
  },
});

const emit = defineEmits(['update:modelValue']);

const platformOptions = [
  { label: 'Android', value: 'android', icon: IconAndroid },
  { label: 'Windows', value: 'windows', icon: IconWindows },
  { label: 'Mac', value: 'mac', icon: IconMac },
  { label: 'Linux', value: 'linux', icon: IconLinux },
  { label: 'All Platforms', value: 'all', icon: null }, // No specific icon for 'All'
];

const selectPlatform = (platform) => {
  emit('update:modelValue', platform);
};
</script>

<style scoped>
/* Scoped styles mostly handled by Tailwind classes and theme variables */
</style>
