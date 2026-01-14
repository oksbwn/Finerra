import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

interface User {
    id: string
    email: string
    role: string
    tenant_id: string
    full_name?: string
    avatar?: string
}

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const token = ref<string | null>(localStorage.getItem('access_token'))
    const isAuthenticated = computed(() => !!token.value)

    async function fetchUser() {
        if (!token.value) return
        try {
            const response = await apiClient.get('/auth/me')
            user.value = response.data
        } catch (error) {
            console.error("Failed to fetch user profile", error)
            // If 401, logout logic is handled by interceptor, but we can double check
        }
    }

    async function login(email: string, password: string) {
        try {
            const formData = new FormData()
            formData.append('username', email)
            formData.append('password', password)

            const response = await apiClient.post('/auth/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })

            token.value = response.data.access_token
            if (token.value) {
                localStorage.setItem('access_token', token.value)
                await fetchUser() // Fetch profile immediately
            }

        } catch (error) {
            throw error
        }
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('access_token')
    }

    // Initialize: Fetch user if token exists
    if (token.value) {
        fetchUser()
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        logout,
        fetchUser
    }
})
