<template>
  <div 
    class="fixed right-0 top-1/2 -translate-y-1/2 z-50"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- Toggle Button - Partially Visible -->
    <button
      v-if="!isOpen"
      @click="toggleChat"
      :class="[
        'flex items-center justify-center rounded-l-2xl transition-all duration-300 ease-out hover:scale-110',
        isHovered ? 'translate-x-0' : 'translate-x-1/2'
      ]"
      :style="buttonStyle"
      title="AI Assistant"
    >
      <div class="p-4">
        <svg 
          class="w-12 h-12" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="1.5" 
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" 
          />
        </svg>
      </div>
    </button>

    <!-- Chat Window -->
    <div 
      v-if="isOpen" 
      class="mr-4 w-[400px] rounded-2xl shadow-2xl flex flex-col h-[550px] overflow-hidden border-2"
      :style="chatWindowStyle"
    >
      <!-- Header -->
      <div 
        class="p-4 flex justify-between items-center shrink-0 border-b"
        :style="headerStyle"
      >
        <div class="flex items-center gap-3">
          <div 
            class="w-10 h-10 rounded-full flex items-center justify-center"
            :style="iconContainerStyle"
          >
            <svg 
              class="w-6 h-6" 
              :style="{ color: currentTheme === 'dark' ? '#60a5fa' : '#2563eb' }"
              fill="currentColor" 
              viewBox="0 0 16 16"
            >
              <path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path>
            </svg>
          </div>
          <div>
            <h2 
              class="text-base font-bold"
              :style="{ color: currentTheme === 'dark' ? '#f0f6fc' : '#1f2328' }"
            >AI Assistant</h2>
            <p 
              class="text-xs"
              :style="{ color: currentTheme === 'dark' ? '#7d8590' : '#656d76' }"
            >Online</p>
          </div>
        </div>
        <button
          @click="toggleChat"
          :class="[
            'p-2 rounded-full transition-colors',
            currentTheme === 'dark' 
              ? 'hover:bg-gray-700 text-gray-400 hover:text-white' 
              : 'hover:bg-gray-200 text-gray-500 hover:text-gray-800'
          ]"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Messages -->
      <div 
        ref="messagesContainer" 
        class="flex-1 p-4 overflow-y-auto"
        :style="messagesAreaStyle"
      >
        <!-- Welcome Message -->
        <div v-if="messages.length === 0" class="text-center py-10">
          <div 
            class="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
            :style="welcomeIconStyle"
          >
            <svg 
              class="w-8 h-8" 
              :style="{ color: currentTheme === 'dark' ? '#60a5fa' : '#2563eb' }"
              fill="currentColor" 
              viewBox="0 0 16 16"
            >
              <path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path>
            </svg>
          </div>
          <p 
            class="font-semibold text-lg mb-2"
            :style="{ color: currentTheme === 'dark' ? '#f0f6fc' : '#1f2328' }"
          >Hi! I'm your AI assistant.</p>
          <p 
            class="text-sm max-w-[280px] mx-auto"
            :style="{ color: currentTheme === 'dark' ? '#7d8590' : '#656d76' }"
          >Ask me to recommend apps or help you find what you need.</p>
        </div>

        <div v-for="(message, index) in messages" :key="index" class="mb-4">
          <div :class="[message.fromUser ? 'flex justify-end' : 'flex justify-start']">
            <!-- User Message -->
            <div 
              v-if="message.fromUser" 
              class="max-w-[85%] px-4 py-3 rounded-2xl rounded-tr-sm text-sm shadow-md"
              :style="userMessageStyle"
            >
              <p class="whitespace-pre-wrap leading-relaxed">{{ message.text }}</p>
            </div>
            <!-- AI Message -->
            <div 
              v-else 
              class="max-w-[85%] px-4 py-3 rounded-2xl rounded-tl-sm text-sm shadow-md border"
              :style="aiMessageStyle"
            >
              <p class="whitespace-pre-wrap leading-relaxed">{{ message.text }}</p>
            </div>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="isLoading" class="flex justify-start mb-4">
          <div 
            class="px-4 py-3 rounded-2xl rounded-tl-sm shadow-md border"
            :style="loadingIndicatorStyle"
          >
            <div class="flex gap-1.5 items-center h-5">
              <span 
                class="w-2 h-2 rounded-full animate-bounce"
                :style="{ background: currentTheme === 'dark' ? '#58a6ff' : '#0969da' }"
              ></span>
              <span 
                class="w-2 h-2 rounded-full animate-bounce"
                :style="{ background: currentTheme === 'dark' ? '#58a6ff' : '#0969da', animationDelay: '0.1s' }"
              ></span>
              <span 
                class="w-2 h-2 rounded-full animate-bounce"
                :style="{ background: currentTheme === 'dark' ? '#58a6ff' : '#0969da', animationDelay: '0.2s' }"
              ></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div 
        class="p-4 border-t shrink-0"
        :style="inputAreaStyle"
      >
        <div class="flex gap-2">
          <input
            type="text"
            v-model="newMessage"
            @keyup.enter="sendMessage"
            placeholder="Ask me anything..."
            :disabled="isLoading"
            class="flex-1 px-4 py-3 text-sm rounded-xl focus:outline-none focus:ring-2 disabled:opacity-50 transition-all border"
            :style="inputStyle"
          />
          <button
            @click="sendMessage"
            :disabled="isLoading || !newMessage.trim()"
            class="px-4 py-3 rounded-xl transition-all flex items-center justify-center disabled:cursor-not-allowed hover:scale-105 active:scale-95"
            :style="sendButtonStyle"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed } from 'vue';
import { aiAPI } from '../services/api';

const isOpen = ref(false);
const isHovered = ref(false);
const messages = ref([]);
const newMessage = ref('');
const isLoading = ref(false);
const messagesContainer = ref(null);

// Get current theme from document
const currentTheme = computed(() => {
  if (typeof document === 'undefined') return 'dark';
  const theme = document.documentElement.getAttribute('data-theme');
  return theme || 'dark';
});

// Button styles based on theme
const buttonStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#1f6feb' : '#0969da',
    color: '#ffffff',
    boxShadow: isDark 
      ? '0 4px 20px rgba(31, 111, 235, 0.4), 0 0 0 1px rgba(255,255,255,0.1)' 
      : '0 4px 20px rgba(9, 105, 218, 0.3), 0 0 0 1px rgba(0,0,0,0.05)'
  };
});

// Chat window styles
const chatWindowStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#0d1117' : '#ffffff',
    borderColor: isDark ? '#30363d' : '#d0d7de'
  };
});

const headerStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#161b22' : '#f6f8fa',
    borderColor: isDark ? '#30363d' : '#d0d7de'
  };
});

const iconContainerStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? 'rgba(88, 166, 255, 0.15)' : 'rgba(9, 105, 218, 0.1)'
  };
});

const messagesAreaStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#0d1117' : '#ffffff'
  };
});

const welcomeIconStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? 'rgba(88, 166, 255, 0.15)' : 'rgba(9, 105, 218, 0.1)'
  };
});

const userMessageStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#1f6feb' : '#0969da',
    color: '#ffffff'
  };
});

const aiMessageStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#21262d' : '#f6f8fa',
    color: isDark ? '#e6edf3' : '#1f2328',
    borderColor: isDark ? '#30363d' : '#d0d7de'
  };
});

const loadingIndicatorStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#21262d' : '#f6f8fa',
    borderColor: isDark ? '#30363d' : '#d0d7de'
  };
});

const inputAreaStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#161b22' : '#f6f8fa',
    borderColor: isDark ? '#30363d' : '#d0d7de'
  };
});

const inputStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  return {
    background: isDark ? '#0d1117' : '#ffffff',
    color: isDark ? '#f0f6fc' : '#1f2328',
    borderColor: isDark ? '#30363d' : '#d0d7de',
    boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)'
  };
});

const sendButtonStyle = computed(() => {
  const isDark = currentTheme.value === 'dark';
  const disabled = isLoading.value || !newMessage.value.trim();
  return {
    background: isDark ? '#1f6feb' : '#0969da',
    color: '#ffffff',
    opacity: disabled ? '0.5' : '1'
  };
});

const toggleChat = () => {
  isOpen.value = !isOpen.value;
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  const text = newMessage.value.trim();
  if (!text || isLoading.value) return;

  messages.value.push({ text, fromUser: true });
  newMessage.value = '';
  isLoading.value = true;
  scrollToBottom();

  try {
    const response = await aiAPI.chat(text, {
      current_page: window.location.pathname,
    });

    const data = response.data || response;
    const reply = data.reply || data.message || 'Sorry, I could not process your request.';

    messages.value.push({ text: reply, fromUser: false });
  } catch (error) {
    console.error('AI chat error:', error);
    messages.value.push({
      text: 'Sorry, I encountered an error. Please try again.',
      fromUser: false
    });
  }

  isLoading.value = false;
  scrollToBottom();
};
</script>

<style scoped>
/* Custom scrollbar for messages */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.8);
}
</style>
