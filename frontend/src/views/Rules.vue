<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import { financeApi } from '@/api/client'
import CustomSelect from '@/components/CustomSelect.vue'
import { useNotificationStore } from '@/stores/notification'
import { DEFAULT_CATEGORIES } from '@/constants'

const notify = useNotificationStore()

const activeTab = ref('rules')
const categories = ref<any[]>([])

const rules = ref<any[]>([])
const suggestions = ref<any[]>([])
const loading = ref(true) // Loading state shared
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const ruleToDelete = ref<string | null>(null)

const isEditing = ref(false)
const editingId = ref<string | null>(null)
const newRule = ref({
    name: '',
    category: '',
    keywords: ''
})

// Category State
const showCategoryModal = ref(false)
const showDeleteCategoryConfirm = ref(false)
const categoryToDelete = ref<string | null>(null)
const isEditingCategory = ref(false)
const editingCategoryId = ref<string | null>(null)
const newCategory = ref({ name: '', icon: '🏷️' })

const categoryOptions = computed(() => {
    // Transform backend categories to select options
    return categories.value.map(c => ({
        label: `${c.icon} ${c.name}`,
        value: c.name // We still store name as string in transactions
    }))
})

async function fetchData() {
    loading.value = true
    try {
        const [rulesRes, suggestionsRes, catsRes] = await Promise.all([
            financeApi.getRules(),
            financeApi.getRuleSuggestions(),
            financeApi.getCategories()
        ])
        rules.value = rulesRes.data
        suggestions.value = suggestionsRes.data
        categories.value = catsRes.data
    } catch (err) {
        console.error("Failed to fetch data", err)
        notify.error("Failed to load data")
    } finally {
        loading.value = false
    }
}

// ... Rule functions (deleteRule, confirmDelete, etc) ...

// --- Category Functions ---
function openAddCategoryModal() {
    isEditingCategory.value = false
    editingCategoryId.value = null
    newCategory.value = { name: '', icon: '🏷️' }
    showCategoryModal.value = true
}

function openEditCategoryModal(cat: any) {
    isEditingCategory.value = true
    editingCategoryId.value = cat.id
    newCategory.value = { name: cat.name, icon: cat.icon }
    showCategoryModal.value = true
}

async function saveCategory() {
    if (!newCategory.value.name) return
    try {
        if (isEditingCategory.value && editingCategoryId.value) {
            await financeApi.updateCategory(editingCategoryId.value, newCategory.value)
            notify.success("Category updated")
        } else {
            await financeApi.createCategory(newCategory.value)
            notify.success("Category created")
        }
        showCategoryModal.value = false
        fetchData()
    } catch (err) {
        notify.error("Failed to save category")
    }
}

async function deleteCategory(id: string) {
    categoryToDelete.value = id
    showDeleteCategoryConfirm.value = true
}

async function confirmDeleteCategory() {
    if (!categoryToDelete.value) return
    try {
        await financeApi.deleteCategory(categoryToDelete.value)
        notify.success("Category deleted")
        fetchData()
    } catch (err) {
        notify.error("Failed to delete category")
    } finally {
        showDeleteCategoryConfirm.value = false
    }
}

onMounted(() => {
    fetchData()
})
// End of script logic

// --- Rule Functions ---
async function deleteRule(id: string) {
    ruleToDelete.value = id
    showDeleteConfirm.value = true
}

async function confirmDelete() {
    if (!ruleToDelete.value) return
    try {
        await financeApi.deleteRule(ruleToDelete.value)
        notify.success("Rule deleted")
        fetchData()
    } catch (err) {
        notify.error("Failed to delete rule")
    } finally {
        showDeleteConfirm.value = false
        ruleToDelete.value = null
    }
}

function openAddModal() {
    isEditing.value = false
    editingId.value = null
    newRule.value = { name: '', category: '', keywords: '' }
    showModal.value = true
}

function openEditModal(rule: any) {
    isEditing.value = true
    editingId.value = rule.id
    newRule.value = {
        name: rule.name,
        category: rule.category,
        keywords: rule.keywords.join(', ')
    }
    showModal.value = true
}

async function approveSuggestion(s: any) {
    try {
        await financeApi.createRule({
            name: s.name,
            category: s.category,
            keywords: s.keywords,
            priority: 5
        })
        notify.success(`Rule for "${s.name}" approved!`)
        fetchData() // Refresh
    } catch (err) {
        console.error(err)
        notify.error("Failed to approve rule")
    }
}

async function saveRule() {
    if (!newRule.value.name || !newRule.value.category || !newRule.value.keywords) return
    
    const keywordList = newRule.value.keywords.split(',').map(k => k.trim())
    const payload = {
        ...newRule.value,
        keywords: keywordList,
        priority: 10
    }

    try {
        if (isEditing.value && editingId.value) {
             await financeApi.updateRule(editingId.value, payload)
             notify.success("Rule updated successfully!")
        } else {
             await financeApi.createRule(payload)
             notify.success("New rule created successfully!")
        }
        
        showModal.value = false
        newRule.value = { name: '', category: '', keywords: '' }
        fetchData()
    } catch (err) {
        console.error(err)
        notify.error("Failed to save rule")
    }
}

onMounted(() => {
    fetchRules()
})
</script>

<template>
    <MainLayout>
        <div class="page-header">
            <div>
                <h1>Manage Finance 🛠️</h1>
                <p class="subtitle">Configure your rules and categories.</p>
            </div>
            <div class="header-actions">
                 <button v-if="activeTab === 'rules'" @click="openAddModal" class="btn btn-primary">
                    + New Rule
                </button>
                 <button v-if="activeTab === 'categories'" @click="openAddCategoryModal" class="btn btn-primary">
                    + New Category
                </button>
            </div>
        </div>

        <div class="tabs">
            <button :class="['tab-btn', { active: activeTab === 'rules' }]" @click="activeTab = 'rules'">📝 Rules</button>
            <button :class="['tab-btn', { active: activeTab === 'categories' }]" @click="activeTab = 'categories'">🏷️ Categories</button>
        </div>

        <div v-if="loading" class="loading">Loading...</div>

        <!-- RULES TAB -->
        <div v-else-if="activeTab === 'rules'">
             <!-- Suggestions Section -->
            <div v-if="suggestions.length > 0" class="suggestions-section">
                <h2 class="section-title">💡 Smart Suggestions</h2>
                <div class="grid">
                    <div v-for="s in suggestions" :key="s.name" class="card suggestion-card">
                        <div class="rule-header">
                            <h3>{{ s.name }}</h3>
                            <button @click="approveSuggestion(s)" class="btn btn-sm btn-primary">
                                Approve
                            </button>
                        </div>
                         <div class="keywords">
                            <span class="keyword-tag">{{ s.keywords[0] }}</span>
                            <span class="arrow">→</span>
                            <span class="category-pill">{{ s.category }}</span>
                        </div>
                        <div class="meta">Based on {{ s.confidence }} manual entri(es)</div>
                    </div>
                </div>
            </div>

            <!-- Existing Rules -->
            <h2 class="section-title" v-if="suggestions.length > 0">Active Rules</h2>
            <div class="grid">
                <div v-for="rule in rules" :key="rule.id" class="card rule-card">
                    <div class="rule-header">
                        <h3>{{ rule.name }}</h3>
                        <div class="actions">
                             <button @click="openEditModal(rule)" class="btn-icon">✏️</button>
                             <button @click="deleteRule(rule.id)" class="btn-icon danger">🗑️</button>
                        </div>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                         <span class="category-pill">{{ rule.category }}</span>
                    </div>
                    <div class="keywords">
                        <span v-for="k in rule.keywords" :key="k" class="keyword-tag">{{ k }}</span>
                    </div>
                </div>
            </div>
            
            <div v-if="rules.length === 0 && suggestions.length === 0" class="empty-state">
                <p>No rules found. Add one to automate your life!</p>
            </div>
        </div>

        <!-- CATEGORIES TAB -->
        <div v-else-if="activeTab === 'categories'">
            <div class="grid">
                <div v-for="cat in categories" :key="cat.id" class="card category-card">
                    <div class="cat-content">
                        <span class="cat-icon">{{ cat.icon }}</span>
                        <span class="cat-name">{{ cat.name }}</span>
                    </div>
                    <div class="actions">
                        <button @click="openEditCategoryModal(cat)" class="btn-icon">✏️</button>
                        <button @click="deleteCategory(cat.id)" class="btn-icon danger">🗑️</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add/Edit Rule Modal -->
        <div v-if="showModal" class="modal-overlay-global">
            <div class="modal-global">
                 <div class="modal-header">
                    <h2 class="modal-title">{{ isEditing ? 'Edit Rule' : 'New Rule' }}</h2>
                    <button class="btn-icon" @click="showModal = false">✕</button>
                </div>
                
                <form @submit.prevent="saveRule">
                    <div class="form-group">
                        <label class="form-label">Rule Name</label>
                        <input v-model="newRule.name" class="form-input" required placeholder="e.g. Ride Apps" />
                    </div>

                    <div class="form-group">
                        <label class="form-label">Category</label>
                        <CustomSelect 
                            v-model="newRule.category" 
                             :options="categoryOptions"
                            placeholder="Select or Type Category"
                            allow-new
                        />
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Keywords (Comma Separated)</label>
                        <textarea v-model="newRule.keywords" class="form-input" rows="3" placeholder="Uber, Lyft, Ola"></textarea>
                    </div>

                    <div class="modal-footer">
                         <button type="button" @click="showModal = false" class="btn btn-outline">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Rule</button>
                    </div>
                </form>
            </div>
        </div>
        
        <!-- Add/Edit Category Modal -->
        <div v-if="showCategoryModal" class="modal-overlay-global">
            <div class="modal-global">
                <div class="modal-header">
                    <h2 class="modal-title">{{ isEditingCategory ? 'Edit Category' : 'New Category' }}</h2>
                    <button class="btn-icon" @click="showCategoryModal = false">✕</button>
                </div>
                
                <form @submit.prevent="saveCategory">
                     <div class="form-group">
                        <label class="form-label">Icon (Emoji)</label>
                        <input v-model="newCategory.icon" class="form-input" style="font-size: 1.5rem; width: 60px;" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Category Name</label>
                        <input v-model="newCategory.name" class="form-input" required placeholder="e.g. Subscriptions" />
                    </div>
                    <div class="modal-footer">
                         <button type="button" @click="showCategoryModal = false" class="btn btn-outline">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Category</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Delete Confirmation Modal (Rule) -->
        <div v-if="showDeleteConfirm" class="modal-overlay-global">
            <div class="modal-global" style="max-width: 400px;">
                <div class="modal-header">
                    <h2 class="modal-title">Delete Rule</h2>
                    <button class="btn-icon" @click="showDeleteConfirm = false">✕</button>
                </div>
                <p>Are you sure you want to delete this rule? This action cannot be undone.</p>
                <div class="modal-footer">
                    <button @click="showDeleteConfirm = false" class="btn btn-outline">Cancel</button>
                    <button @click="confirmDelete" class="btn btn-primary danger-btn">Delete</button>
                </div>
            </div>
        </div>

        <!-- Delete Confirmation Modal (Category) -->
        <div v-if="showDeleteCategoryConfirm" class="modal-overlay-global">
            <div class="modal-global" style="max-width: 400px;">
                <div class="modal-header">
                    <h2 class="modal-title">Delete Category</h2>
                    <button class="btn-icon" @click="showDeleteCategoryConfirm = false">✕</button>
                </div>
                <p>Are you sure you want to delete this category? Active transactions may lose their formatting.</p>
                <div class="modal-footer">
                    <button @click="showDeleteCategoryConfirm = false" class="btn btn-outline">Cancel</button>
                    <button @click="confirmDeleteCategory" class="btn btn-primary danger-btn">Delete</button>
                </div>
            </div>
        </div>
    </MainLayout>
</template>

<style scoped>
.tabs { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 1px solid var(--color-border); padding-bottom: 0px; }
.tab-btn { background: none; border: none; padding: 0.5rem 1rem; cursor: pointer; color: var(--color-text-muted); font-weight: 500; border-bottom: 2px solid transparent; transition: all 0.2s; font-size: 1rem; }
.tab-btn.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }
.tab-btn:hover { color: var(--color-text-main); }

.category-card { display: flex; justify-content: space-between; align-items: center; }
.cat-content { display: flex; align-items: center; gap: 1rem; }
.cat-icon { font-size: 1.5rem; background: var(--color-background); width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; border-radius: 50%; }
.cat-name { font-weight: 600; font-size: 1.1rem; }

.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--spacing-xl); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--spacing-lg); }
.card { background: var(--color-surface); padding: var(--spacing-lg); border-radius: var(--radius-lg); border: 1px solid var(--color-border); box-shadow: var(--shadow-sm); }
.rule-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
.actions { display: flex; gap: 0.5rem; }
.danger { color: var(--color-danger, #ef4444); }
.danger:hover { background: #fee2e2; }
.danger-btn { background: var(--color-danger, #ef4444); border-color: var(--color-danger, #ef4444); color: white; }
.danger-btn:hover { background: #dc2626; border-color: #dc2626; }
.rule-header h3 { margin: 0; font-size: 1.1rem; }
.category-pill { background: var(--color-primary-light); color: var(--color-primary); padding: 0.25rem 0.5rem; border-radius: 1rem; font-size: 0.8rem; font-weight: 500; }
.keywords { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.keyword-tag { background: var(--color-background); padding: 0.2rem 0.6rem; border-radius: 0.5rem; font-size: 0.8rem; border: 1px solid var(--color-border); color: var(--color-text-muted); }
.modal-overlay-global { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-global { background: var(--color-surface); padding: 2rem; border-radius: 1rem; width: 100%; max-width: 500px; box-shadow: var(--shadow-xl); max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.modal-title { margin: 0; font-size: 1.25rem; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 1.2rem; padding: 0.2rem; border-radius: 0.25rem; transition: background 0.2s; }
.btn-icon:hover { background: var(--color-background); }
.form-group { margin-bottom: 1rem; }
.form-label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-input { width: 100%; padding: 0.75rem; border: 1px solid var(--color-border); border-radius: 0.5rem; background: var(--color-background); color: var(--color-text-main); }
.modal-footer { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; }
.loading { text-align: center; padding: 2rem; color: var(--color-text-muted); }
.empty-state { grid-column: 1/-1; text-align: center; padding: 4rem; background: var(--color-surface); border-radius: 1rem; color: var(--color-text-muted); border: 2px dashed var(--color-border); }

.suggestions-section { margin-bottom: var(--spacing-xl); }
.section-title { font-size: 1.1rem; color: var(--color-primary); margin-bottom: var(--spacing-md); font-weight: 600; }
.suggestion-card { border: 1px dashed var(--color-primary); background: var(--color-primary-light); }
.arrow { margin: 0 0.5rem; color: var(--color-text-muted); }
.meta { font-size: 0.8rem; color: var(--color-text-muted); margin-top: 0.5rem; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
</style>
