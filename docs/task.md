# Settings Refactoring Tasks

## Goal: Decouple `Settings.vue` and Child Components
- [x] Create `stores/ai.ts` for AI state management
- [x] Refactor `AISettings.vue` to use `useAiStore`
    - Removed props: `modelValue`, `aiModels`, `isTesting`, `testResult`
    - Removed emits: `update:modelValue`, `save`, `test`, `refresh-models`
- [x] Refactor `ParserSettings.vue`
    - Removed props: `aiForm`
    - Implemented `useAiStore` integration
    - Added local connection testing and syncing
- [x] Refactor `AccountsSettings.vue`
    - Removed props: `accounts`, `goals`, `tenants`, `familyMembers`, `searchQuery`
    - Implemented local `fetchData`
- [x] Refactor `DevicesSettings.vue`
    - Removed props: `devices`, `familyMembers`, `searchQuery`
    - Implemented local `fetchData`
- [x] Refactor `EmailSettings.vue`
    - Removed props: `emailConfigs`, `familyMembers`, `searchQuery`
    - Implemented local `fetchData`
- [x] Refactor `FamilySettings.vue`
    - Removed props: `tenants`, `familyMembers`, `accounts`, `currentUser`
    - Implemented local `fetchData`
- [x] Clean up `Settings.vue`
    - Removed monolithic `fetchData`
    - Removed unused refs and imports
    - Simplified template to simple tab switching

## Bug Fixes & Polish
- [x] Restore Family Tab CSS (Hero, Cards, Gradients)
- [x] Fix Log Cleanup Scheduler (`get_db` generator error)
- [x] Fix Parser Sync Animation (infinite spinner)
- [x] Merge PatternManagement into ParserSettings & Fix Edit/Delete
- [x] Improve AI Parser Error Logging (Report specific errors like 'Quota Exceeded' instead of generic failure)
- [x] Identify Root Cause: Gemini API Quota Exceeded (RESOURCE_EXHAUSTED) & Backend Crash during reload
