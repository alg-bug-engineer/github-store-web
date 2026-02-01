<template>
  <div class="min-h-screen bg-bg-primary text-text-primary">
    <div class="min-h-screen lg:grid lg:grid-cols-[240px_minmax(0,1fr)]">
      <!-- Desktop Sidebar -->
      <aside class="hidden lg:flex flex-col border-r border-border-default bg-bg-secondary/70 backdrop-blur sticky top-0 h-screen">
        <div class="h-16 flex items-center px-5">
          <router-link to="/discover" class="flex items-center gap-2 hover:opacity-80">
            <svg height="28" viewBox="0 0 16 16" width="28" fill="currentColor">
              <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
            </svg>
            <span class="text-lg font-semibold">GitHub Store</span>
          </router-link>
        </div>

        <nav class="flex-1 min-h-0 px-3 pb-6 overflow-y-auto">
          <div class="space-y-6">
            <div>
              <p class="text-xs uppercase tracking-widest text-text-tertiary px-3 mb-2">Store</p>
              <div class="space-y-1">
                <router-link
                  to="/discover"
                  class="nav-item"
                  :class="{ 'nav-item-active': isActive('/discover') || isActive('/') }"
                >
                  <span class="nav-icon">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                    </svg>
                  </span>
                  Discover
                </router-link>
                <router-link
                  to="/charts"
                  class="nav-item"
                  :class="{ 'nav-item-active': isActive('/charts') }"
                >
                  <span class="nav-icon">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M2 2.5A1.5 1.5 0 0 1 3.5 1h9A1.5 1.5 0 0 1 14 2.5v11a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5Zm2.25 2a.75.75 0 0 0 0 1.5h6.5a.75.75 0 0 0 0-1.5Zm0 3a.75.75 0 0 0 0 1.5h4.5a.75.75 0 0 0 0-1.5Z"></path>
                    </svg>
                  </span>
                  Charts
                </router-link>
                <router-link
                  to="/search"
                  class="nav-item"
                  :class="{ 'nav-item-active': isActive('/search') }"
                >
                  <span class="nav-icon">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M2.75 2A1.75 1.75 0 0 0 1 3.75v8.5C1 13.216 1.784 14 2.75 14h10.5A1.75 1.75 0 0 0 15 12.25v-6.5A1.75 1.75 0 0 0 13.25 4h-2.5a.75.75 0 0 1-.53-.22l-.94-.94A1.75 1.75 0 0 0 7.53 2Zm0 1.5h4.78a.25.25 0 0 1 .177.073l.94.94c.33.33.78.517 1.247.517h2.356a.25.25 0 0 1 .25.25v6.5a.25.25 0 0 1-.25.25H2.75a.25.25 0 0 1-.25-.25v-8.5a.25.25 0 0 1 .25-.25Z"></path>
                    </svg>
                  </span>
                  Browse
                </router-link>
              </div>
            </div>

            <div>
              <p class="text-xs uppercase tracking-widest text-text-tertiary px-3 mb-2">Collections</p>
              <div class="space-y-1">
                <router-link
                  v-for="collection in collections"
                  :key="collection.value"
                  :to="{ path: '/search', query: { category: collection.value } }"
                  class="nav-item"
                  :class="{ 'nav-item-active': isCollectionActive(collection.value) }"
                >
                  <span class="nav-icon">
                    <span class="nav-dot" :class="collection.dotClass"></span>
                  </span>
                  {{ collection.label }}
                </router-link>
              </div>
            </div>

            <div>
              <p class="text-xs uppercase tracking-widest text-text-tertiary px-3 mb-2">Personal</p>
              <div class="space-y-1">
                <router-link
                  to="/profile"
                  class="nav-item"
                  :class="{ 'nav-item-active': isActive('/profile') }"
                >
                  <span class="nav-icon">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M7.25 1.5a.75.75 0 0 1 1.5 0v2.154a3.001 3.001 0 0 1 1.14.658l1.528-.882a.75.75 0 0 1 .75 1.299l-1.517.876c.1.33.15.678.15 1.04 0 .362-.05.71-.15 1.04l1.517.876a.75.75 0 0 1-.75 1.299l-1.528-.882a3.001 3.001 0 0 1-1.14.658V12a.75.75 0 0 1-1.5 0V9.846a3.001 3.001 0 0 1-1.14-.658l-1.528.882a.75.75 0 0 1-.75-1.299l1.517-.876A3.01 3.01 0 0 1 5.5 6.75c0-.362.05-.71.15-1.04L4.133 4.834a.75.75 0 1 1 .75-1.299l1.528.882A3.001 3.001 0 0 1 7.25 3.654Z"></path>
                    </svg>
                  </span>
                  Starred
                </router-link>
                <router-link
                  to="/settings"
                  class="nav-item"
                  :class="{ 'nav-item-active': isActive('/settings') }"
                >
                  <span class="nav-icon">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M9.605 1.05a1 1 0 0 1 .99.858l.2 1.356c.244.105.475.233.69.382l1.265-.73a1 1 0 0 1 1.366.366l.5.866a1 1 0 0 1-.366 1.366l-1.265.73c.03.25.03.503 0 .753l1.265.73a1 1 0 0 1 .366 1.366l-.5.866a1 1 0 0 1-1.366.366l-1.265-.73a3.63 3.63 0 0 1-.69.382l-.2 1.356a1 1 0 0 1-.99.858h-1a1 1 0 0 1-.99-.858l-.2-1.356a3.63 3.63 0 0 1-.69-.382l-1.265.73a1 1 0 0 1-1.366-.366l-.5-.866a1 1 0 0 1 .366-1.366l1.265-.73a3.98 3.98 0 0 1 0-.753l-1.265-.73a1 1 0 0 1-.366-1.366l.5-.866a1 1 0 0 1 1.366-.366l1.265.73c.215-.149.446-.277.69-.382l.2-1.356a1 1 0 0 1 .99-.858Zm-1.605 4.7a2.25 2.25 0 1 0 0 4.5 2.25 2.25 0 0 0 0-4.5Z"></path>
                    </svg>
                  </span>
                  Settings
                </router-link>
              </div>
            </div>
          </div>
        </nav>

        <!-- AI Sidebar -->
        <AISidebar />

        <div class="border-t border-border-default px-4 py-4 flex items-center justify-between">
          <ThemeToggle />
          <div class="flex items-center gap-2 text-sm">
            <template v-if="isLoggedIn">
              <button
                @click="logout"
                class="px-3 py-1.5 text-xs border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
              >
                Sign out
              </button>
            </template>
            <template v-else>
              <router-link
                to="/login"
                class="px-3 py-1.5 text-xs border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
              >
                Sign in
              </router-link>
            </template>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="flex min-h-screen flex-col">
        <!-- Mobile Header -->
        <header class="lg:hidden sticky top-0 z-40 border-b border-border-default bg-bg-primary/90 backdrop-blur">
          <div class="flex items-center justify-between h-14 px-4">
            <button
              @click="mobileMenuOpen = true"
              class="p-2 rounded-md hover:bg-bg-tertiary"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <router-link to="/discover" class="flex items-center gap-2">
              <svg height="24" viewBox="0 0 16 16" width="24" fill="currentColor">
                <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
              </svg>
              <span class="text-sm font-semibold">GitHub Store</span>
            </router-link>
            <ThemeToggle />
          </div>
        </header>

        <!-- Mobile Sidebar Drawer -->
        <div v-if="mobileMenuOpen" class="lg:hidden fixed inset-0 z-50">
          <div class="absolute inset-0 bg-black/50" @click="mobileMenuOpen = false"></div>
          <aside class="absolute left-0 top-0 h-full w-72 bg-bg-secondary border-r border-border-default p-4 flex flex-col">
            <div class="flex items-center justify-between mb-4">
              <router-link to="/discover" class="flex items-center gap-2" @click="mobileMenuOpen = false">
                <svg height="24" viewBox="0 0 16 16" width="24" fill="currentColor">
                  <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
                </svg>
                <span class="text-base font-semibold">GitHub Store</span>
              </router-link>
              <button @click="mobileMenuOpen = false" class="p-2 rounded-md hover:bg-bg-tertiary">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div class="space-y-4 overflow-y-auto">
              <div>
                <p class="text-xs uppercase tracking-widest text-text-tertiary px-2 mb-2">Store</p>
                <div class="space-y-1">
                  <router-link to="/discover" class="nav-item" @click="mobileMenuOpen = false">
                    <span class="nav-icon">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                      </svg>
                    </span>
                    Discover
                  </router-link>
                  <router-link to="/charts" class="nav-item" @click="mobileMenuOpen = false">
                    <span class="nav-icon">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M2 2.5A1.5 1.5 0 0 1 3.5 1h9A1.5 1.5 0 0 1 14 2.5v11a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 13.5Zm2.25 2a.75.75 0 0 0 0 1.5h6.5a.75.75 0 0 0 0-1.5Zm0 3a.75.75 0 0 0 0 1.5h4.5a.75.75 0 0 0 0-1.5Z"></path>
                      </svg>
                    </span>
                    Charts
                  </router-link>
                  <router-link to="/search" class="nav-item" @click="mobileMenuOpen = false">
                    <span class="nav-icon">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M2.75 2A1.75 1.75 0 0 0 1 3.75v8.5C1 13.216 1.784 14 2.75 14h10.5A1.75 1.75 0 0 0 15 12.25v-6.5A1.75 1.75 0 0 0 13.25 4h-2.5a.75.75 0 0 1-.53-.22l-.94-.94A1.75 1.75 0 0 0 7.53 2Zm0 1.5h4.78a.25.25 0 0 1 .177.073l.94.94c.33.33.78.517 1.247.517h2.356a.25.25 0 0 1 .25.25v6.5a.25.25 0 0 1-.25.25H2.75a.25.25 0 0 1-.25-.25v-8.5a.25.25 0 0 1 .25-.25Z"></path>
                      </svg>
                    </span>
                    Browse
                  </router-link>
                </div>
              </div>
              <div class="px-2">
                <p class="text-xs uppercase tracking-widest text-text-tertiary mb-2">View Mode</p>
                <ViewModeSwitch v-model="viewMode" />
              </div>
              <div>
                <p class="text-xs uppercase tracking-widest text-text-tertiary px-2 mb-2">Collections</p>
                <div class="space-y-1">
                  <router-link
                    v-for="collection in collections"
                    :key="collection.value"
                    :to="{ path: '/search', query: { category: collection.value } }"
                    class="nav-item"
                    @click="mobileMenuOpen = false"
                  >
                    <span class="nav-icon">
                      <span class="nav-dot" :class="collection.dotClass"></span>
                    </span>
                    {{ collection.label }}
                  </router-link>
                </div>
              </div>
              <div>
                <p class="text-xs uppercase tracking-widest text-text-tertiary px-2 mb-2">Personal</p>
                <div class="space-y-1">
                  <router-link to="/profile" class="nav-item" @click="mobileMenuOpen = false">
                    <span class="nav-icon">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M7.25 1.5a.75.75 0 0 1 1.5 0v2.154a3.001 3.001 0 0 1 1.14.658l1.528-.882a.75.75 0 0 1 .75 1.299l-1.517.876c.1.33.15.678.15 1.04 0 .362-.05.71-.15 1.04l1.517.876a.75.75 0 0 1-.75 1.299l-1.528-.882a3.001 3.001 0 0 1-1.14.658V12a.75.75 0 0 1-1.5 0V9.846a3.001 3.001 0 0 1-1.14-.658l-1.528.882a.75.75 0 0 1-.75-1.299l1.517-.876A3.01 3.01 0 0 1 5.5 6.75c0-.362.05-.71.15-1.04L4.133 4.834a.75.75 0 1 1 .75-1.299l1.528.882A3.001 3.001 0 0 1 7.25 3.654Z"></path>
                      </svg>
                    </span>
                    Starred
                  </router-link>
                  <router-link to="/settings" class="nav-item" @click="mobileMenuOpen = false">
                    <span class="nav-icon">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
                        <path d="M9.605 1.05a1 1 0 0 1 .99.858l.2 1.356c.244.105.475.233.69.382l1.265-.73a1 1 0 0 1 1.366.366l.5.866a1 1 0 0 1-.366 1.366l-1.265.73c.03.25.03.503 0 .753l1.265.73a1 1 0 0 1 .366 1.366l-.5.866a1 1 0 0 1-1.366.366l-1.265-.73a3.63 3.63 0 0 1-.69.382l-.2 1.356a1 1 0 0 1-.99.858h-1a1 1 0 0 1-.99-.858l-.2-1.356a3.63 3.63 0 0 1-.69-.382l-1.265.73a1 1 0 0 1-1.366-.366l-.5-.866a1 1 0 0 1 .366-1.366l1.265-.73a3.98 3.98 0 0 1 0-.753l-1.265-.73a1 1 0 0 1-.366-1.366l.5-.866a1 1 0 0 1 1.366-.366l1.265.73c.215-.149.446-.277.69-.382l.2-1.356a1 1 0 0 1 .99-.858Zm-1.605 4.7a2.25 2.25 0 1 0 0 4.5 2.25 2.25 0 0 0 0-4.5Z"></path>
                      </svg>
                    </span>
                    Settings
                  </router-link>
                </div>
              </div>
            </div>
            <div class="mt-auto pt-4 border-t border-border-default flex items-center justify-between">
              <ThemeToggle />
              <div class="text-sm">
                <template v-if="isLoggedIn">
                  <button
                    @click="logout"
                    class="px-3 py-1.5 text-xs border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
                  >
                    Sign out
                  </button>
                </template>
                <template v-else>
                  <router-link
                    to="/login"
                    class="px-3 py-1.5 text-xs border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
                    @click="mobileMenuOpen = false"
                  >
                    Sign in
                  </router-link>
                </template>
              </div>
            </div>
          </aside>
        </div>

        <!-- Desktop Toolbar -->
        <div class="hidden lg:block border-b border-border-default bg-bg-primary/80 backdrop-blur sticky top-0 z-30">
          <div class="flex items-center gap-4 px-6 py-3">
            <div class="flex-1">
              <div class="relative">
                <input
                  v-model="headerSearchQuery"
                  type="text"
                  placeholder="Search applications, tools, extensions..."
                  class="w-full px-4 py-2 text-sm bg-bg-secondary text-text-primary placeholder-text-secondary border border-border-default rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent"
                  @keyup.enter="handleHeaderSearch"
                />
                <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
            <ViewModeSwitch v-model="viewMode" />
            <div class="flex items-center gap-3">
              <template v-if="isLoggedIn">
                <router-link
                  to="/profile"
                  class="px-3 py-2 text-sm border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
                >
                  Profile
                </router-link>
                <button
                  @click="logout"
                  class="px-3 py-2 text-sm border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
                >
                  Sign out
                </button>
              </template>
              <template v-else>
                <router-link
                  to="/login"
                  class="px-3 py-2 text-sm border border-border-default rounded-md hover:border-header-text hover:text-header-text transition-colors"
                >
                  Sign in
                </router-link>
              </template>
            </div>
          </div>
        </div>

        <main class="flex-1 px-4 lg:px-6 py-4">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuth } from './stores/auth';
import { categoriesAPI } from './services/api';
import ViewModeSwitch from './components/ViewModeSwitch.vue';
import ThemeToggle from './components/ThemeToggle.vue';
import AISidebar from './components/AISidebar.vue';

const router = useRouter();
const route = useRoute();
const mobileMenuOpen = ref(false);
const headerSearchQuery = ref('');
const viewMode = ref(localStorage.getItem('viewMode') || 'apps');

const { isLoggedIn, logout: authLogout } = useAuth();

// 颜色映射
const colorToDotClass = {
  blue: 'nav-dot-blue',
  green: 'nav-dot-green',
  purple: 'nav-dot-purple',
  amber: 'nav-dot-amber',
  pink: 'nav-dot-pink',
  cyan: 'nav-dot-cyan',
  red: 'nav-dot-red',
  gray: 'nav-dot-gray',
};

// 动态加载的分类
const collections = ref([]);

// 加载分类配置
const loadCategories = async () => {
  try {
    const response = await categoriesAPI.getAll();
    const data = response.data || response;
    collections.value = (data.categories || []).map(cat => ({
      label: cat.label,
      value: cat.id,
      dotClass: colorToDotClass[cat.color] || 'nav-dot-gray',
    }));
  } catch (error) {
    console.error('Failed to load categories:', error);
    // 使用默认分类
    collections.value = [
      { label: 'Dev Tools', value: 'developer_tools', dotClass: 'nav-dot-blue' },
      { label: 'Productivity', value: 'productivity', dotClass: 'nav-dot-green' },
      { label: 'Media', value: 'media', dotClass: 'nav-dot-purple' },
      { label: 'System', value: 'utilities', dotClass: 'nav-dot-amber' },
    ];
  }
};

const isActive = (path) => {
  if (path === '/search') return route.path.startsWith('/search');
  if (path === '/') return route.path === '/';
  return route.path === path;
};

const isCollectionActive = (value) => {
  return route.path.startsWith('/search') && route.query.category === value;
};

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  }
);

watch(viewMode, (newValue) => {
  localStorage.setItem('viewMode', newValue);
  if (route.path === '/search') {
    router.replace({ query: { ...route.query, view: newValue !== 'apps' ? newValue : undefined } });
  } else {
    router.push({ path: '/search', query: { view: newValue !== 'apps' ? newValue : undefined } });
  }
});

onMounted(() => {
  loadCategories();
  if (route.query.view) {
    viewMode.value = route.query.view;
  }
});

const handleHeaderSearch = () => {
  if (headerSearchQuery.value.trim()) {
    router.push({ path: '/search', query: { q: headerSearchQuery.value, view: viewMode.value } });
    headerSearchQuery.value = '';
  }
};

const logout = () => {
  authLogout();
  mobileMenuOpen.value = false;
  router.push('/discover');
};
</script>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 14px;
  color: var(--text-secondary, #8b949e);
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.nav-item:hover {
  background-color: var(--bg-tertiary, #161b22);
  color: var(--text-primary, #e6edf3);
  transform: translateX(2px);
}

.nav-item-active {
  background-color: rgba(56, 139, 253, 0.12);
  color: var(--accent-primary, #58a6ff);
}

.nav-icon {
  width: 20px;
  display: inline-flex;
  justify-content: center;
}

.nav-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  display: inline-block;
}

.nav-dot-blue {
  background-color: #58a6ff;
}

.nav-dot-green {
  background-color: #3fb950;
}

.nav-dot-purple {
  background-color: #a371f7;
}

.nav-dot-amber {
  background-color: #d29922;
}

.nav-dot-pink {
  background-color: #db61a2;
}

.nav-dot-cyan {
  background-color: #39c5cf;
}

.nav-dot-red {
  background-color: #f85149;
}

.nav-dot-gray {
  background-color: #8b949e;
}
</style>
