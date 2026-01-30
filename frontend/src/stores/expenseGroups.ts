import { defineStore } from 'pinia';
import axios from 'axios';

export interface ExpenseGroup {
    id: string;
    name: string;
    description: string;
    is_active: boolean;
    created_at: string;
}

export const useExpenseGroupStore = defineStore('expenseGroups', {
    state: () => ({
        groups: [] as ExpenseGroup[],
        loading: false,
        error: null as string | null,
    }),

    actions: {
        async fetchGroups() {
            this.loading = true;
            try {
                const response = await axios.get('/api/finance/expense-groups');
                this.groups = response.data;
                this.error = null;
            } catch (err: any) {
                this.error = 'Failed to fetch expense groups';
                console.error(err);
            } finally {
                this.loading = false;
            }
        },

        async createGroup(name: string, description: string) {
            try {
                const response = await axios.post('/api/finance/expense-groups', { name, description });
                this.groups.push(response.data);
            } catch (err: any) {
                throw new Error('Failed to create expense group');
            }
        },

        async updateGroup(id: string, name: string, description: string, is_active: boolean) {
            try {
                const response = await axios.put(`/api/finance/expense-groups/${id}`, { name, description, is_active });
                const index = this.groups.findIndex(g => g.id === id);
                if (index !== -1) {
                    this.groups[index] = response.data;
                }
            } catch (err: any) {
                throw new Error('Failed to update expense group');
            }
        },

        async deleteGroup(id: string) {
            try {
                await axios.delete(`/api/finance/expense-groups/${id}`);
                this.groups = this.groups.filter(g => g.id !== id);
            } catch (err: any) {
                throw new Error('Failed to delete expense group');
            }
        }
    },
});
