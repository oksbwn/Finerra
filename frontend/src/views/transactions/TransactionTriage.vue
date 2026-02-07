<script setup lang="ts">
import { ref, computed } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'
import { useCurrency } from '@/composables/useCurrency'

const { formatAmount } = useCurrency()

// Props
const props = defineProps<{
    activeSubTab: 'pending' | 'training'
    accounts: any[]
    categories: any[]
    triageTransactions: any[]
    triagePagination: { total: number; limit: number; skip: number }
    triageSearchQuery: string
    triageSourceFilter: string
    triageSortKey: string
    triageSortOrder: 'asc' | 'desc'
    unparsedMessages: any[]
    trainingPagination: { total: number; limit: number; skip: number }
    trainingSortKey: string
    trainingSortOrder: 'asc' | 'desc'
}>()

// Emits
const emit = defineEmits<{
    'update:activeSubTab': [value: 'pending' | 'training']
    'update:triageSearchQuery': [value: string]
    'update:triageSourceFilter': [value: string]
    'update:triageSortKey': [value: string]
    'update:triageSortOrder': [value: 'asc' | 'desc']
    'update:triagePagination': [value: { total: number; limit: number; skip: number }]
    'update:trainingSortKey': [value: string]
    'update:trainingSortOrder': [value: 'asc' | 'desc']
    'update:trainingPagination': [value: { total: number; limit: number; skip: number }]
    'approveTriage': [txn: any]
    'rejectTriage': [id: string]
    'bulkRejectTriage': []
    'startLabeling': [msg: any]
    'dismissTraining': [id: string]
    'bulkDismissTraining': []
    'refreshTriage': []
}>()

// Local State
const selectedTriageIds = defineModel<string[]>('selectedTriageIds', { default: [] })
const selectedTrainingIds = defineModel<string[]>('selectedTrainingIds', { default: [] })
const expandedTrainingIds = ref(new Set<string>())

// Computed
const accountOptions = computed(() => {
    return props.accounts.map(a => ({ label: a.name, value: a.id }))
})

const categoryOptions = computed(() => {
    const list: any[] = []
    const flatten = (cats: any[], depth = 0) => {
        cats.forEach(c => {
            const prefix = depth > 0 ? '　'.repeat(depth) + '└ ' : ''
            list.push({
                label: `${prefix}${c.icon || '🏷️'} ${c.name}`,
                value: c.name
            })
            if (c.subcategories && c.subcategories.length > 0) {
                flatten(c.subcategories, depth + 1)
            }
        })
    }
    flatten(props.categories)
    if (!list.find(o => o.value === 'Uncategorized')) {
        list.push({ label: '🏷️ Uncategorized', value: 'Uncategorized' })
    }
    return list
})

const filteredTriageTransactions = computed(() => {
    let filtered = props.triageTransactions

    if (props.triageSearchQuery) {
        const q = props.triageSearchQuery.toLowerCase()
        filtered = filtered.filter(t =>
            (t.recipient && t.recipient.toLowerCase().includes(q)) ||
            (t.description && t.description.toLowerCase().includes(q)) ||
            (t.external_id && t.external_id.toLowerCase().includes(q)) ||
            (t.amount && String(t.amount).includes(q))
        )
    }

    if (props.triageSourceFilter && props.triageSourceFilter !== 'ALL') {
        filtered = filtered.filter(t => t.source === props.triageSourceFilter)
    }

    return filtered
})

const sortedTrainingMessages = computed(() => {
    const sorted = [...props.unparsedMessages]
    sorted.sort((a, b) => {
        let aVal, bVal
        if (props.trainingSortKey === 'created_at') {
            aVal = new Date(a.created_at).getTime()
            bVal = new Date(b.created_at).getTime()
        } else if (props.trainingSortKey === 'sender') {
            aVal = (a.sender || '').toLowerCase()
            bVal = (b.sender || '').toLowerCase()
        } else {
            return 0
        }

        if (props.trainingSortOrder === 'asc') {
            return aVal > bVal ? 1 : -1
        } else {
            return aVal < bVal ? 1 : -1
        }
    })
    return sorted
})

// Methods
function getAccountName(id: string) {
    const acc = props.accounts.find(a => a.id === id)
    return acc ? acc.name : 'Unknown Account'
}

function formatDate(dateStr: string) {
    if (!dateStr) return { day: 'N/A', meta: '' }

    const d = new Date(dateStr)
    if (isNaN(d.getTime())) {
        return { day: '?', meta: dateStr.split('T')[0] || dateStr }
    }

    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    const time = d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

    if (d.toDateString() === today.toDateString()) {
        return { day: 'Today', meta: time }
    }
    if (d.toDateString() === yesterday.toDateString()) {
        return { day: 'Yesterday', meta: time }
    }

    const currentYear = today.getFullYear()
    const txnYear = d.getFullYear()

    let formatOptions: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' }
    if (txnYear !== currentYear) {
        formatOptions.year = 'numeric'
    }

    const monthDay = d.toLocaleDateString('en-US', formatOptions)
    return {
        day: monthDay,
        meta: time
    }
}

function toggleSelectAllTriage() {
    if (selectedTriageIds.value.length === filteredTriageTransactions.value.length && filteredTriageTransactions.value.length > 0) {
        selectedTriageIds.value = []
    } else {
        selectedTriageIds.value = filteredTriageTransactions.value.map(t => t.id)
    }
}

function toggleSelectAllTraining() {
    if (selectedTrainingIds.value.length === props.unparsedMessages.length && props.unparsedMessages.length > 0) {
        selectedTrainingIds.value = []
    } else {
        selectedTrainingIds.value = props.unparsedMessages.map(m => m.id)
    }
}

function toggleTrainingExpand(id: string) {
    if (expandedTrainingIds.value.has(id)) {
        expandedTrainingIds.value.delete(id)
    } else {
        expandedTrainingIds.value.add(id)
    }
}

function handleTriagePaginationLimitChange(newLimit: number) {
    emit('update:triagePagination', { ...props.triagePagination, limit: newLimit, skip: 0 })
}

function handleTriagePaginationPrev() {
    emit('update:triagePagination', { ...props.triagePagination, skip: props.triagePagination.skip - props.triagePagination.limit })
}

function handleTriagePaginationNext() {
    emit('update:triagePagination', { ...props.triagePagination, skip: props.triagePagination.skip + props.triagePagination.limit })
}

function handleTrainingPaginationLimitChange(newLimit: number) {
    emit('update:trainingPagination', { ...props.trainingPagination, limit: newLimit, skip: 0 })
}

function handleTrainingPaginationPrev() {
    emit('update:trainingPagination', { ...props.trainingPagination, skip: props.trainingPagination.skip - props.trainingPagination.limit })
}

function handleTrainingPaginationNext() {
    emit('update:trainingPagination', { ...props.trainingPagination, skip: props.trainingPagination.skip + props.trainingPagination.limit })
}
</script>

<template>
    <div class="triage-view animate-in">
        <div class="triage-tabs mb-6">
            <button class="triage-tab-btn" :class="{ active: activeSubTab === 'pending' }"
                @click="emit('update:activeSubTab', 'pending')">
                Pending Inbox ({{ triagePagination.total }})
            </button>
            <button class="triage-tab-btn" :class="{ active: activeSubTab === 'training' }"
                @click="emit('update:activeSubTab', 'training')">
                Training Area ({{ trainingPagination.total }})
            </button>
        </div>

        <div v-if="activeSubTab === 'pending'">
            <div class="alert-info-glass mb-4">
                <div class="alert-icon">🔒</div>
                <div class="alert-text">
                    <strong>Review Intake</strong>: These transactions were auto-detected but require
                    categorization or confirmation before affecting your balance.
                </div>
            </div>

            <div class="triage-filter-bar mb-4">
                <div class="triage-search-box">
                    <span class="search-icon-mini">🔍</span>
                    <input type="text" :value="triageSearchQuery"
                        @input="emit('update:triageSearchQuery', ($event.target as HTMLInputElement).value)"
                        placeholder="Search by merchant, ID or amount..." class="triage-search-input-premium">
                </div>

                <div class="source-toggle-group">
                    <button class="source-chip" :class="{ active: triageSourceFilter === 'ALL' }"
                        @click="emit('update:triageSourceFilter', 'ALL')">All Sources</button>
                    <button class="source-chip" :class="{ active: triageSourceFilter === 'SMS' }"
                        @click="emit('update:triageSourceFilter', 'SMS')">SMS</button>
                    <button class="source-chip" :class="{ active: triageSourceFilter === 'EMAIL' }"
                        @click="emit('update:triageSourceFilter', 'EMAIL')">Email</button>
                </div>

                <!-- Sort Controls Pending -->
                <div class="flex items-center gap-2 ml-auto">
                    <CustomSelect :modelValue="triageSortKey" @update:modelValue="emit('update:triageSortKey', $event)"
                        :options="[{ label: 'Date', value: 'date' }, { label: 'Amount', value: 'amount' }, { label: 'Description', value: 'description' }]"
                        class="w-32 text-xs" />
                    <button @click="emit('update:triageSortOrder', triageSortOrder === 'asc' ? 'desc' : 'asc')"
                        class="btn-icon-circle-small bg-white border border-gray-200" title="Toggle Order">
                        {{ triageSortOrder === 'asc' ? '↑' : '↓' }}
                    </button>
                </div>
            </div>

            <div class="bulk-action-bar-triage mb-4 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <label class="flex items-center gap-2 cursor-pointer text-xs font-bold text-muted">
                        <input type="checkbox" @change="toggleSelectAllTriage"
                            :checked="selectedTriageIds.length === filteredTriageTransactions.length && filteredTriageTransactions.length > 0"
                            class="rounded border-gray-300 text-indigo-600" />
                        Select All Filtered
                    </label>
                    <button v-if="selectedTriageIds.length > 0" @click="emit('bulkRejectTriage')"
                        class="bg-rose-50 text-rose-600 px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-2">
                        🗑️ Discard {{ selectedTriageIds.length }}
                    </button>
                </div>
                <button @click="emit('refreshTriage')" class="btn-icon-circle-small">🔄</button>
            </div>

            <div class="triage-grid">
                <div v-for="txn in filteredTriageTransactions" :key="txn.id" class="glass-card triage-card"
                    :class="[txn.amount < 0 ? 'debit-theme' : 'credit-theme', { 'is-transfer-active': txn.is_transfer, 'selected': selectedTriageIds.includes(txn.id) }]">
                    <div class="triage-card-header">
                        <div class="header-left">
                            <input type="checkbox" v-model="selectedTriageIds" :value="txn.id" class="mr-2" />
                            <span class="source-tag" :class="txn.source.toLowerCase()">{{ txn.source }}</span>
                            <span v-if="txn.is_ai_parsed" class="ai-badge-mini pulse"
                                title="Extracted using Gemini AI">✨ AI Verified</span>
                            <span v-if="txn.is_transfer" class="transfer-badge-mini"
                                title="Auto-detected as internal transfer">🔄 Self-Transfer</span>
                        </div>
                        <span class="triage-date">{{ formatDate(txn.date).day }} <span class="date-sep">•</span>
                            {{ formatDate(txn.date).meta }}</span>
                    </div>

                    <div class="triage-card-body">
                        <div class="triage-main-content">
                            <div class="triage-amount-display" :class="txn.amount < 0 ? 'expense' : 'income'">
                                <div class="amount-val">{{ formatAmount(Math.abs(txn.amount)) }}</div>
                                <div class="amount-indicator">{{ txn.amount < 0 ? 'Debit' : 'Credit' }}</div>
                                </div>

                                <div class="triage-details-info">
                                    <h3 class="triage-title">{{ txn.recipient || txn.description }}</h3>
                                    <div class="triage-account-info">
                                        <span class="acc-indicator"></span>
                                        {{ getAccountName(txn.account_id) }}
                                    </div>
                                </div>
                            </div>

                            <div class="triage-meta-pills">
                                <div class="meta-pill" v-if="txn.description">
                                    <span class="pill-icon">📝</span> {{ txn.description }}
                                </div>
                                <div class="meta-pill" v-if="txn.external_id">
                                    <span class="pill-icon">🆔</span> {{ txn.external_id }}
                                </div>
                                <div class="meta-pill highlight" v-if="txn.balance">
                                    <span class="pill-icon">💰</span> Bal: ₹{{ txn.balance.toFixed(2) }}
                                </div>
                            </div>

                            <div v-if="txn.raw_message" class="triage-raw-box">
                                <div class="raw-label">Origin Message</div>
                                <div class="raw-content-text">{{ txn.raw_message }}</div>
                            </div>
                        </div>

                        <div class="triage-card-actions">
                            <div class="action-top-row">
                                <div class="triage-input-group">
                                    <div class="toggle-control">
                                        <label class="premium-switch">
                                            <input type="checkbox" v-model="txn.is_transfer"
                                                @change="txn.exclude_from_reports = txn.is_transfer">
                                            <span class="premium-slider"></span>
                                        </label>
                                        <span class="toggle-text">{{ txn.is_transfer ? 'Internal Transfer' :
                                            'Expense/Income' }}</span>
                                    </div>

                                    <div class="toggle-control">
                                        <label class="premium-switch">
                                            <input type="checkbox" v-model="txn.exclude_from_reports">
                                            <span class="premium-slider" style="background-color: #fee2e2;"></span>
                                        </label>
                                        <span class="toggle-text" style="color: #991b1b;">Exclude from
                                            Reports</span>
                                    </div>

                                    <div class="select-container">
                                        <CustomSelect v-if="txn.is_transfer" v-model="txn.to_account_id"
                                            :options="accountOptions.filter(a => a.value !== txn.account_id)"
                                            :placeholder="txn.amount < 0 ? 'To Account (Tracked)' : 'From Account (Tracked)'"
                                            class="triage-select-premium" />
                                        <CustomSelect v-else v-model="txn.category" :options="categoryOptions"
                                            placeholder="Assign Category" class="triage-select-premium" />
                                    </div>
                                </div>
                            </div>

                            <div class="action-bottom-row">
                                <button @click="emit('rejectTriage', txn.id)"
                                    class="btn-triage-secondary">Discard</button>

                                <div class="approval-cluster">
                                    <button @click="emit('approveTriage', txn)" class="btn-triage-primary">
                                        Confirm Entry
                                        <span class="btn-shimmer"></span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div v-if="triagePagination.total === 0" class="empty-state-triage">
                        <div class="empty-glow-icon">✨</div>
                        <h3>Inbox zero!</h3>
                        <p>No new transactions waiting for review.</p>
                    </div>

                    <!-- Triage Pagination & Page Size -->
                    <div v-if="triagePagination.total > 0"
                        class="mt-6 flex items-center justify-between border-t border-gray-100 pt-6">
                        <div class="flex items-center gap-4">
                            <span class="text-[10px] text-muted font-mono">
                                {{ triagePagination.skip + 1 }}–{{ Math.min(triagePagination.skip +
                                    triagePagination.limit,
                                    triagePagination.total) }} of {{ triagePagination.total }}
                            </span>
                            <div class="flex items-center gap-2">
                                <span class="text-[10px] text-muted uppercase font-bold tracking-wider">Size:</span>
                                <select :value="triagePagination.limit"
                                    @change="handleTriagePaginationLimitChange(Number(($event.target as HTMLSelectElement).value))"
                                    class="text-[10px] bg-white border border-gray-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-bold text-slate-700">
                                    <option :value="10">10</option>
                                    <option :value="20">20</option>
                                    <option :value="50">50</option>
                                    <option :value="100">100</option>
                                </select>
                            </div>
                        </div>
                        <div class="flex items-center gap-1" v-if="triagePagination.total > triagePagination.limit">
                            <button @click="handleTriagePaginationPrev" :disabled="triagePagination.skip === 0"
                                class="btn-pagination-compact">Prev</button>
                            <button @click="handleTriagePaginationNext"
                                :disabled="triagePagination.skip + triagePagination.limit >= triagePagination.total"
                                class="btn-pagination-compact">Next</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Training Area -->
            <div v-if="activeSubTab === 'training'">
                <div class="alert-info-glass mb-4 training-alert">
                    <div class="alert-icon">🤖</div>
                    <div class="alert-text">
                        <strong>Interactive Training</strong>: These messages look like transactions but could
                        not be parsed. Label them to help the system learn!
                    </div>
                </div>

                <div class="bulk-action-bar-training mb-4 flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <label class="flex items-center gap-2 cursor-pointer text-xs font-bold text-amber-800/60">
                            <input type="checkbox" @change="toggleSelectAllTraining"
                                :checked="selectedTrainingIds.length === unparsedMessages.length && unparsedMessages.length > 0"
                                class="rounded border-amber-300 text-amber-600" />
                            Select All Current
                        </label>
                        <button v-if="selectedTrainingIds.length > 0" @click="emit('bulkDismissTraining')"
                            class="bg-amber-100 text-amber-800 px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-2">
                            🗑️ Dismiss {{ selectedTrainingIds.length }}
                        </button>
                    </div>
                    <!-- Sort Controls Training -->
                    <div class="flex items-center gap-2">
                        <CustomSelect :modelValue="trainingSortKey"
                            @update:modelValue="emit('update:trainingSortKey', $event)"
                            :options="[{ label: 'Date', value: 'created_at' }, { label: 'Sender', value: 'sender' }]"
                            class="w-32 text-xs" />
                        <button @click="emit('update:trainingSortOrder', trainingSortOrder === 'asc' ? 'desc' : 'asc')"
                            class="btn-icon-circle-small bg-white border border-amber-200 text-amber-700"
                            title="Toggle Order">
                            {{ trainingSortOrder === 'asc' ? '↑' : '↓' }}
                        </button>
                        <button @click="emit('refreshTriage')" class="btn-icon-circle-small amber-themed">🔄</button>
                    </div>
                </div>

                <div class="triage-grid">
                    <div v-for="msg in sortedTrainingMessages" :key="msg.id"
                        class="glass-card triage-card training-theme"
                        :class="{ 'selected': selectedTrainingIds.includes(msg.id) }">
                        <div class="triage-card-header">
                            <div class="header-left">
                                <input type="checkbox" v-model="selectedTrainingIds" :value="msg.id" class="mr-2" />
                                <span class="source-tag" :class="msg.source.toLowerCase()">{{ msg.source
                                }}</span>
                                <span class="ai-badge-mini"
                                    style="background: #fef3c7; color: #92400e; border-color: #f59e0b;">🤖 Needs
                                    Training</span>
                            </div>
                            <span class="triage-date">{{ formatDate(msg.created_at).day }}</span>
                        </div>

                        <div class="triage-card-body">
                            <div class="training-content-premium">
                                <div class="training-header">
                                    <div class="training-sender" v-if="msg.sender">
                                        <span class="label">Sender:</span> {{ msg.sender }}
                                    </div>
                                    <div class="training-subject" v-if="msg.subject">
                                        <span class="label">Subject:</span> {{ msg.subject }}
                                    </div>
                                </div>
                                <pre class="training-raw-preview-premium"
                                    :class="{ 'expanded': expandedTrainingIds.has(msg.id) }">{{ msg.raw_content }}</pre>
                                <button v-if="msg.raw_content?.length > 150" @click="toggleTrainingExpand(msg.id)"
                                    class="read-more-btn">
                                    {{ expandedTrainingIds.has(msg.id) ? 'Collapse ▲' : 'Read More ▼' }}
                                </button>
                            </div>
                        </div>

                        <div class="triage-card-actions">
                            <div class="action-bottom-row">
                                <button @click="emit('dismissTraining', msg.id)"
                                    class="btn-triage-secondary">Dismiss</button>
                                <button @click="emit('startLabeling', msg)" class="btn-triage-primary">
                                    Label Fields
                                    <span class="btn-shimmer"></span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-if="trainingPagination.total === 0" class="empty-state-triage">
                    <div class="empty-glow-icon">🛡️</div>
                    <h3>All clear!</h3>
                    <p>No unparsed messages waiting for training.</p>
                </div>

                <!-- Training Area Pagination & Page Size -->
                <div v-if="trainingPagination.total > 0"
                    class="mt-6 flex items-center justify-between border-t border-gray-100 pt-6">
                    <div class="flex items-center gap-4">
                        <span class="text-[10px] text-muted font-mono">
                            {{ trainingPagination.skip + 1 }}–{{ Math.min(trainingPagination.skip +
                                trainingPagination.limit, trainingPagination.total) }} of {{
                                trainingPagination.total }}
                        </span>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] text-muted uppercase font-bold tracking-wider">Page
                                Size:</span>
                            <select :value="trainingPagination.limit"
                                @change="handleTrainingPaginationLimitChange(Number(($event.target as HTMLSelectElement).value))"
                                class="text-[10px] bg-white border border-amber-200 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-amber-500 font-bold text-amber-800">
                                <option :value="10">10</option>
                                <option :value="20">20</option>
                                <option :value="50">50</option>
                                <option :value="100">100</option>
                                <option :value="200">200</option>
                                <option :value="500">500</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex items-center gap-1" v-if="trainingPagination.total > trainingPagination.limit">
                        <button @click="handleTrainingPaginationPrev" :disabled="trainingPagination.skip === 0"
                            class="btn-pagination-compact amber">Prev</button>
                        <button @click="handleTrainingPaginationNext"
                            :disabled="trainingPagination.skip + trainingPagination.limit >= trainingPagination.total"
                            class="btn-pagination-compact amber">Next</button>
                    </div>
                </div>
            </div>
        </div>
</template>

<style scoped>
/* This component inherits most styles from Transactions.vue */
/* Only component-specific overrides needed here */

.triage-view {
    min-height: 400px;
}

.animate-in {
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Utility classes used in template */
.mb-4 {
    margin-bottom: 1rem;
}

.mb-6 {
    margin-bottom: 1.5rem;
}

.mt-6 {
    margin-top: 1.5rem;
}

.mt-2 {
    margin-top: 0.5rem;
}

.mr-2 {
    margin-right: 0.5rem;
}

.ml-auto {
    margin-left: auto;
}

.flex {
    display: flex;
}

.items-center {
    align-items: center;
}

.justify-between {
    justify-content: space-between;
}

.gap-1 {
    gap: 0.25rem;
}

.gap-2 {
    gap: 0.5rem;
}

.gap-4 {
    gap: 1rem;
}

.text-xs {
    font-size: 0.75rem;
}

.text-\[10px\] {
    font-size: 10px;
}

.font-bold {
    font-weight: 700;
}

.uppercase {
    text-transform: uppercase;
}

.tracking-wider {
    letter-spacing: 0.05em;
}

.font-mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

.text-muted {
    color: #6b7280;
}

.text-amber-800\/60 {
    color: rgba(146, 64, 14, 0.6);
}

.rounded {
    border-radius: 0.25rem;
}

.rounded-lg {
    border-radius: 0.5rem;
}

.border-gray-300 {
    border-color: #d1d5db;
}

.border-amber-300 {
    border-color: #fcd34d;
}

.text-indigo-600 {
    color: #4f46e5;
}

.text-amber-600 {
    color: #d97706;
}

.cursor-pointer {
    cursor: pointer;
}

.w-32 {
    width: 8rem;
}

.border-t {
    border-top-width: 1px;
}

.border-gray-100 {
    border-color: #f3f4f6;
}

.pt-6 {
    padding-top: 1.5rem;
}

.px-3 {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
}

.py-1 {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}

.px-1\.5 {
    padding-left: 0.375rem;
    padding-right: 0.375rem;
}

.py-0\.5 {
    padding-top: 0.125rem;
    padding-bottom: 0.125rem;
}

.bg-rose-50 {
    background-color: #fff1f2;
}

.text-rose-600 {
    color: #e11d48;
}

.bg-amber-100 {
    background-color: #fef3c7;
}

.text-amber-800 {
    color: #92400e;
}

.bg-white {
    background-color: white;
}

.border {
    border-width: 1px;
}

.border-gray-200 {
    border-color: #e5e7eb;
}

.border-amber-200 {
    border-color: #fde68a;
}

.text-amber-700 {
    color: #b45309;
}

.focus\:outline-none:focus {
    outline: 2px solid transparent;
    outline-offset: 2px;
}

.focus\:ring-1:focus {
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.05);
}

.focus\:ring-indigo-500:focus {
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.focus\:ring-amber-500:focus {
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.text-slate-700 {
    color: #334155;
}
</style>
