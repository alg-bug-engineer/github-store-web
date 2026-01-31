<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="w-full max-w-sm">
      <!-- Header -->
      <div class="text-center mb-6">
        <svg class="w-12 h-12 mx-auto text-text-primary" fill="currentColor" viewBox="0 0 16 16">
          <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path>
        </svg>
        <h1 class="text-2xl font-semibold text-text-primary mt-4">Create your account</h1>
      </div>

      <!-- Register Form -->
      <div class="bg-bg-secondary border border-border-default rounded-md p-4">
        <form @submit.prevent="handleRegister">
          <!-- Error Message -->
          <div v-if="errorMessage" class="flash flash-error mb-4">
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="flash flash-success mb-4">
            {{ successMessage }}
          </div>

          <div class="mb-4">
            <label for="phone" class="block text-sm font-medium text-text-primary mb-2">Phone Number</label>
            <input
              type="text"
              id="phone"
              v-model="phone"
              class="w-full px-3 py-2 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent focus:bg-bg-secondary"
              placeholder="Enter your phone number"
              required
              :disabled="loading"
            />
          </div>

          <div class="mb-4">
            <label for="nickname" class="block text-sm font-medium text-text-primary mb-2">
              Nickname
              <span class="text-text-secondary font-normal">(optional)</span>
            </label>
            <input
              type="text"
              id="nickname"
              v-model="nickname"
              class="w-full px-3 py-2 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent focus:bg-bg-secondary"
              placeholder="Enter your nickname"
              :disabled="loading"
            />
          </div>

          <div class="mb-4">
            <label for="password" class="block text-sm font-medium text-text-primary mb-2">Password</label>
            <input
              type="password"
              id="password"
              v-model="password"
              class="w-full px-3 py-2 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent focus:bg-bg-secondary"
              placeholder="Create a password"
              required
              :disabled="loading"
            />
            <p class="text-xs text-text-secondary mt-1">Password must be at least 6 characters</p>
          </div>

          <div class="mb-4">
            <label for="confirmPassword" class="block text-sm font-medium text-text-primary mb-2">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              class="w-full px-3 py-2 text-sm bg-bg-tertiary text-text-primary border border-border-default rounded-md focus:outline-none focus:ring-2 focus:ring-accent-tertiary focus:border-transparent focus:bg-bg-secondary"
              placeholder="Confirm your password"
              required
              :disabled="loading"
            />
          </div>

          <button
            type="submit"
            class="w-full btn-primary py-2.5"
            :disabled="loading"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Creating account...
            </span>
            <span v-else>Create account</span>
          </button>
        </form>
      </div>

      <!-- Sign in link -->
      <div class="bg-bg-secondary border border-border-default rounded-md p-4 mt-4 text-center text-sm">
        Already have an account?
        <router-link to="/login" class="text-accent-tertiary hover:underline">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authAPI } from '../services/api';

const phone = ref('');
const nickname = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');
const router = useRouter();

const handleRegister = async () => {
  // Validate passwords match
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match';
    return;
  }

  // Validate password length
  if (password.value.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters';
    return;
  }

  loading.value = true;
  errorMessage.value = '';
  successMessage.value = '';

  try {
    await authAPI.register({
      phone: phone.value,
      nickname: nickname.value || undefined,
      password: password.value
    });

    successMessage.value = 'Account created successfully! Redirecting to login...';

    // Redirect to login after short delay
    setTimeout(() => {
      router.push('/login');
    }, 1500);
  } catch (error) {
    console.error('Registration failed:', error);
    errorMessage.value = error.message || 'Registration failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
