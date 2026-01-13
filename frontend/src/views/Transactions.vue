<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import { useRoute } from 'vue-router'
import CustomSelect from '@/components/CustomSelect.vue'
import { useNotificationStore } from '@/stores/notification'
import ImportModal from '@/components/ImportModal.vue'

// ... existing code ...

const showImportModal = ref(false)

const route = useRoute()
const notify = useNotificationStore()

const transactions = ref<any[]>([])
const accounts = ref<any[]>([])
const categories = ref<any[]>([])
const loading = ref(true)
const selectedAccount = ref<string>('')

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const editingTxnId = ref<string | null>(null)

// Pagination State
const page = ref(1)
const pageSize = ref(10) // Small default for testing
const total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

// Selection State
const selectedIds = ref<Set<string>>(new Set())
const allSelected = computed(() => {
    return transactions.value.length > 0 && transactions.value.every(t => selectedIds.value.has(t.id))
})

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

const categoryOptions = computed(() => {
     // Transform backend categories to select options
    return categories.value.map(c => ({
        label: `${c.icon || '🏷️'} ${c.name}`,
        value: c.name
    }))
})

async function fetchData() {
    loading.value = true
    try {
        if (accounts.value.length === 0) {
           const [accRes, catRes] = await Promise.all([
               financeApi.getAccounts(),
               financeApi.getCategories()
           ])
           accounts.value = accRes.data
           categories.value = catRes.data
        }
        if (!selectedAccount.value && route.query.account_id) {
            selectedAccount.value = route.query.account_id as string
        }
        
        // Pass page/limit
        const res = await financeApi.getTransactions(selectedAccount.value || undefined, page.value, pageSize.value)
        
        // Handle paginated response
        transactions.value = res.data.items
        total.value = res.data.total
        // Keep page within bounds if total reduced
        if (page.value > Math.ceil(total.value / pageSize.value) && page.value > 1) {
            page.value = 1
            fetchData() 
        }
    } catch (e) {
        console.error("Failed to fetch data", e)
        notify.error("Failed to load data")
    } finally {
        loading.value = false
        selectedIds.value.clear() // Clear selection on refresh
    }
}

function changePage(newPage: number) {
    if (newPage < 1 || newPage > totalPages.value) return
    page.value = newPage
    fetchData()
}

// Selection Logic
function toggleSelectAll() {
    if (allSelected.value) {
        selectedIds.value.clear()
    } else {
        transactions.value.forEach(t => selectedIds.value.add(t.id))
    }
}

function toggleSelection(id: string) {
    if (selectedIds.value.has(id)) {
        selectedIds.value.delete(id)
    } else {
        selectedIds.value.add(id)
    }
}

const showDeleteConfirm = ref(false)

function deleteSelected() {
    showDeleteConfirm.value = true
}

async function confirmDelete() {
    loading.value = true // fast visual feedback
    try {
        await financeApi.bulkDeleteTransactions(Array.from(selectedIds.value))
        notify.success(`Deleted ${selectedIds.value.size} transactions`)
        fetchData()
        showDeleteConfirm.value = false
        selectedIds.value.clear()
    } catch (e) {
        notify.error("Failed to delete transactions")
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


function getCategoryDisplay(name: string) {
    if (!name) return '📝 General'
    const cat = categories.value.find(c => c.name === name)
    // If found, return icon + name. If not (e.g. legacy or custom), just name.
    return cat ? `${cat.icon || '🏷️'} ${cat.name}` : `🏷️ ${name}`
}

function getSourceIcon(source: string) {
    switch ((source || '').toUpperCase()) {
        case 'CSV': return '📄'
        case 'EXCEL': return '📊'
        case 'SMS': return '📱'
        case 'EMAIL': return '📧'
        case 'MANUAL': return '👤'
        default: return '👤'
    }
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
                    @update:modelValue="page=1; fetchData()"
                    style="min-width: 250px;"
                />
                
                <button v-if="selectedIds.size > 0" @click="deleteSelected" class="btn btn-danger" style="margin-left: 1rem">
                    <span style="margin-right: 0.5rem">🗑️</span> Delete ({{ selectedIds.size }})
                </button>

                <button @click="showImportModal = true" class="btn btn-outline" style="margin-left: 1rem">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem">📥</span> Import
                </button>
                
                <button @click="openAddModal" class="btn btn-primary" style="margin-left: 1rem">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem">+</span> Add
                </button>

                <ImportModal :isOpen="showImportModal" @close="showImportModal = false" @import-success="fetchData" />
            </div>
        </div>

        <div v-if="loading" class="loading">Loading transactions...</div>

        <div v-else class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th style="width: 40px"><input type="checkbox" :checked="allSelected" @change="toggleSelectAll" :disabled="transactions.length === 0"></th>
                        <th style="width: 40px"></th>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Account</th>
                        <th>Category</th>
                        <th class="text-right">Amount</th>
                        <th class="text-center">Edit</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="txn in transactions" :key="txn.id" :class="{ 'selected-row': selectedIds.has(txn.id) }">
                        <td><input type="checkbox" :checked="selectedIds.has(txn.id)" @change="toggleSelection(txn.id)"></td>
                        <td class="text-center" :title="txn.source">{{ getSourceIcon(txn.source) }}</td>
                        <td>{{ formatDate(txn.date) }}</td>
                        <td>{{ txn.description }}</td>
                        <td>{{ getAccountName(txn.account_id) }}</td>
                        <td><span class="badge">{{ getCategoryDisplay(txn.category) }}</span></td>
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
            
            <!-- Pagination Controls -->
            <div class="pagination-footer" v-if="total > 0">
                <span class="page-info">
                    Showing <strong>{{ (page - 1) * pageSize + 1 }}-{{ Math.min(page * pageSize, total) }}</strong> of <strong>{{ total }}</strong>
                </span>
                <div class="pagination-actions">
                    <button class="btn btn-outline btn-sm" :disabled="page === 1" @click="changePage(page - 1)">
                        ← Previous
                    </button>
                    <button class="btn btn-outline btn-sm" :disabled="page >= totalPages" @click="changePage(page + 1)">
                        Next →
                    </button>
                </div>
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
                            allow-new
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


        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteConfirm" class="modal-overlay-global">
            <div class="modal-global" style="max-width: 400px;">
                <div class="modal-header">
                    <h2 class="modal-title">Delete Transactions?</h2>
                    <button class="btn-icon" @click="showDeleteConfirm = false">✕</button>
                </div>
                <div style="padding: 1.5rem;">
                    <p style="margin-bottom: 1.5rem; color: var(--color-text-muted);">
                        Are you sure you want to delete <strong>{{ selectedIds.size }}</strong> transactions? This action cannot be undone.
                    </p>
                    <div class="modal-footer" style="padding: 0; border: none; background: transparent;">
                        <button class="btn btn-outline" @click="showDeleteConfirm = false">Cancel</button>
                        <button class="btn btn-danger" @click="confirmDelete">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    </MainLayout>
</template>

<style scoped>
/* Professional UI Overhaul */
.header-actions {
    display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;
    background: linear-gradient(to right, rgba(255,255,255,0.8), rgba(255,255,255,0.5));
    backdrop-filter: blur(8px);
    padding: 1.5rem 2rem;
    border-radius: 1.5rem;
    border: 1px solid rgba(255,255,255,0.4);
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.header-actions h1 {
    font-size: 1.75rem; font-weight: 700; color: var(--color-text-main); letter-spacing: -0.02em;
    margin: 0;
}
.actions-row { display: flex; align-items: center; gap: 1rem; }

.table-container {
    background: #fff;
    border-radius: 1.5rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.04);
    overflow: hidden; /* For border radius */
    border: 1px solid rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.data-table { 
    width: 100%; border-collapse: separate; border-spacing: 0; 
}
.data-table th, .data-table td {
    padding: 1.25rem 1.5rem; 
    border-bottom: 1px solid #f3f4f6;
    transition: background-color 0.15s ease;
}
.data-table th {
    background: #f9fafb;
    font-weight: 600; font-size: 0.8rem; 
    color: #6b7280; 
    text-transform: uppercase; letter-spacing: 0.05em;
    border-bottom: 2px solid #e5e7eb;
    white-space: nowrap;
}
.data-table tbody tr {
    transition: all 0.2s ease;
}
.data-table tbody tr:hover {
    background-color: #f9fafb;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    position: relative; z-index: 1;
}
.data-table tbody tr:last-child td {
    border-bottom: none;
}

.text-right { text-align: right; }
.text-center { text-align: center; }
.font-mono { 
    font-family: 'SF Mono', 'Roboto Mono', Menlo, monospace; 
    font-size: 1rem; font-weight: 500; 
}

/* Financial Colors */
.credit { color: #10b981; font-weight: 600; }
.debit { color: #1f2937; font-weight: 500; }

/* Badges */
.badge {
    background: #f3f4f6; 
    color: #374151;
    padding: 0.35rem 0.85rem; 
    border-radius: 9999px; 
    font-size: 0.8rem; font-weight: 600; 
    border: 1px solid #e5e7eb;
    display: inline-flex; align-items: center; gap: 0.35rem;
    transition: all 0.2s;
}
.badge:hover {
    background: #e5e7eb;
    transform: scale(1.05);
}

.empty-state { 
    padding: 4rem 2rem; text-align: center; 
    color: #9ca3af; font-size: 1.1rem; 
    display: flex; flex-direction: column; align-items: center; gap: 1rem;
}

/* Form Styles */
.form-layout-row { display: flex; gap: 1.5rem; }
.half { flex: 1; }
.form-input {
    width: 100%; padding: 0.75rem 1rem;
    border: 1px solid #e5e7eb; border-radius: 0.75rem;
    font-size: 1rem; transition: all 0.2s;
    background: #f9fafb;
}
.form-input:focus {
    border-color: #6366f1; background: #fff;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    outline: none;
}
/* Button Styles */
/* Button Styles - Clean & Minimal */
.btn {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 0.6rem 1.2rem; border-radius: 0.5rem;
    font-weight: 500; font-size: 0.9rem; cursor: pointer;
    transition: all 0.15s ease;
    border: 1px solid transparent;
}
.btn:active { transform: translateY(1px); }

.btn-primary {
    background-color: #4f46e5; color: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.btn-primary:hover {
    background-color: #4338ca;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-outline {
    background-color: white; color: #374151;
    border-color: #d1d5db;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.btn-outline:hover {
    background-color: #f9fafb;
    border-color: #9ca3af; color: #111827;
}

.btn-danger { 
    background-color: #fff; color: #dc2626; 
    border-color: #fecaca;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.btn-danger:hover { 
    background-color: #fef2f2; border-color: #fca5a5; color: #b91c1c; 
}

.btn-icon {
    display: inline-flex; align-items: center; justify-content: center;
    width: 2rem; height: 2rem; padding: 0;
    border-radius: 0.375rem; color: #6b7280;
    transition: color 0.15s, background-color 0.15s;
}
.btn-icon:hover { 
    background-color: #f3f4f6; color: #111827; 
}

.btn-sm {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
}

/* Pagination */
.pagination-footer {
    display: flex; justify-content: space-between; align-items: center; 
    padding: 1rem 1.5rem; 
    border-top: 1px solid #f3f4f6;
    background-color: #fff;
    border-bottom-left-radius: 1.5rem;
    border-bottom-right-radius: 1.5rem;
}
.page-info { 
    color: #6b7280; font-size: 0.875rem; 
}
.page-info strong { color: #111827; font-weight: 600; }
.pagination-actions { display: flex; gap: 0.5rem; }

/* Anim */
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.table-container { animation: fadeIn 0.4s ease-out; }
.header-actions { animation: fadeIn 0.4s ease-out; }
</style>
