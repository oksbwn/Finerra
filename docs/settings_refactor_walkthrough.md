# Settings Refactoring Walkthrough

## Overview
We have successfully decoupled the `Settings.vue` component and its children. Previously, `Settings.vue` was a monolithic component that fetched **all** data (accounts, emails, family, devices, AI) at once, causing performance issues and tight coupling.

Now, `Settings.vue` acts purely as a **tab router**. Each child component (`AccountsSettings`, `EmailSettings`, etc.) is responsible for fetching its own data when mounted. We also introduced a Pinia store (`stores/ai.ts`) to manage AI configuration centrally.

## Key Changes

### 1. State Management
- **New Store**: `stores/ai.ts` handles AI configuration, model fetching, and connection testing.
- **Local State**: `AccountsSettings`, `DevicesSettings`, `EmailSettings`, and `FamilySettings` now manage their own local state (refs) instead of receiving props.

### 2. Component Decoupling
- **`Settings.vue`**: Removed `fetchData`, large props lists, and unused imports. Now only manages `activeTab`.
- **`GeneralSettings.vue`**: Uses `useSettingsStore` directly. Handles its own state and saving logic.
- **`AISettings.vue`**: Uses `useAiStore` directly. No longer emits events or takes props.
- **`ParserSettings.vue`**: Uses `useAiStore` directly. Syncs AI config to parser microservice independently.
- **`AccountsSettings.vue`**: Fetches accounts, goals, tenants, and users on mount. Handles its own search filtering.
- **`DevicesSettings.vue`**: Fetches devices and users on mount. Handles its own search filtering.
- **`EmailSettings.vue`**: Fetches email configs and users on mount. Handles its own search filtering.
- **`FamilySettings.vue`**: Fetches tenants and family members on mount.

## Verification Checklist

Please verify the following functionality in the browser:

### tabs & Navigation
- [ ] **Switching Tabs**: Click through all tabs (General, Accounts, Family, Emails, AI, Devices, Parser). Ensure they load content without errors.
- [ ] **Loading State**: Verify individual tabs show their own loading indicators (or load immediately) rather than a global full-page loader.

### Component Functionality
- [ ] **Accounts**:
    - [ ] Verify list of accounts loads.
    - [ ] Search for an account works.
    - [ ] Add/Edit account modal opens and saves correctly.
- [ ] **Family**:
    - [ ] Verify family members list loads.
    - [ ] Add member / Rename family works.
- [ ] **Emails**:
    - [ ] Verify email configurations load.
    - [ ] Add/Edit email works.
    - [ ] Logs history loads.
- [ ] **AI Integration**:
    - [ ] Verify AI settings are populated (fetched from store).
    - [ ] "Test AI Connection" works.
        - **Note**: If "Extraction Failed", checked backend logs.
        - **Resolved Issue**: Gemini API Quota Exceeded (RESOURCE_EXHAUSTED). Backend crashed during reload. Requires restart and API key check.
- [ ] **Parser Engine**:
    - [ ] Verify parser stats and pattern lists load.
    - [ ] "Sync App AI to Parser" button works.
- [ ] **Devices**:
    - [ ] Verify devices list loads.
    - [ ] Assign/Delete/Ignore actions work.

## Technical Details

### `Settings.vue` Before vs. After

**Before:**
```typescript
// Monolithic fetch
async function fetchData() {
   await Promise.all([getAccounts(), getEmails(), getDevices(), ...])
   // Passes everything as props
}
```

**After:**
```typescript
// Clean Tab Router
<AccountsSettings v-if="activeTab === 'accounts'" />
<EmailSettings v-if="activeTab === 'emails'" />
// No data fetching in parent
```
