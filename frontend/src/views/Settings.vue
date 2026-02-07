<template>
    <MainLayout>
        <div class="settings-view">
            <!-- New Premium Header -->
            <div class="page-header-compact">
                <div class="header-left">
                    <h1 class="page-title">Settings</h1>
                    <div class="header-tabs">
                        <button class="tab-btn" :class="{ active: activeTab === 'general' }"
                            @click="activeTab = 'general'">
                            General
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'accounts' }"
                            @click="activeTab = 'accounts'">
                            Accounts
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'tenants' }"
                            @click="activeTab = 'tenants'">
                            Family
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'emails' }"
                            @click="activeTab = 'emails'">
                            Emails
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'">
                            AI Integration
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'devices' }"
                            @click="activeTab = 'devices'">
                            Devices
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'parser' }"
                            @click="activeTab = 'parser'">
                            Parser Engine
                        </button>
                    </div>
                </div>
            </div>

            <div>
                <GeneralSettings v-if="activeTab === 'general'" />
                <AccountsSettings v-if="activeTab === 'accounts'" />
                <EmailSettings v-if="activeTab === 'emails'" />
                <ParserSettings v-if="activeTab === 'parser'" />
                <FamilySettings v-if="activeTab === 'tenants'" />
                <AISettings v-if="activeTab === 'ai'" />
                <DevicesSettings v-if="activeTab === 'devices'" />
            </div>
        </div>
    </MainLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import GeneralSettings from './settings/GeneralSettings.vue'
import AccountsSettings from './settings/AccountsSettings.vue'
import EmailSettings from './settings/EmailSettings.vue'
import FamilySettings from './settings/FamilySettings.vue'
import AISettings from './settings/AISettings.vue'
import DevicesSettings from './settings/DevicesSettings.vue'
import ParserSettings from './settings/ParserSettings.vue'

const activeTab = ref('general')
</script>

<style scoped>
.settings-view {
    padding-bottom: 4rem;
}

/* Premium Header Styling */
.page-header-compact {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    gap: 1.5rem;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.page-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #111827;
    margin: 0;
    letter-spacing: -0.025em;
}

.header-tabs {
    display: flex;
    gap: 0.125rem;
    background: #f3f4f6;
    padding: 0.125rem;
    border-radius: 0.625rem;
}

.tab-btn {
    padding: 0.375rem 1rem;
    border: none;
    background: transparent;
    border-radius: 0.5rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-btn.active {
    background: white;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Transitions */
.animate-in {
    animation: slideUp 0.4s ease-out forwards;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
