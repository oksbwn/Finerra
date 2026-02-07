<template>
    <div class="tab-content animate-in">


        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div class="glass-card p-6 flex items-center gap-4">
                <div class="p-3 rounded-xl bg-emerald-50 text-emerald-600">
                    <CheckCircle :size="32" />
                </div>
                <div>
                    <h3 class="font-bold text-gray-800">Parser Status</h3>
                    <p class="text-sm" :class="parserStatus.isOnline ? 'text-emerald-600' : 'text-rose-600'">
                        {{ parserStatus.isOnline ? 'Active & Online' : 'Service Down' }}
                    </p>
                </div>
            </div>

            <div class="glass-card p-6 flex items-center gap-4">
                <div class="p-3 rounded-xl bg-indigo-50 text-indigo-600">
                    <Zap :size="32" />
                </div>
                <div>
                    <h3 class="font-bold text-gray-800">24h Throughput</h3>
                    <p class="text-sm text-gray-500">{{ parserStats?.summary?.total_processed || 0 }}
                        Requests</p>
                </div>
            </div>

            <div class="glass-card p-6 flex items-center gap-4">
                <div class="p-3 rounded-xl bg-amber-50 text-amber-600">
                    <ShieldCheck :size="32" />
                </div>
                <div>
                    <h3 class="font-bold text-gray-800">Success Rate</h3>
                    <p class="text-sm text-gray-500">{{ calculateSuccessRate }}% accuracy</p>
                </div>
            </div>
        </div>

        <div class="ai-layout mb-12">
            <!-- Parser Configuration -->
            <div class="ai-config-section">
                <div class="ai-card">
                    <div class="ai-card-header">
                        <BrainCircuit :size="18" class="text-indigo-600" />
                        <h4 class="ai-card-title">Parser AI Configuration</h4>
                    </div>
                    <div class="ai-card-body">
                        <div v-if="appAiMatch"
                            class="mb-6 p-4 bg-emerald-50 border border-emerald-100 rounded-xl flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <span class="text-emerald-600">✨</span>
                                <span class="text-xs text-emerald-800 font-medium">Synced with App
                                    Intelligence</span>
                            </div>
                            <button @click="handleSync"
                                class="text-[10px] uppercase tracking-wider font-bold text-emerald-700 hover:underline">
                                Force Resync
                            </button>
                        </div>
                        <div v-else
                            class="mb-6 p-4 bg-amber-50 border border-amber-100 rounded-xl flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <span class="text-amber-600">⚠️</span>
                                <span class="text-xs text-amber-800 font-medium">Config out of sync with
                                    App</span>
                            </div>
                            <button @click="handleSync"
                                class="px-3 py-1 bg-amber-600 text-white rounded-lg text-[10px] font-bold shadow-sm">
                                Fix Now
                            </button>
                        </div>

                        <div class="flex flex-col gap-6">
                            <div class="text-sm text-gray-500">
                                The Parser Engine runs as a separate microservice. Sync your main
                                application's AI settings (Model & API Key) to ensure consistent
                                parsing.
                            </div>

                            <div class="p-4 bg-gray-50 rounded-xl border border-gray-100 grid grid-cols-2 gap-4">
                                <div>
                                    <label
                                        class="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">Current
                                        Model</label>
                                    <div class="font-mono text-sm font-semibold text-gray-800">{{
                                        parserAiForm.model_name || 'Not Configured' }}</div>
                                </div>
                                <div>
                                    <label
                                        class="text-xs font-bold text-gray-500 uppercase tracking-wider block mb-1">AI
                                        Status</label>
                                    <span
                                        :class="parserAiForm.is_enabled ? 'text-emerald-600 bg-emerald-100' : 'text-gray-500 bg-gray-200'"
                                        class="px-2 py-0.5 rounded textxs font-bold">
                                        {{ parserAiForm.is_enabled ? 'ENABLED' : 'DISABLED' }}
                                    </span>
                                </div>
                            </div>

                            <button @click="handleSync" :disabled="isSyncing"
                                class="flex items-center justify-center w-full px-4 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-200 transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed">
                                <div class="flex items-center gap-2">
                                    <svg v-if="isSyncing" width="18" height="18" viewBox="0 0 24 24" fill="none"
                                        class="animate-spin-slow" stroke="currentColor" stroke-width="2">
                                        <path d="M21 12a9 9 0 11-6.219-8.56" />
                                    </svg>
                                    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none"
                                        stroke="currentColor" stroke-width="2">
                                        <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13" />
                                    </svg>
                                    <span>{{ isSyncing ? 'Syncing...' : 'Sync AI Config to Parser' }}</span>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Performance Breakdown -->
            <div class="ai-playground">
                <div class="ai-card">
                    <div class="ai-card-header">
                        <Activity :size="18" class="text-amber-500" />
                        <h4 class="ai-card-title">Parser Performance</h4>
                    </div>
                    <div class="ai-card-body">
                        <div class="space-y-4">
                            <div v-for="(count, parser) in parserStats?.parser_performance" :key="parser"
                                class="flex flex-col gap-1">
                                <div class="flex justify-between text-xs">
                                    <span class="font-bold text-gray-700">{{ parser }}</span>
                                    <span class="text-muted">{{ count }} hits</span>
                                </div>
                                <div class="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-indigo-500"
                                        :style="{ width: (count / parserStats.summary.total_processed * 100) + '%' }">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Parser History -->
        <div
            class="activity-log-section bg-white/30 backdrop-blur-md rounded-2xl border border-white/20 p-6 overflow-hidden">
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-4">
                    <h3 class="text-lg font-bold flex items-center gap-2">
                        <span class="bg-indigo-100 text-indigo-600 p-2 rounded-lg text-sm">📜</span>
                        Parser Request History
                    </h3>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-[10px] text-muted font-mono bg-gray-100 px-2 py-1 rounded">Total:
                        {{
                            parserLogPagination.total }}</span>
                    <button @click="fetchParserData(undefined, true)" class="btn-icon-circle"
                        title="Refresh">🔄</button>
                </div>
            </div>

            <div class="overflow-x-auto min-h-[300px]">
                <table class="w-full text-left text-sm">
                    <thead class="text-muted border-b border-gray-100">
                        <tr>
                            <th class="pb-3 pr-4 font-semibold w-24">Time</th>
                            <th class="pb-3 pr-4 font-semibold w-20">Source</th>
                            <th class="pb-3 pr-4 font-semibold w-24">Status</th>
                            <th class="pb-3 pr-4 font-semibold max-w-xs">Input Preview</th>
                            <th class="pb-3 pr-4 font-semibold">Extracted Details</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                        <tr v-for="log in parserLogs" :key="log.id" class="hover:bg-white/40 group transition-colors">
                            <td class="py-3 text-xs whitespace-nowrap">{{
                                formatDate(log.created_at).meta }}
                            </td>
                            <td class="py-3">
                                <span
                                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-gray-100 text-gray-600 border border-gray-200">
                                    {{ log.source }}
                                </span>
                            </td>
                            <td class="py-3">
                                <span
                                    :class="log.status === 'success' ? 'text-emerald-700 bg-emerald-50 border border-emerald-100' : 'text-rose-700 bg-rose-50 border border-rose-100'"
                                    class="px-2 py-0.5 rounded-full text-[10px] font-bold flex items-center justify-center w-fit">
                                    {{ log.status }}
                                </span>
                                <div v-if="log.error_message"
                                    class="text-[10px] text-rose-500 mt-1 truncate max-w-[100px]"
                                    :title="log.error_message">
                                    {{ log.error_message }}
                                </div>
                            </td>
                            <td class="py-3 text-xs text-muted max-w-xs">
                                <div class="truncate" :title="JSON.stringify(log.input_payload)">
                                    {{ log.input_payload?.message || log.input_payload?.body ||
                                        log.input_payload?.content || 'Raw Input' }}
                                </div>
                            </td>
                            <td class="py-3 text-xs">
                                <div v-if="log.output_payload" class="flex flex-col gap-1">
                                    <div v-if="log.output_payload.results?.length > 1"
                                        class="font-bold text-indigo-600">
                                        📦 {{ log.output_payload.results.length }} items
                                    </div>
                                    <div v-if="log.output_payload.results?.[0]?.transaction"
                                        class="font-medium text-gray-800">
                                        {{
                                            log.output_payload.results[0].transaction.merchant?.cleaned
                                            ||
                                            log.output_payload.results[0].transaction.description }}
                                    </div>
                                    <div v-if="log.output_payload.results?.[0]?.transaction" class="text-gray-500">
                                        {{
                                            formatAmount(log.output_payload.results[0].transaction.amount)
                                        }}
                                    </div>
                                    <div v-else-if="log.output_payload.error" class="text-rose-500 italic">
                                        {{ log.output_payload.error }}
                                    </div>
                                    <div v-else class="text-gray-400 italic">No extraction</div>
                                </div>
                                <div v-else class="text-gray-400 italic">No output</div>
                            </td>
                        </tr>
                        <tr v-if="parserLogs.length === 0">
                            <td colspan="5" class="py-12 text-center text-muted italic">
                                No parser logs found.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination Controls -->
            <div v-if="parserLogPagination.total > parserLogPagination.limit"
                class="mt-6 flex items-center justify-between border-t border-gray-100 pt-6">
                <!-- ... (keeping existing pagination code) ... -->
                <span class="text-[10px] text-muted">
                    Showing {{ parserLogPagination.skip + 1 }} to {{ Math.min(parserLogPagination.skip +
                        parserLogPagination.limit, parserLogPagination.total) }} of {{ parserLogPagination.total }}
                </span>
                <div class="flex items-center gap-1">
                    <button @click="parserLogPagination.skip -= parserLogPagination.limit; fetchParserData()"
                        :disabled="parserLogPagination.skip === 0"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Previous
                    </button>
                    <button @click="parserLogPagination.skip += parserLogPagination.limit; fetchParserData()"
                        :disabled="parserLogPagination.skip + parserLogPagination.limit >= parserLogPagination.total"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Next
                    </button>
                </div>
            </div>
        </div>

        <div class="mt-12 pattern-management">
            <!-- Header -->
            <div class="section-header">
                <div>
                    <h2 class="section-title">Parser Patterns</h2>
                    <p class="section-subtitle">View and manage transaction parser patterns</p>
                </div>
                <button @click="openAddModal" class="btn-primary">
                    + Add Pattern
                </button>
            </div>

            <!-- Patterns Table -->
            <div class="glass-card">
                <div v-if="patternsLoading" class="loading-state">
                    <div class="loader-spinner"></div>
                    <p>Loading patterns...</p>
                </div>

                <table v-else class="patterns-table">
                    <thead>
                        <tr>
                            <th>Bank</th>
                            <th>Pattern</th>
                            <th>Source / ID</th>
                            <th class="text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="pattern in patterns" :key="pattern.id">
                            <td><span class="bank-badge">{{ pattern.bank_name }}</span></td>
                            <td>
                                <code class="pattern-code" :title="pattern.regex_pattern">{{ pattern.regex_pattern
                                }}</code>
                            </td>
                            <td>
                                <div class="flex flex-col gap-1">
                                    <span v-if="pattern.is_ai_generated" class="source-badge ai">🤖 AI</span>
                                    <span v-else class="source-badge manual">✏️ Manual</span>
                                    <span class="text-[10px] text-gray-400 font-mono">{{ pattern.id.substring(0, 8)
                                    }}</span>
                                </div>
                            </td>
                            <td class="text-right">
                                <button type="button" @click.stop="openEditModal(pattern)" class="btn-icon"
                                    title="Edit">
                                    ✏️
                                </button>
                                <button type="button" @click.stop="confirmDelete(pattern)" class="btn-icon text-red-500"
                                    title="Delete">
                                    🗑️
                                </button>
                            </td>
                        </tr>
                        <tr v-if="patterns.length === 0">
                            <td colspan="4" class="empty-state">
                                <span class="empty-icon">📋</span>
                                <p>No patterns found</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Add/Edit Pattern Modal -->
            <Teleport to="body">
                <div v-if="showPatternModal" class="modal-overlay">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>{{ isEditingPattern ? 'Edit Pattern' : 'New Pattern' }}</h3>
                            <button @click="closePatternModal" class="btn-close">✕</button>
                        </div>

                        <form @submit.prevent="savePattern" class="modal-body">
                            <div class="form-group">
                                <label>Bank / Application Name</label>
                                <input v-model="patternForm.bank_name" class="form-input" required
                                    placeholder="e.g. HDFC Bank"
                                    :disabled="isEditingPattern && patternForm.is_ai_generated" />
                            </div>

                            <div class="form-group">
                                <label>Regex Pattern</label>
                                <textarea v-model="patternForm.regex_pattern" class="form-textarea font-mono text-xs"
                                    rows="3" required placeholder="Regex to capture transactions..."></textarea>
                            </div>

                            <div class="form-group">
                                <label>Field Mapping (JSON)</label>
                                <textarea v-model="patternForm.field_mapping_str"
                                    class="form-textarea font-mono text-xs" rows="3"
                                    placeholder='{"amount": 1, "merchant": 2}'></textarea>
                                <span class="text-xs text-gray-500">Map fields to regex groups (1-based index)</span>
                            </div>

                            <div class="form-group">
                                <label>Confidence Score (0.0 - 1.0)</label>
                                <input type="number" step="0.1" min="0" max="1" v-model.number="patternForm.confidence"
                                    class="form-input" />
                            </div>

                            <div v-if="patternError" class="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm">
                                {{ patternError }}
                            </div>

                            <div class="modal-footer">
                                <button type="button" @click="closePatternModal" class="btn-secondary">Cancel</button>
                                <button type="submit" class="btn-primary" :disabled="patternSaving">
                                    {{ patternSaving ? 'Saving...' :
                                        (isEditingPattern ? 'Update Pattern' : 'Create Pattern')
                                    }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </Teleport>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import {
    CheckCircle, Zap, ShieldCheck, BrainCircuit, Activity
} from 'lucide-vue-next'
import { parserApi, financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import { useAiStore } from '@/stores/ai'

const aiStore = useAiStore()



import { useCurrency } from '@/composables/useCurrency'
const { formatAmount } = useCurrency()

const notify = useNotificationStore()

// --- Internal State ---
const parserStatus = ref({ isOnline: false })
const isSyncing = ref(false)
const parserStats = ref<any>(null)
const parserLogs = ref<any[]>([])
const parserAiForm = ref({
    is_enabled: false,
    model_name: 'models/gemini-1.5-flash',
    api_key: ''
})
const parserLogPagination = ref({ limit: 10, skip: 0, total: 0 })

// --- Computed ---
const calculateSuccessRate = computed(() => {
    if (!parserStats.value?.summary?.total_processed) return 0
    const success = parserStats.value.summary.status_breakdown?.success || 0
    return Math.round((success / parserStats.value.summary.total_processed) * 100)
})

const appAiMatch = computed(() => {
    // Check if app Gemini config matches parser Gemini config
    return aiStore.aiForm.model_name === parserAiForm.value.model_name &&
        aiStore.aiForm.is_enabled === parserAiForm.value.is_enabled
})

// --- Methods ---
const fetchParserData = async (sourceFilter?: string, resetSkip = false) => {
    if (resetSkip) parserLogPagination.value.skip = 0

    try {
        const [health, stats, logs, config] = await Promise.all([
            parserApi.getHealth(),
            parserApi.getStats(),
            parserApi.getLogs({
                limit: parserLogPagination.value.limit,
                offset: parserLogPagination.value.skip,
                source: sourceFilter
            }),
            parserApi.getAiConfig()
        ])
        parserStatus.value.isOnline = health.data?.status === 'ok'
        parserStats.value = stats.data || null
        parserLogs.value = logs.data?.logs || []
        parserLogPagination.value.total = logs.data?.total || 0

        parserAiForm.value = {
            is_enabled: config.data.is_enabled || false,
            model_name: config.data.model_name || 'models/gemini-1.5-flash',
            api_key: '' // Don't show existing key
        }
    } catch (e) {
        parserStatus.value.isOnline = false
        console.error("Failed to fetch parser data", e)
    }
}

async function handleSync() {
    if (!aiStore.aiForm.has_api_key && !aiStore.aiForm.api_key) {
        notify.warning("App AI is not configured.")
        return
    }

    try {
        isSyncing.value = true
        await financeApi.syncAiToParser()
        notify.success("Synced App AI Settings to Parser")
        fetchParserData()
    } catch (e) {
        notify.error("Sync failed: Check if parser microservice is online")
    } finally {
        isSyncing.value = false
    }
}

function formatDate(dateStr: string) {
    if (!dateStr) return { day: 'N/A', meta: '' }
    const d = new Date(dateStr)
    return {
        day: d.toLocaleDateString(),
        meta: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        full: d.toLocaleString()
    }
}

onMounted(() => {
    fetchParserData()
    if (!aiStore.aiForm.model_name) {
        aiStore.fetchAiSettings()
    }
    loadPatterns()
})

// --- Pattern Management Logic ---
import axios from 'axios'
const PARSER_API = 'http://localhost:8001'

const patterns = ref([])
const patternsLoading = ref(false)
const patternSaving = ref(false)
const patternError = ref<string | null>(null)

const showPatternModal = ref(false)
const isEditingPattern = ref(false)
const patternForm = reactive({
    id: null as string | null,
    bank_name: '',
    regex_pattern: '',
    field_mapping_str: '{}',
    confidence: 1.0,
    is_ai_generated: false
})

async function loadPatterns() {
    patternsLoading.value = true
    try {
        const res = await axios.get(`${PARSER_API}/v1/patterns`, {
            params: { limit: 100 }
        })
        patterns.value = res.data.patterns
    } catch (err) {
        console.error('Failed to load patterns:', err)
        notify.error("Failed to load patterns")
    } finally {
        patternsLoading.value = false
    }
}

function openAddModal() {
    isEditingPattern.value = false
    patternForm.id = null
    patternForm.bank_name = ''
    patternForm.regex_pattern = ''
    patternForm.field_mapping_str = '{\n  "amount": 1,\n  "merchant": 2,\n  "date": 3\n}'
    patternForm.confidence = 1.0
    patternForm.is_ai_generated = false
    patternError.value = null
    showPatternModal.value = true
}

function openEditModal(pattern: any) {
    try {
        isEditingPattern.value = true
        patternForm.id = pattern.id
        patternForm.bank_name = pattern.bank_name
        patternForm.regex_pattern = pattern.regex_pattern

        // Safely handle field_mapping
        const mapping = pattern.field_mapping || {}
        patternForm.field_mapping_str = JSON.stringify(mapping, null, 2)

        patternForm.confidence = pattern.confidence !== undefined ? pattern.confidence : 1.0
        patternForm.is_ai_generated = !!pattern.is_ai_generated
        patternError.value = null
        showPatternModal.value = true
    } catch (e) {
        console.error("Error opening edit modal:", e)
        notify.error("Failed to open edit modal")
    }
}

function closePatternModal() {
    showPatternModal.value = false
}

async function savePattern() {
    patternSaving.value = true
    patternError.value = null

    try {
        let mapping = {}
        try {
            mapping = JSON.parse(patternForm.field_mapping_str)
        } catch (e) {
            patternError.value = "Invalid JSON in Field Mapping"
            patternSaving.value = false
            return
        }

        const payload = {
            bank_name: patternForm.bank_name,
            regex_pattern: patternForm.regex_pattern,
            field_mapping: mapping,
            confidence: patternForm.confidence
        }

        if (isEditingPattern.value && patternForm.id) {
            await axios.put(`${PARSER_API}/v1/patterns/${patternForm.id}`, payload)
            notify.success("Pattern updated")
        } else {
            await axios.post(`${PARSER_API}/v1/patterns`, payload)
            notify.success("Pattern created")
        }

        closePatternModal()
        loadPatterns()
    } catch (err: any) {
        console.error("Save failed", err)
        patternError.value = err.response?.data?.detail || "Failed to save pattern"
    } finally {
        patternSaving.value = false
    }
}

async function confirmDelete(pattern: any) {
    if (!confirm(`Are you sure you want to delete the pattern for ${pattern.bank_name}?`)) return

    try {
        await axios.delete(`${PARSER_API}/v1/patterns/${pattern.id}`)
        notify.success("Pattern deleted")
        loadPatterns()
    } catch (err) {
        notify.error("Failed to delete pattern")
    }
}

</script>

<style scoped>
.glass-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
}

.ai-layout {
    display: grid;
    grid-template-columns: 1fr 340px;
    gap: 2.5rem;
    align-items: start;
}

@media (max-width: 1024px) {
    .ai-layout {
        grid-template-columns: 1fr;
    }
}

.ai-card {
    background: white;
    border-radius: 1.25rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    overflow: hidden;
}

.ai-card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid #f3f4f6;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #fafafa;
}

.ai-card-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0;
}

.ai-card-body {
    padding: 1.5rem;
}

.ai-playground {
    position: sticky;
    top: 2rem;
}

.activity-log-section {
    background: white;
}

.animate-spin-slow {
    animation: spin 3s linear infinite;
}

@keyframes spin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

.text-muted {
    color: #6b7280;
}

.text-indigo-600 {
    color: #4f46e5;
}

.text-amber-500 {
    color: #f59e0b;
}

.text-emerald-600 {
    color: #10b981;
}

.text-rose-600 {
    color: #ef4444;
}

.btn-icon-circle {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    border: 1px solid #e5e7eb;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
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

/* Tab History Styles */
.compact-table {
    width: 100%;
    border-collapse: collapse;
}

.compact-table th {
    text-align: left;
    padding: 0.75rem 0.5rem;
}

/* Pattern Management Styles */
.pattern-management {
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
}

.section-subtitle {
    font-size: 0.875rem;
    color: #6b7280;
}

.patterns-table {
    width: 100%;
    border-collapse: collapse;
}

.patterns-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid #e5e7eb;
    font-weight: 600;
    font-size: 0.875rem;
    color: #6b7280;
}

.patterns-table td {
    padding: 1rem;
    border-bottom: 1px solid #f3f4f6;
    vertical-align: top;
}

.bank-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    background: #eff6ff;
    color: #1e40af;
    border-radius: 0.375rem;
    font-weight: 600;
    font-size: 0.75rem;
}

.pattern-code {
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    background: #f9fafb;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    display: inline-block;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    border: 1px solid #e5e7eb;
    color: #dc2626;
}

.source-badge {
    padding: 0.1rem 0.4rem;
    border-radius: 0.25rem;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
}

.source-badge.ai {
    background: #ddd6fe;
    color: #5b21b6;
}

.source-badge.manual {
    background: #e0e7ff;
    color: #3730a3;
}

.btn-icon {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.25rem;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.btn-icon:hover {
    opacity: 1;
    background: #f3f4f6;
    border-radius: 0.25rem;
}

.btn-primary {
    background: #4f46e5;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-primary:hover {
    background: #4338ca;
}

.btn-secondary {
    background: white;
    color: #374151;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 600;
    font-size: 0.875rem;
    border: 1px solid #d1d5db;
    cursor: pointer;
}

.btn-secondary:hover {
    background: #f9fafb;
}

/* Modal */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(2px);
}

.modal-content {
    background: white;
    border-radius: 1rem;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    overflow: hidden;
    animation: modalSlide 0.3s ease-out;
}

@keyframes modalSlide {
    from {
        transform: translateY(20px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.modal-header {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f9fafb;
}

.modal-header h3 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 700;
    color: #111827;
}

.btn-close {
    background: none;
    border: none;
    font-size: 1.25rem;
    color: #6b7280;
    cursor: pointer;
}

.modal-body {
    padding: 1.5rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.375rem;
}

.form-input,
.form-textarea {
    width: 100%;
    padding: 0.625rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    transition: border-color 0.2s;
}

.form-input:focus,
.form-textarea:focus {
    outline: none;
    border-color: #4f46e5;
    ring: 2px solid #e0e7ff;
}

.modal-footer {
    padding-top: 1rem;
    margin-top: 1rem;
    border-top: 1px solid #e5e7eb;
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #9ca3af;
}

.empty-icon {
    font-size: 2.5rem;
    display: block;
    margin-bottom: 0.5rem;
}
</style>
