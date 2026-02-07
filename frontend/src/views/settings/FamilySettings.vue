<template>
    <div class="tab-content animate-in">
        <!-- Family Hero -->
        <div class="family-hero mb-8" v-if="tenants.length > 0">
            <div class="fh-main">
                <div class="fh-avatar-stack">
                    <div v-for="m in familyMembers.slice(0, 3)" :key="m.id" class="stack-avatar">
                        {{ m.avatar || '👤' }}
                    </div>
                </div>
                <div class="fh-text">
                    <h2 class="fh-title">
                        {{ tenants[0].name }}
                        <button @click="openRenameTenantModal(tenants[0])" class="btn-icon-subtle"
                            title="Rename Family">✏️</button>
                    </h2>
                    <p class="fh-subtitle">{{ familyMembers.length }} Members • {{ accounts.length }}
                        Accounts Tracked</p>
                </div>
            </div>
        </div>

        <div class="settings-grid">
            <div v-for="member in familyMembers" :key="member.id" class="glass-card member-profile-card">
                <button @click="openEditMemberModal(member)" class="edit-profile-btn" title="Edit Profile">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
                    </svg>
                </button>

                <div class="profile-header">
                    <div class="profile-avatar-wrapper">
                        <div class="gradient-avatar" :class="getRoleColorClass(member.role)">
                            {{ member.avatar || '👤' }}
                        </div>
                        <div v-if="currentUser && currentUser.id === member.id" class="you-indicator"
                            title="That's You!">
                            👋
                        </div>
                    </div>
                    <h3 class="profile-name">{{ member.full_name || 'Anonymous' }}</h3>
                    <p class="profile-email">{{ member.email }}</p>
                    <div class="role-pill" :class="member.role.toLowerCase()">
                        {{ getRoleIcon(member.role) }} {{ member.role }}
                    </div>
                </div>

                <div class="profile-stats">
                    <div class="stat-item">
                        <span class="stat-val">{{ getMemberAccountCount(member.id) }}</span>
                        <span class="stat-lbl">Accounts</span>
                    </div>
                </div>
            </div>

            <!-- Add New Member Card -->
            <div class="glass-card add-account-card" @click="openAddMemberModal">
                <div class="add-icon-circle">+</div>
                <span>Add Family Member</span>
            </div>
        </div>

        <!-- Add/Edit Family Member Modal -->
        <div v-if="showMemberModal" class="modal-overlay-global">
            <div class="modal-global glass">
                <div class="modal-header">
                    <h2 class="modal-title">{{ isEditingMember ? 'Edit Profile' : 'Add Family Member' }}</h2>
                    <button class="btn-icon-circle" @click="showMemberModal = false">✕</button>
                </div>

                <form @submit.prevent="handleMemberSubmit" class="form-compact">
                    <div class="avatar-picker-grid">
                        <div v-for="a in ['👨‍💼', '👩‍💼', '👶', '👴', '👵', '👨‍🎓', '👩‍🎓', '🐶']" :key="a"
                            class="avatar-option" :class="{ active: memberForm.avatar === a }"
                            @click="memberForm.avatar = a">
                            {{ a }}
                        </div>
                        <input v-model="memberForm.avatar" class="form-input emoji-input-sm" maxlength="2"
                            placeholder="🔍" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Full Name</label>
                        <input v-model="memberForm.full_name" class="form-input" required
                            placeholder="e.g. Sarah Smith" />
                    </div>

                    <div class="form-row">
                        <div class="form-group half">
                            <label class="form-label">Date of Birth</label>
                            <input type="date" v-model="memberForm.dob" class="form-input" />
                        </div>
                        <div class="form-group half">
                            <label class="form-label">PAN Number</label>
                            <div style="position: relative;">
                                <input :type="showPan ? 'text' : 'password'" v-model="memberForm.pan_number"
                                    class="form-input" style="padding-right: 2.5rem;" placeholder="ABCDE1234F"
                                    maxlength="10" />
                                <button type="button" @click="showPan = !showPan"
                                    style="position: absolute; right: 0.5rem; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; opacity: 0.5;">
                                    {{ showPan ? '🙈' : '👁️' }}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Email Address</label>
                        <input v-model="memberForm.email" class="form-input" :disabled="isEditingMember" type="email"
                            required placeholder="sarah@example.com" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Password {{ isEditingMember ? '(Leave empty to keep current)'
                            : ''
                            }}</label>
                        <input v-model="memberForm.password" class="form-input" type="password"
                            :required="!isEditingMember" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Role / Permissions</label>
                        <CustomSelect v-model="memberForm.role" :options="[
                            { label: 'Admin (See everything)', value: 'OWNER' },
                            { label: 'Adult (Edit access)', value: 'ADULT' },
                            { label: 'Child (Watch only / Restricted)', value: 'CHILD' },
                            { label: 'Guest', value: 'GUEST' }
                        ]" />
                    </div>

                    <div class="modal-footer">
                        <button type="button" @click="showMemberModal = false" class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary-glow">
                            {{ isEditingMember ? 'Save Changes' : 'Add Member' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Tenant Rename Modal -->
        <div v-if="showTenantModal" class="modal-overlay-global">
            <div class="modal-global glass">
                <div class="modal-header">
                    <h2 class="modal-title">Rename Family Circle</h2>
                    <button class="btn-icon-circle" @click="showTenantModal = false">✕</button>
                </div>

                <form @submit.prevent="handleRenameTenant" class="form-compact">
                    <div class="form-group">
                        <label class="form-label">New Family Name</label>
                        <input v-model="tenantForm.name" class="form-input" required placeholder="e.g. The Smiths" />
                    </div>
                    <div class="modal-footer">
                        <button type="button" @click="showTenantModal = false" class="btn-secondary">Cancel</button>
                        <button type="submit" class="btn-primary-glow">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'
import CustomSelect from '@/components/CustomSelect.vue'

const notify = useNotificationStore()

// --- Internal State ---
const tenants = ref<any[]>([])
const familyMembers = ref<any[]>([])
const accounts = ref<any[]>([])
const currentUser = ref<any>(null)
const loading = ref(false)

const showMemberModal = ref(false)
const isEditingMember = ref(false)
const memberForm = ref({
    id: '',
    email: '',
    full_name: '',
    password: '',
    role: 'ADULT',
    avatar: '👨‍💼',
    dob: '',
    pan_number: ''
})
const showPan = ref(false)

const showTenantModal = ref(false)
const tenantForm = ref({ id: '', name: '' })

// --- Computed ---


const getMemberAccountCount = (memberId: string) => {
    return accounts.value.filter(a => a.owner_id === memberId).length
}

const getRoleIcon = (role: string) => {
    switch (role) {
        case 'OWNER': return '👑'
        case 'ADULT': return '🛡️'
        case 'CHILD': return '🧸'
        case 'GUEST': return '👀'
        default: return '👤'
    }
}

const getRoleColorClass = (role: string) => {
    switch (role) {
        case 'OWNER': return 'ring-gold'
        case 'ADULT': return 'ring-blue'
        case 'CHILD': return 'ring-green'
        default: return 'ring-gray'
    }
}

// --- Fetch Data ---
async function fetchData() {
    loading.value = true
    try {
        const [tenantsRes, usersRes, accountsRes, meRes] = await Promise.all([
            financeApi.getTenants(),
            financeApi.getUsers(),
            financeApi.getAccounts(),
            financeApi.getMe()
        ])
        tenants.value = tenantsRes.data
        familyMembers.value = usersRes.data
        accounts.value = accountsRes.data
        currentUser.value = meRes.data
    } catch (e) {
        console.error("Failed to fetch family settings", e)
        notify.error("Failed to load family settings")
    } finally {
        loading.value = false
    }
}

// Logic
function openRenameTenantModal(tenant: any) {
    tenantForm.value = { id: tenant.id, name: tenant.name }
    showTenantModal.value = true
}

async function handleRenameTenant() {
    if (!tenantForm.value.name) return
    try {
        await financeApi.updateTenant(tenantForm.value.id, { name: tenantForm.value.name })
        notify.success("Family name updated")
        showTenantModal.value = false
        fetchData()
    } catch (err) {
        notify.error("Rename failed")
    }
}

function openAddMemberModal() {
    isEditingMember.value = false
    memberForm.value = {
        id: '',
        email: '',
        full_name: '',
        password: '',
        role: 'ADULT' as any,
        avatar: '👨‍💼',
        dob: '',
        pan_number: ''
    }
    showPan.value = false
    showMemberModal.value = true
}

function openEditMemberModal(member: any) {
    isEditingMember.value = true
    memberForm.value = {
        id: member.id,
        email: member.email,
        full_name: member.full_name || '',
        password: '',
        role: member.role,
        avatar: member.avatar || '👤',
        dob: member.dob || '',
        pan_number: member.pan_number || ''
    }
    showPan.value = false
    showMemberModal.value = true
}

async function handleMemberSubmit() {
    try {
        if (isEditingMember.value) {
            await financeApi.updateUser(memberForm.value.id, {
                full_name: memberForm.value.full_name,
                avatar: memberForm.value.avatar,
                role: memberForm.value.role,
                dob: memberForm.value.dob || undefined,
                pan_number: memberForm.value.pan_number || undefined,
                password: memberForm.value.password || undefined
            })
            notify.success("Member updated")
        } else {
            await financeApi.createUser(memberForm.value)
            notify.success("Member added successfully")
        }
        showMemberModal.value = false
        fetchData()
    } catch (err: any) {
        notify.error(err.response?.data?.detail || "Action failed")
    }
}

onMounted(() => {
    fetchData()
})
</script>

<style scoped>
/* ==================== FAMILY HERO ==================== */
.family-hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 1rem;
    padding: 2rem;
    color: white;
    box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
    position: relative;
    overflow: hidden;
}

.family-hero::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
    transform: translate(30%, -30%);
}

.fh-main {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    z-index: 1;
}

.fh-avatar-stack {
    display: flex;
    padding-left: 0.75rem;
}

.stack-avatar {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: #eef2ff;
    border: 3px solid rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-left: -0.75rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.fh-text {
    flex: 1;
}

.fh-title {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0 0 0.25rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: white;
}

.fh-subtitle {
    margin: 0;
    opacity: 0.9;
    font-size: 0.875rem;
    font-weight: 500;
}

.btn-icon-subtle {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    color: white;
}

.btn-icon-subtle:hover {
    background: rgba(255, 255, 255, 0.4);
    transform: scale(1.1);
}

/* ==================== GRID & CARDS ==================== */
.settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.5rem;
}

.glass-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    padding: 1.5rem;
    position: relative;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.1);
    border-color: #cbd5e1;
}

/* ==================== MEMBER PROFILE CARD ==================== */
.member-profile-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.edit-profile-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: transparent;
    border: none;
    color: #9ca3af;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: all 0.2s;
}

.edit-profile-btn:hover {
    color: #4f46e5;
    background: #eef2ff;
}

.profile-avatar-wrapper {
    position: relative;
    margin-bottom: 1rem;
}

.gradient-avatar {
    width: 5rem;
    height: 5rem;
    border-radius: 1.5rem;
    background: #f3f4f6;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    border: 4px solid white;
    box-shadow: 0 4px 10px -2px rgba(0, 0, 0, 0.1);
}

/* Role Rings */
.ring-gold {
    border-color: #fbbf24;
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
}

.ring-blue {
    border-color: #60a5fa;
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.ring-green {
    border-color: #4ade80;
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.ring-gray {
    border-color: #9ca3af;
}

.you-indicator {
    position: absolute;
    bottom: -0.5rem;
    right: -0.5rem;
    background: white;
    border-radius: 50%;
    width: 1.75rem;
    height: 1.75rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border: 2px solid #e5e7eb;
}

.profile-name {
    font-size: 1.125rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.25rem 0;
}

.profile-email {
    font-size: 0.8125rem;
    color: #6b7280;
    margin: 0 0 0.75rem 0;
}

.role-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.role-pill.owner {
    background: #fff7ed;
    color: #c2410c;
}

.role-pill.adult {
    background: #eff6ff;
    color: #1d4ed8;
}

.role-pill.child {
    background: #f0fdf4;
    color: #15803d;
}

.role-pill.guest {
    background: #f9fafb;
    color: #4b5563;
}

.profile-stats {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;
    width: 100%;
    display: flex;
    justify-content: center;
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-val {
    font-size: 1.25rem;
    font-weight: 800;
    color: #111827;
}

.stat-lbl {
    font-size: 0.75rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
}

/* ==================== ADD CARD ==================== */
.add-account-card {
    border: 2px dashed #e5e7eb;
    background: #f9fafb;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    cursor: pointer;
    min-height: 280px;
    color: #6b7280;
    font-weight: 600;
}

.add-account-card:hover {
    border-color: #4f46e5;
    background: #eef2ff;
    color: #4f46e5;
    transform: translateY(-4px);
}

.add-icon-circle {
    width: 3.5rem;
    height: 3.5rem;
    border-radius: 50%;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.75rem;
    color: #9ca3af;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: all 0.2s;
}

.add-account-card:hover .add-icon-circle {
    background: #4f46e5;
    color: white;
    transform: scale(1.1) rotate(90deg);
}

/* Modal Foundations duplicated here for scoping or use global classes */
.avatar-picker-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
    gap: 0.5rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.75rem;
}

.avatar-option {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    cursor: pointer;
    border-radius: 0.5rem;
    border: 2px solid transparent;
    transition: all 0.2s;
}

.avatar-option:hover {
    background: white;
    transform: scale(1.1);
}

.avatar-option.active {
    border-color: #4f46e5;
    background: white;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.1);
}

.emoji-input-sm {
    text-align: center;
    padding: 0 !important;
    font-size: 1.25rem;
    width: 100%;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    padding-top: 1.5rem;
    border-top: 1px solid #f3f4f6;
    margin-top: 1.5rem;
}
</style>
