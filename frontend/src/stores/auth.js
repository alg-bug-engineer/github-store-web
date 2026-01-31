import { ref, computed } from 'vue';

// Reactive auth state
const token = ref(localStorage.getItem('access_token'));
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

export const useAuth = () => {
  const isLoggedIn = computed(() => !!token.value);

  const login = (accessToken, userData) => {
    token.value = accessToken;
    user.value = userData;
    localStorage.setItem('access_token', accessToken);
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData));
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  };

  const getToken = () => token.value;
  const getUser = () => user.value;

  return {
    isLoggedIn,
    user,
    token,
    login,
    logout,
    getToken,
    getUser,
  };
};
