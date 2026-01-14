<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import CustomSelect from '@/components/CustomSelect.vue'
import { useNotificationStore } from '@/stores/notification'
import { useCurrency } from '@/composables/useCurrency'

const { formatAmount } = useCurrency()
const notify = useNotificationStore()

const budgets = ref<any[]>([])
const categories = ref<any[]>([])
const loading = ref(true)

const showModal = ref(false)
const newBudget = ref({
    category: '',
    amount_limit: null as number | null
})

// Metrics
const overallBudget = computed(() => budgets.value.find(b => b.category === 'OVERALL'))
const categoryBudgets = computed(() => budgets.value.filter(b => b.category !== 'OVERALL'))

// For Summary Cards (exclude OVERALL from sum to avoid double counting if we just want sum of categories?)
// OR do we want sum of categories?
// Current logic: Sum of ALL budgets. If OVERALL exists, it might be confusing to sum it with others.
// Let's change Summary Cards to: "Total Budget (Sum of Categories)" vs "Overall Limit".
// actually if OVERALL exists, that IS the limit.
// Let's refine summary:
// If OVERALL exists: Show "Overall Limit", "Total Spent", "Remaining".
// If NOT: Show "Sum of Category Budgets", etc.
const effectiveTotalBudget = computed(() => {
    if (overallBudget.value) return Number(overallBudget.value.amount_limit)
    return categoryBudgets.value.reduce((sum, b) => sum + Number(b.amount_limit), 0)
})
const totalSpent = computed(() => {
    if (overallBudget.value) return Number(overallBudget.value.spent)
     return categoryBudgets.value.reduce((sum, b) => sum + Number(b.spent), 0)
})
const totalRemaining = computed(() => effectiveTotalBudget.value - totalSpent.value)

const spendingVelocity = computed(() => {
    const now = new Date()
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
    const dayOfMonth = now.getDate()
    const monthProgress = (dayOfMonth / daysInMonth) * 100
    
    if (!overallBudget.value) return { status: 'stable', diff: 0 }
    
    const diff = overallBudget.value.percentage - monthProgress
    let status = 'stable'
    if (diff > 15) status = 'aggressive'
    else if (diff > 5) status = 'warning'
    
    return { status, diff, monthProgress }
})

const categoryOptions = computed(() => {
    return categories.value.map(c => ({
        label: `${c.icon || '🏷️'} ${c.name}`,
        value: c.name
    }))
})

function getCategoryDisplay(name: string) {
    if (name === 'OVERALL') return { icon: '🏁', text: 'Overall Monthly Limit', color: '#10b981' }
    if (!name) return { icon: '📝', text: 'General', color: '#9ca3af' }
    const cat = categories.value.find(c => c.name === name)
    return cat ? { icon: cat.icon || '🏷️', text: cat.name, color: cat.color || '#3B82F6' } : { icon: '🏷️', text: name, color: '#9ca3af' }
}

async function fetchData() {
    loading.value = true
    try {
        const [budgetRes, catRes] = await Promise.all([
            financeApi.getBudgets(),
            financeApi.getCategories()
        ])
        budgets.value = budgetRes.data
        categories.value = catRes.data
    } catch (e) {
        console.error(e)
        notify.error("Failed to load budgets")
    } finally {
        loading.value = false
    }
}

function openSetBudgetModal(isOverall = false) {
    if (isOverall) {
        newBudget.value = { category: 'OVERALL', amount_limit: null }
    } else {
        newBudget.value = { category: '', amount_limit: null }
    }
    showModal.value = true
}

function editBudget(b: any) {
    newBudget.value = { 
        category: b.category, 
        amount_limit: b.amount_limit 
    }
    showModal.value = true
}

async function saveBudget() {
    if (!newBudget.value.category || !newBudget.value.amount_limit) return
    try {
        await financeApi.setBudget(newBudget.value)
        notify.success("Budget saved")
        showModal.value = false
        fetchData()
    } catch (e) {
        notify.error("Failed to save budget")
    }
}

async function deleteBudget(id: string) {
    if(!confirm("Remove this budget?")) return
    try {
        await financeApi.deleteBudget(id)
        notify.success("Budget removed")
        fetchData()
    } catch (e) {
        notify.error("Failed to remove budget")
    }
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <MainLayout>
        <div class="budgets-view">
            <!-- Premium Header -->
            <div class="page-header-compact">
                <div class="header-left">
                    <h1 class="page-title">Budgets & Limits</h1>
                    <p class="page-subtitle">Define your monthly spending boundaries</p>
                </div>
                
                <div class="header-actions">
                    <button v-if="!overallBudget" class="btn-outline-compact" @click="openSetBudgetModal(true)">
                        + Total Limit
                    </button>
                    <button class="btn-primary-glow" @click="openSetBudgetModal(false)">
                        <span class="btn-icon-plus">+</span> Set Category
                    </button>
                </div>
            </div>

            <div v-if="loading" class="loading-state">
                <div class="loader-spinner"></div>
                <p>Calculating your spending power...</p>
            </div>

            <div v-else class="animate-in">
                    <!-- Overall Budget Hero Card (Premium Midnight) -->
                    <div v-if="overallBudget" class="overall-premium-card">
                        <div class="card-glass-content">
                            <div class="card-top">
                                <div class="card-main">
                                    <div class="card-header-badge">Overall Target</div>
                                    <div class="price-row">
                                        <span class="amount-large">{{ formatAmount(overallBudget.spent) }}</span>
                                        <span class="separator">/</span>
                                        <span class="total-limit">{{ formatAmount(overallBudget.amount_limit) }}</span>
                                    </div>
                                </div>
                                <div class="card-actions">
                                    <button @click="editBudget(overallBudget)" class="btn-glass-sq">✏️</button>
                                </div>
                            </div>

                            <div class="velocity-indicator" :class="spendingVelocity.status">
                                <div class="velocity-icon">
                                    <span v-if="spendingVelocity.status === 'aggressive'">⚠️</span>
                                    <span v-else-if="spendingVelocity.status === 'warning'">🔔</span>
                                    <span v-else>✅</span>
                                </div>
                                <div class="velocity-text">
                                    <template v-if="spendingVelocity.status === 'aggressive'">
                                        Spending is <strong>{{ spendingVelocity.diff.toFixed(0) }}% ahead</strong> of the monthly curve. Consider cooling off.
                                    </template>
                                    <template v-else-if="spendingVelocity.status === 'warning'">
                                        Slightly above pace. {{ formatAmount(overallBudget.remaining) }} left for {{ 30 - new Date().getDate() }} days.
                                    </template>
                                    <template v-else>
                                        Under control. You are spend-aligned with the monthly progress.
                                    </template>
                                </div>
                            </div>

                            <div class="progress-container-lg">
                                <div class="progress-bar-bg-lg">
                                    <div class="progress-bar-fill-lg" 
                                        :style="{ width: Math.min(overallBudget.percentage, 100) + '%' }"
                                        :class="{ 
                                            'warning': overallBudget.percentage > 80 && overallBudget.percentage <= 100,
                                            'danger': overallBudget.percentage > 100 
                                        }"
                                    ></div>
                                    <!-- Month progress vertical line marker -->
                                    <div class="month-marker" :style="{ left: spendingVelocity.monthProgress + '%' }">
                                        <span class="marker-label">Today</span>
                                    </div>
                                </div>
                                <div class="progress-meta">
                                    <span class="percentage-badge" :class="{ 'over': overallBudget.percentage > 100 }">
                                        {{ overallBudget.percentage?.toFixed(1) }}% Utilized
                                    </span>
                                    <span class="remaining-text">
                                        {{ overallBudget.spent > overallBudget.amount_limit ? 'Overspent by ' : 'Safe Capacity: ' }} 
                                        <strong>{{ formatAmount(Math.abs(overallBudget.remaining)) }}</strong>
                                    </span>
                                </div>
                            </div>
                        </div>
                        <div class="mesh-blob blob-1"></div>
                        <div class="mesh-blob blob-2"></div>
                    </div>

                    <!-- Summary Grid -->
                    <div class="summary-widgets-budget">
                        <div class="mini-stat-card glass h-glow-primary">
                            <div class="stat-top">
                                <span class="stat-label">Budgeted</span>
                                <span class="stat-icon-bg gray">📑</span>
                            </div>
                            <div class="stat-value">{{ formatAmount(effectiveTotalBudget) }}</div>
                        </div>
                        <div class="mini-stat-card glass h-glow-danger">
                            <div class="stat-top">
                                <span class="stat-label">Total Outflow</span>
                                <span class="stat-icon-bg red">💸</span>
                            </div>
                            <div class="stat-value">{{ formatAmount(totalSpent) }}</div>
                        </div>
                        <div class="mini-stat-card glass h-glow-success">
                            <div class="stat-top">
                                <span class="stat-label">Budget Safe</span>
                                <span class="stat-icon-bg green">🛡️</span>
                            </div>
                            <div class="stat-value" :class="{ 'negative': totalRemaining < 0 }">{{ formatAmount(totalRemaining) }}</div>
                        </div>
                    </div>

                    <h2 class="section-title">Category Limits</h2>
                    <div class="budget-grid">
                        <div v-for="b in categoryBudgets" :key="b.id" class="glass-card budget-card" :style="{ borderLeft: `4px solid ${getCategoryDisplay(b.category).color}` }">
                            <div class="card-top">
                                <div class="card-main">
                                    <div class="card-icon-wrapper" :style="{ background: getCategoryDisplay(b.category).color + '15', color: getCategoryDisplay(b.category).color }">
                                        {{ getCategoryDisplay(b.category).icon }}
                                    </div>
                                    <span class="card-name">{{ getCategoryDisplay(b.category).text }}</span>
                                </div>
                                <div class="card-actions">
                                    <button @click="editBudget(b)" class="btn-ghost-sm" title="Edit Budget">✏️</button>
                                    <button @click="deleteBudget(b.id)" class="btn-ghost-sm danger" title="Delete Budget">✕</button>
                                </div>
                            </div>
                            <!-- Decorative BG Icon -->
                            <div class="card-bg-icon">{{ getCategoryDisplay(b.category).icon }}</div>
                            
                            <div class="progress-section">
                                <div class="progress-info-compact">
                                    <span class="spent">{{ formatAmount(b.spent) }}</span>
                                    <span class="limit">of {{ formatAmount(b.amount_limit) }}</span>
                                </div>
                                <div class="progress-bar-bg-sm">
                                    <div class="progress-bar-fill-sm" 
                                        :style="{ 
                                            width: Math.min(b.percentage, 100) + '%',
                                            backgroundColor: b.percentage > 100 ? '#ef4444' : (b.percentage > 80 ? '#f59e0b' : getCategoryDisplay(b.category).color)
                                        }"
                                    ></div>
                                </div>
                                <div class="remaining-footer" :class="{ 'over': b.remaining < 0 }">
                                    {{ b.remaining >= 0 ? `${formatAmount(b.remaining)} left` : `${formatAmount(Math.abs(b.remaining))} over` }}
                                </div>
                            </div>
                        </div>

                        <div v-if="categoryBudgets.length === 0" class="empty-card" @click="openSetBudgetModal(false)">
                            <span class="empty-plus">+</span>
                            <p>Enforce category limit</p>
                        </div>
                    </div>
            </div>
        </div>

        <!-- Budget Modal -->
        <div v-if="showModal" class="modal-overlay-global">
            <div class="modal-global glass">
                <div class="modal-header">
                    <h2 class="modal-title">{{ newBudget.category === 'OVERALL' ? 'Total Monthly Limit' : 'Category Budget' }}</h2>
                    <button class="btn-icon-circle" @click="showModal = false">✕</button>
                </div>

                <form @submit.prevent="saveBudget" class="form-compact">
                    <div class="form-group" v-if="newBudget.category !== 'OVERALL'">
                        <label class="form-label">Category</label>
                        <CustomSelect 
                            v-model="newBudget.category"
                            :options="categoryOptions"
                            placeholder="Select Category"
                        />
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Monthly Limit (₹)</label>
                        <div class="amount-input-wrapper">
                            <span class="input-prefix">₹</span>
                            <input type="number" v-model="newBudget.amount_limit" class="form-input" required placeholder="5,000" />
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button type="button" @click="showModal = false" class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary-glow">Save Budget</button>
                    </div>
                </form>
            </div>
        </div>
    </MainLayout>
</template>

<style scoped>
.budgets-view {
    padding-bottom: 4rem;
}

/* Premium Header Styling */
.page-header-compact {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 2rem;
}

.header-left {
    display: flex;
    flex-direction: column;
}

.page-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
    letter-spacing: -0.02em;
}

.page-subtitle {
    font-size: 0.875rem;
    color: #64748b;
    margin: 0.25rem 0 0 0;
}

.header-actions {
    display: flex;
    gap: 0.75rem;
}

/* Premium Midnight Card */
.overall-premium-card {
    background: #0f172a;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 1.5rem;
    padding: 2.25rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    color: white;
    box-shadow: 0 20px 25px -5px rgba(0, 0,0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.card-glass-content {
    position: relative;
    z-index: 10;
}

.card-header-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.price-row {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}

.amount-large { font-size: 2.75rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.05em; }
.separator { font-size: 1.5rem; color: #475569; }
.total-limit { font-size: 1.5rem; font-weight: 600; color: #94a3b8; }

.velocity-indicator {
    margin-top: 1.5rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
}

.velocity-indicator.aggressive { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.2); }
.velocity-indicator.warning { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); }

.velocity-icon { font-size: 1.25rem; }
.velocity-text { color: #cbd5e1; line-height: 1.5; }
.velocity-text strong { color: #f8fafc; font-weight: 700; }

.progress-container-lg {
    margin-top: 2rem;
}

.progress-bar-bg-lg {
    height: 12px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 6px;
    position: relative;
    overflow: visible;
}

.progress-bar-fill-lg {
    height: 100%;
    background: #6366f1;
    border-radius: 6px;
    transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
}

.progress-bar-fill-lg.warning { background: #f59e0b; box-shadow: 0 0 15px rgba(245, 158, 11, 0.3); }
.progress-bar-fill-lg.danger { background: #ef4444; box-shadow: 0 0 15px rgba(239, 68, 68, 0.3); }

.month-marker {
    position: absolute;
    top: -4px;
    bottom: -4px;
    width: 2px;
    background: white;
    z-index: 5;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
}

.marker-label {
    position: absolute;
    top: -20px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    white-space: nowrap;
}

.progress-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 1rem;
}

.percentage-badge {
    padding: 0.25rem 0.75rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
}

.percentage-badge.over { color: #ef4444; background: rgba(239, 68, 68, 0.1); }

.remaining-text { font-size: 0.875rem; color: #94a3b8; }
.remaining-text strong { color: white; }

/* Mesh Blobs */
.mesh-blob {
    position: absolute;
    filter: blur(80px);
    opacity: 0.15;
    border-radius: 50%;
    z-index: 1;
}

.blob-1 { width: 400px; height: 400px; background: #3b82f6; top: -150px; right: -100px; }
.blob-2 { width: 350px; height: 350px; background: #6366f1; bottom: -100px; left: -100px; }

/* Summary Grid */
.summary-widgets-budget {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-bottom: 2.5rem;
}

.mini-stat-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 1.25rem;
    padding: 1.25rem;
    transition: all 0.2s;
}

.mini-stat-card:hover { border-color: #cbd5e1; transform: translateY(-2px); }

/* Category Grid */
.section-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    margin-bottom: 1.25rem;
}

.budget-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.25rem;
}

.glass-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 1.25rem;
    padding: 1.5rem;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}

.card-top { display: flex; justify-content: space-between; align-items: flex-start; position: relative; z-index: 2; }
.card-main { display: flex; align-items: center; gap: 0.75rem; }
.card-name { font-size: 1rem; font-weight: 700; color: #1e293b; }

.card-icon-wrapper {
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 0.625rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    backdrop-filter: blur(4px);
}

.card-bg-icon {
    position: absolute;
    bottom: -1rem;
    right: -1rem;
    font-size: 6rem;
    opacity: 0.05;
    transform: rotate(-15deg);
    pointer-events: none;
    z-index: 0;
    filter: grayscale(100%);
}

.btn-glass-sq {
    width: 2.25rem;
    height: 2.25rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.75rem;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    backdrop-filter: blur(10px);
    transition: all 0.2s;
}

.btn-glass-sq:hover { background: rgba(255, 255, 255, 0.15); transform: translateY(-1px); }
.btn-glass-sq.danger:hover { background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.3); }

/* Buttons */
.btn-primary-glow {
    padding: 0.625rem 1.25rem;
    background: #4f46e5;
    color: white;
    border-radius: 0.75rem;
    font-weight: 600;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
}

.btn-outline-compact {
    padding: 0.625rem 1.25rem;
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
}

.btn-ghost-sm {
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
    border: none;
    background: transparent;
    color: #94a3b8;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-ghost-sm:hover {
    background: #f1f5f9;
    color: #475569;
}

.btn-ghost-sm.danger:hover {
    background: #fef2f2;
    color: #ef4444;
}

/* Animations */
.animate-in { animation: slideUp 0.5s ease-out forwards; }
@keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 640px) {
    .summary-widgets-budget { grid-template-columns: 1fr; }
    .amount-large { font-size: 2rem; }
}
</style>
