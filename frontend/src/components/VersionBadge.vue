<template>
  <span class="version-badge">
    <slot></slot>
  </span>
</template>

<style scoped>
.version-badge {
  background: var(--accent-secondary);
  color: white; /* Hardcoded white, as per plan */
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap; /* Prevent breaking version string */
}
</style>
