<template>
    <MainLayout>
        <div class="categories-page">
            <header class="page-header">
                <div class="header-left">
                    <h1 class="page-title">Management</h1>
                    <div class="header-tabs ml-6">
                        <button class="tab-btn" :class="{ active: activeTab === 'categories' }"
                            @click="activeTab = 'categories'; searchQuery = ''">
                            Categories
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'rules' }"
                            @click="activeTab = 'rules'; searchQuery = ''">
                            Rules
                        </button>
                    </div>
                </div>
                <div class="header-actions">
                    <button v-if="activeTab === 'categories'"
                        class="btn-secondary-premium btn-sm flex items-center gap-2" @click="handleExportCategories"
                        title="Export to JSON">
                        <Download :size="16" /> Export
                    </button>
                    <button v-if="activeTab === 'categories'"
                        class="btn-secondary-premium btn-sm flex items-center gap-2" @click="triggerImport"
                        title="Import from JSON">
                        <Upload :size="16" /> Import
                    </button>
                    <button v-if="activeTab === 'categories'" @click="startAddCategory" class="btn-premium-primary">
                        <div class="btn-glow"></div>
                        <Plus :size="16" />
                        <span>New Category</span>
                    </button>
                    <button v-if="activeTab === 'rules'" @click="openAddRuleModal" class="btn-premium-primary">
                        <div class="btn-glow"></div>
                        <Plus :size="16" />
                        <span>New Rule</span>
                    </button>
                </div>
            </header>

            <!-- Invisible file input for import -->
            <input type="file" ref="fileInput" accept=".json" style="display: none" @change="handleImportCategories" />

            <!-- Categories Tab Content -->
            <div v-if="activeTab === 'categories'" class="animate-in">
                <!-- Stats Overview -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                        @click="activeCategoryFilter = 'all'"
                        :class="{ 'ring-2 ring-indigo-500 bg-indigo-50/50': activeCategoryFilter === 'all' }">
                        <div class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-xl mb-3">📊
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs uppercase tracking-wider font-bold text-gray-500">Total</span>
                            <span class="text-2xl font-bold text-gray-900">{{ categoryStats.total }}</span>
                        </div>
                    </div>
                    <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                        @click="activeCategoryFilter = 'expense'"
                        :class="{ 'ring-2 ring-rose-500 bg-rose-50/50': activeCategoryFilter === 'expense' }">
                        <div class="w-10 h-10 rounded-full bg-rose-100 flex items-center justify-center text-xl mb-3">💸
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs uppercase tracking-wider font-bold text-rose-600">Expenses</span>
                            <span class="text-2xl font-bold text-gray-900">{{ categoryStats.expenses }}</span>
                        </div>
                    </div>
                    <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                        @click="activeCategoryFilter = 'income'"
                        :class="{ 'ring-2 ring-emerald-500 bg-emerald-50/50': activeCategoryFilter === 'income' }">
                        <div
                            class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-xl mb-3">
                            💰
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs uppercase tracking-wider font-bold text-emerald-600">Income</span>
                            <span class="text-2xl font-bold text-gray-900">{{ categoryStats.income }}</span>
                        </div>
                    </div>
                    <div class="stat-card-premium cursor-pointer transition-all hover:scale-[1.02]"
                        @click="activeCategoryFilter = 'transfer'"
                        :class="{ 'ring-2 ring-blue-500 bg-blue-50/50': activeCategoryFilter === 'transfer' }">
                        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-xl mb-3">🔄
                        </div>
                        <div class="flex flex-col">
                            <span class="text-xs uppercase tracking-wider font-bold text-blue-600">Transfers</span>
                            <span class="text-2xl font-bold text-gray-900">{{ categoryStats.transfer }}</span>
                        </div>
                    </div>
                </div>

                <!-- Toolbar -->
                <div
                    class="flex flex-col md:flex-row gap-4 mb-6 sticky top-0 bg-white/50 backdrop-blur-md p-2 rounded-xl z-20 border border-white/20 shadow-sm">
                    <div class="relative flex-1 max-w-sm">
                        <Search class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" :size="18" />
                        <input type="text" v-model="searchQuery" placeholder="Search categories..."
                            class="w-full bg-white border border-gray-200 pl-10 pr-4 py-2.5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-sm">
                    </div>

                    <div class="flex items-center gap-2 overflow-x-auto pb-1 hide-scrollbar ml-auto">
                        <button class="btn-primary-glow flex items-center gap-2 px-4 py-2" @click="startAddCategory">
                            <div class="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center text-xs">+
                            </div>
                            <span>New Category</span>
                        </button>
                    </div>
                </div>

                <!-- Categories Grid (Tree View) -->
                <div v-if="loading" class="flex justify-center py-12">
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
                    <div v-for="cat in rootCategories" :key="cat.id"
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
                                    <span v-if="getChildren(cat.id).length > 0" class="text-[10px] text-muted">
                                        {{ getChildren(cat.id).length }} sub
                                    </span>
                                </div>
                            </div>

                            <div
                                class="hidden group-hover:flex absolute right-2 top-2 bg-white rounded-lg shadow-sm border border-gray-100 p-1 gap-1">
                                <button class="p-1.5 hover:bg-gray-100 rounded text-gray-400 hover:text-indigo-600"
                                    @click.stop="editCategory(cat)">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                        class="current-color stroke-2">
                                        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                                        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                    </svg>
                                </button>
                                <button class="p-1.5 hover:bg-rose-50 rounded text-gray-400 hover:text-rose-600"
                                    @click.stop="startDeleteCategory(cat)">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
                                        class="current-color stroke-2">
                                        <path
                                            d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <!-- Subcategories List -->
                        <div v-if="getChildren(cat.id).length > 0"
                            class="bg-gray-50/50 flex-1 border-t border-gray-100 p-2 space-y-1">
                            <div v-for="child in getChildren(cat.id)" :key="child.id"
                                class="flex items-center gap-2 p-2 rounded-lg hover:bg-white hover:shadow-sm cursor-pointer transition-all group"
                                @click.stop="editCategory(child)">

                                <div class="w-1.5 h-1.5 rounded-full bg-gray-300 group-hover:bg-indigo-400 ml-1">
                                </div>
                                <span class="text-sm shrink-0">{{ child.icon || '🏷️' }}</span>
                                <span
                                    class="text-sm font-medium text-gray-600 group-hover:text-gray-900 truncate flex-1">{{
                                        child.name }}</span>

                                <div
                                    class="hidden group-hover:flex items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button class="p-1 text-gray-400 hover:text-indigo-600"
                                        @click.stop="editCategory(child)">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
                                            class="current-color stroke-2">
                                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Rules Tab Content -->
            <div v-if="activeTab === 'rules'" class="animate-in">
                <!-- Control Bar: Search Left, Title/Count Right (Settings Style) -->
                <div class="flex items-center justify-between mt-4 mb-6 gap-4">
                    <!-- Search Bar Premium -->
                    <div class="search-bar-premium no-margin flex-1 max-w-[320px]">
                        <Search class="search-icon text-gray-400" :size="16" />
                        <input type="text" v-model="searchQuery" placeholder="Search rules..." class="search-input">
                    </div>

                    <!-- Header with Badge -->
                    <div class="header-with-badge flex items-center gap-3">
                        <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wide">Active Rules</h3>
                        <span
                            class="pulse-status-badge bg-indigo-50 text-indigo-700 border border-indigo-100 px-3 py-1 rounded-full text-xs font-bold">
                            {{ filteredRules.length }} Active
                        </span>
                    </div>
                </div>

                <!-- Suggestions -->
                <div v-if="suggestions.length > 0" class="mb-8 animate-in delay-100">
                    <div class="flex items-center gap-2 mb-4">
                        <span
                            class="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                            AI Suggestions
                        </span>
                        <span class="text-xs text-gray-500">Based on your transaction history</span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div v-for="s in suggestions" :key="s.name"
                            class="glass-card p-4 border-l-4 border-l-indigo-500 hover:shadow-md transition-all group relative overflow-hidden">
                            <div
                                class="absolute inset-0 bg-gradient-to-r from-indigo-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                            </div>

                            <div class="relative z-10 flex justify-between items-start">
                                <div>
                                    <div class="font-bold text-gray-900">{{ s.name }}</div>
                                    <div class="text-xs text-gray-500 mt-1"> matches "{{ s.keywords.join(', ') }}"</div>
                                    <div
                                        class="mt-2 text-sm font-medium text-indigo-600 bg-white/80 inline-block px-2 py-1 rounded border border-indigo-100">
                                        {{ getCategoryDisplay(s.category) }}
                                    </div>
                                </div>
                                <div class="flex gap-2">
                                    <button @click="ignoreSuggestion(s)"
                                        class="p-2 hover:bg-gray-100 rounded-lg text-gray-400 hover:text-gray-600 transition-colors"
                                        title="Ignore">
                                        ✕
                                    </button>
                                    <button @click="approveSuggestion(s)"
                                        class="px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-bold shadow-sm hover:bg-indigo-700 transition-colors">
                                        Approve
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Rules List -->
                <div v-if="filteredRules.length === 0"
                    class="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                    <div class="text-4xl mb-3">📜</div>
                    <div class="text-gray-900 font-bold text-lg mb-1">No Rules Found</div>
                    <p class="text-gray-500 text-sm max-w-sm mx-auto">{{ emptyRulesMsg }}</p>
                    <button v-if="!searchQuery" @click="openAddRuleModal" class="mt-4 btn-primary-glow px-4 py-2">
                        Create First Rule
                    </button>
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pb-20">
                    <div v-for="rule in filteredRules" :key="rule.id"
                        class="glass-card flex flex-col hover:shadow-lg transition-all group relative border border-gray-100/50 bg-gradient-to-b from-white to-gray-50/30">

                        <!-- Top Section: Header -->
                        <div class="p-4 flex items-start justify-between gap-3 border-b border-gray-100/50">
                            <div class="flex items-start gap-3 min-w-0">
                                <div
                                    class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-xl shrink-0">
                                    📜
                                </div>
                                <div class="flex flex-col min-w-0">
                                    <div class="flex items-center gap-2">
                                        <h3 class="font-bold text-gray-900 truncate leading-tight">{{ rule.name }}</h3>
                                    </div>
                                    <div class="flex items-center gap-2 mt-1">
                                        <span v-if="rule.exclude_from_reports"
                                            class="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-600 border border-rose-100 uppercase tracking-wider">
                                            Hidden
                                        </span>
                                        <span class="text-xs text-muted flex items-center gap-1">
                                            {{ rule.keywords.length }} keyword{{ rule.keywords.length !== 1 ? 's' : ''
                                            }}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <!-- Assigns To Badge -->
                            <div class="flex flex-col items-end shrink-0">
                                <span
                                    class="text-[10px] text-gray-400 font-bold uppercase tracking-wider mb-0.5">Assigns
                                    To</span>
                                <div
                                    class="px-2 py-1 bg-white border border-gray-100 rounded-lg shadow-sm text-xs font-bold text-gray-800 flex items-center gap-1.5">
                                    {{ getCategoryDisplay(rule.category) }}
                                </div>
                            </div>
                        </div>

                        <!-- Middle Section: Keywords -->
                        <div class="p-4 bg-gray-50/50 flex-1">
                            <div class="flex flex-wrap gap-1.5">
                                <span v-for="(k, idx) in rule.keywords.slice(0, 5)" :key="idx"
                                    class="text-xs bg-white text-gray-600 px-2 py-1 rounded-md border border-gray-200 shadow-sm font-mono">
                                    {{ k }}
                                </span>
                                <span v-if="rule.keywords.length > 5"
                                    class="text-xs bg-gray-100 text-gray-500 px-2 py-1 rounded-md border border-gray-200 font-medium">
                                    +{{ rule.keywords.length - 5 }}
                                </span>
                            </div>
                        </div>

                        <!-- Bottom Section: Actions -->
                        <div
                            class="p-2 flex justify-end gap-1 border-t border-gray-100 bg-white rounded-b-xl opacity-0 group-hover:opacity-100 transition-opacity absolute bottom-0 right-0 left-0 hover:opacity-100 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-20">
                            <button class="btn-icon-sm text-amber-500 hover:bg-amber-50"
                                @click="handleApplyRuleRetrospectively(rule.id)" title="Run on past transactions">
                                <Zap :size="16" />
                            </button>
                            <button class="btn-icon-sm text-gray-400 hover:text-indigo-600 hover:bg-indigo-50"
                                @click="openEditRuleModal(rule)" title="Edit">
                                <Edit2 :size="16" />
                            </button>
                            <button class="btn-icon-sm text-gray-400 hover:text-rose-600 hover:bg-rose-50"
                                @click="deleteRule(rule.id)" title="Delete">
                                <Trash2 :size="16" />
                            </button>
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
                                <label class="block text-sm font-bold text-gray-700 mb-1">Parent Category
                                    (Optional)</label>
                                <CustomSelect v-model="categoryForm.parent_id"
                                    :options="[{ label: 'None (Root)', value: null }, ...categories.filter(c => c.id !== editingCategoryId).map(c => ({ label: `${c.icon} ${c.name}`, value: c.id }))]"
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
                    <p class="text-gray-500 mb-6 text-sm">Existing transactions in this category will become
                        uncategorized. Sub-categories will be unlinked.</p>

                    <div class="flex gap-3 w-full">
                        <button @click="showDeleteCategoryConfirm = false"
                            class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600">Cancel</button>
                        <button @click="confirmDeleteCategory"
                            class="flex-1 py-2.5 rounded-xl bg-rose-500 font-bold text-white hover:bg-rose-600">Delete</button>
                    </div>
                </div>
            </div>

            <!-- Add/Edit Rule Modal -->
            <div v-if="showRuleModal"
                class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div
                    class="bg-white rounded-2xl shadow-xl w-full max-w-md border border-gray-100 flex flex-col max-h-[90vh]">
                    <div class="flex items-center justify-between p-6 border-b border-gray-100">
                        <h2 class="text-xl font-bold text-gray-900">{{ isEditingRule ? 'Edit Rule' : 'New Rule' }}</h2>
                        <button
                            class="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500"
                            @click="showRuleModal = false">✕</button>
                    </div>

                    <div class="p-6 space-y-4 overflow-y-auto">
                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Rule Name</label>
                            <input v-model="newRule.name" placeholder="e.g. Swiggy Orders"
                                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 font-medium">
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Assign Category</label>
                            <CustomSelect v-model="newRule.category"
                                :options="categories.map(c => ({ label: `${c.icon || '🏷️'} ${c.name}`, value: c.name }))"
                                placeholder="Select Category" />
                        </div>

                        <div>
                            <label class="block text-sm font-bold text-gray-700 mb-1">Keywords (Comma separated)</label>
                            <textarea v-model="newRule.keywords" placeholder="swiggy, zomato, food delivery" rows="3"
                                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 outline-none focus:border-indigo-500 font-medium font-mono text-sm"></textarea>
                            <p class="text-xs text-gray-500 mt-1">Transactions containing ANY of these words will match.
                            </p>
                        </div>

                        <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-200">
                            <input type="checkbox" v-model="newRule.exclude_from_reports" id="exclude"
                                class="w-5 h-5 rounded text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="exclude" class="text-sm font-medium text-gray-700 cursor-pointer select-none">
                                Hide matching transactions from reports
                                <span class="block text-xs text-gray-500 font-normal">Good for internal transfers or
                                    reimbursable expenses</span>
                            </label>
                        </div>

                        <button @click="saveRule"
                            class="w-full py-3 rounded-xl bg-indigo-600 font-bold text-white hover:bg-indigo-700 shadow-md mt-2">
                            Save Rule
                        </button>
                    </div>
                </div>
            </div>

            <!-- Delete Rule Confirmation -->
            <div v-if="showRuleDeleteConfirm"
                class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 flex flex-col items-center text-center">
                    <div
                        class="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center text-3xl mb-4 text-rose-500">
                        🗑️</div>
                    <h2 class="text-xl font-bold text-gray-900 mb-2">Delete Rule?</h2>
                    <p class="text-gray-500 mb-6 text-sm">Future transactions will typically be Uncategorized or follow
                        other rules.</p>
                    <div class="flex gap-3 w-full">
                        <button @click="showRuleDeleteConfirm = false"
                            class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600">Cancel</button>
                        <button @click="confirmDeleteRule"
                            class="flex-1 py-2.5 rounded-xl bg-rose-500 font-bold text-white hover:bg-rose-600">Delete</button>
                    </div>
                </div>
            </div>

            <!-- Exclude Confirmation -->
            <div v-if="showExcludeConfirm"
                class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 flex flex-col items-center text-center">
                    <div
                        class="w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center text-3xl mb-4 text-amber-500">
                        👁️‍🗨️</div>
                    <h2 class="text-xl font-bold text-gray-900 mb-2">Hide from Reports?</h2>
                    <p class="text-gray-500 mb-6 text-sm">Matching transactions will NOT appear in analytics or report
                        sums. They will still match the category.</p>
                    <div class="flex gap-3 w-full">
                        <button @click="showExcludeConfirm = false"
                            class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600">Cancel</button>
                        <button @click="confirmSaveRule"
                            class="flex-1 py-2.5 rounded-xl bg-indigo-600 font-bold text-white hover:bg-indigo-700">Confirm
                            & Save</button>
                    </div>
                </div>
            </div>


            <!-- Apply Retro Confirmation - NEW -->
            <div v-if="showApplyRuleConfirm"
                class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 flex flex-col items-center text-center">
                    <div
                        class="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center text-3xl mb-4 text-indigo-600">
                        ⚡</div>
                    <h2 class="text-xl font-bold text-gray-900 mb-2">Run Rule on History?</h2>
                    <p class="text-gray-500 mb-6 text-sm">This will search all <strong>Uncategorized</strong>
                        transactions and apply this rule if they match. This cannot be undone.</p>
                    <div class="flex gap-3 w-full">
                        <button @click="showApplyRuleConfirm = false"
                            class="flex-1 py-2.5 rounded-xl border border-gray-200 font-bold text-gray-600">Cancel</button>
                        <button @click="confirmApplyRule"
                            class="flex-1 py-2.5 rounded-xl bg-indigo-600 font-bold text-white hover:bg-indigo-700">Yes,
                            Run It</button>
                    </div>
                </div>
            </div>

        </div>
    </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, Download, Upload, Search, Zap, Edit2, Trash2 } from 'lucide-vue-next'
import MainLayout from '@/layouts/MainLayout.vue'
import CustomSelect from '@/components/CustomSelect.vue'
import { financeApi } from '@/api/client'
import { useNotificationStore } from '@/stores/notification'

const notify = useNotificationStore()
const loading = ref(true)

const categories = ref<any[]>([])
const activeCategoryFilter = ref('all')
const activeTab = ref('categories')
const searchQuery = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// Rules/Categories State
const rules = ref<any[]>([])
const suggestions = ref<any[]>([])
const showRuleModal = ref(false)
const showExcludeConfirm = ref(false)
const showRuleDeleteConfirm = ref(false)
const showApplyRuleConfirm = ref(false)
const ruleToDelete = ref<string | null>(null)
const ruleToApply = ref<string | null>(null)
const isEditingRule = ref(false)
const editingRuleId = ref<string | null>(null)

const newRule = ref({
    name: '',
    category: '',
    keywords: '',
    exclude_from_reports: false
})

// Modal State
const showCategoryModal = ref(false)
const isEditingCategory = ref(false)
const editingCategoryId = ref<string | null>(null)
const showDeleteCategoryConfirm = ref(false)
const categoryToDelete = ref<any>(null)

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
    '#3B82F6', // Blue
    '#10B981', // Emerald
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Violet
    '#EC4899', // Pink
    '#06B6D4', // Cyan
    '#F97316', // Orange
    '#6366F1', // Indigo
    '#64748B', // Slate
]

const filteredCategories = computed(() => {
    let result = categories.value
    if (activeCategoryFilter.value !== 'all') {
        result = result.filter(c => (c.type || 'expense') === activeCategoryFilter.value)
    }
    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        result = result.filter(c => c.name.toLowerCase().includes(q))
    }
    return result
})

const categoryStats = computed(() => {
    return {
        total: categories.value.length,
        expenses: categories.value.filter(c => (c.type || 'expense') === 'expense').length,
        income: categories.value.filter(c => c.type === 'income').length,
        transfer: categories.value.filter(c => c.type === 'transfer').length,
    }
})

const rootCategories = computed(() => {
    return filteredCategories.value.filter(c => !c.parent_id)
})

function getChildren(parentId: string) {
    return filteredCategories.value.filter(c => c.parent_id === parentId)
}

const filteredRules = computed(() => {
    if (!searchQuery.value) return rules.value

    const q = searchQuery.value.toLowerCase()
    return rules.value.filter(r =>
        r.name.toLowerCase().includes(q) ||
        r.category.toLowerCase().includes(q) ||
        r.keywords.some((k: string) => k.toLowerCase().includes(q))
    )
})

const emptyRulesMsg = computed(() => searchQuery.value ? 'No rules match your search.' : 'No rules found. Define rules to automate categorization.')

function getCategoryDisplay(name: string) {
    if (!name) return '📝 General'
    const cat = categories.value.find(c => c.name === name)
    return cat ? `${cat.icon || '🏷️'} ${cat.name}` : `🏷️ ${name}`
}

onMounted(() => {
    fetchCategories()
})

async function fetchCategories() {
    loading.value = true
    try {
        const [catRes, rulesRes, sugRes] = await Promise.all([
            financeApi.getCategories(),
            financeApi.getRules(),
            financeApi.getRuleSuggestions()
        ])
        categories.value = catRes.data
        rules.value = rulesRes.data
        suggestions.value = sugRes.data
    } catch (e) {
        notify.error("Failed to load data")
        console.error(e)
    } finally {
        loading.value = false
    }
}

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
    try {
        if (isEditingCategory.value && editingCategoryId.value) {
            await financeApi.updateCategory(editingCategoryId.value, categoryForm.value)
            notify.success("Category updated")
        } else {
            await financeApi.createCategory(categoryForm.value)
            notify.success("Category created")
        }
        showCategoryModal.value = false
        fetchCategories()
    } catch (e: any) {
        console.error(e)
        if (e.response && e.response.data && e.response.data.detail) {
            notify.error(e.response.data.detail)
        } else {
            notify.error("Failed to save category")
        }
    }
}

function startDeleteCategory(cat: any) {
    categoryToDelete.value = cat
    showDeleteCategoryConfirm.value = true
}

async function confirmDeleteCategory() {
    if (!categoryToDelete.value) return
    try {
        await financeApi.deleteCategory(categoryToDelete.value.id)
        notify.success("Category deleted")
        showDeleteCategoryConfirm.value = false
        categoryToDelete.value = null
        fetchCategories()
    } catch (e) {
        notify.error("Failed to delete category")
    }
}

function handleExportCategories() {
    const dataStr = JSON.stringify(categories.value, null, 2)
    const blob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `finance_categories_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    notify.success("Categories exported")
}

function triggerImport() {
    fileInput.value?.click()
}

function handleImportCategories(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = async (e) => {
        try {
            const content = e.target?.result as string
            const importedCats = JSON.parse(content)
            if (!Array.isArray(importedCats)) throw new Error("Invalid format")

            notify.info("Importing " + importedCats.length + " categories...")
            let successCount = 0

            for (const cat of importedCats) {
                try {
                    const exists = categories.value.find(c => c.name === cat.name && c.type === cat.type)
                    if (!exists) {
                        await financeApi.createCategory({
                            name: cat.name,
                            type: cat.type || 'expense',
                            icon: cat.icon || '🏷️',
                            color: cat.color || '#3B82F6',
                            parent_id: null
                        })
                        successCount++
                    }
                } catch (err) {
                    // ignore errors for individual categories
                }
            }

            notify.success(`Import complete. Added ${successCount} new categories.`)
            fetchCategories()

        } catch (err) {
            notify.error("Failed to parse category file")
        }
        if (fileInput.value) fileInput.value.value = ''
    }
    reader.readAsText(file)
}


// --- Rule Functions ---
async function deleteRule(id: string) {
    ruleToDelete.value = id
    showRuleDeleteConfirm.value = true
}

async function confirmDeleteRule() {
    if (!ruleToDelete.value) return
    try {
        await financeApi.deleteRule(ruleToDelete.value)
        notify.success("Rule deleted")
        fetchCategories()
    } catch (err) {
        notify.error("Failed to delete rule")
    } finally {
        showRuleDeleteConfirm.value = false
        ruleToDelete.value = null
    }
}

function openAddRuleModal() {
    isEditingRule.value = false
    editingRuleId.value = null
    newRule.value = { name: '', category: '', keywords: '', exclude_from_reports: false }
    showRuleModal.value = true
}

function openEditRuleModal(rule: any) {
    isEditingRule.value = true
    editingRuleId.value = rule.id
    newRule.value = {
        name: rule.name,
        category: rule.category,
        keywords: rule.keywords.join(', '),
        exclude_from_reports: rule.exclude_from_reports || false
    }
    showRuleModal.value = true
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
        fetchCategories()
    } catch (err) {
        console.error(err)
        notify.error("Failed to approve rule")
    }
}

async function ignoreSuggestion(s: any) {
    try {
        await financeApi.ignoreSuggestion({ pattern: s.keywords[0] })
        notify.success(`Suggestion for "${s.name}" ignored`)
        fetchCategories()
    } catch (err) {
        console.error(err)
        notify.error("Failed to ignore suggestion")
    }
}

async function saveRule() {
    if (!newRule.value.name || !newRule.value.category || !newRule.value.keywords) return

    // If auto-exclude is on, ask for confirmation first
    if (newRule.value.exclude_from_reports) {
        showExcludeConfirm.value = true
        return
    }

    // Otherwise proceed directly
    await confirmSaveRule()
}

async function confirmSaveRule() {
    // Parse keywords: comma separated -> list
    const keywordList = newRule.value.keywords.split(',').map(k => k.trim())
    const payload = {
        ...newRule.value,
        keywords: keywordList,
        priority: 10
    }

    try {
        let isUpdate = false
        if (isEditingRule.value && editingRuleId.value) {
            isUpdate = true
            await financeApi.updateRule(editingRuleId.value, payload)
        } else {
            await financeApi.createRule(payload)
        }

        if (newRule.value.exclude_from_reports) {
            notify.success(`Rule saved! ${isUpdate ? 'Matching' : 'Future'} transactions will be hidden from reports.`)
        } else {
            notify.success(isUpdate ? "Rule updated successfully!" : "New rule created successfully!")
        }

        showRuleModal.value = false
        showExcludeConfirm.value = false
        newRule.value = { name: '', category: '', keywords: '', exclude_from_reports: false }
        fetchCategories()
    } catch (err) {
        console.error(err)
        notify.error("Failed to save rule")
    }
}

async function handleApplyRuleRetrospectively(ruleId: string) {
    ruleToApply.value = ruleId
    showApplyRuleConfirm.value = true
}

async function confirmApplyRule() {
    if (!ruleToApply.value) return

    try {
        const res = await financeApi.applyRuleRetrospectively(ruleToApply.value)
        if (res.data.success) {
            notify.success(`Success! Applied to ${res.data.affected} transactions.`)
        } else {
            notify.error(res.data.message || "Failed to apply rule")
        }
    } catch (e) {
        notify.error("Failed to apply rule retrospectively")
    } finally {
        showApplyRuleConfirm.value = false
        ruleToApply.value = null
    }
}
</script>

<style scoped>
.categories-page {
    padding-bottom: 5rem;
}

/* Settings-like Toolbar Styles */
.search-bar-premium {
    display: flex;
    align-items: center;
    background: white;
    padding: 0.5rem 0.875rem;
    border-radius: 0.75rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.search-icon {
    margin-right: 0.625rem;
    opacity: 0.6;
}

.search-input {
    border: none;
    background: transparent;
    outline: none;
    width: 100%;
    font-size: 0.875rem;
    color: #1f2937;
}

.pulse-status-badge {
    position: relative;
    display: inline-flex;
    align-items: center;
}

/* Ensure Rules Header matches Settings */
.header-with-badge h3 {
    margin: 0;
    color: #6b7280;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e5e7eb;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.transaction-count {
    font-size: 0.875rem;
    color: #64748b;
    font-weight: 600;
    background: #f1f5f9;
    padding: 0.375rem 0.75rem;
    border-radius: 2rem;
}

.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
    letter-spacing: -0.01em;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.btn-premium-primary {
    position: relative;
    background: #4f46e5;
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 1rem;
    font-weight: 700;
    font-size: 0.9375rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border: none;
    cursor: pointer;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
}

.btn-premium-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.4);
}

.btn-glow {
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.6s ease-in-out;
}

.btn-premium-primary:hover .btn-glow {
    left: 100%;
}

.glass-card {
    background: white;
    border: 1px solid var(--color-border);
    border-radius: 1rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}

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

.hide-scrollbar::-webkit-scrollbar {
    display: none;
}

.hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.current-color {
    stroke: currentColor;
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

.btn-secondary-premium {
    background: white;
    border: 1px solid var(--color-border);
    color: var(--color-text-main);
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
    transition: all 0.2s;
}

.btn-secondary-premium:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: var(--color-background);
}

.header-tabs {
    display: flex;
    gap: 0.125rem;
    background: #f3f4f6;
    padding: 0.125rem;
    border-radius: 0.625rem;
}

.tab-btn {
    padding: 0.375rem 1rem;
    border: none;
    background: transparent;
    border-radius: 0.5rem;
    font-size: 0.8125rem;
    font-weight: 600;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.tab-btn.active {
    background: white;
    color: #111827;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.btn-icon-sm {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: 0.5rem;
    transition: all 0.2s;
    border: none;
    background: transparent;
    cursor: pointer;
}
</style>
