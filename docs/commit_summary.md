# Commit Summary

## [feat(frontend): Refactor Settings & Integrate Pattern Management]
- Decoupled `Settings.vue` into independent child components (`AccountsSettings`, `AISettings`, etc.)
- Implemented `stores/ai.ts` for centralized AI state management
- Merged `PatternManagement` into `ParserSettings` with full CRUD operations
- Fixed UI bugs: Edit/Delete buttons, Modal Z-Index, Teleport issues

## [fix(backend): Improve AI Error Logging & Pipeline]
- Enhanced `GeminiParser` to return specific error messages (e.g., "Quota Exceeded", "API Key Missing")
- Updated `IngestionPipeline` to log these errors instead of generic "No parser matched"
- Fixed `parse_with_pattern` to handle configuration checks explicitly

## [docs: Update Walkthroughs & Task Tracking]
- Updated `task.md` with completed refactoring and debugging tasks
- Updated `settings_refactor_walkthrough.md` with verification steps and debugging findings
- Added root cause analysis for AI extraction failure (Quota Exceeded)
