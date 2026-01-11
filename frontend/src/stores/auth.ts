import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'
import type { AxiosError } from 'axios'

interface User {
    id: string
    email: string
    role: string
    tenant_id: string
}

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null)
    const token = ref<string | null>(localStorage.getItem('access_token'))
    const isAuthenticated = computed(() => !!token.value)

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
            }

            // Fetch user profile after login (requires implementing /auth/me or deducing from token)
            // For now we decode (or assume backend provides user info separately)

        } catch (error) {
            throw error
        }
    }

    function logout() {
        token.value = null
        user.value = null
        localStorage.removeItem('access_token')
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        logout
    }
})
