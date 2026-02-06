<template>
    <div class="tab-content animate-in">
        <!-- Search Bar -->
        <div class="account-control-bar mb-6">
            <div class="search-bar-premium no-margin" style="flex: 1; max-width: 300px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="search-icon">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="Search email accounts..." class="search-input">
            </div>
            <div class="header-with-badge" style="margin-left: auto; display: flex; align-items: center; gap: 0.75rem;">
                <h3
                    style="margin: 0; font-size: 1rem; font-weight: 700; color: var(--color-text-main); white-space: nowrap;">
                    Email Accounts</h3>
                <span class="pulse-status-badge" style="background: #ecfdf5; color: #047857;">{{
                    emailConfigs.length }} Total</span>
            </div>
        </div>

        <div v-if="syncStatus && syncStatus.status !== 'running'" :class="['sync-alert-premium', syncStatus.status]">
            <div class="alert-icon">
                {{ syncStatus.status === 'completed' ? '✅' : '❌' }}
            </div>
            <div class="alert-body">
                <strong>{{ syncStatus.status === 'completed' ? 'Sync Complete' : 'Sync Failed' }}</strong>
                <p>{{ syncStatus.message || `${syncStatus.stats?.processed} transactions processed.` }}</p>
            </div>
            <button @click="syncStatus = null" class="alert-close">✕</button>
        </div>

        <div class="email-grid">
            <div v-for="config in emailConfigs" :key="config.id" class="email-card-premium">
                <!-- Status Indicator Stripe (Thinner) -->
                <div class="status-stripe-compact" :class="{
                    'active': config.is_active,
                    'inactive': !config.is_active,
                    'auto-sync': config.auto_sync_enabled
                }"></div>

                <div class="p-4 flex flex-col h-full justify-between">
                    <!-- Horizontal Header -->
                    <div class="flex items-start justify-between mb-3">
                        <div class="flex items-center gap-2 overflow-hidden">
                            <div
                                class="w-8 h-8 rounded-full bg-indigo-50 flex items-center justify-center shrink-0 border border-indigo-100">
                                <span class="text-xs">
                                    {{familyMembers.find(u => u.id === config.user_id)?.avatar || '👤'}}
                                </span>
                            </div>
                            <div class="flex flex-col min-w-0">
                                <h3 class="text-sm font-bold truncate text-gray-800" :title="config.email">
                                    {{ config.email }}</h3>
                                <div class="flex items-center gap-2 text-[10px] text-muted">
                                    <span class="server-label-compact">{{ config.imap_server }}</span>
                                    <span v-if="config.auto_sync_enabled"
                                        class="text-green-600 font-bold flex items-center gap-0.5">
                                        <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                            stroke-width="3">
                                            <path d="M21 12a9 9 0 11-6.219-8.56" />
                                        </svg>
                                        Auto
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-center gap-1 shrink-0">
                            <button @click="openHistoryModal(config)"
                                class="p-1.5 rounded-md hover:bg-white text-gray-400 hover:text-indigo-600 transition-colors"
                                title="History">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </button>
                            <button @click="openEditEmailModal(config)"
                                class="p-1.5 rounded-md hover:bg-white text-gray-400 hover:text-indigo-600 transition-colors"
                                title="Settings">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                    <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Footer: Sync Info + Action -->
                    <div class="flex items-center justify-between mt-auto pt-3 border-t border-gray-50/50">
                        <div class="text-[10px] text-muted flex flex-col">
                            <span class="uppercase tracking-wider font-bold opacity-60">Last Sync</span>
                            <span v-if="config.last_sync_at">{{ formatDate(config.last_sync_at).meta }}
                                ({{ formatDate(config.last_sync_at).day }})</span>
                            <span v-else class="text-amber-600">Never</span>
                        </div>

                        <button @click="handleSync(config.id)" :disabled="syncStatus && syncStatus.status === 'running'"
                            class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5"
                            :class="syncStatus && syncStatus.status === 'running'
                                ? 'bg-indigo-50 text-indigo-400 cursor-wait'
                                : 'bg-white border border-gray-200 text-gray-700 hover:border-indigo-300 hover:text-indigo-700 shadow-sm hover:shadow'">
                            <svg v-if="syncStatus && syncStatus.status === 'running'" class="animate-spin" width="12"
                                height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                                <path d="M21 12a9 9 0 11-6.219-8.56" />
                            </svg>
                            <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2.5">
                                <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z" />
                            </svg>
                            {{ syncStatus && syncStatus.status === 'running' ? 'Scanning...' : 'Sync' }}
                        </button>
                    </div>
                </div>
            </div>

            <!-- Add New Email Card -->
            <div v-if="!searchQuery" class="glass-card add-account-card"
                @click="showEmailModal = true; editingEmailConfig = null">
                <div class="add-icon-circle">+</div>
                <span>Add Email Account</span>
            </div>

            <div v-if="emailConfigs.length === 0 && searchQuery" class="empty-placeholder">
                <p>No emails match "{{ searchQuery }}"</p>
            </div>
        </div>

        <!-- RECENT EMAIL SCAN LOGS -->
        <div
            class="activity-log-section mt-12 bg-white/30 backdrop-blur-md rounded-2xl border border-white/20 p-6 overflow-hidden">
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-4">
                    <h3 class="text-lg font-bold flex items-center gap-2">
                        <span class="bg-indigo-100 text-indigo-600 p-2 rounded-lg text-sm">📨</span>
                        Recent Scan Activity
                    </h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-[10px] text-muted font-mono bg-gray-100 px-2 py-1 rounded">Total: {{
                        emailLogPagination.total }}</span>
                    <button @click="fetchEmailLogs(undefined, true)" class="btn-icon-circle"
                        title="Refresh Log">🔄</button>
                </div>
            </div>

            <div class="overflow-x-auto min-h-[300px]">
                <table class="w-full text-left text-sm">
                    <thead class="text-muted border-b border-gray-100">
                        <tr>
                            <th class="pb-3 pr-4 font-semibold">Timestamp</th>
                            <th class="pb-3 pr-4 font-semibold">Account</th>
                            <th class="pb-3 pr-4 font-semibold">Status</th>
                            <th class="pb-3 pr-4 font-semibold">Items</th>
                            <th class="pb-3 pr-4 font-semibold">Message</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                        <tr v-for="log in emailLogs" :key="log.id" class="hover:bg-white/40 transition-colors group">
                            <td class="py-3 pr-4 whitespace-nowrap text-xs">
                                {{ formatDate(log.started_at).meta }}
                            </td>
                            <td class="py-3 pr-4 text-xs font-mono text-muted"
                                :title="emailConfigs.find(c => c.id === log.config_id)?.email">
                                {{(emailConfigs.find(c => c.id === log.config_id)?.email ||
                                    'Unknown').split('@')[0]}}
                            </td>
                            <td class="py-3 pr-4">
                                <span :class="{
                                    'text-emerald-600 bg-emerald-50': log.status === 'completed',
                                    'text-blue-600 bg-blue-50': log.status === 'running',
                                    'text-rose-600 bg-rose-50': log.status === 'error'
                                }" class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                    {{ log.status }}
                                </span>
                            </td>
                            <td class="py-3 pr-4 font-mono text-xs">
                                {{ log.items_processed || 0 }}
                            </td>
                            <td class="py-3 pr-4 max-w-xs truncate text-xs" :title="log.message">
                                {{ log.message }}
                            </td>
                        </tr>
                        <tr v-if="emailLogs.length === 0">
                            <td colspan="5" class="py-12 text-center text-muted italic">
                                <div class="flex flex-col items-center gap-2">
                                    <span class="text-2xl">📭</span>
                                    No scan history found.
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination Controls -->
            <div v-if="emailLogPagination.total > emailLogPagination.limit"
                class="mt-6 flex items-center justify-between border-t border-gray-100 pt-6">
                <span class="text-[10px] text-muted">
                    Showing {{ emailLogPagination.skip + 1 }} to {{ Math.min(emailLogPagination.skip +
                        emailLogPagination.limit, emailLogPagination.total) }} of {{ emailLogPagination.total }}
                </span>
                <div class="flex items-center gap-1">
                    <button @click="emailLogPagination.skip -= emailLogPagination.limit; fetchEmailLogs()"
                        :disabled="emailLogPagination.skip === 0"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Previous
                    </button>
                    <button @click="emailLogPagination.skip += emailLogPagination.limit; fetchEmailLogs()"
                        :disabled="emailLogPagination.skip + emailLogPagination.limit >= emailLogPagination.total"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Next
                    </button>
                </div>
            </div>
        </div>

        <!-- Email Config Modal - PREMIUM REDESIGN -->
        <div v-if="showEmailModal" class="modal-overlay-global" @click.self="showEmailModal = false">
            <div class="email-modal-premium">
                <!-- Modal Header -->
                <div class="email-modal-header">
                    <div class="header-icon-wrapper">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <path
                                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <div class="header-text">
                        <h2 class="email-modal-title">{{ emailModalTitle }}</h2>
                        <p class="email-modal-subtitle">{{ emailModalSubtitle }}</p>
                    </div>
                    <button class="email-modal-close" @click="showEmailModal = false">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                <form @submit.prevent="saveEmailConfig" class="email-modal-form">
                    <!-- Connection Details Section -->
                    <div class="modal-section">
                        <div class="section-header">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M21 12h-8m8 0a9 9 0 11-18 0 9 9 0 0118 0zM8 12V8l4-4 4 4v4" />
                            </svg>
                            <h3>Connection Details</h3>
                        </div>

                        <div class="form-grid grid-2">
                            <div class="form-field">
                                <label>Email Address</label>
                                <div class="input-with-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2" class="input-icon">
                                        <path
                                            d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                                        <polyline points="22,6 12,13 2,6" />
                                    </svg>
                                    <input v-model="emailForm.email" class="premium-input" required
                                        placeholder="name@gmail.com" />
                                </div>
                            </div>

                            <div class="form-field">
                                <label>App Password</label>
                                <div class="input-with-icon">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2" class="input-icon">
                                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                                        <path d="M7 11V7a5 5 0 0110 0v4" />
                                    </svg>
                                    <input type="password" v-model="emailForm.password" class="premium-input" required
                                        placeholder="•••• •••• •••• ••••" />
                                </div>
                            </div>

                            <div class="form-field">
                                <label>IMAP Server</label>
                                <input v-model="emailForm.host" class="premium-input" required
                                    placeholder="imap.gmail.com" />
                            </div>

                            <div class="form-field">
                                <label>Folder</label>
                                <input v-model="emailForm.folder" class="premium-input" placeholder="INBOX" />
                            </div>
                        </div>

                        <div class="field-hint">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="16" x2="12" y2="12" />
                                <line x1="12" y1="8" x2="12.01" y2="8" />
                            </svg>
                            Use a generated <strong>App Password</strong>, not your main password.
                        </div>
                    </div>

                    <!-- Assignment Section -->
                    <div class="modal-section">
                        <div class="section-header">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                            <h3>Ownership & Automation</h3>
                        </div>

                        <div class="form-grid grid-2">
                            <div class="form-field">
                                <label>Assign to Family Member</label>
                                <CustomSelect v-model="emailForm.user_id as any" :options="[
                                    { label: '👤 Unassigned (Self)', value: null as any },
                                    ...familyMembers.map(m => ({ label: `${m.avatar || '👤'} ${m.full_name || m.email}`, value: (m.id as any) }))
                                ]" placeholder="Select inbox owner" />
                            </div>

                            <div class="toggle-field-premium">
                                <div class="toggle-content">
                                    <div class="toggle-icon-wrapper active">
                                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                                            stroke="currentColor" stroke-width="2">
                                            <path d="M21 12a9 9 0 11-6.219-8.56" />
                                        </svg>
                                    </div>
                                    <div class="toggle-info">
                                        <span class="toggle-title">Auto Sync</span>
                                    </div>
                                </div>
                                <label class="switch-premium">
                                    <input type="checkbox" v-model="emailForm.auto_sync">
                                    <span class="slider-premium"></span>
                                </label>
                            </div>
                        </div>

                        <div class="field-hint">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <polyline points="20 6 9 17 4 12" />
                            </svg>
                            Imported transactions will automatically assign to the owner. Syncs every 15 mins.
                        </div>
                    </div>

                    <!-- Advanced Actions (Edit Mode Only) -->
                    <div v-if="editingEmailConfig" class="advanced-actions-section">
                        <div class="advanced-actions-header">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <circle cx="12" cy="12" r="1" />
                                <circle cx="12" cy="5" r="1" />
                                <circle cx="12" cy="19" r="1" />
                            </svg>
                            <span>Advanced & History Controls</span>
                        </div>

                        <div class="form-grid grid-2 mb-2">
                            <div class="form-field">
                                <label>Custom Sync Point</label>
                                <input type="datetime-local" v-model="emailForm.last_sync_at" class="premium-input"
                                    style="height: 40px;" />
                            </div>
                            <div class="advanced-actions-buttons" style="align-self: flex-end; gap: 0.5rem;">
                                <button type="button" @click="rewindSync(3)" class="btn-advanced"
                                    style="height: 40px; flex: 1;" title="Rescan last 3 hours">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2">
                                        <polyline points="1 4 1 10 7 10" />
                                        <path d="M3.51 15a9 9 0 102.13-9.36L1 10" />
                                    </svg>
                                    Rewind 3h
                                </button>
                                <button type="button" @click="resetSyncHistory" class="btn-advanced"
                                    style="height: 40px; flex: 1;" title="Reset all history tracking">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                        stroke-width="2">
                                        <path d="M21 12a9 9 0 11-6.219-8.56" />
                                        <path d="M12 7v5l3 3" />
                                    </svg>
                                    Reset
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Modal Footer -->
                    <div class="email-modal-footer">
                        <button v-if="editingEmailConfig" type="button" @click="deleteEmailConfig(editingEmailConfig)"
                            class="btn-advanced danger mr-auto">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                            </svg>
                            Remove Configuration
                        </button>
                        <button type="button" @click="showEmailModal = false"
                            class="btn-secondary-premium">Cancel</button>
                        <button type="submit" class="btn-primary-premium">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <polyline points="20 6 9 17 4 12" />
                            </svg>
                            {{ editingEmailConfig ? 'Update Configuration' : 'Connect Account' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Sync History Modal -->
        <div v-if="showHistoryModal" class="modal-overlay-global">
            <div class="modal-global modal-lg glass">
                <div class="modal-header">
                    <h2 class="modal-title">Sync History</h2>
                    <button class="btn-icon-circle" @click="showHistoryModal = false">✕</button>
                </div>

                <div class="history-list p-4">
                    <div v-if="syncLogs.length === 0" class="empty-state-small text-center py-8 text-muted italic">No
                        logs
                        found.</div>
                    <table v-else class="compact-table w-full text-left text-sm">
                        <thead class="border-b border-gray-100">
                            <tr>
                                <th class="pb-2">Status</th>
                                <th class="pb-2">Time</th>
                                <th class="pb-2">Items</th>
                                <th class="pb-2">Message</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-50">
                            <tr v-for="log in syncLogs" :key="log.id" class="hover:bg-gray-50/50 transition-colors">
                                <td class="py-2 text-center">{{ getLogIcon(log.status) }}</td>
                                <td class="py-2 text-xs">{{ formatDateFull(log.started_at) }}</td>
                                <td class="py-2 text-xs font-mono">{{ log.items_processed || 0 }}</td>
                                <td class="py-2 text-xs text-muted truncate max-w-xs" :title="log.message">{{
                                    log.message
                                }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="modal-footer">
                    <button type="button" @click="showHistoryModal = false" class="btn-secondary">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import CustomSelect from '@/components/CustomSelect.vue'

// --- Internal State ---
const emailConfigs = ref<any[]>([])
const familyMembers = ref<any[]>([])
const searchQuery = ref('')
const loading = ref(false)

const notify = useNotificationStore()

const showEmailModal = ref(false)
const editingEmailConfig = ref<string | null>(null)
const showHistoryModal = ref(false)
const syncLogs = ref<any[]>([])
const selectedHistoryConfigId = ref<string | null>(null)
const isSyncing = ref(false)
const syncStatus = ref<any>(null)

const emailForm = ref({
    email: '',
    password: '',
    host: 'imap.gmail.com',
    folder: 'INBOX',
    auto_sync: false,
    user_id: null as string | null,
    last_sync_at: '' as string // For custom date/time setting
})

// Email Logs State
const emailLogs = ref<any[]>([])
const emailLogPagination = ref({ total: 0, limit: 10, skip: 0 })

// --- Computed ---
const emailModalTitle = computed(() => editingEmailConfig.value ? 'Edit Email Configuration' : 'Connect Email Account')
const emailModalSubtitle = computed(() => editingEmailConfig.value ? 'Update your email sync settings' : 'Link your bank email for automatic transaction imports')

// --- Methods ---
const fetchEmailLogs = async (configId?: string, resetSkip = false) => {
    try {
        if (resetSkip) emailLogPagination.value.skip = 0
        const res = await financeApi.getEmailLogs({
            limit: emailLogPagination.value.limit,
            skip: emailLogPagination.value.skip,
            config_id: configId
        })
        emailLogs.value = res.data.items
        emailLogPagination.value.total = res.data.total
    } catch (e) {
        console.error("Failed to fetch email logs", e)
    }
}

async function handleSync(configId: string) {
    isSyncing.value = true
    syncStatus.value = { status: 'running', configId }
    try {
        const res = await financeApi.syncEmailConfig(configId)
        syncStatus.value = { ...res.data, configId }
        if (res.data.status === 'completed') {
            fetchEmailLogs(undefined, true)
            fetchEmailLogs(undefined, true)
            fetchData()
        }
    } catch (e: any) {
        syncStatus.value = { status: 'error', message: e.response?.data?.detail || "Sync failed", configId }
    } finally {
        isSyncing.value = false
    }
}

async function saveEmailConfig() {
    try {
        const payload: any = {
            email: emailForm.value.email,
            password: emailForm.value.password,
            imap_server: emailForm.value.host,
            folder: emailForm.value.folder,
            auto_sync_enabled: emailForm.value.auto_sync,
            user_id: emailForm.value.user_id
        }

        if (emailForm.value.last_sync_at) {
            payload.last_sync_at = new Date(emailForm.value.last_sync_at).toISOString()
        }

        if (editingEmailConfig.value) {
            await financeApi.updateEmailConfig(editingEmailConfig.value, payload)
            notify.success("Email configuration updated")
        } else {
            await financeApi.createEmailConfig(payload)
            notify.success("Email configuration added")
        }

        showEmailModal.value = false
        emailForm.value = { email: '', password: '', host: 'imap.gmail.com', folder: 'INBOX', auto_sync: false, user_id: null, last_sync_at: '' }
        fetchData()
    } catch (e) {
        notify.error("Failed to save email config")
    }
}

function openEditEmailModal(config: any) {
    emailForm.value = {
        email: config.email,
        password: config.password,
        host: config.imap_server,
        folder: config.folder,
        auto_sync: config.auto_sync_enabled || false,
        user_id: config.user_id || null,
        last_sync_at: config.last_sync_at ? new Date(config.last_sync_at).toISOString().slice(0, 16) : ''
    }
    editingEmailConfig.value = config.id
    showEmailModal.value = true
}

async function rewindSync(hours: number) {
    if (!editingEmailConfig.value) return
    const configId = editingEmailConfig.value

    const now = new Date()
    now.setHours(now.getHours() - hours)

    try {
        await financeApi.updateEmailConfig(configId, { last_sync_at: now.toISOString() })
        notify.info(`Rewound config. Triggering sync...`)
        showEmailModal.value = false
        await handleSync(configId)
        fetchData()
    } catch (e) {
        notify.error("Failed to rewind sync")
    }
}

async function resetSyncHistory() {
    if (!editingEmailConfig.value) return
    const configId = editingEmailConfig.value
    if (!confirm("This will force a DEEP SCAN of ALL emails. This takes time. Continue?")) return
    try {
        await financeApi.updateEmailConfig(configId, { reset_sync_history: true })
        notify.info("Deep scan requested. Starting...")
        showEmailModal.value = false
        await handleSync(configId)
        fetchData()
    } catch (e) {
        notify.error("Failed to reset sync history")
    }
}

async function deleteEmailConfig(id: string) {
    if (!confirm("Are you sure you want to remove this email account? This will stop future syncs.")) return
    try {
        await financeApi.deleteEmailConfig(id)
        notify.success("Email account removed")
        showEmailModal.value = false
        fetchData()
    } catch (e) {
        notify.error("Failed to remove email config")
    }
}

async function openHistoryModal(config: any) {
    selectedHistoryConfigId.value = config.id
    showHistoryModal.value = true
    syncLogs.value = []
    try {
        const res = await financeApi.getEmailSyncLogs(config.id)
        syncLogs.value = res.data
    } catch (e) {
        notify.error("Failed to fetch logs")
    }
}

function formatDate(dateStr: string) {
    if (!dateStr) return { day: 'N/A', meta: '' }
    const d = new Date(dateStr)
    return {
        day: d.toLocaleDateString(),
        meta: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        full: d.toLocaleString()
    }
}

function formatDateFull(dateStr: string) {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString()
}

const getLogIcon = (status: string) => {
    if (status === 'completed') return '✅'
    if (status === 'error') return '❌'
    return '⏳'
}

onMounted(() => {
    fetchEmailLogs()
    fetchData()
})

const fetchData = async () => {
    loading.value = true
    try {
        const [emailRes, usersRes] = await Promise.all([
            financeApi.getEmailConfigs(),
            financeApi.getUsers()
        ])
        emailConfigs.value = emailRes.data
        familyMembers.value = usersRes.data
    } catch (e) {
        console.error("Failed to fetch email settings", e)
        notify.error("Failed to load email settings")
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
/* ==================== PREMIUM EMAIL CARDS ==================== */
.email-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
}

.email-card-premium {
    position: relative;
    background: white;
    border-radius: 1rem;
    border: 1px solid #e5e7eb;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.email-card-premium:hover {
    border-color: #d1d5db;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.status-stripe-compact {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #10b981, #34d399);
    opacity: 0.8;
}

.status-stripe-compact.inactive {
    background: linear-gradient(180deg, #9ca3af, #d1d5db);
    opacity: 0.5;
}

.status-stripe-compact.auto-sync {
    background: linear-gradient(180deg, #6366f1, #818cf8, #6366f1);
    background-size: 100% 200%;
    animation: gradient-slide-v 3s ease infinite;
}

@keyframes gradient-slide-v {

    0%,
    100% {
        background-position: 50% 0%;
    }

    50% {
        background-position: 50% 100%;
    }
}

.server-label-compact {
    font-size: 0.65rem;
    color: #6b7280;
    font-weight: 600;
    background: #f3f4f6;
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
}

.sync-alert-premium {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.25rem;
    border-radius: 1rem;
    margin-bottom: 1.5rem;
    border-left: 4px solid;
}

.sync-alert-premium.completed {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-left-color: #10b981;
}

.sync-alert-premium.error {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border-left-color: #ef4444;
}

.alert-icon {
    font-size: 1.5rem;
}

.alert-body {
    flex: 1;
}

.alert-body strong {
    display: block;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
}

.alert-body p {
    margin: 0;
    font-size: 0.875rem;
    color: #6b7280;
}

.alert-close {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.05);
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background 0.2s;
    color: #6b7280;
}

.add-account-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px dashed #e5e7eb;
    color: #6b7280;
    gap: 0.5rem;
    border-radius: 1rem;
}

.add-account-card:hover {
    border-color: #4f46e5;
    color: #4f46e5;
    background: #f5f3ff;
}

.add-icon-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
}

.btn-icon-circle {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    border: 1px solid #e5e7eb;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.text-muted {
    color: #6b7280;
}

.animate-spin {
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

.account-control-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.search-bar-premium {
    position: relative;
    width: 100%;
}

.search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
}

.search-input {
    width: 100%;
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
}

.search-input:focus {
    outline: none;
    border-color: #4f46e5;
}

.pulse-status-badge {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 9999px;
    font-weight: 700;
}

/* EMAIL MODAL PREMIUM STYLES */
.email-modal-premium {
    background: white;
    border-radius: 1.5rem;
    width: 95%;
    max-width: 650px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    position: relative;
    animation: modalSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.email-modal-header {
    padding: 1.5rem 2rem;
    border-bottom: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
}

.header-icon-wrapper {
    width: 48px;
    height: 48px;
    background: #f5f3ff;
    color: #6366f1;
    border-radius: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-text {
    flex: 1;
}

.email-modal-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
}

.email-modal-subtitle {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0;
}

.email-modal-close {
    width: 32px;
    height: 32px;
    border-radius: 0.75rem;
    border: 1px solid #e2e8f0;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
}

.email-modal-close:hover {
    background: #f8fafc;
    color: #ef4444;
    border-color: #fee2e2;
}

.email-modal-form {
    padding: 1.5rem 2rem;
}

.modal-section {
    margin-bottom: 2rem;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f1f5f9;
}

.section-header h3 {
    font-size: 0.8125rem;
    font-weight: 700;
    color: #475569;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.form-grid {
    display: grid;
    gap: 1rem;
}

.grid-2 {
    grid-template-columns: repeat(2, 1fr);
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
}

.form-field label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #4b5563;
    margin-left: 0.25rem;
}

.input-with-icon {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
}

.premium-input {
    width: 100%;
    padding: 0.75rem 1rem;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 0.75rem;
    font-size: 0.875rem;
    transition: all 0.2s;
}

.premium-input:focus {
    outline: none;
    border-color: #6366f1;
    background: white;
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.input-with-icon .premium-input {
    padding-left: 2.75rem;
}

.field-hint {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.5rem;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 0.75rem;
}

.toggle-field-premium {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.25rem;
    background: #f8fafc;
    border-radius: 1rem;
    border: 1px solid #e2e8f0;
}

.toggle-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.toggle-icon-wrapper {
    width: 32px;
    height: 32px;
    background: white;
    border-radius: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #e2e8f0;
}

.toggle-icon-wrapper.active {
    color: #6366f1;
    background: #f5f3ff;
    border-color: #ddd6fe;
}

.toggle-title {
    font-size: 0.875rem;
    font-weight: 700;
    color: #1e293b;
}

.switch-premium {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
}

.switch-premium input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider-premium {
    position: absolute;
    cursor: pointer;
    inset: 0;
    background: #e2e8f0;
    transition: .4s;
    border-radius: 34px;
}

.slider-premium:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background: white;
    transition: .4s;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

input:checked+.slider-premium {
    background: #6366f1;
}

input:checked+.slider-premium:before {
    transform: translateX(20px);
}

.advanced-actions-section {
    background: #f8fafc;
    border-radius: 1rem;
    padding: 1.25rem;
    border: 1px dashed #cbd5e1;
}

.advanced-actions-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

.btn-advanced {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 0 1rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-advanced:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
}

.btn-advanced.danger {
    color: #ef4444;
    border-color: #fee2e2;
}

.btn-advanced.danger:hover {
    background: #fef2f2;
}

.email-modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 1rem;
    padding: 1.25rem 2rem;
    border-top: 1px solid #f1f5f9;
    background: #f8fafc;
    position: sticky;
    bottom: 0;
}

.btn-secondary-premium {
    height: 40px;
    padding: 0 1.5rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
}

.btn-primary-premium {
    height: 40px;
    padding: 0 1.5rem;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

@keyframes modalSlideUp {
    from {
        transform: translateY(20px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}
</style>
