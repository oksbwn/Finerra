<template>
    <div class="tab-content animate-in">
        <!-- Account Summary Widgets -->
        <div class="summary-widgets">
            <div class="mini-stat-card glass h-glow-primary">
                <div class="stat-top">
                    <span class="stat-label">Total Liquid Wealth</span>
                    <span class="stat-icon-bg gray">⚖️</span>
                </div>
                <div class="stat-value">{{ formatAmount(accountMetrics.total) }}</div>
            </div>
            <div class="mini-stat-card glass h-glow-success">
                <div class="stat-top">
                    <span class="stat-label">Bank Balance</span>
                    <span class="stat-icon-bg green">🏦</span>
                </div>
                <div class="stat-value">{{ formatAmount(accountMetrics.bank) }}</div>
            </div>
            <div class="mini-stat-card glass h-glow-warning">
                <div class="stat-top">
                    <span class="stat-label">Cash on Hand</span>
                    <span class="stat-icon-bg yellow">💵</span>
                </div>
                <div class="stat-value">{{ formatAmount(accountMetrics.cash) }}</div>
            </div>
            <div class="mini-stat-card glass h-glow-danger">
                <div class="stat-top">
                    <span class="stat-label">Credit Consumed</span>
                    <span class="stat-icon-bg red">💳</span>
                </div>
                <div class="stat-value">{{ formatAmount(accountMetrics.credit) }}</div>
            </div>
        </div>

        <!-- Untrusted Accounts (Premium Style) -->
        <div v-if="untrustedAccounts.length > 0" class="alert-section mb-8">
            <div class="header-with-badge match-header mb-4">
                <h3 style="margin: 0; font-size: 1rem; font-weight: 700; color: #b45309;">⚠️ New Detected
                    Accounts</h3>
                <span class="pulse-status-badge" style="background: #fffbeb; color: #b45309;">{{
                    untrustedAccounts.length }} Action Needed</span>
            </div>

            <div class="settings-grid">
                <div v-for="acc in untrustedAccounts" :key="acc.id"
                    class="glass-card account-card-premium untrusted-card">
                    <div class="acc-card-top">
                        <div class="acc-icon-wrapper" :class="acc.type.toLowerCase()">
                            {{ getAccountTypeIcon(acc.type) }}
                        </div>
                        <div class="acc-actions" style="gap: 0.5rem;">
                            <button @click="openEditAccountModal(acc, true)" class="btn-icon-subtle success"
                                title="Verify Account">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2.5">
                                    <path d="M20 6L9 17l-5-5" />
                                </svg>
                            </button>
                            <button @click="deleteAccountRequest(acc)" class="btn-icon-subtle danger"
                                title="Reject / Remove">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                    stroke-width="2">
                                    <path d="M18 6L6 18M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="acc-card-main">
                        <div class="acc-label-row">
                            <span class="acc-type">{{ getAccountTypeLabel(acc.type) }}</span>
                            <span class="status-badge-mini inactive">Untrusted</span>
                        </div>
                        <h3 class="acc-name">{{ acc.name }}</h3>
                    </div>

                    <div class="acc-card-footer">
                        <div class="acc-balance-group">
                            <span class="acc-balance-label">Balance</span>
                            <span class="acc-balance-val">{{ formatAmount(acc.balance || 0) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Verified Accounts Control Bar (Search Left, Title Right) -->
        <div class="account-control-bar mt-8 mb-6">
            <!-- Search on Left -->
            <div class="search-bar-premium no-margin" style="flex: 1; max-width: 300px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="search-icon">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="Search accounts..." class="search-input">
            </div>

            <!-- Title on Right -->
            <div class="header-with-badge" style="margin-left: auto; display: flex; align-items: center; gap: 0.75rem;">
                <h3
                    style="margin: 0; font-size: 1rem; font-weight: 700; color: var(--color-text-main); white-space: nowrap;">
                    Tracked Accounts</h3>
                <span class="pulse-status-badge" style="background: #ecfdf5; color: #047857;">{{
                    verifiedAccounts.length }} Active</span>
            </div>
        </div>

        <!-- Verified Accounts Grid -->
        <div class="settings-grid">
            <div v-for="acc in verifiedAccounts" :key="acc.id" class="glass-card account-card-premium"
                :class="{ 'verified-highlight': acc.is_verified }" @click="openEditAccountModal(acc)">
                <div class="acc-card-top">
                    <div class="acc-icon-wrapper" :class="acc.type.toLowerCase()">
                        {{ getAccountTypeIcon(acc.type) }}
                    </div>
                    <div class="acc-actions">
                        <!-- Edit Icon replaced button -->
                        <button class="btn-icon-subtle" title="Edit Options">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                        </button>
                    </div>
                </div>

                <div class="acc-card-main">
                    <h3 class="acc-name">{{ acc.name }}</h3>
                    <div class="acc-meta">
                        <span class="acc-type">{{ getAccountTypeLabel(acc.type) }}</span>
                        <span v-if="acc.account_mask" class="acc-mask">••{{ acc.account_mask }}</span>

                        <!-- Goal Linked Badge -->
                        <span v-if="acc.linked_goals && acc.linked_goals.length > 0" class="goal-linked-badge"
                            :title="'Linked to: ' + acc.linked_goals.join(', ')">
                            🎯 {{ acc.linked_goals[0] }}
                            <span v-if="acc.linked_goals.length > 1">+{{ acc.linked_goals.length - 1
                                }}</span>
                        </span>
                        <span v-else-if="accountGoalMap[acc.id]" class="goal-linked-badge"
                            :title="'Linked to: ' + accountGoalMap[acc.id].join(', ')">
                            🎯 {{ accountGoalMap[acc.id][0] }}
                            <span v-if="accountGoalMap[acc.id].length > 1">+{{ accountGoalMap[acc.id].length
                                - 1 }}</span>
                        </span>
                    </div>
                    <div class="acc-owner-row mt-3">
                        <div class="owner-pill">
                            <span class="owner-avatar-xs">{{ resolveOwnerAvatar(acc) }}</span>
                            <span class="owner-name-xs">{{ resolveOwnerName(acc) }}</span>
                        </div>
                    </div>
                </div>

                <div class="acc-card-footer">
                    <div class="acc-balance-group">
                        <span class="acc-balance-label">Current Balance</span>
                        <span class="acc-balance-val"
                            :class="{ 'text-red': Number(acc.balance) < 0 && acc.type !== 'CREDIT_CARD' }">
                            {{ formatAmount(Math.abs(Number(acc.balance || 0)), acc.currency) }}
                            <span v-if="acc.type === 'CREDIT_CARD'" class="balance-tag">used</span>
                        </span>
                    </div>

                    <div v-if="acc.type === 'CREDIT_CARD' && acc.credit_limit" class="acc-limit-group">
                        <div class="limit-bar-bg">
                            <div class="limit-bar-fill"
                                :style="{ width: Math.min(((Math.abs(Number(acc.balance || 0))) / Number(acc.credit_limit)) * 100, 100) + '%' }">
                            </div>
                        </div>
                        <span class="limit-text">{{ Math.round((Math.abs(Number(acc.balance || 0)) /
                            Number(acc.credit_limit)) * 100) }}% utilized</span>
                    </div>
                </div>
            </div>

            <!-- Add New Card (Empty State) -->
            <div v-if="!searchQuery" class="glass-card add-account-card" @click="openCreateAccountModal">
                <div class="add-icon-circle">+</div>
                <span>Add New Account</span>
            </div>
        </div>

        <div v-if="verifiedAccounts.length === 0 && searchQuery" class="empty-placeholder">
            <p>No accounts match "{{ searchQuery }}"</p>
        </div>

        <!-- Account Modal -->
        <div v-if="showAccountModal" class="modal-overlay-global">
            <div class="modal-global glass">
                <div class="modal-header">
                    <h2 class="modal-title">{{ editingAccountId ? 'Edit Account' : 'New Account' }}</h2>
                    <button class="btn-icon-circle" @click="showAccountModal = false">✕</button>
                </div>

                <form @submit.prevent="handleAccountSubmit" class="form-compact">
                    <div class="form-group">
                        <label class="form-label">Account Name</label>
                        <input v-model="newAccount.name" class="form-input" required placeholder="e.g. HDFC Savings" />
                    </div>


                    <div class="form-row">
                        <div class="form-group half">
                            <label class="form-label">Type</label>
                            <CustomSelect v-model="newAccount.type" :options="[
                                { label: '🏦 Bank Account', value: 'BANK' },
                                { label: '💳 Credit Card', value: 'CREDIT_CARD' },
                                { label: '💸 Loan / EMIs', value: 'LOAN' },
                                { label: '👛 Wallet / Cash', value: 'WALLET' },
                                { label: '📈 Investment', value: 'INVESTMENT' }
                            ]" />
                        </div>
                        <div class="form-group half">
                            <label class="form-label">Currency</label>
                            <CustomSelect v-model="newAccount.currency" :options="[
                                { label: 'INR - Indian Rupee', value: 'INR' },
                                { label: 'USD - US Dollar', value: 'USD' }
                            ]" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Account Mask (Last 4 Digits)</label>
                        <input v-model="newAccount.account_mask" class="form-input" placeholder="e.g. 1234"
                            maxlength="4" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Account Owner</label>
                        <CustomSelect v-model="newAccount.owner_id"
                            :options="familyMembers.map(m => ({ label: m.full_name || m.email, value: m.id }))"
                            placeholder="Select Owner" />
                    </div>

                    <div class="form-row">
                        <div class="form-group" :class="newAccount.type === 'CREDIT_CARD' ? 'half' : 'full'">
                            <label class="form-label">{{ consumedLimitMsg }}</label>
                            <input type="number" v-model.number="newAccount.balance" class="form-input" step="0.01" />
                        </div>
                        <div v-if="newAccount.type === 'CREDIT_CARD'" class="form-group half">
                            <label class="form-label">Total Credit Limit</label>
                            <input type="number" v-model.number="newAccount.credit_limit" class="form-input" step="0.01"
                                placeholder="e.g. 100000" />
                        </div>
                    </div>

                    <div v-if="newAccount.type === 'CREDIT_CARD'" class="form-row">
                        <div class="form-group half">
                            <label class="form-label">Billing Day (1-31)</label>
                            <input type="number" v-model.number="newAccount.billing_day" class="form-input" min="1"
                                max="31" placeholder="e.g. 15" />
                        </div>
                        <div v-if="newAccount.type === 'CREDIT_CARD'" class="form-group half">
                            <label class="form-label">Due Day (1-31)</label>
                            <input type="number" v-model.number="newAccount.due_day" class="form-input" min="1" max="31"
                                placeholder="e.g. 5" />
                        </div>
                    </div>

                    <div class="setting-toggle-row">
                        <div class="toggle-label">
                            <span class="font-medium">Verified Account</span>
                            <span class="text-xs text-muted">Trust transactions from this source</span>
                        </div>
                        <label class="switch">
                            <input type="checkbox" v-model="newAccount.is_verified">
                            <span class="slider round"></span>
                        </label>
                    </div>

                    <div class="modal-footer">
                        <button type="button" @click="showAccountModal = false" class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary-glow">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Delete Account Confirmation -->
        <div v-if="showAccountDeleteConfirm" class="modal-overlay-global">
            <div class="modal-global glass alert max-w-md">
                <div class="modal-icon-header danger">🗑️</div>
                <h2 class="modal-title">Delete Account?</h2>
                <div class="alert-info-box mb-6">
                    <p class="mb-2">You are about to delete <strong>{{ accountToDelete?.name }}</strong>.</p>
                    <p class="text-danger font-bold" v-if="accountTxCount > 0">
                        ⚠️ This will also permanently delete {{ accountTxCount }} transactions.
                    </p>
                    <p v-else class="text-muted">No transactions are currently linked to this account.</p>
                </div>
                <p class="text-xs text-muted mb-6">This action cannot be undone. Are you absolutely sure?</p>

                <div class="modal-footer">
                    <button @click="showAccountDeleteConfirm = false" class="btn-secondary"
                        :disabled="isDeletingAccount">Cancel</button>
                    <button @click="confirmAccountDelete" class="btn-danger-glow" :disabled="isDeletingAccount">
                        {{ isDeletingAccount ? 'Deleting...' : 'Yes, Delete Everything' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCurrency } from '@/composables/useCurrency'
import { financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import CustomSelect from '@/components/CustomSelect.vue'

const notify = useNotificationStore()
const { formatAmount } = useCurrency()

// --- Internal State ---
const accounts = ref<any[]>([])
const goals = ref<any[]>([])
const tenants = ref<any[]>([])
const familyMembers = ref<any[]>([])
const searchQuery = ref('')
const loading = ref(false)

const showAccountModal = ref(false)
const editingAccountId = ref<string | null>(null)
const newAccount = ref({
    name: '',
    type: 'BANK',
    currency: 'INR',
    account_mask: '',
    balance: 0,
    credit_limit: null as number | null,
    billing_day: null as number | null,
    due_day: null as number | null,
    is_verified: true,
    tenant_id: '',
    owner_id: ''
})

const showAccountDeleteConfirm = ref(false)
const accountToDelete = ref<any>(null)
const accountTxCount = ref(0)
const isDeletingAccount = ref(false)

// --- Computed ---
const consumedLimitMsg = computed(() => newAccount.value.type === 'CREDIT_CARD' ? 'Consumed Limit' : 'Current Balance')

const verifiedAccounts = computed(() => {
    let filtered = accounts.value.filter(a => a.is_verified !== false)
    if (searchQuery.value) {
        filtered = filtered.filter(a => a.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
    }
    return filtered
})
const untrustedAccounts = computed(() => accounts.value.filter(a => a.is_verified === false))

const accountMetrics = computed(() => {
    let total = 0
    let cash = 0
    let bank = 0
    let credit = 0

    accounts.value.forEach(a => {
        const bal = Number(a.balance || 0)
        if (a.type === 'CREDIT_CARD' || a.type === 'LOAN') {
            credit += bal
            total -= bal
        } else {
            total += bal
            if (a.type === 'BANK') bank += bal
            if (a.type === 'WALLET' || a.type === 'CASH') cash += bal
        }
    })

    return { total, cash, bank, credit }
})

const accountGoalMap = computed(() => {
    const map: Record<string, string[]> = {}
    if (!goals.value) return map

    goals.value.forEach(goal => {
        if (goal.assets) {
            goal.assets.forEach((asset: any) => {
                if (asset.linked_account_id) {
                    if (!map[asset.linked_account_id]) map[asset.linked_account_id] = []
                    map[asset.linked_account_id].push(goal.name)
                }
            })
        }
    })
    return map
})

function getAccountTypeIcon(type: string) {
    const icons: Record<string, string> = {
        'BANK': '🏦',
        'CREDIT_CARD': '💳',
        'LOAN': '💸',
        'WALLET': '👛',
        'INVESTMENT': '📈'
    }
    return icons[type] || '💰'
}

function getAccountTypeLabel(type: string) {
    const labels: Record<string, string> = {
        'BANK': 'Bank account',
        'CREDIT_CARD': 'Credit Card',
        'LOAN': 'Loans / EMIs',
        'WALLET': 'Wallet / Cash',
        'INVESTMENT': 'Investment'
    }
    return labels[type] || type
}

const resolveOwnerAvatar = (account: any) => {
    if (account.owner_id) {
        const member = familyMembers.value.find(m => m.id === account.owner_id)
        if (member && member.avatar) return member.avatar
    }
    return '👨\u200D👩\u200D👧\u200D👦'
}

const resolveOwnerName = (account: any) => {
    if (account.owner_id) {
        const member = familyMembers.value.find(m => m.id === account.owner_id)
        if (member) return member.full_name || member.email
    }
    return 'Family'
}

async function fetchData() {
    loading.value = true
    try {
        const [accRes, goalsRes, tenantsRes, usersRes] = await Promise.all([
            financeApi.getAccounts(),
            financeApi.getInvestmentGoals(),
            financeApi.getTenants(),
            financeApi.getUsers()
        ])
        accounts.value = accRes.data
        goals.value = goalsRes.data
        tenants.value = tenantsRes.data
        familyMembers.value = usersRes.data
    } catch (err) {
        console.error('Failed to fetch account settings data', err)
        notify.error("Failed to load data")
    } finally {
        loading.value = false
    }
}

// --- Methods ---
function openCreateAccountModal() {
    editingAccountId.value = null
    newAccount.value = {
        name: '', type: 'BANK', currency: 'INR',
        account_mask: '', balance: 0,
        credit_limit: null,
        billing_day: null,
        due_day: null,
        is_verified: true,
        tenant_id: tenants.value[0]?.id || '',
        owner_id: ''
    }
    showAccountModal.value = true
}

onMounted(() => {
    fetchData()
})

function openEditAccountModal(account: any, autoVerify: boolean = false) {
    editingAccountId.value = account.id
    newAccount.value = {
        name: account.name,
        type: account.type,
        currency: account.currency,
        account_mask: account.account_mask,
        balance: account.balance,
        credit_limit: account.credit_limit,
        billing_day: account.billing_day,
        due_day: account.due_day,
        owner_id: account.owner_id,
        tenant_id: account.tenant_id,
        is_verified: autoVerify ? true : account.is_verified
    }
    showAccountModal.value = true
}

async function handleAccountSubmit() {
    try {
        const payload = {
            ...newAccount.value,
            balance: Number(newAccount.value.balance),
            credit_limit: newAccount.value.type === 'CREDIT_CARD' ? Number(newAccount.value.credit_limit) : null,
            billing_day: (newAccount.value.type === 'CREDIT_CARD' && newAccount.value.billing_day) ? Number(newAccount.value.billing_day) : null,
            due_day: (newAccount.value.type === 'CREDIT_CARD' && newAccount.value.due_day) ? Number(newAccount.value.due_day) : null
        }

        if (editingAccountId.value) {
            await financeApi.updateAccount(editingAccountId.value, payload)
            notify.success("Account updated")
        } else {
            await financeApi.createAccount(payload)
            notify.success("Account created")
        }
        showAccountModal.value = false
        fetchData()
    } catch (e) {
        notify.error("Failed to save account")
    }
}

async function deleteAccountRequest(account: any) {
    accountToDelete.value = account
    accountTxCount.value = 0
    try {
        const res = await financeApi.getAccountTransactionCount(account.id)
        accountTxCount.value = res.data.count
    } catch (e) {
        console.error("Failed to fetch tx count", e)
    }
    showAccountDeleteConfirm.value = true
}

async function confirmAccountDelete() {
    if (!accountToDelete.value) return
    isDeletingAccount.value = true
    try {
        await financeApi.deleteAccount(accountToDelete.value.id)
        notify.success("Account and related data removed")
        showAccountDeleteConfirm.value = false
        fetchData()
    } catch (e) {
        notify.error("Failed to delete account")
    } finally {
        isDeletingAccount.value = false
        accountToDelete.value = null
    }
}
</script>

<style scoped>
/* --- Premium Accounts Tab CSS --- */
.summary-widgets {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}

.mini-stat-card {
    padding: 1.25rem;
    border-radius: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mini-stat-card:hover {
    transform: translateY(-4px);
}

.stat-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 800;
    color: #1e293b;
    letter-spacing: -0.02em;
}

.stat-icon-bg {
    width: 32px;
    height: 32px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.stat-icon-bg.gray {
    background: #f1f5f9;
}

.stat-icon-bg.green {
    background: #ecfdf5;
}

.stat-icon-bg.yellow {
    background: #fffbeb;
}

.stat-icon-bg.red {
    background: #fef2f2;
}

.h-glow-primary:hover {
    box-shadow: 0 15px 30px -10px rgba(99, 102, 241, 0.2);
    border-color: #6366f1;
}

.h-glow-success:hover {
    box-shadow: 0 15px 30px -10px rgba(16, 185, 129, 0.2);
    border-color: #10b981;
}

.h-glow-warning:hover {
    box-shadow: 0 15px 30px -10px rgba(245, 158, 11, 0.2);
    border-color: #f59e0b;
}

.h-glow-danger:hover {
    box-shadow: 0 15px 30px -10px rgba(239, 68, 68, 0.2);
    border-color: #ef4444;
}

.account-card-premium {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.account-card-premium:hover {
    border-color: #6366f1;
    transform: translateY(-2px);
}

.acc-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.acc-icon-wrapper {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    background: #f8fafc;
    border: 1px solid #f1f5f9;
}

.acc-icon-wrapper.bank {
    background: #e0f2fe;
    color: #0284c7;
}

.acc-icon-wrapper.credit_card {
    background: #fef2f2;
    color: #dc2626;
}

.acc-icon-wrapper.wallet {
    background: #ecfdf5;
    color: #059669;
}

.acc-name {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
}

.acc-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.acc-type {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
}

.acc-mask {
    padding: 2px 6px;
    background: #f1f5f9;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #64748b;
}

.goal-linked-badge {
    padding: 2px 8px;
    background: #f5f3ff;
    color: #6366f1;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 700;
    border: 1px solid #ddd6fe;
}

.owner-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 2px 8px 2px 4px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 99px;
}

.owner-avatar-xs {
    font-size: 0.75rem;
}

.owner-name-xs {
    font-size: 0.7rem;
    font-weight: 600;
    color: #475569;
}

.acc-balance-group {
    display: flex;
    flex-direction: column;
}

.acc-balance-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 0.125rem;
}

.acc-balance-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
}

.acc-balance-val.text-red {
    color: #ef4444;
}

.balance-tag {
    font-size: 0.65rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    margin-left: 0.25rem;
}

.acc-limit-group {
    margin-top: 0.5rem;
}

.limit-bar-bg {
    height: 6px;
    background: #f1f5f9;
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 0.25rem;
}

.limit-bar-fill {
    height: 100%;
    background: linear-gradient(to right, #6366f1, #ef4444);
    border-radius: 3px;
}

.limit-text {
    font-size: 0.7rem;
    font-weight: 600;
    color: #94a3b8;
}

.verified-highlight {
    border-top: 3px solid #10b981 !important;
}

.untrusted-card {
    border-top: 3px solid #f59e0b !important;
}

.btn-icon-subtle {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-icon-subtle:hover {
    background: #f1f5f9;
    color: #6366f1;
}

.btn-icon-subtle.success {
    color: #10b981;
}

.btn-icon-subtle.danger {
    color: #ef4444;
}

.glass-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
}

.settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 0.875rem;
}

.add-account-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 150px;
    border: 2px dashed #e5e7eb;
    cursor: pointer;
    transition: all 0.2s;
    color: #6b7280;
    gap: 0.75rem;
    border-radius: 1rem;
}

.add-account-card:hover {
    border-color: #4f46e5;
    color: #4f46e5;
    background: #f5f3ff;
}

.add-icon-circle {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

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

.account-control-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.search-bar-premium {
    position: relative;
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
</style>
