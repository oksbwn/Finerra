<template>
    <div class="tab-content animate-in">
        <!-- Search Bar -->
        <div class="account-control-bar mb-6">
            <div class="search-bar-premium no-margin" style="flex: 1; max-width: 300px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="search-icon">
                    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input type="text" v-model="searchQuery" placeholder="Search devices..." class="search-input">
            </div>
            <div class="header-with-badge" style="margin-left: auto; display: flex; align-items: center; gap: 0.75rem;">
                <h3
                    style="margin: 0; font-size: 1rem; font-weight: 700; color: var(--color-text-main); white-space: nowrap;">
                    Mobile Devices</h3>
                <span class="pulse-status-badge" style="background: #ecfdf5; color: #047857;">{{
                    devices.length }} Total</span>
            </div>
        </div>

        <!-- PENDING DEVICES -->
        <div v-if="devices.some(d => !d.is_approved && !d.is_ignored)" class="mb-8">
            <div class="device-section-header">
                <div class="device-section-title">
                    <span>🔔 Pending Approval</span>
                    <span class="badge-count warning">{{devices.filter(d => !d.is_approved &&
                        !d.is_ignored).length}}</span>
                </div>
            </div>
            <div class="devices-grid-premium">
                <div v-for="device in devices.filter(d => !d.is_approved && !d.is_ignored)" :key="device.id"
                    class="device-card-premium unapproved">
                    <div class="dev-header">
                        <div class="dev-icon-wrapper"
                            :class="{ 'android': device.device_name.toLowerCase().includes('pixel') || device.device_name.toLowerCase().includes('samsung'), 'apple': device.device_name.toLowerCase().includes('iphone') || device.device_name.toLowerCase().includes('ipad') }">
                            {{ (device.device_name.toLowerCase().includes('iphone') ||
                                device.device_name.toLowerCase().includes('ipad')) ? '' : '📱' }}
                        </div>
                        <div class="dev-info-main">
                            <h3 class="dev-name">{{ device.device_name }}</h3>
                        </div>
                    </div>
                    <div class="dev-meta">
                        <div class="meta-row">
                            <div class="flex items-center gap-1">
                                <span class="meta-val text-xs">
                                    {{ (getDeviceUser(device.user_id)?.full_name ||
                                        getDeviceUser(device.user_id)?.email || 'Unassigned').split('@')[0]
                                    }}
                                </span>
                                <button @click="openAssignModal(device)" class="btn-icon-tiny">✎</button>
                            </div>
                            <span class="meta-val text-xs text-muted" title="First Seen">
                                🕒 {{ formatDate(device.created_at).day }}
                            </span>
                        </div>
                    </div>
                    <div class="dev-id-footer">
                        <div class="dev-id-row">
                            <span class="dev-id-mono">{{ device.device_id }}</span>
                            <button @click="copyToClipboard(device.device_id)" class="copy-small-btn"
                                title="Copy Full ID">📋</button>
                        </div>
                    </div>
                    <div class="dev-actions">
                        <button @click="toggleDeviceApproval(device)" class="btn-dev primary">Approve</button>
                        <button @click="toggleDeviceIgnored(device, true)" class="btn-dev secondary">Ignore</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- ACTIVE DEVICES -->
        <div class="device-section-header">
            <div class="device-section-title">
                <span>✅ Active Devices</span>
                <span class="badge-count">{{devices.filter(d => d.is_approved).length}}</span>
            </div>
        </div>

        <div class="devices-grid-premium mb-12">
            <div v-for="device in devices.filter(d => d.is_approved)" :key="device.id" class="device-card-premium"
                :class="{
                    'ignored': device.is_ignored,
                    'online-accent': isOnline(device.last_seen_at),
                    'offline-accent': !isOnline(device.last_seen_at)
                }">
                <div class="dev-header">
                    <div class="dev-icon-wrapper"
                        :class="{ 'android': device.device_name.toLowerCase().includes('pixel') || device.device_name.toLowerCase().includes('samsung'), 'apple': device.device_name.toLowerCase().includes('iphone') || device.device_name.toLowerCase().includes('ipad') }">
                        {{ (device.device_name.toLowerCase().includes('iphone') ||
                            device.device_name.toLowerCase().includes('ipad')) ? '' : '📱' }}
                    </div>
                    <div class="dev-info-main">
                        <h3 class="dev-name">{{ device.device_name }}</h3>
                    </div>
                </div>

                <div class="dev-meta">
                    <div class="meta-row">
                        <div class="flex items-center gap-2">
                            <span class="meta-val p-0 text-xs flex items-center gap-1">
                                <img v-if="getDeviceUser(device.user_id)?.avatar?.length > 4"
                                    :src="getDeviceUser(device.user_id)?.avatar" class="w-4 h-4 rounded-full" />
                                {{ getDeviceUser(device.user_id)?.full_name ||
                                    getDeviceUser(device.user_id)?.email || 'Unassigned' }}
                            </span>
                            <button @click="openAssignModal(device)" class="btn-icon-tiny">✎</button>
                        </div>
                        <span class="meta-val text-xs text-muted" title="Last Synchronization">
                            Sync: {{ formatDate(device.last_seen_at || device.created_at).meta }}
                        </span>
                    </div>
                </div>
                <div class="dev-id-footer">
                    <div class="dev-id-row">
                        <span class="dev-id-mono">{{ device.device_id }}</span>
                        <button @click="copyToClipboard(device.device_id)" class="copy-small-btn"
                            title="Copy Full ID">📋</button>
                    </div>
                </div>

                <div class="dev-actions">
                    <button @click="toggleDeviceEnabled(device)" class="btn-dev secondary">
                        {{ device.is_enabled ? 'Pause' : 'Resume' }}
                    </button>
                    <button @click="deleteDeviceRequest(device)" class="btn-dev danger"
                        style="flex: 0 0 2.25rem;">🗑️</button>
                </div>
            </div>

            <div v-if="devices.filter(d => d.is_approved).length === 0" class="empty-placeholder col-span-full">
                <div class="empty-state-content">
                    <div class="empty-icon-large">📱</div>
                    <h3>No Devices Connected</h3>
                    <p>Login from the mobile app to see your devices here.</p>
                </div>
            </div>
        </div>

        <!-- IGNORED DEVICES -->
        <div v-if="devices.some(d => d.is_ignored)" class="mt-8">
            <div class="device-section-header">
                <div class="device-section-title text-muted">
                    <span>🚫 Ignored Devices</span>
                </div>
            </div>
            <div class="devices-grid-premium">
                <div v-for="device in devices.filter(d => d.is_ignored)" :key="device.id"
                    class="device-card-premium ignored">
                    <div class="dev-header">
                        <div class="dev-icon-wrapper">
                            📱
                        </div>
                        <div class="dev-info-main">
                            <h3 class="dev-name text-muted">{{ device.device_name }}</h3>
                            <span class="dev-id-mono">{{ device.device_id }}</span>
                        </div>
                        <div class="status-indicator">Ignored</div>
                    </div>
                    <div class="dev-actions">
                        <button @click="toggleDeviceIgnored(device, false)" class="btn-dev secondary">Restore</button>
                        <button @click="deleteDeviceRequest(device)" class="btn-dev danger">Delete
                            Forever</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- RECENT ACTIVITY LOG -->
        <div
            class="activity-log-section mt-12 bg-white/30 backdrop-blur-md rounded-2xl border border-white/20 p-6 overflow-hidden">
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-4">
                    <h3 class="text-lg font-bold flex items-center gap-2">
                        <span class="bg-indigo-100 text-indigo-600 p-2 rounded-lg text-sm">📋</span>
                        Recent Activity Log
                    </h3>
                    <button v-if="selectedEvents.length > 0" @click="handleBulkDeleteEvents"
                        class="bg-rose-50 text-rose-600 px-3 py-1.5 rounded-lg text-xs font-bold border border-rose-100 transition-all hover:bg-rose-100 flex items-center gap-2 animate-in slide-in-from-left">
                        🗑️ Delete {{ selectedEvents.length }} Selected
                    </button>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-[10px] text-muted font-mono bg-gray-100 px-2 py-1 rounded">Total:
                        {{ eventPagination.total }}</span>
                    <button @click="fetchIngestionEvents(undefined, true)" class="btn-icon-circle"
                        title="Refresh Log">🔄</button>
                </div>
            </div>

            <div class="overflow-x-auto min-h-[300px]">
                <table class="w-full text-left text-sm">
                    <thead class="text-muted border-b border-gray-100">
                        <tr>
                            <th class="pb-3 w-8">
                                <input type="checkbox" @change="toggleSelectAllEvents"
                                    :checked="selectedEvents.length === ingestionEvents.length && ingestionEvents.length > 0"
                                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                            </th>
                            <th class="pb-3 pr-4 font-semibold">Timestamp</th>
                            <th class="pb-3 pr-4 font-semibold">Event</th>
                            <th class="pb-3 pr-4 font-semibold">Device</th>
                            <th class="pb-3 pr-4 font-semibold">Status</th>
                            <th class="pb-3 pr-4 font-semibold">Message</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                        <tr v-for="event in ingestionEvents" :key="event.id"
                            class="hover:bg-white/40 transition-colors group">
                            <td class="py-3">
                                <input type="checkbox" :value="event.id" :checked="selectedEvents.includes(event.id)"
                                    @change="selectedEvents.includes(event.id) ? selectedEvents = selectedEvents.filter(id => id !== event.id) : selectedEvents.push(event.id)"
                                    class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                            </td>
                            <td class="py-3 pr-4 whitespace-nowrap text-xs">
                                {{ formatDate(event.created_at).meta }}
                            </td>
                            <td class="py-3 pr-4">
                                <span
                                    class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-gray-100">
                                    {{ event.event_type.replace('_', ' ') }}
                                </span>
                            </td>
                            <td class="py-3 pr-4 text-xs font-mono text-muted">
                                {{ event.device_id }}
                            </td>
                            <td class="py-3 pr-4">
                                <span :class="{
                                    'text-emerald-600 bg-emerald-50': event.status === 'success',
                                    'text-amber-600 bg-amber-50': event.status === 'warning',
                                    'text-rose-600 bg-rose-50': event.status === 'error',
                                    'text-slate-600 bg-slate-50': event.status === 'skipped'
                                }" class="px-2 py-0.5 rounded-full text-[10px] font-bold">
                                    {{ event.status }}
                                </span>
                            </td>
                            <td class="py-3 pr-4 max-w-xs truncate text-xs" :title="event.message">
                                {{ event.message }}
                            </td>
                        </tr>
                        <tr v-if="ingestionEvents.length === 0">
                            <td colspan="6" class="py-12 text-center text-muted italic">
                                <div class="flex flex-col items-center gap-2">
                                    <span class="text-2xl">🔍</span>
                                    No activity logs found.
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <!-- Pagination Controls -->
            <div v-if="eventPagination.total > eventPagination.limit"
                class="mt-6 flex items-center justify-between border-t border-gray-100 pt-6">
                <span class="text-[10px] text-muted">
                    Showing {{ eventPagination.skip + 1 }} to {{ Math.min(eventPagination.skip +
                        eventPagination.limit, eventPagination.total) }} of {{ eventPagination.total }}
                </span>
                <div class="flex items-center gap-1">
                    <button @click="eventPagination.skip -= eventPagination.limit; fetchIngestionEvents()"
                        :disabled="eventPagination.skip === 0"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Previous
                    </button>
                    <button @click="eventPagination.skip += eventPagination.limit; fetchIngestionEvents()"
                        :disabled="eventPagination.skip + eventPagination.limit >= eventPagination.total"
                        class="p-1 px-3 rounded-md bg-white border border-gray-200 text-xs font-bold disabled:opacity-50 hover:bg-gray-50 transition-all">
                        Next
                    </button>
                </div>
            </div>
        </div>

        <!-- Device Assignment Modal -->
        <div v-if="showDeviceAssignModal" class="modal-overlay-global">
            <div class="modal-global glass">
                <div class="modal-header">
                    <h2 class="modal-title">Assign Device</h2>
                    <button class="btn-icon-circle" @click="showDeviceAssignModal = false">✕</button>
                </div>

                <form @submit.prevent="confirmAssignUser" class="form-compact p-6">
                    <div class="form-group mb-4">
                        <label class="form-label">Display Name</label>
                        <input v-model="editDeviceName" class="form-input" placeholder="e.g. iPhone 15 Pro" />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Assign to Member</label>
                        <CustomSelect v-model="selectedAssignUserId"
                            :options="familyMembers.map(m => ({ label: m.full_name || m.email, value: m.id }))"
                            placeholder="Select Owner" />
                    </div>

                    <div class="modal-footer">
                        <button type="button" @click="showDeviceAssignModal = false"
                            class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary-glow">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Device Delete Confirmation -->
        <div v-if="showDeviceDeleteConfirm" class="modal-overlay-global">
            <div class="modal-global glass alert max-w-md">
                <div class="modal-icon-header danger"
                    style="font-size: 2rem; display: flex; justify-content: center; padding: 1rem;">🗑️</div>
                <h2 class="modal-title text-center">Remove Device?</h2>
                <div class="alert-info-box mb-6 p-4 bg-red-50 text-red-700 rounded-lg mx-6 text-center">
                    <p>Permanently remove <strong>{{ deviceToDelete?.device_name }}</strong>?</p>
                </div>
                <div class="modal-footer">
                    <button @click="showDeviceDeleteConfirm = false" class="btn-secondary">Cancel</button>
                    <button @click="confirmDeleteDevice" class="btn-danger-glow"
                        style="background: #ef4444; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; border: none; font-weight: 600;">Yes,
                        Delete</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { mobileApi, financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import CustomSelect from '@/components/CustomSelect.vue'

const notify = useNotificationStore()

// --- Internal State ---
const devices = ref<any[]>([])
const familyMembers = ref<any[]>([])
const searchQuery = ref('')
const loading = ref(false)

// Modal State
const showDeviceAssignModal = ref(false)
const deviceToAssign = ref<any>(null)
const selectedAssignUserId = ref<string | null>(null)
const editDeviceName = ref('')
const showDeviceDeleteConfirm = ref(false)
const deviceToDelete = ref<any>(null)



// Ingestion Events State
const ingestionEvents = ref<any[]>([])
const eventPagination = ref({ total: 0, limit: 10, skip: 0 })
const selectedEvents = ref<string[]>([])
const isDeletingEvents = ref(false)

function formatDate(dateStr: string) {
    if (!dateStr) return { day: 'N/A', meta: '' }
    const d = new Date(dateStr)
    return {
        day: d.toLocaleDateString(),
        meta: d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        full: d.toLocaleString()
    }
}

const getDeviceUser = (userId: string) => {
    if (!userId) return null
    return familyMembers.value.find(u => u.id === userId)
}

const isOnline = (dateStr: string) => {
    if (!dateStr) return false
    const lastSeen = new Date(dateStr).getTime()
    const now = new Date().getTime()
    return (now - lastSeen) < (10 * 60 * 1000) // 10 minutes
}

const fetchIngestionEvents = async (deviceId?: string, resetSkip = false) => {
    try {
        if (resetSkip) eventPagination.value.skip = 0
        const res = await financeApi.getIngestionEvents({
            limit: eventPagination.value.limit,
            skip: eventPagination.value.skip,
            device_id: deviceId
        })
        ingestionEvents.value = res.data.items
        eventPagination.value.total = res.data.total
        selectedEvents.value = []
    } catch (e) {
        console.error("Failed to fetch events", e)
    }
}

const toggleSelectAllEvents = () => {
    if (selectedEvents.value.length === ingestionEvents.value.length) {
        selectedEvents.value = []
    } else {
        selectedEvents.value = ingestionEvents.value.map(e => e.id)
    }
}

const fetchData = async () => {
    try {
        const [devicesRes, usersRes] = await Promise.all([
            mobileApi.getDevices(),
            financeApi.getUsers()
        ])
        devices.value = devicesRes.data
        familyMembers.value = usersRes.data
    } catch (e) {
        console.error("Failed to fetch device settings", e)
        notify.error("Failed to load device settings")
    }
}

onMounted(() => {
    fetchIngestionEvents()
    fetchData()
})

function openAssignModal(device: any) {
    deviceToAssign.value = device
    selectedAssignUserId.value = device.user_id || null
    editDeviceName.value = device.device_name || ''
    showDeviceAssignModal.value = true
}

async function confirmAssignUser() {
    if (!deviceToAssign.value) return
    try {
        await mobileApi.updateDevice(deviceToAssign.value.id, {
            device_name: editDeviceName.value,
            user_id: selectedAssignUserId.value
        })
        notify.success("Device settings updated")
        showDeviceAssignModal.value = false
        fetchData()
    } catch (e: any) {
        notify.error("Failed to update device")
    }
}

const toggleDeviceApproval = async (device: any) => {
    try {
        await mobileApi.toggleApproval(device.id, !device.is_approved)
        fetchData()
    } catch (e) {
        notify.error("Failed to toggle device approval")
    }
}

const toggleDeviceIgnored = async (device: any, ignored: boolean) => {
    try {
        await mobileApi.toggleIgnored(device.id, ignored)
        notify.success(ignored ? "Device ignored" : "Device restored")
        fetchData()
    } catch (e) {
        notify.error("Failed to update status")
    }
}

const toggleDeviceEnabled = async (device: any) => {
    try {
        await mobileApi.toggleEnabled(device.id, !device.is_enabled)
        notify.success(device.is_enabled ? "Device ingestion disabled" : "Device ingestion enabled")
        fetchData()
    } catch (e) {
        notify.error("Failed to update device status")
    }
}

const deleteDeviceRequest = (device: any) => {
    deviceToDelete.value = device
    showDeviceDeleteConfirm.value = true
}

const confirmDeleteDevice = async () => {
    if (!deviceToDelete.value) return
    try {
        await mobileApi.deleteDevice(deviceToDelete.value.id)
        notify.success("Device permanently removed")
        showDeviceDeleteConfirm.value = false
        fetchData()
    } catch (e) {
        notify.error("Failed to delete device")
    } finally {
        deviceToDelete.value = null
    }
}

const handleBulkDeleteEvents = async () => {
    if (selectedEvents.value.length === 0) return
    isDeletingEvents.value = true
    try {
        await financeApi.bulkDeleteEvents(selectedEvents.value)
        notify.success(`Deleted ${selectedEvents.value.length} events`)
        fetchIngestionEvents(undefined, true)
    } catch (e) {
        notify.error("Failed to delete events")
    } finally {
        isDeletingEvents.value = false
    }
}

const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    notify.success("Device ID copied!")
}
</script>

<style scoped>
/* ==================== PREMIUM DEVICE CARDS ==================== */
.device-section-header {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #f3f4f6;
}

.device-section-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.9375rem;
    font-weight: 700;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-count {
    font-size: 0.75rem;
    padding: 2px 8px;
    background: #e5e7eb;
    color: #4b5563;
    border-radius: 9999px;
    font-weight: 700;
}

.badge-count.warning {
    background: #fffbeb;
    color: #d97706;
}

.devices-grid-premium {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 0.75rem;
}

.device-card-premium {
    background: white;
    border: 1px solid #f1f5f9;
    border-radius: 0.5rem;
    padding: 0.625rem;
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.device-card-premium:hover {
    border-color: #4f46e5;
    box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.08);
}

.device-card-premium.unapproved {
    background: #fffbeb;
    border-top: 3px solid #f59e0b;
}

.device-card-premium.ignored {
    opacity: 0.6;
    background: #f8fafc;
}

.dev-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.dev-icon-wrapper {
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
    background: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

.dev-icon-wrapper.apple {
    background: #e0f2fe;
    color: #0284c7;
}

.dev-icon-wrapper.android {
    background: #dcfce7;
    color: #059669;
}

.dev-info-main {
    flex: 1;
    min-width: 0;
}

.dev-name {
    font-size: 0.9375rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.dev-id-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.625rem;
    color: #64748b;
    background: white;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    word-break: break-all;
    flex: 1;
}

.dev-id-footer {
    padding: 0.375rem 0.5rem;
    background: #f8fafc;
    border-radius: 0.375rem;
    border: 1px solid #f1f5f9;
}

.dev-id-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
}

.device-card-premium.online-accent {
    border-top: 3px solid #10b981;
}

.device-card-premium.offline-accent {
    border-top: 3px solid #ef4444;
}

.meta-val {
    color: #1e293b;
    font-weight: 500;
}

.meta-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.dev-actions {
    display: flex;
    gap: 0.375rem;
    margin-top: 0.25rem;
}

.btn-dev {
    flex: 1;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.375rem 0.5rem;
    border-radius: 0.375rem;
    border: 1px solid transparent;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn-dev.primary {
    background: #4f46e5;
    color: white;
}

.btn-dev.primary:hover {
    background: #4338ca;
}

.btn-dev.secondary {
    background: white;
    color: #475569;
    border-color: #e2e8f0;
}

.btn-dev.secondary:hover {
    border-color: #cbd5e1;
    background: #f8fafc;
}

.btn-dev.danger {
    background: #fff1f2;
    color: #e11d48;
    border-color: #fecdd3;
}

.btn-dev.danger:hover {
    background: #ffe4e6;
}

.copy-small-btn {
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 0.8rem;
    opacity: 0.6;
    transition: opacity 0.2s;
    padding: 2px;
}

.copy-small-btn:hover {
    opacity: 1;
    color: #4f46e5;
}

.btn-icon-tiny {
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 0.75rem;
    color: #4f46e5;
    padding: 2px;
    line-height: 1;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.btn-icon-tiny:hover {
    opacity: 1;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #6b7280;
    padding: 0.25rem 0.625rem;
    border-radius: 9999px;
    background: #f3f4f6;
}

.activity-log-section {
    background: white;
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

.account-control-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.search-bar-premium {
    position: relative;
}

.search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
}

.search-input {
    width: 100%;
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
}

.search-input:focus {
    outline: none;
    border-color: #4f46e5;
}

.pulse-status-badge {
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 9999px;
    font-weight: 700;
}
</style>
