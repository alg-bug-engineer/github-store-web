<template>
  <div class="relative inline-block text-left">
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="inline-flex justify-center w-full rounded-md border border-border-default shadow-sm px-4 py-2 bg-bg-secondary text-sm font-medium text-text-primary hover:bg-bg-tertiary focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2 focus:ring-offset-bg-primary"
      id="menu-button"
      aria-expanded="true"
      aria-haspopup="true"
    >
      {{ selectedOptionLabel }}
      <svg
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

    <div
      v-if="isOpen"
      class="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-bg-secondary ring-1 ring-black ring-opacity-5 focus:outline-none z-10"
      role="menu"
      aria-orientation="vertical"
      aria-labelledby="menu-button"
      tabindex="-1"
    >
      <div class="py-1" role="none">
        <button
          v-for="option in options"
          :key="option.value"
          @click="selectOption(option.value)"
          :class="{
            'bg-bg-tertiary text-accent-primary': modelValue === option.value,
            'text-text-primary hover:bg-bg-tertiary': modelValue !== option.value,
          }"
          class="block w-full text-left px-4 py-2 text-sm transition-colors duration-100"
          role="menuitem"
          tabindex="-1"
        >
          {{ option.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue';
import { onMounted, onUnmounted } from 'vue';


const props = defineProps({
  modelValue: {
    type: [String, Number],
    required: true,
  },
  options: {
    type: Array,
    required: true,
    // Example: [{ label: 'Option 1', value: 'opt1' }, { label: 'Option 2', value: 'opt2' }]
  },
  defaultLabel: {
    type: String,
    default: 'Select Option',
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);

const selectedOptionLabel = computed(() => {
  const selected = props.options.find(option => option.value === props.modelValue);
  return selected ? selected.label : props.defaultLabel;
});

const selectOption = (value) => {
  emit('update:modelValue', value);
  isOpen.value = false;
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
