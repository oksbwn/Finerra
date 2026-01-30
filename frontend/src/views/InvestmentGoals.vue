<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import { useCurrency } from '@/composables/useCurrency'
import { useNotificationStore } from '@/stores/notification'
import CustomSelect from '@/components/CustomSelect.vue'
import {
    Plus,
    Calendar,
    Trash2,
    Pencil,
    TrendingUp,
    Coins,
    Building2,
    X,
    ChevronDown,
    ChevronUp
} from 'lucide-vue-next'

const notify = useNotificationStore()
const { formatAmount } = useCurrency()

const goals = ref<any[]>([])
const accounts = ref<any[]>([])
const portfolio = ref<any[]>([])
const loading = ref(true)
const showModal = ref(false)
const showDeleteModal = ref(false)
const goalToDelete = ref<string | null>(null)
const showAssetModal = ref(false)
const isEditing = ref(false)
const editingId = ref<string | null>(null)
const selectedGoalId = ref<string | null>(null)
const expandedGoals = ref<Record<string, boolean>>({})

const toggleExpand = (goalId: string) => {
    expandedGoals.value[goalId] = !expandedGoals.value[goalId]
}

const goalForm = ref({
    name: '',
    target_amount: 0,
    target_date: '',
    icon: '🎯',
    color: '#3b82f6'
})

const assetForm = ref({
    type: 'MANUAL', // MANUAL, BANK_ACCOUNT, MUTUAL_FUND
    name: '',
    manual_amount: 0,
    interest_rate: 0,
    linked_account_id: null as string | null,
    holding_id: null as string | null
})

const fetchGoals = async () => {
    loading.value = true
    try {
        const res = await financeApi.getInvestmentGoals()
        goals.value = res.data
    } catch (e) {
        notify.error("Failed to load goals")
    } finally {
        loading.value = false
    }
}

const fetchAccounts = async () => {
    try {
        const res = await financeApi.getAccounts()
        accounts.value = res.data.filter((a: any) => a.type === 'BANK' || a.type === 'INVESTMENT')
    } catch (e) {
        console.error("Failed to fetch accounts")
    }
}

const fetchPortfolio = async () => {
    try {
        const res = await financeApi.getPortfolio()
        portfolio.value = res.data
    } catch (e) {
        console.error("Failed to fetch portfolio")
    }
}

const openAddModal = () => {
    isEditing.value = false
    editingId.value = null
    goalForm.value = {
        name: '',
        target_amount: 0,
        target_date: '',
        icon: '🎯',
        color: '#3b82f6'
    }
    showModal.value = true
}

const openEditModal = (goal: any) => {
    isEditing.value = true
    editingId.value = goal.id
    goalForm.value = {
        name: goal.name,
        target_amount: Number(goal.target_amount),
        target_date: goal.target_date ? goal.target_date.split('T')[0] : '',
        icon: goal.icon || '🎯',
        color: goal.color || '#3b82f6'
    }
    showModal.value = true
}

const handleGoalSubmit = async () => {
    try {
        if (isEditing.value && editingId.value) {
            await financeApi.updateInvestmentGoal(editingId.value, goalForm.value)
            notify.success("Goal updated")
        } else {
            await financeApi.createInvestmentGoal(goalForm.value)
            notify.success("Goal created")
        }
        showModal.value = false
        fetchGoals()
    } catch (e) {
        notify.error("Failed to save goal")
    }
}

const confirmDelete = (id: string) => {
    goalToDelete.value = id
    showDeleteModal.value = true
}

const deleteGoal = async () => {
    if (!goalToDelete.value) return
    try {
        await financeApi.deleteInvestmentGoal(goalToDelete.value)
        notify.success("Goal deleted")
        showDeleteModal.value = false
        goalToDelete.value = null
        fetchGoals()
    } catch (e) {
        notify.error("Failed to delete goal")
    }
}

const openAssetModal = (goalId: string) => {
    selectedGoalId.value = goalId
    assetForm.value = {
        type: 'MANUAL',
        name: '',
        manual_amount: 0,
        interest_rate: 0,
        linked_account_id: null,
        holding_id: null
    }
    showAssetModal.value = true
    fetchPortfolio() // Refresh when opening
}

const handleAssetSubmit = async () => {
    if (!selectedGoalId.value) return
    try {
        const payload = { ...assetForm.value }
        // Clean up empty strings to avoid DB constraint issues
        if (!payload.linked_account_id) payload.linked_account_id = null
        if (!payload.holding_id) payload.holding_id = null

        if (payload.type === 'MUTUAL_FUND') {
            if (!payload.holding_id) throw new Error("Please select a fund")
            await financeApi.linkHoldingToGoal(selectedGoalId.value, payload.holding_id)
            notify.success("Mutual Fund linked to goal")
        } else {
            await (financeApi as any).addGoalAsset(selectedGoalId.value, payload)
            notify.success("Asset added to goal")
        }
        showAssetModal.value = false
        fetchGoals()
    } catch (e: any) {
        notify.error(e.message || "Failed to add asset")
    }
}

const removeAsset = async (assetId: string) => {
    try {
        await (financeApi as any).removeGoalAsset(assetId)
        notify.success("Asset removed")
        fetchGoals()
    } catch (e) {
        notify.error("Failed to remove asset")
    }
}

const unlinkHolding = async (goalId: string, holdingId: string) => {
    if (!confirm('Are you sure you want to remove this mutual fund from the goal?')) return
    try {
        await financeApi.unlinkHoldingFromGoal(goalId, holdingId)
        notify.success("Mutual fund unlinked")
        fetchGoals()
    } catch (e) {
        notify.error("Failed to unlink mutual fund")
    }
}

const accountOptions = computed(() => {
    return accounts.value.map(acc => ({
        label: `${acc.name} (${formatAmount(acc.balance)})`,
        value: acc.id
    }))
})

const portfolioOptions = computed(() => {
    if (!portfolio.value || !Array.isArray(portfolio.value)) return []
    return portfolio.value.map(fund => ({
        label: `${fund.folio_number || 'No Folio'} • ${formatAmount(fund.current_value || 0)} • ${fund.scheme_name || 'Unnamed Fund'}`,
        value: fund.id
    }))
})

onMounted(() => {
    fetchGoals()
    fetchAccounts()
    fetchPortfolio()
})
</script>

<template>
    <MainLayout>
        <div class="goals-container">
            <header class="page-header">
                <div class="header-left">
                    <h1 class="page-title">Financial Goals</h1>
                    <span class="transaction-count ml-4">{{ goals.length }} goals</span>
                </div>
                <div class="header-actions">
                    <button @click="openAddModal" class="btn-premium-primary">
                        <div class="btn-glow"></div>
                        <Plus :size="16" />
                        <span>New Goal</span>
                    </button>
                </div>
            </header>

            <div v-if="loading" class="flex justify-center items-center py-20">
                <div class="loader"></div>
            </div>

            <div v-else-if="goals.length === 0" class="empty-state glass">
                <div class="empty-icon">🎯</div>
                <h3>No Goals Set</h3>
                <p>Start by creating your first financial goal.</p>
                <button @click="openAddModal" class="btn-clean-primary mt-4">Create Goal</button>
            </div>

            <div v-else class="goals-grid">
                <div v-for="goal in goals" :key="goal.id" class="goal-card glass"
                    :style="{ borderTopColor: goal.color }">
                    <div class="goal-card-header">
                        <div class="goal-icon-bg" :style="{ backgroundColor: goal.color + '15' }">
                            <span class="goal-emoji" :style="{ color: goal.color }">{{ goal.icon }}</span>
                        </div>
                        <div class="goal-title-area">
                            <h3>{{ goal.name }}</h3>
                            <div class="goal-date" v-if="goal.target_date">
                                <Calendar :size="14" />
                                <span>{{ new Date(goal.target_date).toLocaleDateString() }}</span>
                            </div>
                        </div>
                        <div class="goal-actions">
                            <button @click="openEditModal(goal)" class="action-btn">
                                <Pencil :size="16" />
                            </button>
                            <button @click="confirmDelete(goal.id)" class="action-btn danger">
                                <Trash2 :size="16" />
                            </button>
                        </div>
                    </div>

                    <div class="goal-progress-section">
                        <div class="progress-stats">
                            <span class="amount-current">{{ formatAmount(goal.current_amount) }}</span>
                            <span class="amount-target">of {{ formatAmount(goal.target_amount) }}</span>
                        </div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill"
                                :style="{ width: goal.progress_percentage + '%', background: `linear-gradient(90deg, ${goal.color}, ${goal.color}dd)` }">
                            </div>
                        </div>
                        <div class="progress-percentage" :style="{ color: goal.color }">
                            {{ Math.round(goal.progress_percentage) }}% achieved
                            <span class="remaining" v-if="goal.remaining_amount > 0">
                                • {{ formatAmount(goal.remaining_amount) }} to go
                            </span>
                        </div>
                    </div>

                    <div class="goal-assets-section">
                        <div class="assets-header">
                            <h4>Linked Assets</h4>
                            <button @click="openAssetModal(goal.id)" class="add-asset-link"
                                :style="{ color: goal.color, backgroundColor: goal.color + '10' }">
                                <Plus :size="14" /> Add Asset
                            </button>
                        </div>
                        <div class="assets-list">
                            <!-- Linked Mutual Funds (Automatic) -->
                            <template v-if="goal.holdings && goal.holdings.length > 0">
                                <div v-for="(holding, index) in goal.holdings" :key="holding.id" class="asset-item"
                                    v-show="expandedGoals[goal.id] || (index as number) < 2">
                                    <div class="asset-info">
                                        <TrendingUp :size="16" class="text-blue-500" />
                                        <span class="truncate max-w-[200px]" :title="holding.scheme_name">
                                            <span class="text-xs text-gray-400 mr-1">Fund:</span>
                                            {{ holding.scheme_name || holding.id }}
                                        </span>
                                    </div>
                                    <div class="asset-right">
                                        <span class="asset-value">{{ formatAmount(holding.current_value) }}</span>
                                        <button @click="unlinkHolding(goal.id, holding.id)" class="remove-asset">
                                            <X :size="14" />
                                        </button>
                                    </div>
                                </div>
                            </template>

                            <!-- Individual Assets -->
                            <div v-for="(asset, index) in goal.assets" :key="asset.id" class="asset-item"
                                v-show="expandedGoals[goal.id] || (index + (goal.holdings ? goal.holdings?.length : 0)) < 2">
                                <div class="asset-info">
                                    <Building2 v-if="asset.type === 'BANK_ACCOUNT' || asset.type === 'bank_account'"
                                        :size="16" class="text-green-500" />
                                    <Coins v-else :size="16" class="text-orange-500" />
                                    <span class="truncate max-w-[150px]" :title="asset.display_name || asset.name">
                                        <span class="text-xs text-gray-400 mr-1">{{ (asset.type === 'BANK_ACCOUNT'
                                            ||
                                            asset.type === 'bank_account') ?
                                            'Bank:' : 'Asset:' }}</span>
                                        {{ asset.display_name || asset.name || asset.type || 'Unnamed Account' }}
                                    </span>
                                </div>
                                <div class="asset-right">
                                    <span class="asset-value">{{
                                        formatAmount(asset.current_value || asset.manual_amount || 0) }}</span>
                                    <button @click="removeAsset(asset.id)" class="remove-asset">
                                        <X :size="14" />
                                    </button>
                                </div>
                            </div>

                            <div v-if="goal.holdings_count === 0 && (!goal.assets || goal.assets.length === 0)"
                                class="no-assets">
                                No assets linked yet.
                            </div>

                            <!-- Expand/Collapse Button -->
                            <div v-if="(goal.holdings.length + goal.assets.length) > 2" class="expand-section">
                                <button @click="toggleExpand(goal.id)" class="btn-expand">
                                    <span v-if="!expandedGoals[goal.id]">
                                        Show {{ (goal.holdings.length + goal.assets.length) - 2 }} more
                                        <ChevronDown :size="14" />
                                    </span>
                                    <span v-else>
                                        Show less
                                        <ChevronUp :size="14" />
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Goal Create/Edit Modal -->
        <div v-if="showModal" class="modal-overlay-global">
            <div class="modal-global glass premium-modal animate-in">
                <div class="modal-header">
                    <h2 class="text-2xl font-bold text-slate-800">{{ isEditing ? 'Edit Goal' : 'New Goal' }}</h2>
                    <button @click="showModal = false" class="close-btn">
                        <X :size="20" />
                    </button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="handleGoalSubmit" class="premium-form">
                        <div class="form-row mb-6">
                            <div class="form-group" style="flex: 0 0 100px;">
                                <label class="field-label">Icon</label>
                                <div class="icon-input-wrapper">
                                    <input v-model="goalForm.icon" class="icon-input-clean" maxlength="2" />
                                </div>
                            </div>
                            <div class="form-group flex-1">
                                <label class="field-label">Goal Name</label>
                                <input v-model="goalForm.name" class="premium-input" placeholder="e.g. Dream House"
                                    required />
                            </div>
                        </div>

                        <div class="form-group mb-6">
                            <label class="field-label">Target Amount</label>
                            <input type="number" v-model.number="goalForm.target_amount" class="premium-input"
                                placeholder="Amount" required />
                        </div>

                        <div class="form-group mb-6">
                            <label class="field-label">Target Date (Optional)</label>
                            <input type="date" v-model="goalForm.target_date" class="premium-input" />
                        </div>

                        <div class="form-group mb-8">
                            <label class="field-label">Goal Color</label>
                            <div class="color-presets">
                                <button type="button"
                                    v-for="c in ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']"
                                    :key="c" :style="{ backgroundColor: c }" class="color-box"
                                    :class="{ active: goalForm.color === c }" @click="goalForm.color = c"></button>
                            </div>
                        </div>

                        <div class="modal-footer">
                            <button type="button" @click="showModal = false" class="btn btn-text">Cancel</button>
                            <button type="submit" class="btn-primary-large">Save Goal</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- Asset Linking Modal -->
        <div v-if="showAssetModal" class="modal-overlay-global" @click.self="showAssetModal = false">
            <div class="modal-global glass premium-modal animate-in compact-modal">
                <div class="modal-header">
                    <h2 class="text-xl font-bold text-slate-800">Add Asset</h2>
                    <button @click="showAssetModal = false" class="close-btn">
                        <X :size="20" />
                    </button>
                </div>
                <div class="modal-body">
                    <div class="asset-type-tabs mb-8">
                        <button @click="assetForm.type = 'MANUAL'"
                            :class="{ active: assetForm.type === 'MANUAL' }">Manual
                            Entry</button>
                        <button @click="assetForm.type = 'BANK_ACCOUNT'"
                            :class="{ active: assetForm.type === 'BANK_ACCOUNT' }">Linked Bank</button>
                        <button @click="assetForm.type = 'MUTUAL_FUND'"
                            :class="{ active: assetForm.type === 'MUTUAL_FUND' }">Mutual Fund</button>
                    </div>

                    <form @submit.prevent="handleAssetSubmit" class="premium-form">
                        <div v-if="assetForm.type === 'MANUAL'">
                            <div class="form-group mb-6">
                                <label class="field-label">Asset Name</label>
                                <input v-model="assetForm.name" class="premium-input" placeholder="e.g. EPF, RD"
                                    required />
                            </div>
                            <div class="form-group mb-6">
                                <label class="field-label">Current Amount</label>
                                <input type="number" v-model.number="assetForm.manual_amount" class="premium-input"
                                    required />
                            </div>
                            <div class="form-group mb-8">
                                <label class="field-label">Expected Interest Rate (%)</label>
                                <input type="number" step="0.1" v-model.number="assetForm.interest_rate"
                                    class="premium-input" />
                            </div>
                        </div>

                        <div v-else-if="assetForm.type === 'BANK_ACCOUNT'">
                            <div class="form-group mb-8">
                                <label class="field-label">Select Bank Account</label>
                                <CustomSelect v-model="assetForm.linked_account_id" :options="accountOptions"
                                    placeholder="Choose an account" />
                            </div>
                        </div>

                        <div v-else>
                            <div class="form-group mb-8">
                                <label class="field-label">Select Mutual Fund</label>
                                <CustomSelect v-model="assetForm.holding_id" :options="portfolioOptions"
                                    placeholder="Choose a fund" />
                            </div>
                        </div>

                        <div class="modal-footer">
                            <button type="button" @click="showAssetModal = false" class="btn btn-text">Cancel</button>
                            <button type="submit" class="btn-primary-large">Attach Asset</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- DELETE CONFIRMATION MODAL -->
        <div v-if="showDeleteModal" class="modal-overlay-global" @click.self="showDeleteModal = false">
            <div class="modal-global glass premium-modal animate-in compact-modal">
                <div class="modal-header">
                    <h2 class="text-xl font-bold text-slate-800">Delete Goal?</h2>
                    <button @click="showDeleteModal = false" class="close-btn">
                        <X :size="20" />
                    </button>
                </div>
                <div class="modal-body text-center">
                    <div class="w-20 h-20 bg-rose-50 rounded-3xl flex items-center justify-center mx-auto mb-6">
                        <Trash2 :size="32" class="text-rose-500" />
                    </div>
                    <p class="text-slate-600 mb-8 px-4">Are you sure you want to delete this goal? This action cannot be
                        undone.</p>

                    <div class="flex gap-4">
                        <button @click="showDeleteModal = false" class="btn btn-text flex-1">Keep it</button>
                        <button @click="deleteGoal"
                            class="flex-1 bg-rose-500 hover:bg-rose-600 text-white font-bold py-3 px-6 rounded-2xl transition-all shadow-lg shadow-rose-200">
                            Delete Goal
                        </button>
                    </div>
                </div>
            </div>
        </div>

    </MainLayout>
</template>

<style scoped>
.goals-container {
    padding-bottom: 5rem;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.transaction-count {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 600;
    background: #f1f5f9;
    padding: 0.375rem 0.75rem;
    border-radius: 2rem;
}

.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
    letter-spacing: -0.01em;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.btn-premium-primary {
    position: relative;
    background: #4f46e5;
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 1rem;
    font-weight: 700;
    font-size: 0.9375rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border: none;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn-premium-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.4);
}

.btn-glow {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.6s ease-in-out;
}

.btn-premium-primary:hover .btn-glow {
    left: 100%;
}

.goals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 2rem;
}

.goal-card.glass {
    background: white;
    padding: 1.5rem;
    border-radius: 1.5rem;
    border: 1px solid #f1f5f9;
    border-top-width: 5px;
    border-top-style: solid;
    border-top-color: transparent;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.goal-card.glass:hover {
    transform: translateY(-8px);
    box-shadow: 0 25px 30px -10px rgba(0, 0, 0, 0.08);
    border-color: #e2e8f0;
}

.goal-card-header {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.goal-icon-bg {
    width: 3rem;
    height: 3rem;
    border-radius: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.3s ease;
}

.goal-card.glass:hover .goal-icon-bg {
    transform: scale(1.1) rotate(-5deg);
}

.goal-emoji {
    font-size: 1.5rem;
}

.goal-title-area {
    flex: 1;
}

.goal-title-area h3 {
    font-size: 1.35rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
    letter-spacing: -0.01em;
}

.goal-date {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: #64748b;
    margin-top: 0.4rem;
    font-weight: 500;
}

.goal-actions {
    display: flex;
    gap: 0.625rem;
}

.action-btn {
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 0.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    background: #f8fafc;
    transition: all 0.2s;
    border: 1px solid #f1f5f9;
}

.action-btn:hover {
    background: #f1f5f9;
    color: #4f46e5;
    border-color: #e2e8f0;
    transform: scale(1.05);
}

.action-btn.danger:hover {
    background: #fef2f2;
    color: #ef4444;
    border-color: #fee2e2;
}

.goal-progress-section {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 1rem;
    border: 1px solid #f1f5f9;
}

.progress-stats {
    display: flex;
    align-items: baseline;
    gap: 0.625rem;
    margin-bottom: 1rem;
}

.amount-current {
    font-size: 1.5rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
}

.amount-target {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 500;
}

.progress-bar-container {
    height: 10px;
    background: #e2e8f0;
    border-radius: 100px;
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 100px;
    transition: width 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.progress-percentage {
    font-size: 0.8125rem;
    font-weight: 700;
    color: #475569;
}

.remaining {
    color: #94a3b8;
    font-weight: 500;
}

.goal-assets-section h4 {
    font-size: 0.9375rem;
    font-weight: 800;
    color: #334155;
    margin-bottom: 1rem;
}

.assets-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.add-asset-link {
    font-size: 0.8125rem;
    font-weight: 700;
    color: #4f46e5;
    display: flex;
    align-items: center;
    gap: 0.375rem;
    background: #f5f3ff;
    padding: 0.4rem 0.75rem;
    border-radius: 0.75rem;
    transition: all 0.2s;
}

.add-asset-link:hover {
    background: #4f46e5;
    color: white;
    transform: translateY(-1px);
}

.assets-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.asset-item {
    padding: 0.875rem 1rem;
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s;
}

.asset-item:hover {
    border-color: #e2e8f0;
    background: #fafafa;
}

.asset-info {
    display: flex;
    align-items: center;
    gap: 0.875rem;
    font-size: 0.875rem;
    color: #475569;
    font-weight: 600;
}

.asset-right {
    display: flex;
    align-items: center;
    gap: 0.875rem;
}

.asset-value {
    font-weight: 800;
    color: #1e293b;
}

.remove-asset {
    color: #cbd5e1;
    transition: all 0.2s;
    padding: 0.25rem;
    border-radius: 0.5rem;
}

.remove-asset:hover {
    color: #ef4444;
    background: #fef2f2;
}

.no-assets {
    text-align: center;
    padding: 1.5rem;
    font-size: 0.875rem;
    color: #94a3b8;
    border: 2px dashed #f1f5f9;
    border-radius: 1.25rem;
    font-weight: 500;
}

.expand-section {
    display: flex;
    justify-content: center;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px dashed #f1f5f9;
}

.btn-expand {
    background: none;
    border: none;
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    padding: 4px 8px;
    border-radius: 6px;
}

.btn-expand span {
    display: flex;
    align-items: center;
    gap: 4px;
}

.btn-expand:hover {
    color: #4f46e5;
    background: #f1f5f9;
}

.form-group-row {
    display: flex;
    gap: 1.25rem;
}

.icon-input-wrapper {
    background: #f8fafc;
    border: 2px solid #f1f5f9;
    border-radius: 1rem;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.icon-input-wrapper:focus-within {
    border-color: #4f46e5;
    background: white;
}

.icon-input-clean {
    background: transparent;
    border: none;
    text-align: center;
    width: 3.5rem;
    font-size: 1.75rem;
    outline: none;
}

.color-presets {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}

.color-box {
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 0.75rem;
    border: 3px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
    padding: 0;
}

.color-box.active {
    border-color: #0f172a;
    transform: scale(1.1);
}

.asset-type-tabs {
    display: flex;
    background: #f8fafc;
    padding: 0.375rem;
    border-radius: 1rem;
    gap: 0.375rem;
    border: 1px solid #f1f5f9;
}

.asset-type-tabs button {
    flex: 1;
    padding: 0.625rem;
    font-size: 0.875rem;
    font-weight: 700;
    border-radius: 0.75rem;
    transition: all 0.2s;
    color: #64748b;
    border: none;
}

.asset-type-tabs button.active {
    background: #ffffff;
    color: #4f46e5;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.empty-state {
    text-align: center;
    padding: 6rem 2rem;
    background: white;
    border-radius: 3rem;
    border: 1px solid #f1f5f9;
}

.empty-icon {
    font-size: 5rem;
    margin-bottom: 1.5rem;
    filter: drop-shadow(0 10px 15px rgba(0, 0, 0, 0.1));
}

.empty-state h3 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 0.75rem;
}

.loader {
    width: 48px;
    height: 48px;
    border: 4px solid #f1f5f9;
    border-top: 4px solid #4f46e5;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes animate-in {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-in {
    animation: animate-in 0.4s ease-out forwards;
}

/* Modal and Form Styles */
.modal-overlay-global {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-global {
    background: white;
    border-radius: 2rem;
    width: 100%;
    max-width: 550px;
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.2);
    /* Removed overflow: hidden to prevent dropdown clipping */
}

.modal-global.compact-modal {
    max-width: 480px;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2.5rem 1.5rem;
}

.close-btn {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
    transition: all 0.2s;
    background: #f8fafc;
}

.close-btn:hover {
    background: #f1f5f9;
    color: #475569;
}

.modal-body {
    padding: 0 2.5rem 2.5rem;
    overflow: visible;
    /* Ensure dropdowns pop out */
}

.field-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 700;
    color: #334155;
    margin-bottom: 0.75rem;
}

.premium-input {
    width: 100%;
    padding: 0.875rem 1.25rem;
    background: #f8fafc;
    border: 2px solid #f1f5f9;
    border-radius: 1rem;
    font-size: 1rem;
    font-weight: 500;
    color: #1e293b;
    transition: all 0.2s;
    outline: none;
}

.premium-input:focus {
    background: white;
    border-color: #4f46e5;
    box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

.form-row {
    display: flex;
    gap: 1.5rem;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1rem;
}

.btn-primary-large {
    background: #4f46e5;
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: white;
    padding: 0.875rem 1.75rem;
    border-radius: 1rem;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    cursor: pointer;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
    transition: all 0.3s;
}

.btn-primary-large:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.4);
}

.btn-text {
    padding: 0.875rem 1.5rem;
    border-radius: 1rem;
    font-weight: 700;
    color: #64748b;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-text:hover {
    background: #f1f5f9;
    color: #1e293b;
}

@media (max-width: 640px) {
    .modal-global {
        width: 95%;
        margin: 0 auto;
    }

    .modal-header,
    .modal-body {
        padding: 1.5rem;
    }
}
</style>
