import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => {
    // Handle wrapped response format
    if (response.data && response.data.code === 200 && response.data.data) {
      return response.data;
    }
    return response.data;
  },
  (error) => {
    if (error.response) {
      // Handle 401 unauthorized
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        // Optionally redirect to login
        // window.location.href = '/login';
      }
      // Return error message from server
      const message = error.response.data?.message || error.response.data?.error || 'Request failed';
      return Promise.reject(new Error(message));
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/me'),
};

// Repositories API
export const repositoriesAPI = {
  search: (params) => api.get('/repositories/', { params }),
  getDetail: (owner, repo) => api.get(`/repositories/${owner}/${repo}`),
  getTopics: (params) => api.get('/repositories/topics/', { params }),
  summarize: (repoId) => api.post(`/ai/repositories/${repoId}/summarize`),
  getReleases: (owner, repo, params) => api.get(`/repositories/${owner}/${repo}/releases`, { params }),
  getAssets: (releaseId, params) => api.get(`/repositories/releases/${releaseId}/assets`, { params }),
  getStatsOverview: () => api.get('/stats/overview'),
};

// Discover API
export const discoverAPI = {
  getHome: () => api.get('/discover/home'),
  getHot: (params) => api.get('/discover/hot', { params }),
  getNew: (params) => api.get('/discover/new', { params }),
  getCategory: (category, params) => api.get(`/discover/category/${category}`, { params }),
  getPersonalized: (params) => api.get('/discover/personalized', { params }),
};

// Favorites API
export const favoritesAPI = {
  list: (params) => api.get('/favorites', { params }),
  add: (repoId, note) => api.post('/favorites', { repo_id: repoId, note }),
  remove: (repoId) => api.delete(`/favorites/${repoId}`),
  check: (repoId) => api.get(`/favorites/check/${repoId}`),
};

// AI Chat API
export const aiAPI = {
  chat: (message, context) => api.post('/ai/chat', { message, context }),
  getHistory: (params) => api.get('/ai/history', { params }),
};

export default api;
