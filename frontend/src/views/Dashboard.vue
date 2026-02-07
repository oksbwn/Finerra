<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import { useRouter } from 'vue-router'
import { useTransactionHelpers } from '@/composables/useTransactionHelpers'
import { useDashboardHelpers } from '@/composables/useDashboardHelpers'
import { useAuthStore } from '@/stores/auth'
import { useCurrency } from '@/composables/useCurrency'
import Sparkline from '@/components/Sparkline.vue'
import {
    ChevronDown, Users, Wallet, PieChart, CreditCard, Landmark, Sparkles, Activity, CalendarDays
} from 'lucide-vue-next'

const router = useRouter()
const auth = useAuthStore()
const { formatAmount } = useCurrency()

// --- State ---
const loading = ref(true)
const selectedMember = ref<string | null>(null)
const familyMembers = ref<any[]>([])
const accounts = ref<any[]>([])
const categories = ref<any[]>([])
const budgets = ref<any[]>([])
const expenseGroups = ref<any[]>([])

const mfPortfolio = ref({
    invested: 0,
    current: 0,
    pl: 0,
    plPercent: 0,
    xirr: 0,
    trend: [] as number[],
    allocation: { equity: 0, debt: 0, hybrid: 0, other: 0 } as any,
    topPerformer: null as any,
    loading: true
})

const netWorthTrend = ref<number[]>([])
const spendingTrend = ref<number[]>([])
const recurringTransactions = ref<any[]>([])

const metrics = ref({
    breakdown: {
        net_worth: 0,
        bank_balance: 0,
        cash_balance: 0,
        credit_debt: 0,
        investment_value: 0,
        total_credit_limit: 0,
        available_credit: 0,
        overall_credit_utilization: 0
    },
    monthly_spending: 0,
    total_excluded: 0,
    excluded_income: 0,
    top_spending_category: null as { name: string, amount: number } | null,
    budget_health: {
        limit: 0,
        spent: 0,
        percentage: 0
    },
    credit_intelligence: [] as any[],
    recent_transactions: [] as any[],
    currency: 'INR'
})

// --- Computed ---
const selectedMemberName = computed(() => {
    if (!selectedMember.value) return 'All Members'
    const member = familyMembers.value.find(m => m.id === selectedMember.value)
    return member ? (member.full_name || member.email) : 'All Members'
})

const budgetPulse = computed(() => {
    return budgets.value
        .filter(b => b.category !== 'OVERALL')
        .sort((a, b) => b.percentage - a.percentage)
        .slice(0, 3)
})

const netWorth = computed(() => {
    const liquid = (metrics.value.breakdown.bank_balance || 0) + (metrics.value.breakdown.cash_balance || 0)
    const totalInvestments = mfPortfolio.value.current || 0
    const totalDebt = metrics.value.breakdown.credit_debt || 0
    return liquid + totalInvestments - totalDebt
})

const sortedCredit = computed(() => {
    return [...metrics.value.credit_intelligence].sort((a, b) => {
        if (a.days_until_due === null) return 1
        if (b.days_until_due === null) return -1
        return a.days_until_due - b.days_until_due
    })
})

const creditSummary = computed(() => {
    const totalLimit = metrics.value.breakdown.total_credit_limit || 0
    const totalDebt = metrics.value.breakdown.credit_debt || 0
    const utilization = totalLimit > 0 ? (totalDebt / totalLimit) * 100 : 0
    return { totalLimit, totalDebt, utilization }
})

const upcomingBills = computed(() => {
    return recurringTransactions.value
        .filter(t => t.status === 'ACTIVE')
        .slice(0, 3)
})

// --- Helpers & Composables ---
const { formatDate, getCategoryDisplay } = useTransactionHelpers(accounts, categories, expenseGroups)
const { getGreeting, getBankBrand } = useDashboardHelpers()

function selectMember(id: string | null) {
    selectedMember.value = id
}

function getCategoryDetails(name: string) {
    const display = getCategoryDisplay(name)
    return { icon: display.icon, color: display.color }
}

const greetingEmoji = computed(() => {
    const g = getGreeting()
    if (g.includes('Morning')) return '🌅'
    if (g.includes('Afternoon')) return '☀️'
    return '🌙'
})

// --- Data Fetching ---
async function fetchAllData() {
    loading.value = true
    mfPortfolio.value.loading = true
    const userId = selectedMember.value || undefined

    setTimeout(() => { loading.value = false }, 300)

    // 1. Metrics
    financeApi.getMetrics(undefined, undefined, undefined, userId)
        .then(res => { metrics.value = res.data })
        .catch(e => console.warn("Metrics fetch failed", e))

    // 2. Portfolio
    financeApi.getPortfolio(userId)
        .then(pfRes => {
            if (pfRes && pfRes.data && Array.isArray(pfRes.data)) {
                let invested = 0, current = 0
                pfRes.data.forEach((h: any) => {
                    invested += Number(h.invested_value || h.investedValue || h.invested_amount || 0)
                    current += Number(h.current_value || h.currentValue || h.value || 0)
                })
                mfPortfolio.value.invested = invested
                mfPortfolio.value.current = current
                mfPortfolio.value.pl = current - invested
                mfPortfolio.value.plPercent = invested > 0 ? ((current - invested) / invested) * 100 : 0
            }
        })
        .catch(e => console.warn("Portfolio fetch failed", e))

    // 3. Analytics
    financeApi.getAnalytics(userId)
        .then(anRes => {
            if (anRes && anRes.data) {
                mfPortfolio.value.xirr = Number(anRes.data.xirr || 0)
                mfPortfolio.value.allocation = anRes.data.asset_allocation || { equity: 0, debt: 0, hybrid: 0, other: 0 }
                if (anRes.data.top_gainers?.length > 0) {
                    const top = anRes.data.top_gainers[0]
                    mfPortfolio.value.topPerformer = {
                        schemeName: top.scheme_name || top.scheme,
                        plPercent: Number(top.pl_percent || top.returns || 0)
                    }
                }
                mfPortfolio.value.loading = false
            }
        })
        .catch(e => {
            console.warn("Analytics fetch failed", e)
            mfPortfolio.value.loading = false
        })

    // 4. Timeline
    financeApi.getPerformanceTimeline('1m', '1d', userId)
        .then(res => {
            const timeline = Array.isArray(res.data) ? res.data : (res.data.timeline || [])
            mfPortfolio.value.trend = timeline.map((p: any) => Number(p.value || 0))
        })
        .catch(e => console.warn("Timeline fetch failed", e))

    // 5. Recurring
    financeApi.getRecurringTransactions()
        .then(res => { recurringTransactions.value = res.data })
        .catch(e => console.warn("Recurring fetch failed", e))

    // 6. Net Worth Trend
    financeApi.getNetWorthTimeline(30, userId)
        .then(res => { netWorthTrend.value = res.data.map((p: any) => Number(p.total || 0)) })
        .catch(e => console.warn("Net worth trend failed", e))

    // 7. Spending Trend
    financeApi.getSpendingTrend(userId)
        .then(res => { spendingTrend.value = res.data.map((p: any) => Number(p.amount || 0)) })
        .catch(e => console.warn("Spending trend failed", e))
}

async function fetchMetadata() {
    try {
        const [usersRes, catRes, budgetRes, accRes, expRes] = await Promise.all([
            financeApi.getUsers(),
            financeApi.getCategories(),
            financeApi.getBudgets(),
            financeApi.getAccounts(),
            financeApi.getExpenseGroups()
        ])
        familyMembers.value = usersRes.data
        categories.value = catRes.data
        budgets.value = budgetRes.data
        accounts.value = accRes.data
        expenseGroups.value = expRes.data
    } catch (e) {
        console.error("Failed to fetch dashboard metadata", e)
    }
}

onMounted(async () => {
    await fetchMetadata()
    await fetchAllData()
})

watch(selectedMember, () => fetchAllData())
</script>

<template>
    <MainLayout>
        <v-container fluid class="dashboard-page pa-6 pa-md-10">
            <!-- Header -->
            <div
                class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center mb-10 gap-6 reveal-anim">
                <div>
                    <h1 class="text-h4 font-weight-black mb-1 d-flex align-center">
                        <span class="mr-3">{{ greetingEmoji }}</span>
                        {{ getGreeting() }}, {{ (auth.user?.full_name || auth.user?.email || 'User').split(' ')[0] }}
                    </h1>
                    <p class="text-subtitle-1 text-slate-500 font-weight-bold">
                        Your family's financial state at a glance.
                    </p>
                </div>

                <div class="d-flex align-center gap-4">
                    <v-menu offset="12" transition="scale-transition" v-if="auth.user?.role !== 'CHILD'">
                        <template v-slot:activator="{ props }">
                            <v-btn v-bind="props" variant="flat" class="member-selector-btn pa-2 pr-4" height="48"
                                rounded="pill">
                                <div class="d-flex align-center">
                                    <template v-if="selectedMember">
                                        <v-avatar size="32" class="bg-primary-light mr-3 premium-avatar-ring">
                                            <span class="text-caption font-weight-black">{{
                                                selectedMemberName.charAt(0).toUpperCase() }}</span>
                                        </v-avatar>
                                    </template>
                                    <template v-else>
                                        <div class="bg-indigo-lighten-5 rounded-circle pa-2 mr-3">
                                            <Users :size="18" class="text-primary" />
                                        </div>
                                    </template>
                                    <span class="font-weight-bold">{{ selectedMemberName }}</span>
                                    <ChevronDown :size="16" class="ml-2 opacity-50" />
                                </div>
                            </v-btn>
                        </template>
                        <v-card width="260" class="premium-glass-card pa-2 mt-2" rounded="xl" elevation="10" border>
                            <v-list density="compact" nav bg-color="transparent">
                                <v-list-item @click="selectMember(null)" :active="selectedMember === null" rounded="xl"
                                    color="primary">
                                    <template v-slot:prepend>
                                        <Users :size="18" class="mr-3" />
                                    </template>
                                    <v-list-item-title class="font-weight-bold">All Members</v-list-item-title>
                                </v-list-item>
                                <v-divider class="my-2 opacity-10"></v-divider>
                                <v-list-item v-for="user in familyMembers" :key="user.id" @click="selectMember(user.id)"
                                    :active="selectedMember === user.id" rounded="xl" color="primary">
                                    <template v-slot:prepend>
                                        <v-avatar size="28" class="bg-primary-light mr-3 premium-avatar-ring">
                                            <span class="text-caption font-weight-black">{{ (user.full_name ||
                                                user.email).charAt(0).toUpperCase() }}</span>
                                        </v-avatar>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">{{ user.full_name ||
                                        user.email.split('@')[0]
                                    }}</v-list-item-title>
                                </v-list-item>
                            </v-list>
                        </v-card>
                    </v-menu>

                </div>
            </div>

            <!-- Loading State -->
            <v-row v-if="loading">
                <v-col v-for="i in 4" :key="`skel-${i}`" cols="12" sm="6" lg="3">
                    <v-skeleton-loader type="card" class="premium-glass-card" height="170"></v-skeleton-loader>
                </v-col>
                <v-col cols="12" md="6" v-for="i in 2" :key="`skel-list-${i}`">
                    <v-skeleton-loader type="article" class="premium-glass-card" height="400"></v-skeleton-loader>
                </v-col>
            </v-row>

            <v-row v-else class="reveal-anim">
                <!-- ROW 1: Standardized Metric Cards -->
                <v-col cols="12" sm="6" lg="3">
                    <v-card class="premium-glass-card metric-card-v2" @click="router.push('/')">
                        <div class="d-flex justify-space-between align-start">
                            <div class="metric-icon-box bg-indigo-soft">
                                <Landmark :size="24" />
                            </div>
                            <Sparkline v-if="netWorthTrend.length > 1" :data="netWorthTrend" color="#6366f1"
                                :height="32" width="70" />
                        </div>
                        <div>
                            <div class="text-caption text-slate-500 font-weight-bold text-uppercase mb-1"
                                style="letter-spacing: 1px;">Total Net Worth</div>
                            <div class="metric-value text-indigo-darken-2 text-h5 font-weight-black">{{
                                formatAmount(netWorth) }}
                            </div>
                        </div>
                    </v-card>
                </v-col>

                <v-col cols="12" sm="6" lg="3">
                    <v-card class="premium-glass-card metric-card-v2" @click="router.push('/transactions')">
                        <div class="d-flex justify-space-between align-start">
                            <div class="metric-icon-box bg-rose-soft">
                                <Wallet :size="24" />
                            </div>
                            <Sparkline v-if="spendingTrend.length > 1" :data="spendingTrend" color="#e11d48"
                                :height="32" width="70" />
                        </div>
                        <div>
                            <div class="text-caption text-slate-500 font-weight-bold text-uppercase mb-1"
                                style="letter-spacing: 1px;">Monthly Spending</div>
                            <div class="metric-value text-error text-h5 font-weight-black">{{
                                formatAmount(metrics.monthly_spending,
                                    metrics.currency) }}
                            </div>
                        </div>
                    </v-card>
                </v-col>

                <v-col cols="12" sm="6" lg="3">
                    <v-card class="premium-glass-card metric-card-v2" @click="router.push('/budgets')">
                        <div class="d-flex justify-space-between align-start">
                            <div class="metric-icon-box bg-amber-soft">
                                <PieChart :size="24" />
                            </div>
                            <div class="text-h6 font-weight-black"
                                :class="metrics.budget_health.percentage > 90 ? 'text-error' : 'text-amber-darken-2'">
                                {{ metrics.budget_health.percentage.toFixed(0) }}%
                            </div>
                        </div>
                        <div>
                            <div class="text-caption text-slate-500 font-weight-bold text-uppercase mb-1"
                                style="letter-spacing: 1px;">Budget Health</div>
                            <v-progress-linear :model-value="Math.min(metrics.budget_health.percentage, 100)" height="8"
                                rounded="pill" color="amber" class="mt-2"></v-progress-linear>
                        </div>
                    </v-card>
                </v-col>

                <v-col cols="12" sm="6" lg="3">
                    <v-card class="premium-glass-card metric-card-v2" @click="router.push('/mutual-funds')">
                        <div class="d-flex justify-space-between align-start">
                            <div class="metric-icon-box bg-emerald-soft">
                                <Sparkles :size="24" />
                            </div>
                            <div v-if="!mfPortfolio.loading && mfPortfolio.invested > 0">
                                <v-chip size="small" color="success" variant="flat" class="font-weight-black">
                                    <Sparkles :size="12" class="mr-1" /> {{ mfPortfolio.xirr.toFixed(1) }}% XIRR
                                </v-chip>
                            </div>
                        </div>
                        <div>
                            <div class="text-caption text-slate-500 font-weight-bold text-uppercase mb-1"
                                style="letter-spacing: 1px;">Investments</div>
                            <div class="metric-value text-success text-h5 font-weight-black">{{
                                formatAmount(mfPortfolio.current) }}
                            </div>
                        </div>
                    </v-card>
                </v-col>

                <!-- ROW 2: Budget Pulse -->
                <v-col cols="12" v-if="budgetPulse.length > 0">
                    <div class="d-flex justify-space-between align-center mb-6">
                        <h2 class="premium-section-title">
                            <PieChart :size="22" stroke-width="3" /> Budget Pulse
                        </h2>
                        <v-btn variant="text" size="small" color="primary" @click="router.push('/budgets')"
                            class="font-weight-black">Manage</v-btn>
                    </div>

                    <v-row>
                        <v-col v-for="b in budgetPulse" :key="b.id" cols="12" sm="6" md="4" lg="3">
                            <v-card class="premium-glass-card pa-5" @click="router.push('/budgets')">
                                <div class="d-flex justify-space-between align-center mb-3">
                                    <span
                                        class="text-subtitle-2 font-weight-black text-slate-600 d-flex align-center gap-2">
                                        {{ getCategoryDetails(b.category).icon }} {{ b.category }}
                                        <v-chip size="x-small"
                                            :color="b.percentage > 100 ? 'error' : (b.percentage > 85 ? 'warning' : 'success')"
                                            variant="tonal" class="font-weight-bold">
                                            {{ b.percentage > 100 ? 'Crit' : (b.percentage > 85 ? 'Warn' : 'Good') }}
                                        </v-chip>
                                    </span>
                                    <span class="text-caption font-weight-black"
                                        :class="b.percentage > 100 ? 'text-error' : 'text-primary'">
                                        {{ b.percentage.toFixed(0) }}%
                                    </span>
                                </div>
                                <v-progress-linear :model-value="Math.min(b.percentage, 100)" height="4" rounded="pill"
                                    :color="b.percentage > 100 ? 'error' : (b.percentage > 85 ? 'warning' : 'primary')"
                                    class="mb-3"></v-progress-linear>
                                <div class="text-caption text-slate-400 d-flex justify-space-between font-weight-bold">
                                    <span>{{ formatAmount(b.spent, metrics.currency) }}</span>
                                    <span>of {{ formatAmount(b.amount_limit, metrics.currency) }}</span>
                                </div>
                            </v-card>
                        </v-col>
                    </v-row>
                </v-col>

                <!-- ROW 3: Side-by-Side Activity and Bills -->
                <v-col cols="12" lg="7">
                    <v-card class="premium-glass-card pa-8 h-100">
                        <div class="d-flex justify-space-between align-center mb-8">
                            <h2 class="premium-section-title">
                                <Activity :size="22" stroke-width="3" /> Recent Activity
                            </h2>
                            <v-btn variant="tonal" rounded="xl" size="small" color="primary"
                                @click="router.push('/transactions')" class="font-weight-black px-6">View All</v-btn>
                        </div>
                        <v-list bg-color="transparent" class="pa-0">
                            <v-list-item v-for="txn in metrics.recent_transactions.slice(0, 5)" :key="txn.id"
                                class="premium-list-item px-4 py-3 interactive-list-item">
                                <template v-slot:prepend>
                                    <v-avatar size="48" :color="getCategoryDetails(txn.category).color + '15'"
                                        class="mr-4 premium-avatar-ring">
                                        <span class="text-h6">{{ getCategoryDetails(txn.category).icon }}</span>
                                    </v-avatar>
                                </template>
                                <v-list-item-title class="font-weight-bold text-subtitle-1">{{ txn.description ||
                                    'Transaction'
                                }}</v-list-item-title>
                                <v-list-item-subtitle class="text-caption font-weight-bold text-slate-400 mt-1">
                                    {{ formatDate(txn.date).day }} • {{ txn.account_owner_name || 'Personal' }}
                                </v-list-item-subtitle>
                                <template v-slot:append>
                                    <div class="text-subtitle-1 font-weight-black"
                                        :class="txn.amount > 0 ? 'text-success' : 'text-slate-700'">
                                        {{ txn.amount > 0 ? '+' : '' }}{{ formatAmount(Math.abs(txn.amount),
                                            metrics.currency) }}
                                    </div>
                                </template>
                            </v-list-item>
                        </v-list>
                    </v-card>
                </v-col>

                <v-col cols="12" lg="5">
                    <v-card class="premium-glass-card pa-8 h-100">
                        <div class="d-flex justify-space-between align-center mb-8">
                            <h2 class="premium-section-title">
                                <CalendarDays :size="22" stroke-width="3" /> Upcoming Bills
                            </h2>
                        </div>
                        <div v-if="upcomingBills.length > 0">
                            <v-list bg-color="transparent" class="pa-0">
                                <v-list-item v-for="bill in upcomingBills" :key="bill.id"
                                    class="premium-list-item px-4 py-3 interactive-list-item">
                                    <template v-slot:prepend>
                                        <div class="metric-icon-box bg-slate-50 mr-4">
                                            {{ getCategoryDetails(bill.category).icon }}
                                        </div>
                                    </template>
                                    <v-list-item-title class="font-weight-bold">{{ bill.description
                                    }}</v-list-item-title>
                                    <v-list-item-subtitle class="text-caption font-weight-bold text-rose-500">Due {{
                                        formatDate(bill.next_date).day }}</v-list-item-subtitle>
                                    <template v-slot:append>
                                        <div class="text-subtitle-1 font-weight-black">{{ formatAmount(bill.amount) }}
                                        </div>
                                    </template>
                                </v-list-item>
                            </v-list>
                        </div>
                        <div v-else class="text-center py-10">
                            <div class="text-h2 mb-4 opacity-10">📅</div>
                            <p class="text-slate-400 font-weight-bold">Relax, no bills due soon.</p>
                        </div>
                    </v-card>
                </v-col>

                <!-- ROW 4: Credit Intelligence -->
                <v-col cols="12">
                    <v-card class="premium-glass-card pa-8 overflow-visible">
                        <div
                            class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center mb-8 gap-4">
                            <h2 class="premium-section-title">
                                <CreditCard :size="22" stroke-width="3" /> Credit Intelligence
                            </h2>

                            <div class="credit-outlook-container reveal-anim"
                                v-if="metrics.credit_intelligence.length > 0">
                                <div class="d-flex justify-space-between mb-2">
                                    <span class="text-caption font-weight-black text-slate-500">TOTAL CREDIT
                                        OUTLOOK</span>
                                    <span class="text-caption font-weight-black text-primary">{{
                                        formatAmount(creditSummary.totalDebt) }} utilized of {{
                                            formatAmount(creditSummary.totalLimit) }}</span>
                                </div>
                                <div class="credit-outlook-bar">
                                    <div class="outlook-fill bg-primary"
                                        :style="{ width: Math.min(creditSummary.utilization, 100) + '%' }"></div>
                                    <div class="outlook-marker" style="left: 30%" title="Ideal Utilization (30%)"></div>
                                </div>
                            </div>
                        </div>

                        <div v-if="sortedCredit.length > 0" class="px-2">
                            <div v-for="(card, index) in sortedCredit" :key="card.id">
                                <div class="credit-info-bar-v3 reveal-anim"
                                    :style="{ borderColor: getBankBrand(card.name).color + '40' }">
                                    <!-- Brand & Name (Digital Wallet Style) -->
                                    <div class="credit-brand-col">
                                        <div class="mini-credit-card flex-shrink-0"
                                            :style="{ background: getBankBrand(card.name).gradient }">
                                            <div class="card-chip"></div>
                                            <component :is="getBankBrand(card.name).icon" :size="20"
                                                class="card-icon-overlay" :color="getBankBrand(card.name).logoColor" />
                                            <div class="card-logo"
                                                :style="{ color: getBankBrand(card.name).logoColor }">{{
                                                    getBankBrand(card.name).logo }}</div>
                                            <div class="card-number"
                                                :style="{ color: getBankBrand(card.name).textColor }">•••• {{
                                                    card.last_digits || '0000' }}</div>
                                        </div>
                                        <div class="ml-5 overflow-hidden">
                                            <div class="text-subtitle-1 font-weight-black text-truncate">{{ card.name }}
                                            </div>
                                            <div class="text-caption font-weight-bold text-slate-400">....{{
                                                card.last_digits || '0000' }}
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Utilization & Health -->
                                    <div class="credit-progress-col">
                                        <div class="d-flex justify-space-between mb-1">
                                            <div class="d-flex align-center">
                                                <span
                                                    class="text-caption font-weight-black text-slate-500 uppercase mr-2">Utilization</span>
                                                <v-chip size="x-small"
                                                    :color="card.utilization > 30 ? (card.utilization > 70 ? 'error' : 'warning') : 'success'"
                                                    variant="flat" class="font-weight-black">
                                                    {{ card.utilization > 30 ? (card.utilization > 70 ? 'Critical' :
                                                        'Caution') :
                                                        'Healthy' }}
                                                </v-chip>
                                            </div>
                                            <span class="text-caption font-weight-black"
                                                :class="card.utilization > 70 ? 'text-error' : 'text-primary'">{{
                                                    card.utilization.toFixed(0) }}%</span>
                                        </div>
                                        <div class="v3-progress-container">
                                            <v-progress-linear :model-value="Math.min(card.utilization, 100)"
                                                height="12" rounded="pill"
                                                :color="card.utilization > 70 ? 'error' : 'primary'"></v-progress-linear>
                                            <div class="v3-safe-zone" title="30% Threshold"></div>
                                        </div>
                                    </div>

                                    <!-- Financial Snapshot -->
                                    <div class="credit-data-col">
                                        <div class="d-flex gap-8">
                                            <div class="text-right">
                                                <div class="text-caption text-slate-400 font-weight-black">BALANCE</div>
                                                <div class="text-subtitle-1 font-weight-black">{{
                                                    formatAmount(card.balance)
                                                    }}</div>
                                            </div>
                                            <div class="text-right">
                                                <div class="text-caption text-slate-400 font-weight-black">AVAILABLE
                                                </div>
                                                <div class="text-subtitle-1 font-weight-black text-primary">{{
                                                    formatAmount((card.limit
                                                        || 0) - (card.balance || 0)) }}</div>
                                            </div>
                                        </div>
                                        <div class="text-caption text-right font-weight-black mt-1"
                                            :class="card.days_until_due < 7 && card.days_until_due !== null ? 'text-error animate-pulse' : 'text-slate-500'">
                                            <span v-if="card.days_until_due !== null">Due in {{ card.days_until_due }}
                                                days</span>
                                            <span v-else>No Cycle Data</span>
                                        </div>
                                    </div>
                                </div>
                                <!-- Visible Separator -->
                                <v-divider v-if="index < sortedCredit.length - 1" class="my-4 opacity-20"
                                    color="black"></v-divider>
                            </div>
                        </div>
                        <div v-else class="text-center py-12">
                            <p class="text-slate-400 font-weight-bold italic">No credit lines detected in your accounts.
                            </p>
                        </div>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </MainLayout>
</template>

<style scoped>
/* Mesh Gradient Animation */
@keyframes meshGradient {
    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

.dashboard-page {
    background: linear-gradient(-45deg, #f8fafc, #f1f5f9, #eff6ff, #fdf4ff);
    background-size: 400% 400%;
    animation: meshGradient 15s ease infinite;
    min-height: 100vh;
    position: relative;
}

/* Design Tokens & Premium Components */
.v-card.premium-glass-card {
    background: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.6) !important;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05) !important;
    border-radius: 24px !important;
    transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
    overflow: hidden;
}

.v-card.premium-glass-card:hover {
    transform: translateY(-6px);
    background: rgba(255, 255, 255, 0.85) !important;
    box-shadow: 0 12px 40px rgba(31, 38, 135, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.8) !important;
}

/* Metric Specific Styles */
.metric-card-v2 {
    height: 170px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.5rem !important;
}

.metric-icon-box {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.metric-value {
    font-size: 1.85rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

/* Section Headers */
.premium-section-title {
    font-size: 1.35rem;
    font-weight: 900;
    letter-spacing: -0.01em;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.header-right-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.header-left {
    display: flex;
    flex-direction: column;
}

.greeting-pre {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    font-weight: 500;
    margin-bottom: 0.25rem;
}

.user-name {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--color-text-main);
    margin: 0;
    line-height: 1.1;
}

.date-badge {
    background: white;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-muted);
    border: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
}

.member-selector-container {
    position: relative;
}

.member-selector-trigger {
    display: flex;
    align-items: center;
    background: white;
    border: 1px solid var(--color-border);
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-main);
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow-sm);
}

.member-selector-trigger:hover {
    border-color: var(--color-primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.premium-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 0.75rem;
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(10px);
    border: 1px solid var(--color-border);
    border-radius: 1rem;
    box-shadow: var(--shadow-lg);
    width: 240px;
    padding: 0.5rem;
    z-index: 200;
}

.dropdown-item {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem;
    color: var(--color-text-main);
}

.dropdown-item:hover {
    background: var(--color-background);
    color: var(--color-primary);
}

.dropdown-item.active {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: 600;
}

.dropdown-divider {
    height: 1px;
    background: var(--color-border);
    margin: 0.5rem;
}

.avatar-mini {
    width: 24px;
    height: 24px;
    background: var(--color-primary-light);
    color: var(--color-primary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    margin-right: 0.75rem;
    text-transform: uppercase;
}

.member-info {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.member-info .name {
    font-weight: 600;
    font-size: 0.85rem;
}

.member-info .role {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    text-transform: capitalize;
}

/* Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}


/* Skeleton Loading */
.skeleton-grid {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.skeleton-card {
    background: white;
    border-radius: 1.25rem;
    padding: 1.5rem;
    border: 1px solid var(--color-border);
    overflow: hidden;
    position: relative;
}

.skeleton-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.6) 50%,
            transparent 100%);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% {
        left: -100%;
    }

    100% {
        left: 100%;
    }
}

.skeleton-card-wide {
    grid-column: span 2;
}

.skeleton-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.skeleton-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--color-background);
}

.skeleton-text {
    background: var(--color-background);
    border-radius: 0.5rem;
    height: 12px;
    margin-bottom: 0.75rem;
}

.skeleton-text-xs {
    width: 40%;
    height: 10px;
}

.skeleton-text-sm {
    width: 60%;
    height: 12px;
}

.skeleton-text-md {
    width: 50%;
    height: 16px;
    margin-bottom: 1.5rem;
}

.skeleton-text-lg {
    width: 70%;
    height: 24px;
    margin-bottom: 0.5rem;
}

.skeleton-chart {
    width: 100%;
    height: 180px;
    background: var(--color-background);
    border-radius: 0.75rem;
    position: relative;
    overflow: hidden;
}

.skeleton-bar {
    width: 100%;
    height: 8px;
    background: var(--color-background);
    border-radius: 1rem;
    margin: 0.75rem 0;
}

/* Old loader (kept for compatibility) */
.loading-state {
    padding: 4rem;
    text-align: center;
    color: var(--color-text-muted);
}

.spinner {
    width: 30px;
    height: 30px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #4f46e5;
    border-radius: 50%;
    margin: 0 auto 1rem;
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

/* Grid Layout */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
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

/* Sync Monitor */
.sync-monitor-banner {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
    padding: 0.5rem;
    background: #f8fafc;
    border: 1px dashed #e2e8f0;
    border-radius: 12px;
}

.sync-pill {
    font-size: 0.7rem;
    font-weight: 700;
    color: #64748b;
    padding: 0.25rem 0.6rem;
    background: white;
    border-radius: 20px;
    border: 1px solid #f1f5f9;
}

/* Metric Cards */
.metric-card {
    background: white;
    border-radius: 1.25rem;
    padding: 1.25rem;
    border: 1px solid var(--color-border);
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
    cursor: default;
}

/* Hover Glows */
.h-glow-primary:hover {
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.15);
    border-color: #a5b4fc;
}

.h-glow-danger:hover {
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.15);
    border-color: #fca5a5;
}

.h-glow-warning:hover {
    box-shadow: 0 8px 20px rgba(245, 158, 11, 0.15);
    border-color: #fcd34d;
    cursor: pointer;
}

.h-glow-blue:hover {
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
    border-color: #93c5fd;
    cursor: pointer;
}

.h-glow-green:hover {
    box-shadow: 0 8px 20px rgba(16, 185, 129, 0.15);
    border-color: #6ee7b7;
    cursor: pointer;
}

.card-icon-bg {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin-bottom: 0.75rem;
}

.purple {
    background: #eef2ff;
    color: #4f46e5;
}

.red {
    background: #fef2f2;
    color: #ef4444;
}

.orange {
    background: #fffbeb;
    color: #f59e0b;
}

.blue {
    background: #eff6ff;
    color: #3b82f6;
}

.green {
    background: #ecfdf5;
    color: #10b981;
}

.indigo {
    background: #e0e7ff;
    color: #6366f1;
}

.card-data {
    display: flex;
    flex-direction: column;
}

.label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.value {
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--color-text-main);
    letter-spacing: -0.025em;
}

/* Complex Cards */
.card-top-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
}

.card-top-row .card-icon-bg {
    margin-bottom: 0;
}

.mini-percent {
    font-size: 0.8rem;
    font-weight: 700;
    color: #374151;
    background: #f3f4f6;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
}

.mini-percent.danger {
    color: #dc2626;
    background: #fef2f2;
}

.mini-percent.success {
    color: #059669;
    background: #ecfdf5;
}

.progress-bar-xs {
    height: 6px;
    background: #f3f4f6;
    border-radius: 3px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.progress-bar-xs .fill {
    height: 100%;
    background: #f59e0b;
    border-radius: 3px;
}

.progress-bar-xs .fill.blue {
    background: #3b82f6;
}

.sub-text {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    font-weight: 500;
}

/* Investment Specifics */
.card-sparkline {
    margin-top: 0.75rem;
    margin-bottom: 0.5rem;
    height: 24px;
}

.tp-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px dashed #e2e8f0;
    margin-top: 0.5rem;
}

.tp-label {
    font-size: 0.65rem;
    color: var(--color-text-muted);
    font-weight: 600;
    max-width: 70%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tp-val {
    font-size: 0.7rem;
    font-weight: 800;
}

.tp-val.success {
    color: #10b981;
}

.empty-state-diag {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    font-style: italic;
    padding: 0.5rem;
    background: #f8fafc;
    border-radius: 6px;
    text-align: center;
}

/* Asset Allocation Bar */
.mini-allocation-bar {
    display: flex;
    height: 6px;
    border-radius: 3px;
    background: #f1f5f9;
    overflow: hidden;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.allocation-segment {
    height: 100%;
}

.allocation-segment.equity {
    background: #6366f1;
}

.allocation-segment.debt {
    background: #10b981;
}

.allocation-segment.hybrid {
    background: #f59e0b;
}

/* Upcoming Bills */
.upcoming-bills-section {
    margin-top: 1.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid #f1f5f9;
}

.sub-section-header h4 {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

.upcoming-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.bill-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    border-radius: 8px;
    background: rgba(248, 250, 252, 0.5);
    transition: background 0.2s;
}

.bill-row:hover {
    background: #f1f5f9;
}

.bill-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.bill-icon {
    font-size: 1.25rem;
    padding: 0.4rem;
    background: white;
    border-radius: 6px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.bill-info {
    display: flex;
    flex-direction: column;
}

.bill-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-dark);
}

.bill-date {
    font-size: 0.7rem;
    color: var(--color-text-muted);
}

.bill-amount {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-text-dark);
}

/* Sections */
.dashboard-section {
    background: white;
    border-radius: 1.25rem;
    border: 1px solid var(--color-border);
    padding: 1.5rem;
}

.snapshot-section {
    grid-column: span 2;
}

.activity-section {
    grid-column: span 2;
}

.pulse-section {
    grid-column: span 4;
}

.credit-intel-section {
    grid-column: span 4;
}

.header-with-badge {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.pulse-status-badge {
    padding: 0.25rem 0.5rem;
    background: #e0e7ff;
    color: #4338ca;
    font-size: 0.65rem;
    font-weight: 800;
    border-radius: 4px;
    text-transform: uppercase;
}

.glass-panel {
    background: rgba(255, 255, 255, 0.8);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
}

.section-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-text-main);
}

.btn-text {
    background: none;
    border: none;
    font-size: 0.8rem;
    font-weight: 600;
    color: #4f46e5;
    cursor: pointer;
}

.btn-text:hover {
    text-decoration: underline;
}

/* Snapshot Grid */
.snapshot-grid {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.snapshot-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem;
    border-radius: 0.75rem;
    background: #f9fafb;
    transition: all 0.2s;
}

.snapshot-item:hover {
    background: #f3f4f6;
}

.snap-icon {
    font-size: 1.25rem;
}

.snap-info {
    display: flex;
    flex-direction: column;
}

.snap-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-text-muted);
}

.snap-val {
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-text-main);
}

.snap-util {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.125rem 0.375rem;
    border-radius: 4px;
    display: inline-block;
    margin-top: 0.25rem;
    width: fit-content;
}

.util-low {
    background: #dcfce7;
    color: #166534;
}

.util-medium {
    background: #ffedd5;
    color: #9a3412;
}

.util-high {
    background: #fee2e2;
    color: #991b1b;
}

/* Recent Activity */
.recent-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.recent-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f3f4f6;
}

.recent-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.recent-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.cat-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.recent-meta {
    display: flex;
    flex-direction: column;
}

.recent-desc {
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--color-text-main);
}

.recent-date-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.recent-date {
    font-size: 0.7rem;
    color: var(--color-text-muted);
}

.owner-badge {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--color-primary);
    background: var(--color-primary-light);
    padding: 0.125rem 0.5rem;
    border-radius: 1rem;
    text-transform: capitalize;
}

.recent-amount {
    font-weight: 700;
    font-size: 0.9rem;
    color: var(--color-text-main);
}

.recent-amount.credit {
    color: #10b981;
}

.empty-state-sm {
    text-align: center;
    color: var(--color-text-muted);
    font-size: 0.85rem;
    padding: 2rem 0;
}

/* Pulse Grid */
.pulse-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.pulse-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.875rem;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}

.pulse-card:hover {
    border-color: #cbd5e1;
    transform: scale(1.02);
}

.pulse-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.pulse-cat {
    font-size: 0.8125rem;
    font-weight: 700;
    color: #374151;
}

.pulse-percent {
    font-size: 0.8125rem;
    font-weight: 800;
    color: #6366f1;
}

.pulse-percent.danger {
    color: #ef4444;
}

.pulse-bar-bg {
    height: 4px;
    background: #e5e7eb;
    border-radius: 2px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.pulse-bar-fill {
    height: 100%;
    transition: width 1s ease-out;
}

.pulse-footer {
    font-size: 0.7rem;
    color: #64748b;
    font-weight: 500;
}

.pulse-critical {
    animation: criticalPulse 2s infinite;
    border-color: #fecaca !important;
}

@keyframes criticalPulse {
    0% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
}

/* Credit Intelligence List */
.credit-list {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.card-intel-item {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 0.875rem;
    padding: 1rem;
}

.card-intel-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.card-intel-name {
    font-weight: 700;
    font-size: 0.9rem;
    color: #1e293b;
}

.card-intel-status {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.125rem 0.5rem;
    border-radius: 1rem;
    background: #f1f5f9;
    color: #475569;
}

.card-intel-status.warning {
    background: #fff7ed;
    color: #ea580c;
}

.card-intel-status.danger {
    background: #fef2f2;
    color: #dc2626;
}

.card-intel-util {
    margin-bottom: 0.75rem;
}

.util-bar-bg {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    margin-bottom: 0.25rem;
    overflow: hidden;
}

.util-bar-fill {
    height: 100%;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.util-text {
    font-size: 0.65rem;
    font-weight: 600;
    color: #64748b;
}

.card-intel-footer {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
    border-top: 1px dashed #e2e8f0;
    padding-top: 0.75rem;
    margin-top: 0.25rem;
}

.intel-stat {
    display: flex;
    flex-direction: column;
}

.stat-label {
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    color: #94a3b8;
    font-weight: 700;
}

.stat-value {
    font-size: 0.8rem;
    font-weight: 700;
    color: #334155;
}

/* Mobile Responsive */
@media (max-width: 1024px) {
    .dashboard-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .pulse-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }

    .snapshot-section,
    .activity-section {
        grid-column: span 1;
    }
}

/* Credit Intelligence V3 */
.credit-outlook-container {
    flex: 1;
    max-width: 400px;
    background: rgba(255, 255, 255, 0.4);
    padding: 1rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.5);
}

.credit-outlook-bar {
    height: 8px;
    background: rgba(0, 0, 0, 0.05);
    border-radius: 10px;
    position: relative;
    overflow: hidden;
}

.outlook-fill {
    height: 100%;
    transition: width 1s cubic-bezier(0.22, 1, 0.36, 1);
}

.outlook-marker {
    position: absolute;
    top: 0;
    width: 2px;
    height: 100%;
    background: #10b981;
    /* Green safe mark */
    z-index: 2;
}

.credit-info-bar-v3 {
    display: grid;
    grid-template-columns: 280px 1fr 280px;
    align-items: center;
    gap: 2.3rem;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.4);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    margin-bottom: 1.25rem;
    transition: all 0.3s ease;
}

.credit-info-bar-v3:hover {
    background: rgba(255, 255, 255, 0.7);
}

.credit-brand-col {
    display: flex;
    align-items: center;
}

/* Mini Credit Card (Digital Wallet Style) */
.mini-credit-card {
    width: 80px;
    height: 50px;
    border-radius: 8px;
    position: relative;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    overflow: hidden;
    flex-shrink: 0;
}

.mini-credit-card:hover {
    transform: scale(1.1) rotate(-2deg);
    z-index: 10;
}

.mini-credit-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0) 50%);
    pointer-events: none;
}

.card-chip {
    width: 12px;
    height: 9px;
    background: linear-gradient(135deg, #e2c074 0%, #aa8b45 100%);
    border-radius: 2px;
    position: absolute;
    top: 8px;
    left: 8px;
    opacity: 0.9;
}

.card-logo {
    position: absolute;
    top: 8px;
    right: 8px;
    font-size: 0.5rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.card-number {
    position: absolute;
    bottom: 6px;
    left: 8px;
    font-size: 0.55rem;
    font-family: monospace;
    letter-spacing: 1px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.v3-progress-container {
    position: relative;
    width: 100%;
}

.v3-safe-zone {
    position: absolute;
    top: 0;
    left: 30%;
    width: 2px;
    height: 100%;
    background: rgba(16, 185, 129, 0.3);
    z-index: 10;
}

.credit-data-col {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

@media (max-width: 1264px) {
    .credit-info-bar-v3 {
        grid-template-columns: 1fr;
        gap: 1.25rem;
    }

    .credit-data-col {
        align-items: flex-start;
    }
}

.card-icon-overlay {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    opacity: 0.15;
    pointer-events: none;
}

.interactive-list-item {
    transition: all 0.2s ease;
    border-radius: 12px;
}

.interactive-list-item:hover {
    background: rgba(255, 255, 255, 0.6) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}
</style>
