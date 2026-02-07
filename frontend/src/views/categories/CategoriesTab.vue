<template>
    <div class="animate-in">
        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                @click="categoriesStore.searchFilter = 'all'"
                :class="{ 'ring-2 ring-indigo-500 bg-indigo-50/50': categoriesStore.searchFilter === 'all' }">
                <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl mb-3">📊</div>
                <div class="flex flex-col">
                    <span class="text-xs uppercase tracking-wider font-bold text-gray-500">Total</span>
                    <span class="text-2xl font-bold text-gray-900">{{ categoriesStore.categoryStats.total }}</span>
                </div>
            </div>
            <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                @click="categoriesStore.searchFilter = 'expense'"
                :class="{ 'ring-2 ring-rose-500 bg-rose-50/50': categoriesStore.searchFilter === 'expense' }">
                <div class="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-xl mb-3">💸</div>
                <div class="flex flex-col">
                    <span class="text-xs uppercase tracking-wider font-bold text-rose-600">Expenses</span>
                    <span class="text-2xl font-bold text-gray-900">{{ categoriesStore.categoryStats.expenses }}</span>
                </div>
            </div>
            <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                @click="categoriesStore.searchFilter = 'income'"
                :class="{ 'ring-2 ring-emerald-500 bg-emerald-50/50': categoriesStore.searchFilter === 'income' }">
                <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-xl mb-3">💰
                </div>
                <div class="flex flex-col">
                    <span class="text-xs uppercase tracking-wider font-bold text-emerald-600">Income</span>
                    <span class="text-2xl font-bold text-gray-900">{{ categoriesStore.categoryStats.income }}</span>
                </div>
            </div>
            <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                @click="categoriesStore.searchFilter = 'transfer'"
                :class="{ 'ring-2 ring-blue-500 bg-blue-50/50': categoriesStore.searchFilter === 'transfer' }">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-xl mb-3">🔄</div>
                <div class="flex flex-col">
                    <span class="text-xs uppercase tracking-wider font-bold text-blue-600">Transfers</span>
                    <span class="text-2xl font-bold text-gray-900">{{ categoriesStore.categoryStats.transfer }}</span>
                </div>
            </div>
        </div>

        <!-- Toolbar -->
        <div
            class="flex flex-col md:flex-row gap-4 mb-6 sticky top-0 bg-white/50 backdrop-blur-md p-2 rounded-xl z-20 border border-white/20 shadow-sm">
            <div class="relative flex-1 max-w-sm">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" :size="18" />
                <input type="text" v-model="categoriesStore.searchQuery" placeholder="Search categories..."
                    class="w-full bg-white border border-gray-200 pl-10 pr-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm">
            </div>

            <div class="flex items-center gap-2 overflow-x-auto pb-1 hide-scrollbar ml-auto">
                <button class="btn-secondary-premium btn-sm flex items-center gap-2"
                    @click="categoriesStore.exportCategories" title="Export to JSON">
                    <Download :size="16" /> Export
                </button>
                <button class="btn-secondary-premium btn-sm flex items-center gap-2" @click="triggerImport"
                    title="Import from JSON">
                    <Upload :size="16" /> Import
                </button>
                <div class="h-6 w-px bg-gray-200 mx-1"></div>
                <button class="btn-primary-glow flex items-center gap-2 px-4 py-2" @click="startAddCategory">
                    <div class="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs">+</div>
                    <span>New Category</span>
                </button>

                <!-- Invisible file input for import, moved from parent -->
                <input type="file" ref="fileInput" accept=".json" style="display: none"
                    @change="handleImportCategories" />
            </div>
        </div>

        <!-- Categories Grid (Tree View) -->
        <div v-if="categoriesStore.loading" class="flex justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 pb-20">
            <!-- Add New Card (Inline) -->
            <div class="glass-card hover:bg-gray-50 transition-colors border-dashed border-2 border-gray-200 cursor-pointer flex flex-col items-center justify-center min-h-[160px] gap-3 group"
                @click="startAddCategory">
                <div
                    class="w-12 h-12 rounded-full bg-indigo-50 group-hover:bg-indigo-100 text-indigo-600 flex items-center justify-center text-xl transition-colors">
                    +</div>
                <span class="font-bold text-gray-600 group-hover:text-indigo-700">Add Category</span>
            </div>

            <!-- Render Root Categories -->
            <div v-for="cat in categoriesStore.rootCategories" :key="cat.id"
                class="glass-card p-0 overflow-hidden flex flex-col h-full hover:shadow-md transition-all duration-300">
                <div class="p-4 flex items-start gap-3 cursor-pointer relative group" @click="editCategory(cat)"
                    :style="{ background: `linear-gradient(to right, ${cat.color}10, transparent)` }">

                    <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0 shadow-sm"
                        :style="{ backgroundColor: cat.color + '25', color: cat.color }">
                        {{ cat.icon || '🏷️' }}
                    </div>

                    <div class="flex-1 min-w-0">
                        <h3 class="font-bold text-gray-800 truncate">{{ cat.name }}</h3>
                        <div class="flex items-center gap-2 mt-1">
                            <span
                                class="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded text-gray-500 bg-white/50 border border-gray-100">
                                {{ (cat.type || 'expense').toUpperCase() }}
                            </span>
                            <span v-if="categoriesStore.getChildren(cat.id).length > 0" class="text-[10px] text-muted">
                                {{ categoriesStore.getChildren(cat.id).length }} sub
                            </span>
                        </div>
                    </div>

                    <div
                        class="hidden group-hover:flex absolute right-2 top-2 bg-white rounded-lg shadow-sm border border-gray-100 p-1 gap-1">
                        <button class="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-indigo-600"
                            @click.stop="editCategory(cat)">
                            <Edit2 :size="14" />
                        </button>
                        <button class="p-1.5 hover:bg-rose-50 rounded text-gray-400 hover:text-rose-600"
                            @click.stop="startDeleteCategory(cat)">
                            <Trash2 :size="14" />
                        </button>
                    </div>
                </div>

                <!-- Subcategories List -->
                <div v-if="categoriesStore.getChildren(cat.id).length > 0"
                    class="bg-gray-50/50 flex-1 border-t border-gray-100 p-2 space-y-1">
                    <div v-for="child in categoriesStore.getChildren(cat.id)" :key="child.id"
                        class="flex items-center gap-2 p-2 rounded-lg hover:bg-white hover:shadow-sm cursor-pointer transition-all group"
                        @click.stop="editCategory(child)">

                        <div class="w-1.5 h-1.5 rounded-full bg-gray-300 group-hover:bg-indigo-400 ml-1"></div>
                        <span class="text-sm shrink-0">{{ child.icon || '🏷️' }}</span>
                        <span class="text-sm font-medium text-gray-600 group-hover:text-gray-900 truncate flex-1">{{
                            child.name }}</span>

                        <div
                            class="hidden group-hover:flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <button class="p-1 text-gray-400 hover:text-indigo-600" @click.stop="editCategory(child)">
                                <Edit2 :size="12" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add/Edit Category Modal -->
        <div v-if="showCategoryModal"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div
                class="bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col max-h-[90vh]">
                <div class="flex items-center justify-between p-6 border-b border-gray-100">
                    <h2 class="text-xl font-bold text-gray-900">{{ modalTitle }}</h2>
                    <button
                        class="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500"
                        @click="showCategoryModal = false">✕</button>
                </div>

                <form @submit.prevent="saveCategory" class="overflow-y-auto p-6 flex flex-col gap-5">
                    <!-- Preview Section -->
                    <div class="flex items-center gap-4 p-4 rounded-xl border border-gray-100"
                        :style="{ background: `${categoryForm.color}10` }">
                        <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shadow-sm"
                            :style="{ background: `${categoryForm.color}20`, color: categoryForm.color }">
                            {{ categoryForm.icon || '🏷️' }}
                        </div>
                        <div class="flex flex-col text-left">
                            <div class="font-bold text-lg text-gray-900 truncate">{{ previewName }}</div>
                            <div class="text-[10px] font-bold uppercase tracking-widest text-gray-500">{{
                                categoryForm.type }}</div>
                        </div>
                    </div>

                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Icon (Emoji)</label>
                            <div class="flex items-center gap-2">
                                <input v-model="categoryForm.icon"
                                    class="w-12 h-12 text-center text-2xl border border-gray-200 rounded-xl outline-none focus:border-indigo-500"
                                    required maxlength="2" />
                                <div
                                    class="flex flex-wrap gap-2 flex-1 items-center bg-gray-50 p-2 rounded-xl border border-gray-100">
                                    <span
                                        v-for="e in ['💰', '🛒', '🚗', '🏠', '🍔', '🎮', '🏥', '✈️', '🎓', '👔', '🛍️', '🍿']"
                                        :key="e" @click="categoryForm.icon = e"
                                        class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white hover:shadow-sm cursor-pointer transition-all text-lg">
                                        {{ e }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Category Name</label>
                            <input v-model="categoryForm.name"
                                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 font-medium"
                                required placeholder="e.g. Subscriptions" />
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Parent Category (Optional)</label>
                            <CustomSelect v-model="categoryForm.parent_id"
                                :options="[{ label: 'None (Root)', value: null }, ...categoriesStore.categories.filter(c => c.id !== editingCategoryId).map(c => ({ label: `${c.icon} ${c.name}`, value: c.id }))]"
                                placeholder="Select Parent" />
                        </div>

                        <div class="grid grid-cols-2 gap-4 text-left">
                            <div>
                                <label class="block text-sm font-bold text-gray-700 mb-1">Type</label>
                                <CustomSelect v-model="categoryForm.type" :options="[
                                    { label: '🔴 Expense', value: 'expense' },
                                    { label: '🟢 Income', value: 'income' },
                                    { label: '🔄 Transfer', value: 'transfer' }
                                ]" />
                            </div>
                            <div class="flex flex-col">
                                <label class="block text-sm font-bold text-gray-700 mb-1">Theme Color</label>
                                <div class="flex items-center gap-2 p-1 bg-white border border-gray-200 rounded-xl">
                                    <input type="color" v-model="categoryForm.color"
                                        class="w-8 h-8 rounded-lg cursor-pointer border-none p-0 overflow-hidden" />
                                    <div class="flex flex-wrap gap-1">
                                        <div v-for="c in colorPresets.slice(0, 5)" :key="c"
                                            @click="categoryForm.color = c"
                                            class="w-4 h-4 rounded-full cursor-pointer hover:scale-110 transition-transform ring-1 ring-black/5"
                                            :style="{ background: c }">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-4 flex gap-3">
                        <button type="button" @click="showCategoryModal = false"
                            class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600 hover:bg-gray-50">Cancel</button>
                        <button type="submit"
                            class="flex-1 py-2.5 rounded-xl bg-indigo-600 font-bold text-white hover:bg-indigo-700 shadow-md">Save
                            Category</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Delete Confirmation Modal -->
        <div v-if="showDeleteCategoryConfirm"
            class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 flex flex-col items-center text-center">
                <div
                    class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center text-3xl mb-4 text-rose-500">
                    🗑️</div>
                <h2 class="text-xl font-bold text-gray-900 mb-2">Delete Category?</h2>
                <p class="text-gray-500 mb-6 text-sm">Existing transactions in this category will become uncategorized.
                    Sub-categories will be unlinked.</p>

                <div class="flex gap-3 w-full">
                    <button @click="showDeleteCategoryConfirm = false"
                        class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600">Cancel</button>
                    <button @click="confirmDeleteCategory"
                        class="flex-1 py-2.5 rounded-xl bg-rose-500 font-bold text-white hover:bg-rose-600">Delete</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Edit2, Trash2, Download, Upload } from 'lucide-vue-next'
import CustomSelect from '@/components/CustomSelect.vue'
import { useCategoriesStore } from '@/stores/finance/categories'

const categoriesStore = useCategoriesStore()

// Local UI State (Modals)
const showCategoryModal = ref(false)
const isEditingCategory = ref(false)
const editingCategoryId = ref<string | null>(null)
const showDeleteCategoryConfirm = ref(false)
const categoryToDelete = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

function triggerImport() {
    fileInput.value?.click()
}

function handleImportCategories(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (file) {
        categoriesStore.importCategories(file)
    }
    if (fileInput.value) fileInput.value.value = ''
}

const categoryForm = ref({
    name: '',
    icon: '🏷️',
    color: '#3B82F6',
    type: 'expense',
    parent_id: null as string | null
})

const modalTitle = computed(() => isEditingCategory.value ? 'Edit Category' : 'New Category')
const previewName = computed(() => categoryForm.value.name || 'New Category')

const colorPresets = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#EC4899', '#06B6D4', '#F97316', '#6366F1', '#64748B'
]

onMounted(() => {
    categoriesStore.fetchCategories()
})

function startAddCategory() {
    isEditingCategory.value = false
    editingCategoryId.value = null
    categoryForm.value = {
        name: '',
        icon: '🏷️',
        color: '#3B82F6',
        type: 'expense',
        parent_id: null
    }
    showCategoryModal.value = true
}

function editCategory(cat: any) {
    isEditingCategory.value = true
    editingCategoryId.value = cat.id
    categoryForm.value = { ...cat }
    showCategoryModal.value = true
}

async function saveCategory() {
    let success = false
    if (isEditingCategory.value && editingCategoryId.value) {
        success = await categoriesStore.updateCategory(editingCategoryId.value, categoryForm.value)
    } else {
        success = await categoriesStore.createCategory(categoryForm.value)
    }

    if (success) {
        showCategoryModal.value = false
    }
}

function startDeleteCategory(cat: any) {
    categoryToDelete.value = cat
    showDeleteCategoryConfirm.value = true
}

async function confirmDeleteCategory() {
    if (!categoryToDelete.value) return
    const success = await categoriesStore.deleteCategory(categoryToDelete.value.id)
    if (success) {
        showDeleteCategoryConfirm.value = false
        categoryToDelete.value = null
    }
}

// Expose open modal method if parent wants to trigger it (e.g. from header)
defineExpose({
    startAddCategory
})
</script>

<style scoped>
/* Reused styles from original file */
.stat-card-premium {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 1rem;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: var(--shadow-sm);
}

.glass-card {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 1rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}

.btn-primary-glow {
    background: var(--color-primary);
    color: white;
    border-radius: 0.5rem;
    transition: all 0.2s;
}

.btn-primary-glow:hover {
    background: var(--color-primary-dark);
    box-shadow: 0 0 15px var(--color-primary-light);
}

.hide-scrollbar::-webkit-scrollbar {
    display: none;
}
</style>
