<template>
    <MainLayout>
        <div class="categories-page">
            <header class="page-header">
                <div class="header-left">
                    <h1 class="page-title">Management</h1>
                    <div class="header-tabs ml-6">
                        <button class="tab-btn" :class="{ active: activeTab === 'categories' }"
                            @click="activeTab = 'categories'">
                            Categories
                        </button>
                        <button class="tab-btn" :class="{ active: activeTab === 'rules' }" @click="activeTab = 'rules'">
                            Rules
                        </button>
                    </div>
                </div>
                <!-- Header Actions moved to specific tabs -->
            </header>

            <!-- Tab Content -->
            <KeepAlive>
                <CategoriesTab v-if="activeTab === 'categories'" />
                <RulesTab v-else-if="activeTab === 'rules'" />
            </KeepAlive>

        </div>
    </MainLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import CategoriesTab from '@/views/categories/CategoriesTab.vue'
import RulesTab from '@/views/categories/RulesTab.vue'

const activeTab = ref('categories')
</script>

<style scoped>
.categories-page {
    padding-bottom: 5rem;
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

.page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
    letter-spacing: -0.01em;
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
</style>
