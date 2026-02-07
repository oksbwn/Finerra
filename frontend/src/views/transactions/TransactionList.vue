<script setup lang="ts">
import { computed } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'
import { useCurrency } from '@/composables/useCurrency'

const { formatAmount } = useCurrency()

// Props
const props = defineProps<{
    transactions: any[]
    accounts: any[]
    categories: any[]
    expenseGroups: any[]
    total: number
    loading: boolean
    selectedAccount: string
    categoryFilter: string
    searchQuery: string
    startDate: string
    endDate: string
    selectedTimeRange: string
    page: number
    pageSize: number
    txnSortKey: string
    txnSortOrder: 'asc' | 'desc'
}>()

// Emits
const emit = defineEmits<{
    'update:selectedAccount': [value: string]
    'update:categoryFilter': [value: string]
    'update:searchQuery': [value: string]
    'update:startDate': [value: string]
    'update:endDate': [value: string]
    'update:selectedTimeRange': [value: string]
    'update:page': [value: number]
    'sortChange': [key: string]
    'editTxn': [txn: any]
    'deleteSelected': []
    'importCsv': []
    'fetchData': []
    'resetFilters': []
}>()

// Local State
const selectedIds = defineModel<Set<string>>('selectedIds', { default: () => new Set() })

// Computed
const totalPages = computed(() => Math.ceil(props.total / props.pageSize))
const allSelected = computed(() => {
    return props.transactions.length > 0 && props.transactions.every(t => selectedIds.value.has(t.id))
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

const timeRangeOptions = [
    { label: 'All Time', value: 'all' },
    { label: 'Today', value: 'today' },
    { label: 'This Week', value: 'this-week' },
    { label: 'This Month', value: 'this-month' },
    { label: 'Last Month', value: 'last-month' },
    { label: 'Custom Range', value: 'custom' }
]

// Methods
function toggleSelectAll() {
    if (allSelected.value) {
        selectedIds.value.clear()
    } else {
        props.transactions.forEach(t => selectedIds.value.add(t.id))
    }
}

function toggleSelection(id: string) {
    if (selectedIds.value.has(id)) {
        selectedIds.value.delete(id)
    } else {
        selectedIds.value.add(id)
    }
}

function changePage(newPage: number) {
    if (newPage < 1 || newPage > totalPages.value) return
    emit('update:page', newPage)
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

function getAccountName(id: string) {
    const acc = props.accounts.find(a => a.id === id)
    return acc ? acc.name : 'Unknown Account'
}

function getCategoryDisplay(name: string) {
    if (!name || name === 'Uncategorized') return { icon: '🏷️', text: 'Uncategorized', color: '#9ca3af' }

    const cat = props.categories.find(c => c.name === name)
    if (cat) {
        let text = cat.name
        if (cat.parent_name) {
            text = `${cat.parent_name} › ${cat.name}`
        }
        return { icon: cat.icon || '🏷️', text: text, color: cat.color || '#3B82F6' }
    }

    return { icon: '🏷️', text: name, color: '#9ca3af' }
}

function getExpenseGroupName(id: string) {
    if (!id) return null
    const group = props.expenseGroups.find(g => g.id === id)
    return group ? group.name : null
}

function handleTimeRangeChange(val: string) {
    emit('update:selectedTimeRange', val)
}

function handleReset() {
    emit('resetFilters')
}
</script>

<template>
    <!-- Filter Bar -->
    <div class="filter-bar">
        <div class="filter-main">
            <div class="filter-group">
                <span class="filter-label">Time Range:</span>
                <div class="range-pill-group">
                    <button v-for="opt in timeRangeOptions" :key="opt.value" class="range-pill"
                        :class="{ active: selectedTimeRange === opt.value }" @click="handleTimeRangeChange(opt.value)">
                        {{ opt.label }}
                    </button>
                </div>
            </div>

            <div class="filter-divider" v-if="selectedTimeRange === 'custom'"></div>

            <div class="filter-group animate-in" v-if="selectedTimeRange === 'custom'">
                <input type="date" :value="startDate"
                    @input="emit('update:startDate', ($event.target as HTMLInputElement).value); emit('fetchData')"
                    class="date-input" />
                <span class="filter-separator">to</span>
                <input type="date" :value="endDate"
                    @input="emit('update:endDate', ($event.target as HTMLInputElement).value); emit('fetchData')"
                    class="date-input" />
            </div>

            <div class="filter-divider"></div>

            <div class="filter-group list-search-group">
                <div class="list-search-container">
                    <span class="search-icon-small">🔍</span>
                    <input type="text" :value="searchQuery"
                        @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
                        placeholder="Search description..." class="list-search-input">
                </div>
            </div>

            <div class="filter-divider"></div>

            <div class="filter-group">
                <CustomSelect :modelValue="categoryFilter"
                    @update:modelValue="emit('update:categoryFilter', $event); emit('fetchData')"
                    :options="[{ label: 'All Categories', value: '' }, ...categoryOptions]" placeholder="All Categories"
                    class="category-filter-select" />
            </div>
        </div>

        <button v-if="startDate || endDate || searchQuery || categoryFilter" class="btn-link" @click="handleReset">
            Reset
        </button>
    </div>

    <!-- Table -->
    <div class="content-card">
        <table class="modern-table">
            <thead>
                <tr>
                    <th class="col-checkbox">
                        <input type="checkbox" :checked="allSelected" @change="toggleSelectAll"
                            :disabled="transactions.length === 0">
                    </th>
                    <th class="col-date cursor-pointer hover:bg-gray-50" @click="emit('sortChange', 'date')">
                        Date
                        <span v-if="txnSortKey === 'date'" class="text-indigo-600 ml-1">{{ txnSortOrder ===
                            'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th class="col-recipient cursor-pointer hover:bg-gray-50"
                        @click="emit('sortChange', 'description')">
                        Recipient / Source
                        <span v-if="txnSortKey === 'description'" class="text-indigo-600 ml-1">{{ txnSortOrder
                            === 'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th class="col-description">Description</th>
                    <th class="col-amount cursor-pointer hover:bg-gray-50" @click="emit('sortChange', 'amount')">
                        Amount
                        <span v-if="txnSortKey === 'amount'" class="text-indigo-600 ml-1">{{ txnSortOrder ===
                            'asc' ? '↑' : '↓' }}</span>
                    </th>
                    <th class="col-actions"></th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="txn in transactions" :key="txn.id" :class="{ 'row-selected': selectedIds.has(txn.id) }">
                    <td class="col-checkbox">
                        <input type="checkbox" :checked="selectedIds.has(txn.id)" @change="toggleSelection(txn.id)">
                    </td>
                    <td class="col-date">
                        <div class="date-cell">
                            <div class="date-day">{{ formatDate(txn.date).day }}</div>
                            <div class="date-meta">{{ formatDate(txn.date).meta }}</div>
                        </div>
                    </td>
                    <td class="col-recipient">
                        <div class="txn-recipient">
                            <div class="txn-primary">{{ txn.recipient || txn.description }}</div>
                            <div class="txn-source-meta" v-if="txn.source">
                                <span class="source-icon-mini">{{ txn.source === 'SMS' ? '📱' : (txn.source ===
                                    'EMAIL' ? '📧' : '⌨️') }}</span>
                                {{ txn.source }}
                            </div>
                        </div>
                    </td>
                    <td class="col-description">
                        <div class="txn-description">
                            <div class="txn-description-text">
                                {{ txn.description }}
                                <span v-if="txn.latitude || txn.location_name" class="location-trigger"
                                    :title="txn.location_name || 'Location available'">
                                    📍
                                </span>
                            </div>
                            <div class="txn-meta-row">
                                <span class="account-badge">{{ getAccountName(txn.account_id) }}</span>

                                <span v-if="txn.is_ai_parsed" class="ai-badge-mini" title="Extracted using Gemini AI">✨
                                    AI</span>
                                <span v-if="txn.is_transfer" class="ai-badge-mini active-transfer"
                                    title="Auto-detected as internal transfer">🔄 Self-Transfer</span>
                                <span v-if="txn.exclude_from_reports" class="ai-badge-mini active-hidden"
                                    title="Excluded from reports and analytics">🚫 Hidden</span>
                                <span v-if="txn.is_emi" class="ai-badge-mini active-emi" title="Linked to EMI Loan">🏦
                                    EMI</span>

                                <div class="category-pill-wrapper">
                                    <span class="category-pill"
                                        :style="{ borderLeft: '3px solid ' + getCategoryDisplay(txn.category).color }">
                                        <span class="category-icon">{{ getCategoryDisplay(txn.category).icon
                                        }}</span>
                                        {{ getCategoryDisplay(txn.category).text }}
                                    </span>
                                </div>

                                <span class="ref-id-pill" v-if="txn.expense_group_id">
                                    <span class="ref-icon">📁</span> {{
                                        getExpenseGroupName(txn.expense_group_id) }}
                                </span>
                                <span class="ref-id-pill" v-if="txn.external_id">
                                    <span class="ref-icon">🆔</span> {{ txn.external_id }}
                                </span>
                            </div>
                        </div>
                    </td>
                    <td class="col-amount">
                        <div class="amount-cell"
                            :class="{ 'is-income': Number(txn.amount) > 0 && !txn.is_transfer, 'is-expense': Number(txn.amount) < 0 && !txn.is_transfer, 'is-transfer': txn.is_transfer }">
                            <span class="amount-icon">{{ txn.is_transfer ? '🔄' : (Number(txn.amount) > 0 ? '↓'
                                : '↑') }}</span>
                            <span class="amount-value">{{ formatAmount(Math.abs(Number(txn.amount))) }}</span>
                        </div>
                    </td>
                    <td class="col-actions">
                        <button class="icon-btn-edit" @click="emit('editTxn', txn)" title="Edit">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2.5">
                                <path
                                    d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>

        <div v-if="transactions.length === 0" class="empty-state">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
            </svg>
            <p>No transactions found</p>
        </div>

        <!-- Compact Pagination -->
        <div class="pagination-bar" v-if="total > 0">
            <span class="page-info">
                {{ (page - 1) * pageSize + 1 }}–{{ Math.min(page * pageSize, total) }} of {{ total }}
            </span>
            <div class="pagination-controls">
                <button class="page-btn" :disabled="page === 1" @click="changePage(page - 1)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 18l-6-6 6-6" />
                    </svg>
                </button>
                <button class="page-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18l6-6-6-6" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Filter Bar */
.filter-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    padding: 0.625rem 1rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    margin-bottom: 1.25rem;
}

.filter-main {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.list-search-container {
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon-small {
    position: absolute;
    left: 0.75rem;
    font-size: 0.8rem;
    color: #9ca3af;
}

.list-search-input {
    padding: 0.45rem 0.75rem 0.45rem 2rem;
    font-size: 0.8125rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    background: white;
    width: 220px;
    outline: none;
    transition: all 0.2s;
}

.list-search-input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.category-filter-select {
    min-width: 180px;
}

.filter-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

.filter-divider {
    width: 1px;
    height: 24px;
    background: #e5e7eb;
    margin: 0 0.25rem;
}

.range-pill-group {
    display: flex;
    gap: 0.375rem;
    background: #f3f4f6;
    padding: 2px;
    border-radius: 0.5rem;
    height: 36px;
    box-sizing: border-box;
    align-items: center;
}

.range-pill {
    padding: 0 0.75rem;
    height: 32px;
    border: none;
    background: transparent;
    border-radius: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 500;
    color: #4b5563;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
    display: flex;
    align-items: center;
}

.range-pill:hover:not(.active) {
    color: #111827;
    background: #e5e7eb;
}

.range-pill.active {
    background: white;
    color: #4f46e5;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.date-input {
    height: 36px;
    padding: 0 0.625rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.8125rem;
    color: #374151;
    background: white;
    outline: none;
    transition: border-color 0.2s;
    box-sizing: border-box;
}

.date-input:focus {
    border-color: #4f46e5;
}

.filter-separator {
    font-size: 0.75rem;
    color: #9ca3af;
    font-weight: 500;
}

.animate-in {
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateX(-10px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.btn-link {
    background: none;
    border: none;
    color: #4f46e5;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.375rem;
    transition: background 0.2s;
}

.btn-link:hover {
    background: #eff6ff;
}

/* Content Card */
.content-card {
    background: white;
    border-radius: 0.75rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    overflow-x: auto;
    border: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
    position: relative;
}

/* Modern Table */
.modern-table {
    width: 100%;
    min-width: 900px;
    border-collapse: collapse;
    font-size: 0.875rem;
    table-layout: fixed;
}

.modern-table thead th {
    background: #f9fafb;
    padding: 0.5rem 0.6rem;
    text-align: left;
    font-weight: 600;
    font-size: 0.7rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 2px solid #e5e7eb;
    position: sticky;
    top: 0;
    z-index: 10;
}

.modern-table tbody td {
    padding: 0.4rem 0.6rem;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
    vertical-align: middle;
}

.modern-table tbody tr:last-child td {
    border-bottom: none;
}

.modern-table tbody tr:nth-child(even) {
    background: #fafafa;
}

.modern-table tbody tr:hover {
    background: #f3f4f6;
}

.modern-table tbody tr.row-selected {
    background: #eff6ff;
}

.modern-table tbody tr.row-selected:hover {
    background: #dbeafe;
}

/* Column Sizing */
.col-checkbox {
    width: 40px;
    text-align: center;
    padding-left: 1rem !important;
}

.col-date {
    width: 110px;
    min-width: 110px;
    font-variant-numeric: tabular-nums;
}

.col-recipient {
    width: 250px;
    min-width: 200px;
    font-weight: 500;
}

.col-description {
    width: auto;
    min-width: 300px;
    color: #4b5563;
}

.col-amount {
    width: 120px;
    text-align: right;
    padding-right: 1.5rem !important;
}

.col-actions {
    width: 50px;
    text-align: center;
    padding-right: 1rem !important;
}

/* Date Cell */
.date-cell {
    line-height: 1.3;
}

.date-day {
    font-size: 0.875rem;
    font-weight: 600;
    color: #111827;
}

.date-meta {
    font-size: 0.65rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

/* Transaction Description */
.txn-description {
    line-height: 1.4;
}

.txn-primary {
    color: #111827;
    font-weight: 600;
    font-size: 0.875rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 0rem;
}

.txn-description-text {
    font-size: 0.75rem;
    color: #6b7280;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 0.125rem;
}

.txn-meta-row {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    flex-wrap: wrap;
}

.account-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.125rem 0.5rem;
    background: #f1f5f9;
    color: #475569;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid #e2e8f0;
}

.txn-source-meta {
    font-size: 0.65rem;
    color: #94a3b8;
    margin-top: 2px;
    display: flex;
    align-items: center;
    gap: 4px;
    font-weight: 500;
}

.source-icon-mini {
    font-size: 0.75rem;
}

.location-trigger {
    cursor: help;
    font-size: 0.8rem;
    margin-left: 4px;
    opacity: 0.8;
}

.ai-badge-mini {
    display: inline-flex;
    align-items: center;
    padding: 0.125rem 0.5rem;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid #bfdbfe;
}

.ai-badge-mini.active-transfer {
    background: #ecfdf5;
    color: #059669;
    border-color: #a7f3d0;
}

.ai-badge-mini.active-hidden {
    background: #fff1f2;
    color: #e11d48;
    border-color: #fecdd3;
}

.ai-badge-mini.active-emi {
    background: #eff6ff;
    color: #2563eb;
    border-color: #bfdbfe;
}

/* Category Pill */
.category-pill-wrapper {
    display: inline-block;
}

.category-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.15rem 0.6rem;
    background: #ffffff;
    color: #334155;
    border-radius: 6px;
    font-size: 0.725rem;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.category-icon {
    font-size: 0.8rem;
}

.ref-id-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.125rem 0.5rem;
    background: #fef3c7;
    color: #92400e;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    white-space: nowrap;
    border: 1px solid #fde68a;
}

.ref-icon {
    font-size: 0.75rem;
}

/* Amount Cell with Icon */
.amount-cell {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.375rem;
}

.amount-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.125rem;
    height: 1.125rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 700;
}

.amount-cell.is-income .amount-icon {
    background: #d1fae5;
    color: #059669;
}

.amount-cell.is-expense .amount-icon {
    background: #fee2e2;
    color: #dc2626;
}

.amount-cell.is-transfer .amount-icon {
    background: #e0e7ff;
    color: #4f46e5;
}

.amount-value {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    font-size: 0.875rem;
}

.amount-cell.is-income .amount-value {
    color: #059669;
}

.amount-cell.is-expense .amount-value {
    color: #374151;
}

.amount-cell.is-transfer .amount-value {
    color: #6b7280;
}

/* Icon Button */
.icon-btn-edit {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    padding: 0;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.icon-btn-edit:hover {
    background: #f8fafc;
    color: #4f46e5;
    border-color: #4f46e5;
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Empty State */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 2rem;
    color: #9ca3af;
    gap: 0.75rem;
}

.empty-state svg {
    opacity: 0.5;
}

.empty-state p {
    margin: 0;
    font-size: 0.875rem;
}

/* Pagination Bar */
.pagination-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-top: 1px solid #e5e7eb;
    background: #fafafa;
}

.page-info {
    font-size: 0.875rem;
    color: #6b7280;
}

.pagination-controls {
    display: flex;
    gap: 0.25rem;
}

.page-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    padding: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.375rem;
    color: #374151;
    cursor: pointer;
    transition: all 0.15s ease;
}

.page-btn:hover:not(:disabled) {
    background: #f9fafb;
    border-color: #d1d5db;
}

.page-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

.cursor-pointer {
    cursor: pointer;
}

.hover\:bg-gray-50:hover {
    background-color: rgb(249 250 251 / 1);
}

.text-indigo-600 {
    color: rgb(79 70 229 / 1);
}

.ml-1 {
    margin-left: 0.25rem;
}
</style>
