# Tasks: Docusaurus Book Site - Physical AI & Humanoid Robotics

**Input**: Design documents from `/specs/001-docusaurus-book/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅  
**Branch**: `001-docusaurus-book`  
**Created**: 2025-12-06

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Source code**: `book/` subdirectory at repository root
- **Components**: `book/src/components/[ComponentName]/`
- **Content**: `book/docs/` (English), `book/i18n/ur/` (Urdu)
- **Tests**: `book/tests/unit/`, `book/tests/e2e/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Docusaurus scaffolding

- [x] T001 Initialize Docusaurus project with `npx create-docusaurus@latest book classic --typescript` in repository root
- [x] T002 Configure TypeScript in `book/tsconfig.json` per project standards
- [x] T003 [P] Add ESLint and Prettier config in `book/.eslintrc.js` and `book/.prettierrc`
- [x] T004 [P] Create `book/README.md` with developer setup instructions
- [x] T005 [P] Update `book/package.json` with all dependencies from plan.md

**Checkpoint**: Docusaurus project builds and runs locally (`npm start`) ✅

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Configure i18n in `book/docusaurus.config.ts` with English (default) and Urdu locales
- [x] T007 Setup sidebar autogeneration in `book/sidebars.ts`
- [x] T008 [P] Create base theme variables in `book/src/css/custom.css`
- [x] T009 [P] Create RTL stylesheet in `book/src/css/rtl.css` for Urdu locale
- [x] T010 [P] Configure Prism syntax highlighting themes (light: github, dark: dracula) in `book/docusaurus.config.ts`
- [x] T011 Setup global MDX component registration in `book/src/theme/MDXComponents.tsx`
- [x] T012 [P] Add static assets: `book/static/img/logo.svg` and `book/static/img/favicon.ico`
- [x] T013 [P] Configure navbar with locale dropdown in `book/docusaurus.config.ts`

**Checkpoint**: Foundation ready - i18n configured, sidebar working, themes applied, MDX components registerable ✅

---

## Phase 3: User Story 1 - Reader Navigates Textbook (Priority: P1) 🎯 MVP

**Goal**: Readers can browse chapters sequentially or jump to specific topics using sidebar navigation

**Independent Test**: Open site, navigate through chapters, verify content renders correctly

### Implementation for User Story 1

- [ ] T014 [US1] Create homepage in `book/src/pages/index.tsx` with book title, description, and "Start Reading" button
- [ ] T015 [P] [US1] Create Chapter 1 category metadata in `book/docs/01-introduction/_category_.json`
- [ ] T016 [P] [US1] Create Chapter 2 category metadata in `book/docs/02-humanoid-robotics/_category_.json`
- [ ] T017 [P] [US1] Create Chapter 3 category metadata in `book/docs/03-sensors-actuators/_category_.json`
- [ ] T018 [P] [US1] Create Chapter 4 category metadata in `book/docs/04-ai-integration/_category_.json`
- [ ] T019 [US1] Create `book/docs/01-introduction/1.0-overview.mdx` with ChapterHeader and placeholder content
- [ ] T020 [P] [US1] Create `book/docs/01-introduction/1.1-what-is-physical-ai.mdx` with section content
- [ ] T021 [P] [US1] Create `book/docs/01-introduction/1.2-history-evolution.mdx` with section content
- [ ] T022 [P] [US1] Create `book/docs/01-introduction/1.3-exercises.mdx` with exercise placeholders
- [ ] T023 [P] [US1] Create `book/docs/01-introduction/1.4-summary.mdx` with chapter summary
- [ ] T024 [US1] Create `book/docs/02-humanoid-robotics/2.0-overview.mdx` with ChapterHeader and placeholder content
- [ ] T025 [P] [US1] Create `book/docs/02-humanoid-robotics/2.1-anatomy.mdx` with section content
- [ ] T026 [P] [US1] Create `book/docs/02-humanoid-robotics/2.2-locomotion.mdx` with section content
- [ ] T027 [US1] Create `book/docs/03-sensors-actuators/3.0-overview.mdx` with ChapterHeader and placeholder content
- [ ] T028 [P] [US1] Create `book/docs/03-sensors-actuators/3.1-sensor-types.mdx` with section content
- [ ] T029 [US1] Create `book/docs/04-ai-integration/4.0-overview.mdx` with ChapterHeader and placeholder content
- [ ] T030 [P] [US1] Create `book/docs/04-ai-integration/4.1-machine-learning.mdx` with section content
- [ ] T031 [US1] Implement ChapterHeader component in `book/src/components/ChapterHeader/index.tsx` per contract
- [ ] T032 [P] [US1] Create ChapterHeader styles in `book/src/components/ChapterHeader/styles.module.css`

**Checkpoint**: 4 chapters with X.Y.Z structure navigable, sidebar autogenerates, homepage links to Chapter 1

---

## Phase 4: User Story 2 - Reader Selects Difficulty Track (Priority: P2)

**Goal**: Readers see difficulty level indicators (beginner/intermediate/advanced) on content sections

**Independent Test**: View chapter pages and verify difficulty badges display with correct colors and labels

### Implementation for User Story 2

- [ ] T033 [US2] Implement DifficultyBadge component in `book/src/components/DifficultyBadge/index.tsx` per contract
- [ ] T034 [P] [US2] Create DifficultyBadge styles in `book/src/components/DifficultyBadge/styles.module.css`
- [ ] T035 [US2] Add DifficultyBadge to MDXComponents registration in `book/src/theme/MDXComponents.tsx`
- [ ] T036 [US2] Update `book/docs/01-introduction/1.0-overview.mdx` frontmatter with difficulty: beginner
- [ ] T037 [P] [US2] Update `book/docs/01-introduction/1.1-what-is-physical-ai.mdx` frontmatter with difficulty: beginner
- [ ] T038 [P] [US2] Update `book/docs/02-humanoid-robotics/2.0-overview.mdx` frontmatter with difficulty: intermediate
- [ ] T039 [P] [US2] Update `book/docs/03-sensors-actuators/3.0-overview.mdx` frontmatter with difficulty: intermediate
- [ ] T040 [P] [US2] Update `book/docs/04-ai-integration/4.0-overview.mdx` frontmatter with difficulty: advanced
- [ ] T041 [US2] Add DifficultyBadge usage examples in chapter content

**Checkpoint**: All chapter pages display difficulty indicators, badges have correct colors and accessibility

---

## Phase 5: User Story 3 - Reader Uses Dark/Light Mode (Priority: P2)

**Goal**: Readers can switch between dark and light themes with preference persistence

**Independent Test**: Toggle theme switch, verify colors change across all pages, refresh and confirm persistence

### Implementation for User Story 3

- [ ] T042 [US3] Configure colorMode in `book/docusaurus.config.ts` with defaultMode: 'light', respectPrefersColorScheme: true
- [ ] T043 [P] [US3] Define dark theme CSS variables in `book/src/css/custom.css`
- [ ] T044 [P] [US3] Define light theme CSS variables in `book/src/css/custom.css`
- [ ] T045 [US3] Ensure DifficultyBadge colors work in both themes (update `styles.module.css`)
- [ ] T046 [US3] Ensure ChapterHeader displays correctly in both themes (update `styles.module.css`)
- [ ] T047 [US3] Verify code block syntax highlighting in both themes (Prism github/dracula)

**Checkpoint**: Theme toggle on all pages, preference persists in localStorage, all components readable in both modes

---

## Phase 6: User Story 4 - Reader Accesses Urdu Translation (Priority: P3)

**Goal**: Urdu-speaking readers can switch to Urdu with RTL layout

**Independent Test**: Switch language to Urdu, verify RTL layout and translated strings appear

### Implementation for User Story 4

- [ ] T048 [US4] Create Urdu navbar translations in `book/i18n/ur/docusaurus-theme-classic/navbar.json`
- [ ] T049 [P] [US4] Create Urdu footer translations in `book/i18n/ur/docusaurus-theme-classic/footer.json`
- [ ] T050 [P] [US4] Create Urdu code blocks translations in `book/i18n/ur/docusaurus-theme-classic/code-block.json`
- [ ] T051 [US4] Create sample Urdu chapter translation in `book/i18n/ur/docusaurus-plugin-content-docs/current/01-introduction/1.0-overview.mdx`
- [ ] T052 [US4] Add RTL-specific layout adjustments in `book/src/css/rtl.css`
- [ ] T053 [P] [US4] Add difficulty level Urdu translations (beginner=مبتدی, intermediate=انٹرمیڈیٹ, advanced=ایڈوانسڈ)
- [ ] T054 [US4] Test RTL layout with sidebar, navigation, and content
- [ ] T055 [US4] Add "Translation pending" notice component for untranslated pages

**Checkpoint**: Urdu locale accessible via dropdown, RTL layout works, at least 1 sample page fully translated

---

## Phase 7: User Story 5 - Reader Sees Chatbot Placeholder (Priority: P3)

**Goal**: Readers see a chatbot placeholder widget indicating AI assistant coming soon

**Independent Test**: Open any chapter page, verify chatbot placeholder icon visible, click shows "Coming soon" message

### Implementation for User Story 5

- [ ] T056 [US5] Implement ChatbotPlaceholder component in `book/src/components/ChatbotPlaceholder/index.tsx` per contract
- [ ] T057 [P] [US5] Create ChatbotPlaceholder styles in `book/src/components/ChatbotPlaceholder/styles.module.css`
- [ ] T058 [US5] Add ChatbotPlaceholder to MDXComponents registration in `book/src/theme/MDXComponents.tsx`
- [ ] T059 [US5] Add ChatbotPlaceholder to all chapter overview pages (1.0, 2.0, 3.0, 4.0)
- [ ] T060 [US5] Implement expand/collapse animation and "Coming soon" modal
- [ ] T061 [US5] Add keyboard accessibility (Tab, Enter/Space) to ChatbotPlaceholder
- [ ] T062 [US5] Ensure ChatbotPlaceholder works in both light/dark modes and RTL layout

**Checkpoint**: Chatbot placeholder visible on all chapter pages, keyboard accessible, shows "Coming soon" on click

---

## Phase 8: Testing & Validation

**Purpose**: Verify all success criteria met

### Unit Tests

- [ ] T063 [P] Create DifficultyBadge unit tests in `book/tests/unit/components/DifficultyBadge.test.tsx`
- [ ] T064 [P] Create ChatbotPlaceholder unit tests in `book/tests/unit/components/ChatbotPlaceholder.test.tsx`
- [ ] T065 [P] Create ChapterHeader unit tests in `book/tests/unit/components/ChapterHeader.test.tsx`

### E2E Tests

- [ ] T066 Create navigation E2E test in `book/tests/e2e/navigation.spec.ts` (SC-004)
- [ ] T067 [P] Create theme toggle E2E test in `book/tests/e2e/theme.spec.ts` (SC-005)
- [ ] T068 [P] Create accessibility E2E test in `book/tests/e2e/accessibility.spec.ts` (SC-003, SC-008)
- [ ] T069 [P] Create mobile responsive E2E test in `book/tests/e2e/mobile.spec.ts` (SC-009)
- [ ] T070 Create Urdu RTL E2E test in `book/tests/e2e/i18n.spec.ts` (SC-006)

### Validation

- [ ] T071 Run Lighthouse audit and verify score ≥ 90 (SC-003)
- [ ] T072 Verify all images have alt text (SC-010)
- [ ] T073 Verify page load time < 3 seconds (SC-002)
- [ ] T074 Run build and verify no errors (SC-001)

**Checkpoint**: All success criteria verified, tests passing

---

## Phase 9: Polish & Documentation

**Purpose**: Final cleanup and documentation

- [ ] T075 [P] Update `book/README.md` with final setup instructions and contribution guide
- [ ] T076 [P] Add inline documentation comments to all custom components
- [ ] T077 Run quickstart.md validation - verify all steps work
- [ ] T078 [P] Add CHANGELOG.md entry for Phase 1 completion
- [ ] T079 Code cleanup: remove unused imports, format all files
- [ ] T080 Final accessibility review with screen reader

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T005)
    │
    ▼
Phase 2: Foundational (T006-T013) ← BLOCKS ALL USER STORIES
    │
    ├──────────────────────────────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
Phase 3: US1 Navigation (T014-T032)          Phase 5: US3 Theme (T042-T047)
    │                                                      │
    ▼                                                      │
Phase 4: US2 Difficulty (T033-T041) ←─────────────────────┘
    │
    ├──────────────────────────────────────────────────────┐
    │                                                      │
    ▼                                                      ▼
Phase 6: US4 Urdu i18n (T048-T055)          Phase 7: US5 Chatbot (T056-T062)
    │                                                      │
    └──────────────────────────────────────────────────────┤
                                                           │
                                                           ▼
                                              Phase 8: Testing (T063-T074)
                                                           │
                                                           ▼
                                              Phase 9: Polish (T075-T080)
```

### User Story Independence

| Story | Can Start After | Dependencies | Independently Testable |
|-------|-----------------|--------------|------------------------|
| US1 Navigation | Phase 2 | None | ✅ Yes |
| US2 Difficulty | T031 (ChapterHeader) | US1 (partial) | ✅ Yes |
| US3 Theme | Phase 2 | None | ✅ Yes |
| US4 Urdu | Phase 2 + T008-T009 | US1 (for content) | ✅ Yes |
| US5 Chatbot | Phase 2 | None | ✅ Yes |

### Parallel Opportunities

**Phase 1**: T003, T004, T005 can run in parallel  
**Phase 2**: T008, T009, T010, T012, T013 can run in parallel  
**Phase 3**: T015-T018, T020-T023, T025-T026, T028, T030, T032 can run in parallel  
**Phase 4**: T034, T037-T040 can run in parallel  
**Phase 5**: T043, T044 can run in parallel  
**Phase 6**: T049, T050, T053 can run in parallel  
**Phase 7**: T057 can run with T056  
**Phase 8**: All [P] tests can run in parallel  
**Phase 9**: T075, T076, T078 can run in parallel  

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup ✓
2. Complete Phase 2: Foundational ✓
3. Complete Phase 3: User Story 1 (Navigation)
4. **STOP and VALIDATE**: 4 chapters navigable, homepage works
5. Demo/Deploy MVP

### Recommended Sequence (Solo Developer)

1. **Day 1**: Phase 1 + Phase 2 (Setup + Foundation)
2. **Day 2**: Phase 3 (US1 - Navigation) ← MVP Complete
3. **Day 3**: Phase 4 + Phase 5 (US2 Difficulty + US3 Theme)
4. **Day 4**: Phase 6 (US4 - Urdu i18n)
5. **Day 5**: Phase 7 + Phase 8 (US5 Chatbot + Testing)
6. **Day 6**: Phase 9 (Polish + Documentation)

### Parallel Team Strategy (3 Developers)

After Phase 2 complete:
- **Dev A**: Phase 3 (US1) → Phase 4 (US2)
- **Dev B**: Phase 5 (US3) → Phase 7 (US5)
- **Dev C**: Phase 6 (US4) → Phase 8 (Testing)
- **All**: Phase 9 (Polish)

---

## Task-to-Requirement Mapping

| Requirement | Tasks |
|-------------|-------|
| FR-001 Homepage | T014 |
| FR-002 X.Y.Z numbering | T015-T030 |
| FR-003 Sidebar navigation | T007 |
| FR-004 Dark/Light theme | T042-T047 |
| FR-005 Frontmatter | T019-T030, T036-T040 |
| FR-006 English + Urdu | T006, T048-T055 |
| FR-007 RTL layout | T009, T052, T054 |
| FR-008 Semantic HTML + ARIA | T031, T033, T056, T061 |
| FR-009 Alt text | T072 |
| FR-010 Chatbot placeholder | T056-T062 |
| FR-011 Mobile responsive | T069 |
| FR-012 Keyboard navigation | T061, T068 |
| FR-013 Difficulty indicators | T033-T041 |
| FR-014 4 chapters scaffolded | T015-T030 |

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [USn] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution principles verified: Context7-First, TDD, Accessibility, Smallest Diff
- Route implementation to `book-builder` subagent per CLAUDE.md
