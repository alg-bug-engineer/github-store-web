<template>
  <div class="inline-flex flex-row items-center gap-2 flex-nowrap shrink-0">
    <button
      @click="selectView('apps')"
      class="flex flex-row items-center justify-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg border-2 transition-all whitespace-nowrap shrink-0 w-24"
      :class="modelValue === 'apps' 
        ? 'border-accent-primary text-accent-primary bg-accent-primary/10' 
        : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border-default'"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
      <span class="whitespace-nowrap">Apps</span>
    </button>

    <button
      @click="selectView('all')"
      class="flex flex-row items-center justify-center gap-1.5 px-3 py-1.5 text-sm font-medium rounded-lg border-2 transition-all whitespace-nowrap shrink-0 w-24"
      :class="modelValue === 'all' 
        ? 'border-accent-primary text-accent-primary bg-accent-primary/10' 
        : 'border-transparent text-text-secondary hover:text-text-primary hover:border-border-default'"
    >
      <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
      <span class="whitespace-nowrap">All</span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: 'apps',
  },
});

const emit = defineEmits(['update:modelValue']);

const selectView = (view) => {
  emit('update:modelValue', view);
};
</script>
