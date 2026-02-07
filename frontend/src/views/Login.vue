<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Mail, Lock, ArrowRight, Loader2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showForgotDialog = ref(false)

async function handleLogin() {
    loading.value = true
    error.value = ''
    try {
        await authStore.login(email.value, password.value)
        router.push('/')
    } catch (e: any) {
        error.value = 'Invalid credentials'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <v-app>
        <v-main class="auth-page">
            <!-- Animated Background Mesh -->
            <div class="mesh-background">
                <div class="mesh-blob blob-1"></div>
                <div class="mesh-blob blob-2"></div>
                <div class="mesh-blob blob-3"></div>
            </div>

            <v-container class="auth-container" fluid>
                <v-row align="center" justify="center" class="fill-height">
                    <v-col cols="12" sm="8" md="4" lg="4">
                        <v-card class="glass-card auth-card" :class="{ 'shake': error }" elevation="0">
                            <div class="auth-header">
                                <v-avatar size="64" class="logo-wrapper" rounded="lg">
                                    <v-img src="/logo.png" alt="WealthFam Logo" cover></v-img>
                                </v-avatar>
                                <h1 class="welcome-title">Welcome Back</h1>
                                <p class="welcome-subtitle">Securely access your family wealth dashboard</p>
                            </div>

                            <v-form @submit.prevent="handleLogin" class="auth-form">
                                <v-text-field v-model="email" label="Email Address" placeholder="name@family.com"
                                    variant="outlined" color="primary" required hide-details="auto"
                                    class="premium-input">
                                    <template v-slot:prepend-inner>
                                        <Mail :size="20" class="input-icon" />
                                    </template>
                                </v-text-field>

                                <div class="password-group">
                                    <div class="label-row">
                                        <span class="custom-label">Password</span>
                                        <button type="button" class="forgot-link"
                                            @click="showForgotDialog = true">Forgot?</button>
                                    </div>
                                    <v-text-field v-model="password" placeholder="••••••••" variant="outlined"
                                        color="primary" type="password" required hide-details="auto"
                                        class="premium-input">
                                        <template v-slot:prepend-inner>
                                            <Lock :size="20" class="input-icon" />
                                        </template>
                                    </v-text-field>
                                </div>

                                <v-expand-transition>
                                    <v-alert v-if="error" type="error" variant="tonal" class="error-alert"
                                        density="compact">
                                        {{ error }}
                                    </v-alert>
                                </v-expand-transition>

                                <v-btn type="submit" color="primary" size="x-large" block class="btn-primary-glow"
                                    :loading="loading">
                                    <div class="btn-content">
                                        Sign In
                                        <ArrowRight :size="20" class="arrow-icon" />
                                    </div>
                                    <template v-slot:loader>
                                        <Loader2 :size="28" class="spinner" />
                                    </template>
                                </v-btn>
                            </v-form>

                            <div class="auth-footer">
                                <p>
                                    New to WealthFam?
                                    <router-link to="/register" class="signup-link">Create Family Account</router-link>
                                </p>
                            </div>
                        </v-card>

                        <div class="trust-footer">
                            <p>Enterprise-grade security for your family's future</p>
                        </div>
                    </v-col>
                </v-row>
            </v-container>

            <!-- Forgot Password Dialog -->
            <v-dialog v-model="showForgotDialog" max-width="400">
                <v-card class="glass-card pa-4" style="border-radius: 1.5rem !important;">
                    <v-card-title class="text-h5 font-weight-bold">Reset Password</v-card-title>
                    <v-card-text>
                        For security reasons, please contact your <strong>Family Administrator</strong> to reset your
                        password.
                        <br /><br />
                        If you are the administrator and lost access, please contact WealthFam support.
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="primary" variant="text" @click="showForgotDialog = false">Got it</v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-main>
    </v-app>
</template>

<style scoped>
.auth-page {
    position: relative;
    overflow: hidden;
    background: #f8fafc;
    min-height: 100vh;
    display: flex;
    align-items: center;
}

/* Mesh Background Animation */
.mesh-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 0;
    background: radial-gradient(circle at 50% 50%, #f1f5f9 0%, #e2e8f0 100%);
}

.mesh-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
}

.blob-1 {
    width: 600px;
    height: 600px;
    background: #4f46e5;
    top: -150px;
    left: -150px;
    animation: float 20s infinite alternate;
}

.blob-2 {
    width: 500px;
    height: 500px;
    background: #8b5cf6;
    bottom: -100px;
    right: -100px;
    animation: float 25s infinite alternate-reverse;
}

.blob-3 {
    width: 400px;
    height: 400px;
    background: #0ea5e9;
    top: 40%;
    right: 15%;
    animation: float 18s infinite alternate;
}

@keyframes float {
    0% {
        transform: translateY(0) scale(1);
    }

    100% {
        transform: translateY(40px) scale(1.1);
    }
}

.auth-container {
    position: relative;
    z-index: 10;
    padding: 1rem;
}

.auth-card {
    padding: 2.5rem;
    border-radius: 2rem !important;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1) !important;
}

.auth-header {
    text-align: center;
    margin-bottom: 2rem;
}

.logo-wrapper {
    background: white !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    margin-bottom: 1.5rem;
}

.welcome-title {
    font-size: 1.875rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin-bottom: 0.5rem;
}

.welcome-subtitle {
    color: #64748b;
    font-size: 0.875rem;
    font-weight: 500;
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.premium-input :deep(.v-field__outline) {
    --v-field-border-opacity: 0.1;
    border-radius: 0.75rem;
}

.premium-input :deep(.v-field--focused .v-field__outline) {
    --v-field-border-opacity: 1;
    box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

.input-icon {
    margin-right: 0.5rem;
    color: #94a3b8;
}

.password-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0.25rem;
}

.custom-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.forgot-link {
    font-size: 0.75rem;
    font-weight: 700;
    color: #4f46e5;
    text-decoration: none;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
}

.forgot-link:hover {
    text-decoration: underline;
}

.error-alert {
    border-radius: 0.5rem;
    margin-top: 0.5rem;
}

.btn-primary-glow {
    height: 3.5rem !important;
    border-radius: 0.75rem !important;
    font-size: 1.125rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    color: white !important;
    transition: all 0.2s !important;
}

.btn-primary-glow:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.arrow-icon {
    transition: transform 0.2s;
}

.btn-primary-glow:hover .arrow-icon {
    transform: translateX(4px);
}

.spinner {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.auth-footer {
    margin-top: 2.5rem;
    text-align: center;
}

.auth-footer p {
    font-size: 0.875rem;
    color: #64748b;
}

.signup-link {
    color: #4f46e5;
    font-weight: 700;
    text-decoration: none;
}

.signup-link:hover {
    text-decoration: underline;
}

.trust-footer {
    margin-top: 2rem;
    text-align: center;
    opacity: 0.6;
}

.trust-footer p {
    font-size: 0.625rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.2em;
}

.shake {
    animation: shake 0.5s cubic-bezier(.36, .07, .19, .97) both;
}

@keyframes shake {

    10%,
    90% {
        transform: translate3d(-1px, 0, 0);
    }

    20%,
    80% {
        transform: translate3d(2px, 0, 0);
    }

    30%,
    50%,
    70% {
        transform: translate3d(-4px, 0, 0);
    }

    40%,
    60% {
        transform: translate3d(4px, 0, 0);
    }
}

@media (max-width: 600px) {
    .auth-card {
        padding: 1.5rem;
    }
}
</style>
