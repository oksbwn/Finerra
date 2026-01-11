<script setup lang="ts">
import { useNotificationStore } from '@/stores/notification'

const store = useNotificationStore()
</script>

<template>
    <div class="toast-container">
        <transition-group name="toast">
            <div 
                v-for="note in store.notifications" 
                :key="note.id" 
                class="toast" 
                :class="note.type"
                @click="store.remove(note.id)"
            >
                <div class="icon" v-if="note.type === 'success'">✓</div>
                <div class="icon" v-if="note.type === 'error'">✕</div>
                <div class="icon" v-if="note.type === 'info'">ℹ</div>
                <div class="content">{{ note.message }}</div>
            </div>
        </transition-group>
    </div>
</template>

<style scoped>
.toast-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    z-index: 9999;
    pointer-events: none; /* Let clicks pass through empty space */
}

.toast {
    pointer-events: auto;
    min-width: 300px;
    padding: 1rem;
    border-radius: 0.5rem;
    background: var(--color-surface);
    color: var(--color-text);
    box-shadow: var(--shadow-md);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    border-left: 4px solid transparent;
}

.toast.success { border-left-color: var(--color-success); }
.toast.error { border-left-color: #ef4444; } /* Red */
.toast.info { border-left-color: var(--color-primary); }

.icon {
    font-weight: bold;
}
.toast.success .icon { color: var(--color-success); }
.toast.error .icon { color: #ef4444; }
.toast.info .icon { color: var(--color-primary); }

/* Animation */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
