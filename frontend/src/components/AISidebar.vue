<template>
  <div class="ai-sidebar">
    <!-- Expanded Chat Panel -->
    <div v-if="isExpanded" class="ai-panel">
      <!-- Header -->
      <div class="ai-panel-header">
        <div class="flex items-center gap-2">
          <div class="ai-icon-container">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path>
            </svg>
          </div>
          <span class="text-sm font-medium text-text-primary">AI Assistant</span>
        </div>
        <button
          @click="togglePanel"
          class="p-1 rounded hover:bg-bg-tertiary text-text-secondary hover:text-text-primary transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Messages Area -->
      <div ref="messagesContainer" class="ai-panel-messages">
        <!-- Welcome Message -->
        <div v-if="messages.length === 0" class="text-center py-6">
          <div class="ai-welcome-icon">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 16 16">
              <path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path>
            </svg>
          </div>
          <p class="text-sm font-medium text-text-primary mt-3">Hi! I'm your AI assistant.</p>
          <p class="text-xs text-text-secondary mt-1 px-4">Ask me to recommend apps or help you find what you need.</p>
        </div>

        <!-- Message List -->
        <div v-for="(message, index) in messages" :key="index" class="mb-3">
          <!-- User Message -->
          <div v-if="message.fromUser" class="flex justify-end">
            <div class="user-message">
              {{ message.text }}
            </div>
          </div>
          <!-- AI Message -->
          <div v-else class="flex flex-col gap-2">
            <div class="ai-message">
              {{ message.text }}
            </div>
            <!-- Project Cards -->
            <div v-if="message.projects && message.projects.length > 0" class="space-y-2">
              <div
                v-for="project in message.projects"
                :key="project.id"
                @click="goToProject(project)"
                class="project-card"
              >
                <div class="flex items-center gap-2">
                  <img
                    v-if="project.avatar_url"
                    :src="project.avatar_url"
                    :alt="project.name"
                    class="w-6 h-6 rounded"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-medium text-text-primary truncate">
                      {{ project.name }}
                    </div>
                    <div class="text-xs text-text-secondary truncate">
                      {{ project.description || 'No description' }}
                    </div>
                  </div>
                  <div class="flex items-center gap-1 text-xs text-text-tertiary shrink-0">
                    <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 16 16">
                      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path>
                    </svg>
                    {{ formatStars(project.stars) }}
                  </div>
                  <svg class="w-3 h-3 text-text-tertiary shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading Indicator -->
        <div v-if="isLoading" class="flex justify-start mb-3">
          <div class="ai-message">
            <div class="flex gap-1 items-center">
              <span class="loading-dot"></span>
              <span class="loading-dot" style="animation-delay: 0.1s"></span>
              <span class="loading-dot" style="animation-delay: 0.2s"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="ai-panel-input">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Ask me anything..."
          :disabled="isLoading"
          class="ai-input"
        />
        <button
          @click="sendMessage"
          :disabled="isLoading || !newMessage.trim()"
          class="ai-send-btn"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Collapsed Toggle Button -->
    <button
      @click="togglePanel"
      class="ai-toggle-btn"
      :class="{ 'ai-toggle-btn-active': isExpanded }"
    >
      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 16 16">
        <path d="M8.878.392a1.75 1.75 0 0 0-1.756 0l-5.25 3.045A1.75 1.75 0 0 0 1 4.951v6.098c0 .624.332 1.2.872 1.514l5.25 3.045a1.75 1.75 0 0 0 1.756 0l5.25-3.045c.54-.313.872-.89.872-1.514V4.951c0-.624-.332-1.2-.872-1.514L8.878.392ZM8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"></path>
      </svg>
      <span>AI Assistant</span>
    </button>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { aiAPI } from '../services/api';

const router = useRouter();

const isExpanded = ref(false);
const messages = ref([]);
const newMessage = ref('');
const isLoading = ref(false);
const messagesContainer = ref(null);
const conversationId = ref(null);

const togglePanel = () => {
  isExpanded.value = !isExpanded.value;
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const formatStars = (stars) => {
  if (!stars) return '0';
  if (stars >= 1000) {
    return (stars / 1000).toFixed(1) + 'k';
  }
  return stars.toString();
};

const goToProject = (project) => {
  router.push(project.url);
};

const sendMessage = async () => {
  const text = newMessage.value.trim();
  if (!text || isLoading.value) return;

  messages.value.push({ text, fromUser: true });
  newMessage.value = '';
  isLoading.value = true;
  scrollToBottom();

  try {
    const response = await aiAPI.chat(text, conversationId.value);
    const data = response.data || response;

    const reply = data.reply || data.message || 'Sorry, I could not process your request.';
    const projects = data.projects || [];

    if (data.conversation_id) {
      conversationId.value = data.conversation_id;
    }

    messages.value.push({
      text: reply,
      fromUser: false,
      projects: projects
    });
  } catch (error) {
    console.error('AI chat error:', error);
    messages.value.push({
      text: 'Sorry, I encountered an error. Please try again.',
      fromUser: false,
      projects: []
    });
  }

  isLoading.value = false;
  scrollToBottom();
};
</script>

<style scoped>
.ai-sidebar {
  display: flex;
  flex-direction: column;
  border-top: 1px solid var(--border-default, #30363d);
}

.ai-toggle-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  font-size: 14px;
  color: var(--text-secondary, #8b949e);
  transition: background-color 0.2s ease, color 0.2s ease;
  border-radius: 12px;
  margin: 8px 12px;
}

.ai-toggle-btn:hover {
  background-color: var(--bg-tertiary, #161b22);
  color: var(--text-primary, #e6edf3);
}

.ai-toggle-btn-active {
  background-color: rgba(56, 139, 253, 0.12);
  color: var(--accent-primary, #58a6ff);
}

.ai-panel {
  display: flex;
  flex-direction: column;
  height: 400px;
  margin: 0 8px 8px 8px;
  border-radius: 12px;
  border: 1px solid var(--border-default, #30363d);
  background-color: var(--bg-secondary, #161b22);
  overflow: hidden;
}

.ai-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid var(--border-default, #30363d);
  background-color: var(--bg-tertiary, #21262d);
}

.ai-icon-container {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(88, 166, 255, 0.15);
  color: var(--accent-primary, #58a6ff);
}

.ai-panel-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.ai-welcome-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background-color: rgba(88, 166, 255, 0.15);
  color: var(--accent-primary, #58a6ff);
}

.user-message {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px 12px 4px 12px;
  font-size: 13px;
  background-color: var(--accent-primary, #1f6feb);
  color: #ffffff;
}

.ai-message {
  max-width: 85%;
  padding: 8px 12px;
  border-radius: 12px 12px 12px 4px;
  font-size: 13px;
  background-color: var(--bg-tertiary, #21262d);
  color: var(--text-primary, #e6edf3);
  border: 1px solid var(--border-default, #30363d);
}

.project-card {
  padding: 8px 10px;
  border-radius: 8px;
  background-color: var(--bg-primary, #0d1117);
  border: 1px solid var(--border-default, #30363d);
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.project-card:hover {
  border-color: var(--accent-primary, #58a6ff);
  background-color: var(--bg-tertiary, #161b22);
}

.ai-panel-input {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border-default, #30363d);
  background-color: var(--bg-tertiary, #21262d);
}

.ai-input {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 8px;
  border: 1px solid var(--border-default, #30363d);
  background-color: var(--bg-primary, #0d1117);
  color: var(--text-primary, #e6edf3);
  outline: none;
  transition: border-color 0.2s ease;
}

.ai-input:focus {
  border-color: var(--accent-primary, #58a6ff);
}

.ai-input:disabled {
  opacity: 0.5;
}

.ai-input::placeholder {
  color: var(--text-tertiary, #484f58);
}

.ai-send-btn {
  padding: 8px 12px;
  border-radius: 8px;
  background-color: var(--accent-primary, #1f6feb);
  color: #ffffff;
  transition: opacity 0.2s ease, transform 0.1s ease;
}

.ai-send-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.ai-send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.ai-send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--accent-primary, #58a6ff);
  animation: bounce 0.6s infinite alternate;
}

@keyframes bounce {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(-4px);
  }
}

/* Custom scrollbar */
.ai-panel-messages::-webkit-scrollbar {
  width: 4px;
}

.ai-panel-messages::-webkit-scrollbar-track {
  background: transparent;
}

.ai-panel-messages::-webkit-scrollbar-thumb {
  background: rgba(139, 148, 158, 0.4);
  border-radius: 2px;
}

.ai-panel-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 148, 158, 0.6);
}
</style>
