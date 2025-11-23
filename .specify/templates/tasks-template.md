---

description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Per the project constitution, Test-Driven Development is MANDATORY. All feature tasks MUST include tests written FIRST following Red-Green-Refactor cycle. Focus on integration tests, with some E2E tests and unit tests only for pure functions. See constitution Exception Process if TDD cannot be followed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per implementation plan
- [ ] T002 Initialize [language] project with [framework] dependencies
- [ ] T003 [P] Configure linting and formatting tools

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T004 Setup database schema and migrations framework
- [ ] T005 [P] Implement authentication/authorization framework
- [ ] T006 [P] Setup API routing and middleware structure
- [ ] T007 Create base models/entities that all stories depend on
- [ ] T008 Configure error handling and logging infrastructure
- [ ] T009 Setup environment configuration management

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 - RED Phase (MANDATORY) ⚠️

> **CONSTITUTION REQUIREMENT: Write these tests FIRST, ensure they FAIL before implementation**
> **Testing Trophy: Integration tests (60-70%) + Unit tests for pure functions (10-20%)**
> **Note: E2E tests written AFTER implementation in Acceptance Validation phase**

- [ ] T010 [P] [US1] Integration test for [core feature behavior] in tests/integration/test_[name].py
- [ ] T011 [P] [US1] Integration test for [edge case/error scenario] in tests/integration/test_[name].py
- [ ] T012 [P] [US1] Unit tests for pure functions in tests/unit/test_[name].py (if pure functions exist)

### Implementation for User Story 1 - GREEN Phase

> **RED phase complete (tests written and failing) - Now implement to make tests GREEN**

- [ ] T013 [P] [US1] Create [Entity1] model in src/models/[entity1].py
- [ ] T014 [P] [US1] Create [Entity2] model in src/models/[entity2].py
- [ ] T015 [US1] Implement [Service] in src/services/[service].py (depends on T013, T014)
- [ ] T016 [US1] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T017 [US1] Add validation and error handling
- [ ] T018 [US1] Add logging for user story 1 operations

### Refactor for User Story 1 - REFACTOR Phase

> **GREEN phase complete (tests passing) - Now REFACTOR to improve code quality**

- [ ] T019 [US1] Refactor for code quality, readability, performance (keep tests green)

### Acceptance Validation for User Story 1 - E2E Tests

> **Implementation complete - Now write E2E tests to VALIDATE full system integration**
> **Testing Trophy: E2E tests (10-20%) validate user journeys work end-to-end**

- [ ] T020 [P] [US1] E2E test for [critical user journey] in tests/e2e/test_[name].py (if critical path)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 - RED Phase (MANDATORY) ⚠️

> **CONSTITUTION REQUIREMENT: Write these tests FIRST, ensure they FAIL before implementation**
> **Note: E2E tests written AFTER implementation in Acceptance Validation phase**

- [ ] T021 [P] [US2] Integration test for [core feature behavior] in tests/integration/test_[name].py
- [ ] T022 [P] [US2] Integration test for [edge case/error scenario] in tests/integration/test_[name].py
- [ ] T023 [P] [US2] Unit tests for pure functions in tests/unit/test_[name].py (if pure functions exist)

### Implementation for User Story 2 - GREEN Phase

> **RED phase complete (tests written and failing) - Now implement to make tests GREEN**

- [ ] T024 [P] [US2] Create [Entity] model in src/models/[entity].py
- [ ] T025 [US2] Implement [Service] in src/services/[service].py
- [ ] T026 [US2] Implement [endpoint/feature] in src/[location]/[file].py
- [ ] T027 [US2] Integrate with User Story 1 components (if needed)

### Refactor for User Story 2 - REFACTOR Phase

> **GREEN phase complete (tests passing) - Now REFACTOR to improve code quality**

- [ ] T028 [US2] Refactor for code quality, readability, performance (keep tests green)

### Acceptance Validation for User Story 2 - E2E Tests

> **Implementation complete - Now write E2E tests to VALIDATE full system integration**

- [ ] T029 [P] [US2] E2E test for [critical user journey] in tests/e2e/test_[name].py (if critical path)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 - RED Phase (MANDATORY) ⚠️

> **CONSTITUTION REQUIREMENT: Write these tests FIRST, ensure they FAIL before implementation**
> **Note: E2E tests written AFTER implementation in Acceptance Validation phase**

- [ ] T030 [P] [US3] Integration test for [core feature behavior] in tests/integration/test_[name].py
- [ ] T031 [P] [US3] Integration test for [edge case/error scenario] in tests/integration/test_[name].py
- [ ] T032 [P] [US3] Unit tests for pure functions in tests/unit/test_[name].py (if pure functions exist)

### Implementation for User Story 3 - GREEN Phase

> **RED phase complete (tests written and failing) - Now implement to make tests GREEN**

- [ ] T033 [P] [US3] Create [Entity] model in src/models/[entity].py
- [ ] T034 [US3] Implement [Service] in src/services/[service].py
- [ ] T035 [US3] Implement [endpoint/feature] in src/[location]/[file].py

### Refactor for User Story 3 - REFACTOR Phase

> **GREEN phase complete (tests passing) - Now REFACTOR to improve code quality**

- [ ] T036 [US3] Refactor for code quality, readability, performance (keep tests green)

### Acceptance Validation for User Story 3 - E2E Tests

> **Implementation complete - Now write E2E tests to VALIDATE full system integration**

- [ ] T037 [P] [US3] E2E test for [critical user journey] in tests/e2e/test_[name].py (if critical path)

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests for newly identified pure functions in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story (Red-Green-Refactor + Acceptance Validation)

1. **RED Phase**: Tests MUST be written FIRST and FAIL before implementation
   - Write all integration tests (primary focus - 60-70%)
   - Write unit tests for pure functions (if any - 10-20%)
   - **Do NOT write E2E tests yet** - implementation must exist first
   - Verify all tests FAIL (proves tests work)
2. **GREEN Phase**: Implement minimal code to pass tests
   - Models before services
   - Services before endpoints
   - Core implementation before integration
   - All integration and unit tests MUST pass before refactor
3. **REFACTOR Phase**: Improve code quality while keeping tests green
   - Clean up, optimize, improve readability
   - Tests stay green throughout refactoring
4. **ACCEPTANCE VALIDATION Phase**: Write E2E tests to validate integration
   - Write E2E tests for critical user journeys (10-20%)
   - Validate full system works from user perspective
   - All E2E tests MUST pass
5. Story complete and validated before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# RED Phase: Launch integration and unit tests together (MANDATORY):
Task: "Integration test for [core feature behavior] in tests/integration/test_[name].py"
Task: "Integration test for [edge case/error scenario] in tests/integration/test_[name].py"
Task: "Unit tests for pure functions in tests/unit/test_[name].py"
# Note: E2E tests NOT written yet - wait until after implementation

# GREEN Phase: Launch all models together:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"

# REFACTOR Phase: After tests pass
Task: "Refactor for code quality, readability, performance"

# ACCEPTANCE VALIDATION Phase: Now write E2E tests
Task: "E2E test for [critical user journey] in tests/e2e/test_[name].py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

### Task Conventions
- [P] tasks = different files, no dependencies (can run in parallel)
- [Story] label maps task to specific user story for traceability (e.g., US1, US2, US3)
- Each user story should be independently completable and testable

### TDD Requirements (Constitution Compliance)
- **RED**: Write integration and unit tests FIRST, verify they FAIL before any implementation
  - Integration tests (60-70%) - drive implementation design
  - Unit tests (10-20%) - for pure functions only
  - **E2E tests NOT written yet** - wait for Acceptance Validation phase
- **GREEN**: Implement code to pass integration/unit tests, commit when tests pass
- **REFACTOR**: Improve code quality while keeping tests green, commit when complete
- **ACCEPTANCE VALIDATION**: Write E2E tests (10-20%) after implementation to validate full system
- Testing Trophy: Integration-first (60-70%), E2E after implementation (10-20%), unit for pure functions (10-20%)
- No implementation code without failing integration/unit tests first

### Workflow
- Commit after each Red-Green-Refactor-Acceptance cycle or logical group
- E2E tests validate integration after implementation completes
- Stop at any checkpoint to validate story independently
- Review test distribution regularly (ensure integration test focus)
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
