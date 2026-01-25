<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
    modelValue: any
    options: Array<{ label: string, value: any }>
    placeholder?: string
    label?: string
    required?: boolean
}>()

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

const selectedLabel = computed(() => {
    const opt = props.options.find(o => o.value === props.modelValue)
    return opt ? opt.label : (props.placeholder || 'Select an option')
})

function toggle() {
    isOpen.value = !isOpen.value
}

function select(value: string | number) {
    emit('update:modelValue', value)
    isOpen.value = false
}

// Close when clicking outside
function handleClickOutside(event: MouseEvent) {
    if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
        isOpen.value = false
    }
}

onMounted(() => { document.addEventListener('click', handleClickOutside) })
onUnmounted(() => { document.removeEventListener('click', handleClickOutside) })
</script>

<template>
    <div class="custom-select-container" ref="containerRef">
        <div class="select-trigger form-input" :class="{ 'open': isOpen, 'placeholder': !modelValue }" @click="toggle">
            <span>{{ selectedLabel }}</span>
            <span class="chevron">▼</span>
        </div>

        <transition name="fade">
            <div v-if="isOpen" class="options-container">
                <div v-for="opt in options" :key="opt.value" class="option-item"
                    :class="{ 'selected': opt.value === modelValue }" @click="select(opt.value)">
                    {{ opt.label }}
                    <span v-if="opt.value === modelValue" class="check">✓</span>
                </div>
            </div>
        </transition>
    </div>
</template>

<style scoped>
.custom-select-container {
    position: relative;
    width: 100%;
}

.select-trigger {
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
}

.select-trigger.placeholder {
    color: var(--color-text-muted);
}

.chevron {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    transition: transform 0.2s;
}

.select-trigger.open .chevron {
    transform: rotate(180deg);
}

.options-container {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    margin-top: 0.5rem;
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    box-shadow: var(--shadow-lg);
    z-index: 50;
    max-height: 250px;
    overflow-y: auto;
    padding: 0.25rem;
}

.option-item {
    padding: 0.5rem 0.75rem;
    cursor: pointer;
    border-radius: 0.25rem;
    color: var(--color-text-main);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.95rem;
}

.option-item:hover {
    background: var(--color-primary-light);
    color: var(--color-primary-dark);
}

.option-item.selected {
    background: var(--color-primary-light);
    color: var(--color-primary);
    font-weight: 500;
}

.check {
    font-size: 0.8rem;
}

/* Scrollbar */
.options-container::-webkit-scrollbar {
    width: 6px;
}

.options-container::-webkit-scrollbar-track {
    background: transparent;
}

.options-container::-webkit-scrollbar-thumb {
    background: var(--color-border);
    border-radius: 3px;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.15s ease, transform 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
    transform: translateY(-5px);
}
</style>
