<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import { useRoute } from 'vue-router'
import CustomSelect from '@/components/CustomSelect.vue'
import { useNotificationStore } from '@/stores/notification'

const route = useRoute()
const notify = useNotificationStore()

const transactions = ref<any[]>([])
const accounts = ref<any[]>([])
const loading = ref(true)
const selectedAccount = ref<string>('')

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const editingTxnId = ref<string | null>(null)

// Form State
const defaultForm = {
    description: '',
    category: '',
    amount: null,
    date: new Date().toISOString().slice(0, 16), // YYYY-MM-DDTHH:mm
    account_id: ''
}
const form = ref({ ...defaultForm })

// Computed for Select Options
const accountOptions = computed(() => {
    return accounts.value.map(a => ({ label: a.name, value: a.id }))
})

const categoryOptions = [
    { label: 'Food & Dining', value: 'Food' },
    { label: 'Groceries', value: 'Groceries' },
    { label: 'Travel & Transport', value: 'Travel' },
    { label: 'Shopping', value: 'Shopping' },
    { label: 'Utilities & Bills', value: 'Utilities' },
    { label: 'Housing & Rent', value: 'Housing' },
    { label: 'Healthcare', value: 'Healthcare' },
    { label: 'Entertainment', value: 'Entertainment' },
    { label: 'Salary / Income', value: 'Salary' },
    { label: 'Investment', value: 'Investment' },
    { label: 'Other', value: 'Other' }
]

async function fetchData() {
    loading.value = true
    try {
        if (accounts.value.length === 0) {
           const accRes = await financeApi.getAccounts()
           accounts.value = accRes.data
        }
        if (!selectedAccount.value && route.query.account_id) {
            selectedAccount.value = route.query.account_id as string
        }
        const res = await financeApi.getTransactions(selectedAccount.value || undefined)
        transactions.value = res.data
    } catch (e) {
        console.error("Failed to fetch transactions", e)
    } finally {
        loading.value = false
    }
}

function formatDate(dateStr: string) {
    return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

function getAccountName(id: string) {
    const acc = accounts.value.find(a => a.id === id)
    return acc ? acc.name : 'Unknown Account'
}

function openAddModal() {
    isEditing.value = false
    editingTxnId.value = null
    form.value = { 
        ...defaultForm, 
        account_id: selectedAccount.value || (accounts.value[0]?.id || ''),
        date: new Date().toISOString().slice(0, 16)
    }
    showModal.value = true
}

function openEditModal(txn: any) {
    isEditing.value = true
    editingTxnId.value = txn.id
    form.value = {
        description: txn.description,
        category: txn.category,
        amount: txn.amount,
        date: txn.date ? txn.date.slice(0, 16) : new Date().toISOString().slice(0, 16),
        account_id: txn.account_id
    }
    showModal.value = true
}

async function handleSubmit() {
    try {
        const payload = {
            description: form.value.description,
            category: form.value.category,
            amount: Number(form.value.amount), // Ensure number
            date: new Date(form.value.date).toISOString(),
            account_id: form.value.account_id
        }

        if (isEditing.value && editingTxnId.value) {
            await financeApi.updateTransaction(editingTxnId.value, payload)
            notify.success("Transaction updated")
        } else {
            // New Transaction
            // Note: client.ts might need update if createTransaction doesn't support all fields, checking...
            // Assuming createTransaction takes TransactionCreate which has these fields
            await financeApi.createTransaction(payload)
            notify.success("Transaction added")
        }
        showModal.value = false
        fetchData()
    } catch (e) {
        console.error(e)
        notify.error("Failed to save transaction")
    }
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <MainLayout>
        <div class="header-actions">
            <h1>Transactions</h1>
            
            <div class="actions-row">
                <CustomSelect 
                    v-model="selectedAccount" 
                    :options="[{ label: 'All Accounts', value: '' }, ...accountOptions]"
                    placeholder="All Accounts"
                    @update:modelValue="fetchData"
                    style="min-width: 250px;"
                />
                
                <button @click="openAddModal" class="btn btn-primary" style="margin-left: 1rem">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem">+</span> Add Transaction
                </button>
            </div>
        </div>

        <div v-if="loading" class="loading">Loading transactions...</div>

        <div v-else class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Account</th>
                        <th>Category</th>
                        <th class="text-right">Amount</th>
                        <th class="text-center">Edit</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="txn in transactions" :key="txn.id">
                        <td>{{ formatDate(txn.date) }}</td>
                        <td>{{ txn.description }}</td>
                        <td>{{ getAccountName(txn.account_id) }}</td>
                        <td><span class="badge">{{ txn.category || 'General' }}</span></td>
                        <td class="text-right font-mono" :class="{'credit': txn.amount > 0, 'debit': txn.amount < 0}">
                             {{ txn.amount }}
                        </td>
                        <td class="text-center">
                            <button @click="openEditModal(txn)" class="btn-icon">✏️</button>
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <div v-if="transactions.length === 0" class="empty-state">
                <p>No transactions found.</p>
            </div>
        </div>

        <!-- Global Styled Modal -->
        <div v-if="showModal" class="modal-overlay-global">
            <div class="modal-global">
                <div class="modal-header">
                    <h2 class="modal-title">{{ isEditing ? 'Edit Transaction' : 'Add Transaction' }}</h2>
                    <button class="btn-icon" @click="showModal = false">✕</button>
                </div>

                <form @submit.prevent="handleSubmit">
                    
                    <div class="form-group" v-if="!isEditing">
                        <label class="form-label">Account</label>
                        <CustomSelect 
                            v-model="form.account_id" 
                            :options="accountOptions"
                            placeholder="Select Account"
                        />
                    </div>

                    <div class="form-layout-row">
                        <div class="form-group half">
                            <label class="form-label">Amount (+ Income, - Expense)</label>
                            <input type="number" step="0.01" v-model="form.amount" class="form-input" required placeholder="-50.00" />
                        </div>
                        <div class="form-group half">
                            <label class="form-label">Date</label>
                             <input type="datetime-local" v-model="form.date" class="form-input" required />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Description</label>
                        <input v-model="form.description" class="form-input" required placeholder="e.g. Grocery shopping" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <CustomSelect 
                            v-model="form.category" 
                            :options="categoryOptions"
                            placeholder="Select Category"
                        />
                    </div>
                   
                    <div class="modal-footer">
                        <button type="button" @click="showModal = false" class="btn btn-outline">
                            <span class="icon-spacer">✕</span> Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            <span class="icon-spacer">💾</span> Save
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
.actions-row { display: flex; align-items: center; }

.table-container {
    background: var(--color-surface);
    border-radius: 1rem;
    box-shadow: var(--shadow-sm);
    overflow-x: auto;
    border: 1px solid var(--color-border);
}
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td {
    padding: var(--spacing-md); border-bottom: 1px solid var(--color-border); text-align: left;
}
.data-table th {
    background: var(--color-background); font-weight: 600; font-size: 0.85rem; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.05em;
}
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-mono { font-family: monospace; font-size: 1.1em; }
.credit { color: var(--color-success); }
.debit { color: var(--color-text-main); } 
.badge {
    background: var(--color-background); padding: 0.25rem 0.75rem; border-radius: 2rem; font-size: 0.75rem; font-weight: 500; border: 1px solid var(--color-border);
}
.empty-state { padding: var(--spacing-xl); text-align: center; color: var(--color-text-muted); }
.icon-spacer { margin-right: 0.5rem; }
.form-layout-row { display: flex; gap: 1rem; }
.half { flex: 1; }
</style>
