import { createRouter, createWebHistory } from 'vue-router'
import SearchPage from '../views/SearchPage.vue'
import DetailPage from '../views/DetailPage.vue'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import DiscoveryPage from '../views/DiscoveryPage.vue'
import ChartsPage from '../views/ChartsPage.vue'
import SettingsPage from '../views/SettingsPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: DiscoveryPage
    },
    {
      path: '/search',
      name: 'search',
      component: SearchPage
    },
    {
      path: '/repo/:owner/:repo',
      name: 'detail',
      component: DetailPage
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfilePage
    },
    {
      path: '/discover',
      name: 'discover',
      component: DiscoveryPage
    },
    {
      path: '/charts',
      name: 'charts',
      component: ChartsPage
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsPage
    }
  ]
})

export default router
