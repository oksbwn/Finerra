<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi, aiApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import { 
    Search, 
    Plus, 
    Upload, 
    RefreshCw,
    Lock,
    FileText,
    Eye,
    EyeOff,
    Mail
} from 'lucide-vue-next'
import { useCurrency } from '@/composables/useCurrency'
import { marked } from 'marked'

const notify = useNotificationStore()
const { formatAmount } = useCurrency()

const activeTab = ref('portfolio') // portfolio, search, import
const isLoading = ref(false)
const portfolio = ref<any[]>([])
const searchResults = ref<any[]>([])
const searchQuery = ref('')
const isSearching = ref(false)
const isAnalyzing = ref(false)
const aiAnalysis = ref('')
const currentUser = ref<any>(null)

// Transaction Form
const showTransactionModal = ref(false)
const selectedFund = ref<any>(null)
const transactionForm = ref({
    type: 'BUY',
    amount: 0,
    units: 0,
    nav: 0,
    date: new Date().toISOString().split('T')[0],
    folio_number: ''
})

// CAS Import
const fileInput = ref<HTMLInputElement | null>(null)
const casFile = ref<File | null>(null)
const casPassword = ref('')
const showCasPassword = ref(false)
const isImporting = ref(false)
const importResult = ref<any>(null)

// Helpers
function getRandomColor(str: string) {
    const colors = [
        '#6366f1', '#3b82f6', '#06b6d4', '#10b981', 
        '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'
    ]
    let hash = 0
    if (!str) return colors[0]
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
}

// Stats
const portfolioStats = computed(() => {
    let invested = 0
    let current = 0
    portfolio.value.forEach(h => {
        invested += h.invested_value
        current += h.current_value
    })
    return {
        invested,
        current,
        pl: current - invested,
        plPercent: invested > 0 ? ((current - invested) / invested) * 100 : 0
    }
})

async function fetchPortfolio() {
    isLoading.value = true
    try {
        const res = await financeApi.getPortfolio()
        portfolio.value = res.data
    } catch (e) {
        console.error(e)
        notify.error("Failed to load portfolio")
    } finally {
        isLoading.value = false
    }
}

async function handleSearch() {
    if (searchQuery.value.length < 2) return
    isSearching.value = true
    try {
        const res = await financeApi.searchFunds(searchQuery.value)
        searchResults.value = res.data
    } catch (e) {
        notify.error("Search failed")
    } finally {
        isSearching.value = false
    }
}

function openBuyModal(fund: any) {
    selectedFund.value = fund
    transactionForm.value = {
        type: 'BUY',
        amount: 0,
        units: 0,
        nav: 0, // Ideally fetch latest NAV here
        date: new Date().toISOString().split('T')[0],
        folio_number: ''
    }
    // Try to fetch latest NAV for this fund
    fetchLatestNav(fund.schemeCode)
    showTransactionModal.value = true
}

async function fetchLatestNav(code: string) {
    if (!code) return
    try {
        const res = await financeApi.getNav(code)
        if (res.data) {
            transactionForm.value.nav = res.data.nav
            notify.info(`Fetched NAV: ₹${res.data.nav} as of ${new Date(res.data.date).toLocaleDateString()}`)
        }
    } catch (e) {
        console.warn("Could not fetch latest NAV")
    }
}

async function submitTransaction() {
    if (!selectedFund.value) return
    try {
        await financeApi.createFundTransaction({
            scheme_code: String(selectedFund.value.schemeCode),
            ...transactionForm.value,
            amount: Number(transactionForm.value.amount),
            units: Number(transactionForm.value.units),
            nav: Number(transactionForm.value.nav),
            date: new Date(transactionForm.value.date).toISOString()
        })
        notify.success("Transaction added")
        showTransactionModal.value = false
        activeTab.value = 'portfolio'
        fetchPortfolio()
        searchQuery.value = ''
        searchResults.value = []
    } catch (e) {
        notify.error("Failed to submit transaction")
    }
}

async function handleCasUpload() {
    if (!casFile.value) return
    isImporting.value = true
    const formData = new FormData()
    formData.append('file', casFile.value)
    if (casPassword.value) formData.append('password', casPassword.value)

    try {
        const res = await financeApi.importCAS(formData)
        importResult.value = res.data
        notify.success(`Imported ${res.data.processed} transactions`)
        fetchPortfolio()
    } catch (e: any) {
        notify.error(e.response?.data?.detail || "Import failed")
    } finally {
        isImporting.value = false
    }
}

async function triggerEmailImport() {
    if (!casPassword.value) {
        notify.info("Please enter CAS password first")
        return
    }
    isImporting.value = true
    try {
        const formData = new FormData()
        formData.append('password', casPassword.value)
        const res = await financeApi.importCASEmail(formData)
        
        const stats = res.data.stats
        if (stats.found > 0) {
            notify.success(`Found ${stats.found} emails, processed ${stats.processed}`)
            fetchPortfolio()
        } else {
            notify.info("No CAS emails found")
        }
    } catch (e) {
        notify.error("Email import failed")
    } finally {
        isImporting.value = false
    }
}

async function generateAIAnalysis() {
    isAnalyzing.value = true
    try {
        const summary = {
            total_invested: portfolioStats.value.invested,
            current_value: portfolioStats.value.current,
            total_holdings: portfolio.value.length,
            holdings: portfolio.value.map(h => ({
                name: h.scheme_name,
                invested: h.invested_value,
                pnl_percent: ((h.current_value - h.invested_value) / h.invested_value) * 100,
                category: h.category || 'Unknown'
            }))
        }
        
        const res = await aiApi.generateSummaryInsights(summary)
        if (res.data && res.data.insights) {
             aiAnalysis.value = res.data.insights
        } else {
             aiAnalysis.value = "AI could not generate insights at this time."
        }
    } catch (error) {
        notify.error("Failed to generate analysis")
        aiAnalysis.value = "Failed to communicate with AI service."
    } finally {
        isAnalyzing.value = false
    }
}

function handleFileSelect(event: any) {
    const file = event.target.files[0]
    if (file) casFile.value = file
}

onMounted(async () => {
    fetchPortfolio()
    try {
        const res = await financeApi.getMe()
        currentUser.value = res.data
        
        // Auto-generate password if available and currently empty
        if (currentUser.value?.pan_number && !casPassword.value) {
            casPassword.value = currentUser.value.pan_number.toUpperCase()
        }
    } catch (e) {
        console.error("Failed to fetch user profile", e)
    }
})
</script>

<template>
    <MainLayout>
        <div class="page-header">
            <div class="header-left">
                <h1 class="page-title">Mutual Funds</h1>
                <div class="header-tabs">
                    <button 
                        class="tab-btn" 
                        :class="{ active: activeTab === 'portfolio' }"
                        @click="activeTab = 'portfolio'"
                    >
                        Portfolio
                    </button>
                    <button 
                        class="tab-btn" 
                        :class="{ active: activeTab === 'search' }"
                        @click="activeTab = 'search'"
                    >
                        Search & Add
                    </button>
                    <button 
                        class="tab-btn" 
                        :class="{ active: activeTab === 'import' }"
                        @click="activeTab = 'import'"
                    >
                        Import CAS
                    </button>
                </div>
                <span class="transaction-count">{{ portfolio.length }} funds</span>
            </div>
            <div class="header-actions">
                <button v-if="activeTab === 'portfolio'" @click="fetchPortfolio" class="btn-premium-secondary" :disabled="isLoading">
                    <RefreshCw :size="16" :class="{ 'spin': isLoading }" />
                    <span>Refresh</span>
                </button>
                <button v-if="activeTab === 'portfolio'" @click="activeTab = 'search'" class="btn-premium-primary">
                    <div class="btn-glow"></div>
                    <Plus :size="16" />
                    <span>New Investment</span>
                </button>
            </div>
        </div>

        <div class="content-container anim-fade-in">
            <!-- PORTFOLIO TAB -->
            <div v-if="activeTab === 'portfolio'" class="analytics-layout">
                <!-- AI Card (Standard from Insights.vue) -->
                <div class="ai-card" :class="{ 'is-loading': isAnalyzing }">
                    <div class="ai-card-content">
                        <div class="ai-header">
                            <div class="ai-title-left">
                                <div class="ai-sparkle-icon">✨</div>
                                <div class="ai-title-group">
                                    <h3 class="ai-card-title">Portfolio Intelligence</h3>
                                    <p class="ai-card-subtitle">AI analysis of holdings, sector risk, and performance</p>
                                </div>
                            </div>
                            <button 
                                @click="generateAIAnalysis"
                                :disabled="isAnalyzing"
                                class="ai-btn-glass"
                            >
                                <svg v-if="!isAnalyzing" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path d="M9 12l2 2 4-4"/></svg>
                                {{ isAnalyzing ? 'Analyzing...' : 'Refresh Analysis' }}
                            </button>
                        </div>
                        
                        <div v-if="aiAnalysis" class="ai-insight-box custom-scrollbar">
                            <div class="ai-insight-text markdown-body" v-html="marked(aiAnalysis)"></div>
                        </div>
                        <div v-else-if="isAnalyzing" class="ai-loading-skeleton">
                            <div class="shimmer-line"></div>
                            <div class="shimmer-line w-3/4"></div>
                            <div class="shimmer-line w-1/2"></div>
                        </div>
                        <p v-else class="ai-card-description">
                            Let AI analyze your asset allocation and sector exposure to suggest optimal rebalancing strategies.
                        </p>
                    </div>
                    <!-- Standard Mesh Blobs -->
                    <div class="mesh-blob blob-1"></div>
                    <div class="mesh-blob blob-2"></div>
                    <div class="mesh-blob blob-3"></div>
                </div>

                <!-- Standard Summary Cards -->
                <div class="summary-cards">
                    <div class="summary-card income">
                        <div class="card-icon">💰</div>
                        <div class="card-content">
                            <span class="card-label">Current Value</span>
                            <span class="card-value">{{ formatAmount(portfolioStats.current) }}</span>
                            <span class="card-trend text-emerald-600">
                                {{ portfolioStats.pl >= 0 ? '↑' : '↓' }} {{ Math.abs(portfolioStats.plPercent).toFixed(2) }}% Returns
                            </span>
                        </div>
                    </div>
                    <div class="summary-card net">
                        <div class="card-icon">📥</div>
                        <div class="card-content">
                            <span class="card-label">Invested Amount</span>
                            <span class="card-value">{{ formatAmount(portfolioStats.invested) }}</span>
                            <span class="card-trend text-indigo-600"> Across {{ portfolio.length }} Funds</span>
                        </div>
                    </div>
                    <div class="summary-card" :class="portfolioStats.pl >= 0 ? 'income' : 'expense'">
                        <div class="card-icon">📈</div>
                        <div class="card-content">
                            <span class="card-label">Overall Profit/Loss</span>
                            <span class="card-value" :class="portfolioStats.pl >= 0 ? 'text-emerald-700' : 'text-rose-700'">
                                {{ portfolioStats.pl >= 0 ? '+' : '' }}{{ formatAmount(portfolioStats.pl) }}
                            </span>
                             <span class="card-trend text-gray-400">Total XIRR pending</span>
                        </div>
                    </div>
                </div>

                <!-- Holdings List (Standard Table) -->
                <div class="analytics-card full-width">
                     <div class="card-header-flex">
                        <h3 class="card-title">Portfolio Holdings</h3>
                        <div class="card-controls">
                             <!-- Optional controls here -->
                        </div>
                    </div>
                    
                    <div class="table-container">
                         <div v-if="portfolio.length === 0 && !isLoading" class="py-12 text-center">
                            <div class="text-4xl mb-3">🌱</div>
                            <h3 class="text-gray-900 font-bold">No investments found</h3>
                            <p class="text-gray-500 text-sm">Add funds or import CAS to start tracking.</p>
                        </div>
                        
                        <table v-else class="modern-table">
                            <thead>
                                <tr>
                                    <th style="width: 40%">Fund Name</th>
                                    <th>Units</th>
                                    <th>Avg Price</th>
                                    <th>Current NAV</th>
                                    <th class="tabular-nums">Current Value</th>
                                    <th>Returns</th>
                                    <th style="width: 60px"></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="holding in portfolio" :key="holding.id">
                                    <td>
                                        <div class="flex items-center gap-3">
                                            <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-sm"
                                                 :style="{ background: getRandomColor(holding.scheme_name) }">
                                                {{ holding.scheme_name[0] }}
                                            </div>
                                            <div>
                                                <div class="font-medium text-gray-900 line-clamp-1" :title="holding.scheme_name">{{ holding.scheme_name }}</div>
                                                <div class="text-xs text-gray-500 font-medium">Folio: {{ holding.folio_number || 'N/A' }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="tabular-nums font-medium text-gray-700">{{ holding.units.toFixed(3) }}</td>
                                    <td class="tabular-nums text-gray-500">{{ formatAmount(holding.average_price) }}</td>
                                    <td class="tabular-nums text-gray-500">{{ formatAmount(holding.last_nav) }}</td>
                                    <td class="tabular-nums font-bold text-gray-900">{{ formatAmount(holding.current_value) }}</td>
                                    <td>
                                        <div :class="holding.profit_loss >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                                            <div class="font-bold text-xs">{{ holding.profit_loss >= 0 ? '+' : '' }}{{ formatAmount(holding.profit_loss) }}</div>
                                            <div class="text-[10px] opacity-80 font-bold">
                                                {{ ((holding.profit_loss / (holding.invested_value || 1)) * 100).toFixed(2) }}%
                                            </div>
                                        </div>
                                    </td>
                                    <td class="text-right">
                                        <button class="icon-btn" @click="openBuyModal(holding)" title="Add Transaction">
                                            <Plus :size="14" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

                <!-- SEARCH TAB (Premium Redesign) -->
            <div v-if="activeTab === 'search'" class="search-container-premium animate-in">
                <div class="search-hero">
                    <Search class="search-icon-large" />
                    <input 
                        v-model="searchQuery" 
                        @keyup.enter="handleSearch"
                        placeholder="Search by fund name or AMFI code..." 
                        type="text"
                        class="search-input-premium"
                        autofocus
                    />
                    <button 
                        v-if="searchQuery"
                        class="absolute right-4 top-1/2 -translate-y-1/2 btn-compact btn-primary"
                        @click="handleSearch"
                        :disabled="isSearching"
                    >
                        {{ isSearching ? 'Searching...' : 'Search' }}
                    </button>
                </div>

                <div v-if="searchResults.length > 0" class="search-results-grid">
                    <div v-for="fund in searchResults" :key="fund.schemeCode" class="fund-card" @click="openBuyModal(fund)">
                        <div class="fund-card-header">
                            <div class="fund-info">
                                <h3>{{ fund.schemeName }}</h3>
                                <div class="fund-category">{{ fund.schemeCode }}</div>
                            </div>
                            <button class="add-btn-round" title="Add Investment">
                                <Plus :size="20" />
                            </button>
                        </div>
                    </div>
                </div>
                
                <div v-else-if="!isSearching && searchQuery" class="empty-state-premium">
                    <div class="empty-icon-premium">🔍</div>
                    <p class="empty-text">No funds found for "{{ searchQuery }}"</p>
                </div>
            </div>

            <!-- IMPORT TAB (Side-by-Side Premium Redesign) -->
            <div v-if="activeTab === 'import'" class="import-tab-content animate-in">
                <div class="import-grid-premium">
                    <!-- PDF UPLOAD CARD -->
                    <div class="glass-import-card">
                        <div class="mode-header">
                            <div class="icon-box-premium indigo">
                                <Upload :size="28" />
                            </div>
                            <h2>PDF Statement</h2>
                            <p>Upload your CAS PDF from CAMS or KFintech.</p>
                        </div>

                        <div 
                            class="upload-zone-premium"
                            @click="fileInput?.click()"
                            :class="{ 'has-file': casFile }"
                        >
                            <input type="file" ref="fileInput" @change="handleFileSelect" accept=".pdf" hidden />
                            <div v-if="casFile" class="upload-file-info animate-fade">
                                <div class="file-icon-wrapper">
                                    <FileText :size="32" />
                                    <div class="file-check">✓</div>
                                </div>
                                <div class="text-lg font-bold text-gray-900 mt-2 truncate w-full px-4">{{ casFile.name }}</div>
                            </div>
                            <div v-else class="upload-placeholder">
                                <div class="upload-icon-circle">
                                    <Upload :size="24" />
                                </div>
                                <div class="upload-text">Browse CAS PDF</div>
                            </div>
                            <!-- Mesh Accents -->
                            <div class="upload-mesh mesh-1"></div>
                        </div>

                        <div class="password-field-group mt-6">
                            <label class="field-label">PDF Password</label>
                            <div class="premium-input-group">
                                <Lock :size="16" class="input-icon-leading" />
                                <input 
                                    :type="showCasPassword ? 'text' : 'password'" 
                                    v-model="casPassword" 
                                    placeholder="e.g. PAN Number" 
                                    class="clean-input" 
                                />
                                <button 
                                    type="button"
                                    class="password-toggle-btn"
                                    @click="showCasPassword = !showCasPassword"
                                >
                                    <Eye v-if="!showCasPassword" :size="18" />
                                    <EyeOff v-else :size="18" />
                                </button>
                            </div>
                        </div>

                        <div class="action-footer mt-auto pt-6">
                             <button 
                                class="btn-primary-large w-full" 
                                @click="handleCasUpload" 
                                :disabled="!casFile || isImporting"
                            >
                                <RefreshCw v-if="isImporting" :size="18" class="spin mr-2" />
                                {{ isImporting ? 'Processing...' : 'Unlock & Import' }}
                            </button>
                        </div>
                    </div>

                    <!-- EMAIL SYNC CARD -->
                    <div class="glass-import-card">
                         <div class="mode-header">
                            <div class="icon-box-premium emerald">
                                <Mail :size="28" />
                            </div>
                            <h2>Email Sync</h2>
                            <p>Scan linked email accounts for recent CAS.</p>
                        </div>

                        <div class="info-box-premium emerald mb-6">
                            <h4>How it works</h4>
                            <p>We securely search for recent emails and process the attachments using the password provided below.</p>
                        </div>
                        
                        <div class="password-field-group mb-6">
                            <label class="field-label">Sync Password</label>
                             <div class="premium-input-group">
                                <Lock :size="16" class="input-icon-leading" />
                                <input 
                                    :type="showCasPassword ? 'text' : 'password'" 
                                    v-model="casPassword" 
                                    placeholder="Enter PDF password" 
                                    class="clean-input" 
                                />
                                <button 
                                    type="button"
                                    class="password-toggle-btn"
                                    @click="showCasPassword = !showCasPassword"
                                >
                                    <Eye v-if="!showCasPassword" :size="18" />
                                    <EyeOff v-else :size="18" />
                                </button>
                            </div>
                        </div>

                        <div class="action-footer mt-auto">
                            <button class="btn-primary-large emerald-theme w-full" @click="triggerEmailImport" :disabled="isImporting">
                                <RefreshCw v-if="isImporting" :size="18" class="spin mr-2" />
                                <span v-else class="mr-2">📧</span>
                                {{ isImporting ? 'Scanning...' : 'Scan My Inbox' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TRANSACTIONS MODAL -->
        <div v-if="showTransactionModal" class="modal-overlay" @click.self="showTransactionModal = false">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Record Transaction</h2>
                    <button class="close-btn" @click="showTransactionModal = false">✕</button>
                </div>
                
                <div class="p-4 bg-slate-50 border border-slate-100 flex items-center gap-4 rounded-2xl mb-8">
                    <div class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-sm"
                         :style="{ background: getRandomColor(selectedFund?.schemeName || selectedFund?.scheme_name) }">
                        {{ (selectedFund?.schemeName || selectedFund?.scheme_name)?.[0] }}
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-0.5">Fund Name</div>
                        <div class="text-sm font-bold text-slate-900 truncate">
                            {{ selectedFund?.schemeName || selectedFund?.scheme_name }}
                        </div>
                    </div>
                </div>

                <div class="space-y-5">
                    <div class="grid grid-cols-2 gap-5">
                        <div class="form-group">
                            <label class="field-label">Type</label>
                            <select v-model="transactionForm.type" class="premium-input">
                                <option value="BUY">Buy</option>
                                <option value="SELL">Sell</option>
                                <option value="SIP">SIP</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="field-label">Date</label>
                            <input type="date" v-model="transactionForm.date" class="premium-input" />
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-5">
                        <div class="form-group">
                            <label class="field-label">Amount (₹)</label>
                            <input type="number" v-model="transactionForm.amount" class="premium-input" placeholder="0.00" />
                        </div>
                        <div class="form-group">
                            <label class="field-label">NAV</label>
                            <input type="number" step="0.0001" v-model="transactionForm.nav" class="premium-input" placeholder="0.0000" />
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label class="field-label">Units</label>
                        <input type="number" step="0.001" v-model="transactionForm.units" class="premium-input" placeholder="0.000" />
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn btn-text" @click="showTransactionModal = false">Cancel</button>
                    <button class="btn-primary-large" @click="submitTransaction">Confirm</button>
                </div>
            </div>
        </div>
    </MainLayout>
</template>

<style scoped>
/* Base Layout */
.content-container {
    width: 100%;
}

.analytics-layout {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

/* Page Header - Consistent with Insights/Transactions */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.header-left {
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
}

.page-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin: 0;
}

.header-tabs {
    display: flex;
    gap: 0.25rem;
    background: #f3f4f6;
    padding: 0.25rem;
    border-radius: 0.5rem;
    margin: 0 1rem;
}

.tab-btn {
    padding: 0.4rem 1rem;
    border: none;
    background: transparent;
    border-radius: 0.375rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn.active {
    background: white;
    color: #4f46e5;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

/* Premium AI Card - Midnight Theme */
.ai-card {
    background: #0f172a;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 1.75rem 2.25rem;
    border-radius: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.ai-card-content {
    position: relative;
    z-index: 10;
}

.ai-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
}

.ai-title-left {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.ai-sparkle-icon {
    font-size: 2rem;
    background: rgba(255, 255, 255, 0.1);
    width: 3.5rem;
    height: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 1rem;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.text-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.ai-card-title {
    font-size: 1.125rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.01em;
    color: #f8fafc;
}

.ai-card-subtitle {
    font-size: 0.8125rem;
    color: #94a3b8;
    margin: 4px 0 0 0;
    font-weight: 400;
}

.ai-insight-box {
    background: rgba(15, 23, 42, 0.4);
    padding: 1.5rem;
    border-radius: 1.25rem;
    backdrop-filter: blur(8px);
    margin-bottom: 0.5rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
    max-height: 400px;
    overflow-y: auto;
}

.ai-btn-glass {
    background: rgba(255, 255, 255, 0.05);
    color: white;
    padding: 0.625rem 1.25rem;
    border-radius: 0.75rem;
    font-weight: 600;
    font-size: 0.8125rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.625rem;
    white-space: nowrap;
}

.ai-btn-glass:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}

.mesh-blob {
    position: absolute;
    filter: blur(80px);
    opacity: 0.15;
    border-radius: 50%;
    z-index: 1;
}

.blob-1 { width: 400px; height: 400px; background: #3b82f6; top: -150px; right: -100px; }
.blob-2 { width: 350px; height: 350px; background: #6366f1; bottom: -100px; left: -100px; }
.blob-3 { width: 250px; height: 250px; background: #1e40af; top: 10%; left: 20%; }

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
}

.summary-card {
    background: white;
    padding: 1.5rem;
    border-radius: 1rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    gap: 1.25rem;
    transition: all 0.3s ease;
}

.summary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.card-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 3rem;
    height: 3rem;
    border-radius: 0.75rem;
    font-size: 1.5rem;
}

.income .card-icon { background: #ecfdf5; color: #10b981; }
.invested .card-icon { background: #e0e7ff; color: #4f46e5; }
.net .card-icon { background: #eff6ff; color: #3b82f6; }

.card-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.card-label {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.card-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
}

.card-trend {
    font-size: 0.625rem;
    font-weight: 700;
    margin-top: 0.25rem;
    display: block;
}

/* Filter Bar & Header Alignment */
.filter-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    background: transparent;
    padding: 0;
    border: none;
}

.filter-left-section {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.transaction-count {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 600;
    background: #f1f5f9;
    padding: 0.375rem 0.75rem;
    border-radius: 2rem;
}

/* Search Tab - Premium Redesign */
.search-container-premium {
    max-width: 800px;
    margin: 4rem auto;
    display: flex;
    flex-direction: column;
    gap: 3rem;
}

.search-hero {
    position: relative;
    width: 100%;
}

.search-input-premium {
    width: 100%;
    padding: 1.5rem 2rem 1.5rem 4rem;
    font-size: 1.25rem;
    color: #0f172a;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); /* Soft shadow */
    transition: all 0.3s ease;
}

.search-input-premium:focus {
    outline: none;
    border-color: #4f46e5;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.search-icon-large {
    position: absolute;
    left: 1.5rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    color: #94a3b8;
}

.search-results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.5rem;
}

.fund-card {
    background: white;
    padding: 1.5rem;
    border-radius: 1.25rem;
    border: 1px solid #f1f5f9;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
}

.fund-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    border-color: #e2e8f0;
}

.fund-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
}

.fund-info h3 {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.4;
    margin: 0 0 0.5rem 0;
}

.fund-category {
    font-size: 0.75rem;
    color: #64748b;
    background: #f8fafc;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    display: inline-block;
    font-weight: 500;
}

.add-btn-round {
    width: 2.5rem;
    height: 2.5rem;
    border-radius: 50%;
    background: #f1f5f9;
    color: #4f46e5;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    cursor: pointer;
    transition: all 0.2s;
}

.add-btn-round:hover {
    background: #4f46e5;
    color: white;
    transform: scale(1.1);
}


.upload-zone-premium {
    margin: 2rem 0;
    border: 2px dashed #e2e8f0;
    border-radius: 1.5rem;
    padding: 3.5rem 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    background: #fdfdfd;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.upload-zone-premium:hover {
    border-color: #4f46e5;
    background: #f5f3ff;
}

.upload-zone-premium.has-file {
    border-color: #10b981;
    background: #f0fdf4;
    border-style: solid;
}

.upload-icon-circle {
    width: 4.5rem;
    height: 4.5rem;
    background: #f1f5f9;
    color: #64748b;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem auto;
    transition: all 0.3s;
}

.upload-zone-premium:hover .upload-icon-circle {
    background: #4f46e5;
    color: white;
    transform: scale(1.1);
}

.upload-file-info {
    position: relative;
    z-index: 2;
}

.file-icon-wrapper {
    position: relative;
    display: inline-block;
    color: #10b981;
}

.file-check {
    position: absolute;
    bottom: -2px;
    right: -2px;
    background: #10b981;
    color: white;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
}

.upload-mesh {
    position: absolute;
    width: 200px;
    height: 200px;
    filter: blur(60px);
    opacity: 0.05;
    z-index: 1;
}

.upload-mesh.mesh-1 { top: -50px; left: -50px; background: #4f46e5; }
.upload-mesh.mesh-2 { bottom: -50px; right: -50px; background: #10b981; }

.password-field-group {
    text-align: left;
    margin-top: 2rem;
}


/* Premium Table */
.holdings-table-container {
    background: white;
    border-radius: 1.5rem;
    border: 1px solid #f1f5f9;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.modern-table th {
    background: #f8fafc;
    padding: 1rem 1.5rem;
    font-size: 0.65rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #f1f5f9;
}

.modern-table td {
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #f8fafc;
    color: #4b5563;
    font-size: 0.875rem;
    vertical-align: middle;
}

.modern-table tr:hover td {
    background: #f9fafb;
}

.modern-table td .font-medium {
    color: #111827;
}

.modern-table .icon-btn {
    width: 28px;
    height: 28px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    background: white;
    color: #6b7280;
    transition: all 0.2s;
}

.modern-table .icon-btn:hover {
    color: #4f46e5;
    background: #f5f3ff;
    border-color: #c4b5fd;
    transform: translateY(-1px);
}

/* Empty State */
.empty-state-premium {
    padding: 6rem 2rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.empty-icon-premium {
    font-size: 4rem;
    color: #e2e8f0;
    opacity: 0.8;
}

.empty-text {
    font-size: 1.125rem;
    color: #94a3b8; /* Muted gray */
    font-weight: 500;
}

/* --- UNIFIED IMPORT STYLES (PREMIUM) --- */

/* Side-by-Side Import Grid */
.import-tab-content {
    max-width: 1200px;
    margin: 0 auto;
}

.import-grid-premium {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2.5rem;
    margin-top: 1rem;
}

.glass-import-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 2.5rem;
    padding: 3rem;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    min-height: 600px;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.glass-import-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.08);
    background: rgba(255, 255, 255, 0.85);
}

.adaptive-card {
    min-height: 500px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: all 0.5s ease;
}

.mode-content {
    animation: fadeIn 0.4s ease-out;
    width: 100%;
}

.icon-box-premium {
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem auto;
}

.icon-box-premium.indigo {
    background: #eef2ff;
    color: #4f46e5;
}

.icon-box-premium.emerald {
    background: #ecfdf5;
    color: #059669;
}

.mode-header {
    text-align: center;
    margin-bottom: 2rem;
}

.mode-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 0.5rem;
}

.mode-header p {
    color: #64748b;
}

.info-box-premium {
    background: rgba(239, 246, 255, 0.6);
    border: 1px solid rgba(191, 219, 254, 0.5);
    border-radius: 1rem;
    padding: 1.25rem;
    margin-bottom: 2rem;
    font-size: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 480px;
    margin-left: auto;
    margin-right: auto;
}

.info-box-premium h4 {
    font-weight: 700;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: flex;
    align-items: center;
}

.field-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

.field-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
}

.field-hint {
    font-size: 0.75rem;
    color: #94a3b8;
    text-align: center;
    margin-top: 0.5rem;
}

.premium-input {
    width: 100%;
    padding: 0.875rem 1rem;
    border-radius: 0.75rem;
    border: 1px solid #e2e8f0;
    background: #fff;
    font-size: 0.95rem;
    transition: all 0.2s;
}

.premium-input:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* New Integrated Input Group */
.premium-input-group {
    position: relative;
    display: flex;
    align-items: center;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 0 0.5rem 0 1rem;
    transition: all 0.2s;
    width: 100%;
    min-height: 3.25rem;
}

.premium-input-group:focus-within {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.clean-input {
    flex: 1;
    background: transparent;
    border: none;
    padding: 0.875rem 0.5rem;
    font-size: 0.95rem;
    color: #1e293b;
    width: 100%;
    outline: none;
}

.input-icon-leading {
    color: #94a3b8;
    flex-shrink: 0;
}

.password-toggle-btn {
    width: 2.25rem;
    height: 2.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0.5rem;
    color: #94a3b8;
    transition: all 0.2s;
    background: transparent;
    border: none;
    cursor: pointer;
    flex-shrink: 0;
}

.password-toggle-btn:hover {
    background: #f1f5f9;
    color: #6366f1;
}

.action-footer {
    margin-top: 2.5rem;
    display: flex;
    justify-content: center;
}

.btn-primary-large {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
    color: white;
    padding: 0.875rem 2.5rem;
    border-radius: 99px;
    font-weight: 600;
    font-size: 1rem;
    box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.3);
    transition: all 0.3s;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.btn-primary-large:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 15px 25px -5px rgba(79, 70, 229, 0.4);
}

.btn-premium-primary {
    background: #0f172a;
    color: white;
    border: none;
    padding: 0.625rem 1.25rem;
    border-radius: 0.75rem;
    font-size: 0.8125rem;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
}

.btn-premium-primary:hover {
    transform: translateY(-2px);
    background: #1e293b;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.3);
}

.btn-premium-secondary {
    background: white;
    color: #475569;
    border: 1px solid #e2e8f0;
    padding: 0.625rem 1.25rem;
    border-radius: 0.75rem;
    font-size: 0.8125rem;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s;
}

.btn-premium-secondary:hover:not(:disabled) {
    background: #f8fafc;
    border-color: #cbd5e1;
    color: #1e293b;
    transform: translateY(-1px);
}

.btn-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
    pointer-events: none;
}

.btn-premium-primary:hover .btn-glow {
    opacity: 1;
}

.info-box-premium.emerald {
    background: rgba(236, 253, 245, 0.6);
    border-color: rgba(167, 243, 208, 0.5);
    color: #064e3b;
}

.btn-primary-large:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.btn-primary-large.emerald-theme {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 10px 20px -5px rgba(5, 150, 105, 0.3);
}

.btn-primary-large.emerald-theme:hover:not(:disabled) {
    box-shadow: 0 15px 25px -5px rgba(5, 150, 105, 0.4);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.3s ease-out;
}

.modal-content {
    background: white;
    width: 100%;
    max-width: 500px;
    border-radius: 2rem;
    padding: 2.5rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    position: relative;
    animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.modal-header h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0;
}

.close-btn {
    background: #f1f5f9;
    border: none;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #64748b;
    transition: all 0.2s;
}

.close-btn:hover {
    background: #e2e8f0;
    color: #0f172a;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 2.5rem;
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
