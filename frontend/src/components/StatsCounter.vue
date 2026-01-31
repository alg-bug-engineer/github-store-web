<template>
  <span ref="counterElement">{{ formattedCount }}</span>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';

const props = defineProps({
  target: {
    type: Number,
    required: true,
  },
  duration: {
    type: Number,
    default: 1500, // milliseconds
  },
});

const currentCount = ref(0);
const counterElement = ref(null);

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return Math.floor(num).toString(); // Ensure integer for smaller numbers
};

const formattedCount = computed(() => formatNumber(currentCount.value));

const animateCount = () => {
  const start = 0;
  const target = props.target;
  const duration = props.duration;
  const startTime = performance.now();

  const update = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeOut = 1 - Math.pow(1 - progress, 3); // easeOutCubic
    
    currentCount.value = start + (target - start) * easeOut;

    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      currentCount.value = target; // Ensure it ends exactly on target
    }
  };

  requestAnimationFrame(update);
};

// Start animation when component is mounted or target changes
watch(() => props.target, (newTarget, oldTarget) => {
  if (newTarget !== oldTarget) {
    animateCount();
  }
});

onMounted(() => {
  // Use Intersection Observer to trigger animation when in view
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      animateCount();
      observer.unobserve(counterElement.value); // Animate only once
    }
  }, { threshold: 0.5 }); // Trigger when 50% of the element is visible

  if (counterElement.value) {
    observer.observe(counterElement.value);
  }
});
</script>

<style scoped>
/* No specific styles needed. */
</style>
