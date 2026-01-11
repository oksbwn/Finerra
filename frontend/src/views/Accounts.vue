<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import CustomSelect from '@/components/CustomSelect.vue'

const accounts = ref<any[]>([])
const loading = ref(true)
const showModal = ref(false)

const verifiedAccounts = computed(() => accounts.value.filter(a => a.is_verified !== false))
const untrustedAccounts = computed(() => accounts.value.filter(a => a.is_verified === false))

// Form Data
const newAccount = ref({
    name: '',
    type: 'BANK',
    currency: 'INR',
    account_mask: '',
    balance: 0,
    owner_name: '',
    is_verified: true
})

async function fetchAccounts() {
    loading.value = true
    try {
        const res = await financeApi.getAccounts()
        accounts.value = res.data
    } catch (e) {
        console.error("Failed to fetch accounts", e)
    } finally {
        loading.value = false
    }
}

const editingId = ref<string | null>(null)

function openCreateModal() {
    editingId.value = null
    newAccount.value = { name: '', type: 'BANK', currency: 'INR', account_mask: '', balance: 0, owner_name: '' }
    showModal.value = true
}

function openEditModal(account: any) {
    editingId.value = account.id
    newAccount.value = {
        name: account.name,
        type: account.type,
        currency: account.currency,
        account_mask: account.account_mask || '',
        owner_name: account.owner_name || '',
        account_mask: account.account_mask || '',
        owner_name: account.owner_name || '',
        balance: account.balance, // Balance might not be editable in backend effectively but we show it
        is_verified: true // Verify on edit
    }
    showModal.value = true
}

import { useNotificationStore } from '@/stores/notification'

const notify = useNotificationStore()

async function handleSubmit() {
    try {
        if (editingId.value) {
            await financeApi.updateAccount(editingId.value, newAccount.value)
            notify.success("Account updated successfully")
        } else {
            await financeApi.createAccount(newAccount.value)
            notify.success("Account created successfully")
        }
        showModal.value = false
        fetchAccounts()
    } catch (e) {
        notify.error("Failed to save account")
    }
}

const getOwnerIcon = (name: string) => {
    const n = name.toLowerCase()
    if (n.includes('dad') || n.includes('father')) return '👨'
    if (n.includes('mom') || n.includes('mother')) return '👩'
    if (n.includes('kid') || n.includes('child')) return '🧒'
    if (n.includes('grand')) return '🧓'
    return '👤'
}

onMounted(() => {
    fetchAccounts()
})
</script>

<template>
    <MainLayout>
        <div class="header-actions">
            <h1>Accounts</h1>
            <button @click="openCreateModal" class="btn btn-primary">
                <span style="font-size: 1.2rem; margin-right: 0.5rem">+</span> Add Account
            </button>
        </div>

        <div v-if="loading" class="loading">Loading accounts...</div>

        <div v-else>
            <!-- Untrusted Accounts Section (if any) -->
            <div v-if="untrustedAccounts.length > 0" class="section-untrusted">
                <h2 class="section-title">⚠️ New Detected Accounts</h2>
                <div class="grid">
                     <div v-for="acc in untrustedAccounts" :key="acc.id" class="card untrusted-card">
                        <div class="card-header">
                            <h3>{{ acc.name }}</h3>
                            <button @click="openEditModal(acc)" class="btn btn-sm btn-primary">
                                Verify
                            </button>
                        </div>
                        <div class="balance">{{ acc.currency }} {{ Number(acc.balance || 0).toFixed(2) }}</div>
                        <div class="meta">Auto-detected from SMS</div>
                    </div>
                </div>
            </div>

            <!-- Verified Accounts -->
            <div class="grid">
                <div v-for="acc in verifiedAccounts" :key="acc.id" class="card">
                    <div class="card-header">
                        <h3>{{ acc.name }}</h3>
                        <button @click="openEditModal(acc)" class="btn-icon" title="Edit Account">
                            ✏️
                        </button>
                    </div>
                    
                    <div class="balance">{{ acc.currency }} {{ Number(acc.balance || 0).toFixed(2) }}</div>
                    
                    <div class="meta">
                        <span v-if="acc.owner_name" class="owner-pill" :title="acc.owner_name">
                            <span style="margin-right: 4px; font-size: 1.1em;">{{ getOwnerIcon(acc.owner_name) }}</span>
                            {{ acc.owner_name }}
                        </span> 
                        <span v-else class="owner-pill" title="Shared / Family">
                            <span style="margin-right: 4px; font-size: 1.1em;">🏠</span> Family
                        </span>
                        {{ acc.type }} 
                        <span v-if="acc.account_mask" class="mask"> •• {{ acc.account_mask }}</span>
                    </div>
                </div>
                
                <div v-if="accounts.length === 0" class="empty-state">
                    <p>No accounts found. Add one to get started!</p>
                </div>
            </div>
        </div>

        <!-- Global Styled Modal -->
        <div v-if="showModal" class="modal-overlay-global">
            <div class="modal-global">
                <div class="modal-header">
                    <h2 class="modal-title">{{ editingId ? 'Edit Account' : 'New Account' }}</h2>
                    <button class="btn-icon" @click="showModal = false">✕</button>
                </div>

                <form @submit.prevent="handleSubmit">
                    <div class="form-group">
                        <label class="form-label">Account Name</label>
                        <input v-model="newAccount.name" class="form-input" required placeholder="e.g. HDFC Savings" />
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Owner (Person)</label>
                        <CustomSelect 
                            v-model="newAccount.owner_name" 
                            :options="[
                                { label: 'Shared / Family', value: '' },
                                { label: 'Dad', value: 'Dad' },
                                { label: 'Mom', value: 'Mom' },
                                { label: 'Kid', value: 'Kid' },
                                { label: 'Other', value: 'Other' }
                            ]"
                            placeholder="Select Owner"
                        />
                    </div>

                    <div class="form-layout-row">
                        <div class="form-group half">
                            <label class="form-label">Type</label>
                            <CustomSelect 
                                v-model="newAccount.type"
                                :options="[
                                    { label: 'Bank Account', value: 'BANK' },
                                    { label: 'Cash Wallet', value: 'CASH' },
                                    { label: 'Investment', value: 'INVESTMENT' },
                                    { label: 'Credit Card', value: 'CREDIT' }
                                ]"
                            />
                        </div>
                        <div class="form-group half">
                            <label class="form-label">Currency</label>
                             <CustomSelect 
                                v-model="newAccount.currency"
                                :options="[
                                    { label: 'INR - Indian Rupee', value: 'INR' },
                                    { label: 'USD - US Dollar', value: 'USD' },
                                    { label: 'EUR - Euro', value: 'EUR' }
                                ]"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Account Link Mask (Last 4 Digits)</label>
                        <input v-model="newAccount.account_mask" class="form-input" placeholder="e.g. 1234" maxlength="4" />
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Initial Balance</label>
                        <input type="number" v-model.number="newAccount.balance" class="form-input" step="0.01" />
                    </div>

                    <div class="modal-footer">
                        <button type="button" @click="showModal = false" class="btn btn-outline">
                            <span style="margin-right:0.5rem">✕</span> Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <span style="margin-right:0.5rem">💾</span> Save Changes
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </MainLayout>
</template>

<style scoped>
.header-actions {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-xl);
}
.grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--spacing-lg);
}
.card {
    background: var(--color-surface);
    padding: var(--spacing-lg);
    border-radius: 1rem;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--color-border);
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--spacing-sm); }
h3 { margin: 0; font-size: 1.1rem; color: var(--color-text-main); font-weight: 600; }

.balance { font-size: 1.5rem; font-weight: 700; color: var(--color-text-main); margin-bottom: 1rem; }

.meta {
    font-size: 0.85rem; color: var(--color-text-muted);
    background: var(--color-background);
    padding: 0.5rem 0.75rem; border-radius: 0.5rem;
    display: flex; align-items: center; gap: 0.5rem;
}

.owner-pill {
    background: white; border: 1px solid var(--color-border);
    padding: 2px 6px; border-radius: 4px;
    font-weight: 600; font-size: 0.75rem; color: var(--color-primary);
}

.form-layout-row { display: flex; gap: 1rem; }
.half { flex: 1; }

.loading { text-align: center; padding: 2rem; color: var(--color-text-muted); }
.empty-state { grid-column: 1/-1; text-align: center; padding: 4rem; background: var(--color-surface); border-radius: 1rem; color: var(--color-text-muted); border: 2px dashed var(--color-border); }

.section-untrusted { margin-bottom: var(--spacing-xl); }
.section-title { font-size: 1.1rem; color: var(--color-warning); margin-bottom: var(--spacing-md); font-weight: 600; }

.untrusted-card { border: 1px dashed var(--color-warning); background: #fffbeb; }
.btn-sm { padding: 0.25rem 0.75rem; font-size: 0.8rem; }
</style>
