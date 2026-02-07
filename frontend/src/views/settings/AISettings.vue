<template>
    <div class="tab-content animate-in">
        <div class="ai-layout max-w-7xl mx-auto">
            <!-- Left Column: Config -->
            <div class="ai-config-section">
                <!-- AI Status Hero -->
                <div class="ai-toggle-banner">
                    <div class="ai-toggle-info">
                        <h3>AI Transaction Safety Net</h3>
                        <p>Automatically extract details when static rules fail.</p>
                    </div>
                    <label class="switch-premium">
                        <input type="checkbox" v-model="aiStore.aiForm.is_enabled">
                        <span class="slider-premium"></span>
                    </label>
                </div>

                <div class="ai-card">
                    <div class="ai-card-header">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2.5" class="text-indigo-600">
                            <path
                                d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                        </svg>
                        <h4 class="ai-card-title">LLM Configuration</h4>
                    </div>
                    <div class="ai-card-body">
                        <form @submit.prevent="aiStore.saveAiSettings" class="space-y-6">
                            <div class="form-row">
                                <div class="ai-input-group half">
                                    <label class="ai-input-label">AI Provider</label>
                                    <CustomSelect v-model="aiStore.aiForm.provider"
                                        :options="[{ label: 'Google Gemini', value: 'gemini' }]" />
                                </div>
                                <div class="ai-input-group half">
                                    <label class="ai-input-label">Model Selection</label>
                                    <div class="flex gap-2">
                                        <CustomSelect v-model="aiStore.aiForm.model_name" :options="aiStore.aiModels"
                                            class="flex-1" />
                                        <button type="button" @click="aiStore.fetchAiModels" class="btn-icon-circle"
                                            title="Refresh Models">🔄</button>
                                    </div>
                                </div>
                            </div>


                            <div class="ai-input-group">
                                <label class="ai-input-label">Secure API Key</label>
                                <input type="password" v-model="aiStore.aiForm.api_key" class="form-input"
                                    :placeholder="aiStore.aiForm.has_api_key ? '••••••••••••••••' : 'Paste API key...'" />
                                <div class="ai-input-helper">
                                    Keys are encrypted at rest. Get your key from the
                                    <a href="https://aistudio.google.com/app/apikey" target="_blank"
                                        class="text-indigo-600 font-bold">Google AI Studio</a>.
                                </div>
                            </div>

                            <div class="ai-input-group">
                                <div class="flex justify-between items-center mb-2">
                                    <label class="ai-input-label m-0">System Instruction</label>
                                    <button type="button" class="text-xs text-indigo-600 font-bold"
                                        @click="resetPrompt">Reset
                                        to Default</button>
                                </div>
                                <textarea v-model="aiStore.aiForm.prompts.parsing" class="form-input font-mono text-xs"
                                    rows="4"></textarea>
                                <p class="ai-input-helper">Define how the AI should structure the extracted
                                    JSON data.</p>
                            </div>

                            <div class="flex justify-end pt-4 border-t border-gray-50">
                                <button type="submit" class="ai-btn-primary">
                                    Save Preferences
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Right Column: Playground -->
            <div class="ai-playground">
                <div class="ai-card">
                    <div class="ai-card-header">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                            stroke-width="2.5" class="text-amber-500">
                            <path d="M12 2L2 7l10 5l10-5l-10-5zM2 17l10 5l10-5M2 12l10 5l10-5" />
                        </svg>
                        <h4 class="ai-card-title">Test Playground</h4>
                    </div>
                    <div class="ai-card-body">
                        <p class="text-[11px] text-muted mb-4 leading-relaxed">
                            Paste a message below to see how the current configuration parses it.
                        </p>

                        <textarea v-model="testMessage" class="form-input text-xs mb-4 bg-gray-50 border-dashed"
                            rows="3" placeholder="e.g. Spent Rs 500 at Amazon..."></textarea>

                        <button @click="handleTest" class="btn-verify width-full mb-6" :disabled="aiStore.isTestingAi">
                            {{ aiStore.isTestingAi ? 'Analyzing...' : 'Test Extraction' }}
                        </button>

                    </div>
                    <div class="ai-console">
                        <div v-if="!aiStore.aiTestResult && !aiStore.isTestingAi" class="text-slate-500 italic">
                            Waiting for data...
                        </div>
                        <div v-if="aiStore.isTestingAi" class="animate-pulse text-indigo-400">
                            > Initializing Gemini provider...
                            <br>> Sending payload...
                        </div>
                        <pre
                            v-if="aiStore.aiTestResult">{{ JSON.stringify(aiStore.aiTestResult.data || aiStore.aiTestResult.message, null, 2) }}</pre>
                    </div>
                </div>

            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'
import { useAiStore } from '@/stores/ai'

const aiStore = useAiStore()


// Use store directly in template for simplicity
const testMessage = ref("Spent Rs 500.50 at Amazon using card ending in 1234 on 14/01/2026")

const resetPrompt = () => {
    aiStore.aiForm.prompts.parsing = "Extract transaction details from the following message. Return JSON with: amount (number), date (DD/MM/YYYY), recipient (string), account_mask (4 digits), ref_id (string or null), type (DEBIT/CREDIT)."
}

const handleTest = () => {
    aiStore.testAi(testMessage.value)
}

onMounted(() => {
    aiStore.fetchAiSettings()
})
</script>

<style scoped>
/* AI Settings Professional Redesign */
.premium-p-8 {
    padding: 2.5rem;
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

.ai-toggle-banner {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.2);
}

.ai-toggle-info h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
}

.ai-toggle-info p {
    margin: 0.25rem 0 0 0;
    font-size: 0.85rem;
    opacity: 0.9;
}

.ai-input-group {
    margin-bottom: 1.5rem;
}

.ai-input-label {
    display: block;
    font-size: 0.8rem;
    font-weight: 600;
    color: #4b5563;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

.ai-input-helper {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.5rem;
    line-height: 1.4;
}

.ai-playground {
    position: sticky;
    top: 2rem;
}

.ai-console {
    background: #0f172a;
    border-radius: 0.75rem;
    padding: 1rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    color: #e2e8f0;
    font-size: 0.75rem;
    min-height: 200px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Switch Redesign */
.switch-premium {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 26px;
}

.switch-premium input {
    opacity: 0;
    width: 0;
    height: 0;
}

.slider-premium {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.3);
    transition: .4s;
    border-radius: 34px;
}

.slider-premium:before {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked+.slider-premium {
    background-color: rgba(255, 255, 255, 0.5);
}

input:checked+.slider-premium:before {
    transform: translateX(24px);
}

.ai-btn-primary {
    background: #4f46e5;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.ai-btn-primary:hover {
    transform: translateY(-1px);
    background: #4338ca;
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

pre {
    word-break: break-all;
    white-space: pre-wrap;
}

.form-row {
    display: flex;
    gap: 1rem;
}

.half {
    flex: 1;
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
    transition: all 0.2s;
}

.btn-icon-circle:hover {
    background: #f3f4f6;
}

.text-indigo-600 {
    color: #4f46e5;
}

.text-amber-500 {
    color: #f59e0b;
}

.text-slate-500 {
    color: #64748b;
}

.text-indigo-400 {
    color: #818cf8;
}

.text-muted {
    color: #6b7280;
}

.width-full {
    width: 100%;
}

.btn-verify {
    padding: 0.5rem 1rem;
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
}

.btn-verify:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.animate-pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: .5;
    }
}
</style>
