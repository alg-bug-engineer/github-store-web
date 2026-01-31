<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-semibold text-text-primary">Settings</h1>
      <p class="text-sm text-text-secondary">Configure tokens and storefront preferences.</p>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="bg-bg-secondary border border-border-default rounded-2xl p-6 space-y-4">
        <h2 class="text-lg font-semibold text-text-primary">API Access</h2>
        <div>
          <label class="block text-sm text-text-secondary mb-2">GitHub Personal Access Token</label>
          <input
            v-model="githubToken"
            type="password"
            placeholder="ghp_xxxxx"
            class="w-full px-4 py-2 text-sm bg-bg-tertiary text-text-primary placeholder-text-secondary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
          />
          <p class="mt-2 text-xs text-text-tertiary">
            Stored locally in your browser. Used to increase GitHub API rate limits.
          </p>
        </div>
        <button class="btn-primary px-4 py-2 text-sm" @click="saveSettings">
          Save Token
        </button>
      </div>

      <div class="bg-bg-secondary border border-border-default rounded-2xl p-6 space-y-4">
        <h2 class="text-lg font-semibold text-text-primary">Preferences</h2>
        <label class="flex items-center justify-between text-sm text-text-secondary">
          Open external links in new tab
          <input type="checkbox" v-model="openExternalInNewTab" class="h-4 w-4" />
        </label>
        <label class="flex items-center justify-between text-sm text-text-secondary">
          Enable compact cards
          <input type="checkbox" v-model="compactCards" class="h-4 w-4" />
        </label>
        <button class="btn-secondary px-4 py-2 text-sm" @click="saveSettings">
          Save Preferences
        </button>
      </div>
    </div>

    <div v-if="saved" class="text-sm text-green-400">
      Settings saved.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const githubToken = ref('');
const openExternalInNewTab = ref(true);
const compactCards = ref(false);
const saved = ref(false);

const saveSettings = () => {
  localStorage.setItem('github_token', githubToken.value);
  localStorage.setItem('open_external_new_tab', openExternalInNewTab.value ? '1' : '0');
  localStorage.setItem('compact_cards', compactCards.value ? '1' : '0');
  saved.value = true;
  setTimeout(() => {
    saved.value = false;
  }, 2000);
};

onMounted(() => {
  githubToken.value = localStorage.getItem('github_token') || '';
  openExternalInNewTab.value = localStorage.getItem('open_external_new_tab') !== '0';
  compactCards.value = localStorage.getItem('compact_cards') === '1';
});
</script>
