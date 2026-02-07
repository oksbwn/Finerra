<template>
    <div class="tab-content animate-in">
        <div class="privacy-card">
            <div class="privacy-header">
                <div class="privacy-icon">🛡️</div>
                <h2 class="privacy-title">Privacy & Anonymity</h2>
                <p class="privacy-subtitle">Adjust how sensitive financial data is displayed across the
                    application.</p>
            </div>

            <div class="form-group">
                <label class="form-label">Masking Factor</label>
                <div class="input-group-flex">
                    <input type="number" v-model.number="localMaskingFactor" min="1" class="form-input"
                        placeholder="1" />
                    <button @click="handleSave" class="btn-primary-glow">Save</button>
                </div>
                <span class="input-hint">Divide all amounts by this number (e.g., 1, 10, 100)</span>
            </div>

            <div class="info-box">
                <span class="info-icon">💡</span>
                <div class="info-content">
                    <h4 class="info-title">How it works</h4>
                    <p class="info-text">
                        If you set the factor to <strong>10</strong>, a transaction of
                        <strong>₹10,000</strong> will be displayed as <strong>₹1,000</strong>.
                        This allows you to share your screen or demo the app without revealing actual
                        values.
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useNotificationStore } from '@/stores/notification'

const settingsStore = useSettingsStore()
const notify = useNotificationStore()

const localMaskingFactor = ref(settingsStore.maskingFactor)

// Sync local state when store changes (optional, but good if changed elsewhere)
watch(() => settingsStore.maskingFactor, (newVal) => {
    localMaskingFactor.value = newVal
})

function handleSave() {
    settingsStore.maskingFactor = localMaskingFactor.value
    notify.success("Settings saved")
}
</script>

<style scoped>
.privacy-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
}

.privacy-header {
    text-align: center;
    margin-bottom: 2rem;
}

.privacy-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.privacy-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.5rem;
}

.privacy-subtitle {
    color: #6b7280;
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #4b5563;
    margin-bottom: 0.5rem;
}

.input-group-flex {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.form-input {
    flex: 1;
    padding: 0.625rem 0.875rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    font-size: 0.875rem;
}

.btn-primary-glow {
    padding: 0.625rem 1.25rem;
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
}

.input-hint {
    display: block;
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.5rem;
}

.info-box {
    background: #f3f4f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-top: 1.5rem;
    display: flex;
    align-items: start;
    gap: 0.75rem;
}

.info-icon {
    font-size: 1.25rem;
}

.info-title {
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.25rem;
}

.info-text {
    font-size: 0.875rem;
    color: #4b5563;
    line-height: 1.5;
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
</style>
