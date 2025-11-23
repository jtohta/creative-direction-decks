<!--
  Sync Impact Report - Constitution v1.5.0
  
  Version: 1.0.0 → ... → 1.4.0 → 1.5.0 (MINOR - Recommended Workflow)
  
  Previous Changes Summary:
  
  v1.0.1: External service testing (HTTP recording/replay)
  v1.0.2: Test naming conventions (language-agnostic)
  v1.0.3: E2E timing clarification (acceptance tests after implementation)
  v1.1.0: Test Execution Strategy (when to run different test scopes)
  v1.1.1: Removed arbitrary coverage percentage targets
  v1.2.0: Exception Process (replaced Complexity Justification, MANDATORY terminology)
  v1.2.1: Test failure handling guidance (fix implementation first)
  v1.3.0: Test Data Management (isolation, parallel execution, resource cleanup)
  v1.4.0: Quick Reference (8 key rules for quick lookup)
  
  v1.5.0 Changes (NEW):
  - Added "Recommended Workflow" section before Governance
    * NEW: Command sequence for implementing features
    * Minimum viable workflow: specify → plan → tasks → implement
    * Recommended workflow: specify → clarify → plan → tasks → analyze → implement
    * Quality gate details: clarify validates testable requirements, analyze verifies TDD
    * Optional checklist for final validation after implementation
    * Embeds constitution compliance into development process
    * Makes it actionable: clear steps to follow the constitution
  
  Templates Status:
  ✅ plan-template.md - No changes required (workflow is process guidance)
  ✅ spec-template.md - No changes required (specification format unchanged)
  ✅ tasks-template.md - No changes required (task structure unchanged)
  
  Follow-up TODOs:
  - None - Recommended Workflow is process guidance
  
  Rationale: MINOR version bump - adds NEW section with substantive operational
  guidance on HOW to use the speckit commands to enforce constitution compliance.
  This is a significant addition that transforms the constitution from "what to do"
  into "how to do it" with concrete command sequences and quality gates.
-->

# Creative Direction Decks Constitution

## Quick Reference

**High-level summary for quick lookup. See sections below for full details.**

### Core Testing Rules

1. **Write Tests First** - Follow Red-Green-Refactor cycle (MANDATORY)
   - RED: Write failing tests
   - GREEN: Implement to make tests pass
   - REFACTOR: Improve code quality while tests stay green

2. **Testing Trophy** - Focus on integration tests (most), some E2E tests, unit tests only for pure functions

3. **Test Execution Strategy**:
   - Active development: Run specific tests for fast feedback
   - Phase checkpoints: Run all feature tests
   - Before commits: Run full test suite

4. **Exception Process** - Use when TDD cannot be followed (document what/why/when/return path)

5. **Test Isolation** - Tests must be isolated with their own data, no shared state, clean up resources

6. **Test Contract** - Tests define the contract, implementation must conform (fix implementation first when tests fail)

7. **E2E Timing** - E2E tests written AFTER implementation to validate integration

8. **External Services** - Use HTTP recording (VCR-style) for external services, not mocks

## Core Principles

### I. Test-First Development (MANDATORY)

**Red-Green-Refactor cycle MUST be strictly enforced for all code changes:**

- **RED**: Write failing tests before any implementation code
  - Tests MUST be written and reviewed before implementation begins
  - Tests MUST fail initially, proving they test something real
  - No implementation code without corresponding failing tests

- **GREEN**: Write minimal code to make tests pass
  - Implement only what's needed to satisfy the test
  - Focus on making it work, not making it perfect
  - All tests MUST pass before proceeding to refactor

- **REFACTOR**: Improve code quality while maintaining passing tests
  - Clean up implementation without changing behavior
  - Tests MUST remain green throughout refactoring
  - No new functionality during refactor phase

**Exception Process**:

When TDD cannot be followed, document the exception with:
- **What**: Which principle/practice cannot be followed
- **Why**: Specific reason (legacy integration, spike/prototype, time-critical hotfix, etc.)
- **When**: Time-box for how long exception applies
- **Return Path**: Plan to return to TDD compliance (refactor, rewrite, etc.)

Exceptions require approval via:
- Code review acknowledgment for minor exceptions (single feature, < 1 week)
- Team lead/architect approval for major exceptions (> 1 week, core systems)

**Rationale**: Red-Green-Refactor ensures every line of code is testable, tested,
and serves a documented purpose. The failing test proves the test works; the
passing test proves the implementation works. Exceptions are sometimes necessary
but must be explicit, time-boxed, and include a plan to return to compliance.

### II. Testing Trophy Paradigm (MANDATORY)

**Test distribution MUST follow the Testing Trophy model:**

```
        /\
       /  \  E2E (Few)
      /    \
     /------\
    / Integration \ (Most)
   /--------------\
  /     Unit      \ (Least - Pure Functions Only)
 /________________\
```

- **Integration Tests (60-70% of test suite)**: Primary testing focus - DRIVE implementation
  - Test multiple components working together
  - Test real data flows and business logic
  - Test service interactions and state management
  - Test API endpoints with real dependencies (HTTP recording for external services)
  - **Written FIRST** in RED phase to drive implementation design
  
- **End-to-End Tests (10-20% of test suite)**: Acceptance validation - VALIDATE integration
  - Test complete user workflows from UI to database
  - Test deployment configurations and environment setup
  - Focus on happy path and critical error scenarios
  - **Written AFTER implementation** to validate full system integration
  - Verify that all components work together from user's perspective
  
- **Unit Tests (10-20% of test suite)**: Pure functions only - DRIVE pure function implementation
  - ONLY write unit tests for pure functions (deterministic, no side effects)
  - NO unit tests for classes, services, or stateful components
  - Examples: data transformers, calculators, validators, formatters
  - **Written FIRST** in RED phase to drive pure function design

**Rationale**: Integration and unit tests drive implementation through TDD - they
are written first and guide design decisions. E2E tests validate that integrated
components work together correctly from the user's perspective - they test the
system after implementation. This approach provides comprehensive coverage while
maintaining practical TDD workflow.

### III. Integration-First Testing

**Integration tests are the foundation of test coverage:**

- Integration tests MUST cover:
  - New feature implementations
  - Changes to existing contracts or interfaces
  - Inter-service communication
  - Database operations and data persistence
  - Authentication and authorization flows
  - Error handling and edge cases

- Integration tests MUST use real implementations:
  - Real database instances (test database, not mocked)
  - Real service instances within the application
  - Actual HTTP requests/responses for APIs
  - Real file system operations (in test directories)

- **External Service Testing (HTTP Recording/Replay)**:
  - NEVER use mocks for external third-party services
  - USE HTTP recording frameworks (e.g., VCR.py, vcr.js, Go-VCR)
  - First test run: Make REAL HTTP requests to external services, record to YAML
  - Subsequent runs: Replay HTTP interactions from YAML files
  - Examples: Payment gateways, email services, external APIs, webhooks
  - Benefits: Test with real API responses without implementation-specific mocking
  
- **Untestable Components**:
  - If a component cannot be tested with real implementations or HTTP recording
    (e.g., specialized file systems, hardware interfaces, unique I/O operations)
  - SURFACE the issue immediately during test planning phase
  - Document why standard testing approaches don't apply
  - Request specific testing guidance before proceeding with implementation

**Rationale**: Integration tests verify that components work together correctly
in realistic conditions. HTTP recording captures real API behavior without
coupling tests to mock implementations. This approach tests actual responses
while maintaining test speed and reliability.

### IV. Pure Functions & Unit Testing

**Unit tests are reserved for pure functions:**

- A function qualifies for unit testing if it is:
  - **Deterministic**: Same input always produces same output
  - **No side effects**: Doesn't modify external state
  - **No I/O**: Doesn't read/write files, databases, or networks
  - **Stateless**: Doesn't depend on or modify mutable state

- Examples of unit-testable pure functions:
  ```
  ✓ formatDate(timestamp) → string
  ✓ calculateDiscount(price, percentage) → number
  ✓ validateEmail(email) → boolean
  ✓ transformData(input) → output
  ✗ UserService.createUser() - has side effects
  ✗ FileRepository.save() - performs I/O
  ✗ AuthMiddleware.verify() - depends on state
  ```

- If you're tempted to mock dependencies for a unit test, write an integration
  test instead

**Rationale**: Pure functions are naturally easy to test and don't require mocks.
Testing impure code with unit tests leads to brittle tests that break with
refactoring and provide false confidence through mocking.

### V. Test Coverage & Quality

**Test quality standards:**

- **Coverage philosophy**:
  - Integration tests MUST cover business logic comprehensively
  - E2E tests MUST cover all critical user journeys
  - Unit tests MUST cover all pure functions
  - Coverage metrics are indicators, not goals - meaningful tests matter more than percentages

- **Test quality checklist**:
  - [ ] Tests follow Arrange-Act-Assert pattern
  - [ ] Tests are atomic (one behavior per test)
  - [ ] Test names clearly describe what they test
  - [ ] Tests verify meaningful scenarios, not just code coverage
  - [ ] Tests fail when they should (verify by breaking implementation)
  - [ ] Tests are independent (can run in any order)

- **Meaningful test scenarios**:
  - Real-world use cases
  - Edge cases and boundary conditions
  - Error conditions and failure modes
  - Security vulnerabilities
  - Different input types/sizes/formats
  - Integration points between components

**Rationale**: High coverage numbers without meaningful tests provide false
confidence. Tests should verify real scenarios that could cause production
failures, not just exercise code paths.

## Development Workflow

### Test-Driven Development Workflow

**Every feature implementation MUST follow this workflow:**

1. **Specification Phase**:
   - Define user stories with acceptance criteria
   - Identify test scenarios (integration tests, unit tests, E2E scenarios)
   - Document expected behavior for all test types
   - E2E scenarios documented but automated tests written later

2. **Test Writing Phase (RED)** - Tests that drive implementation:
   - Write integration tests for feature behavior
   - Write unit tests for pure functions
   - Verify all tests FAIL
   - Get tests reviewed and approved
   - **Note**: E2E tests NOT written yet - implementation must exist first

3. **Implementation Phase (GREEN)**:
   - Write minimal code to pass first test
   - Run tests frequently
   - Add code incrementally to pass more tests
   - Stop when all integration and unit tests pass

4. **Refactor Phase**:
   - Improve code quality, readability, performance
   - Keep tests green throughout
   - No new functionality or test changes
   - Commit when refactoring complete

5. **Acceptance Validation Phase** - E2E tests validate integration:
   - Write E2E tests for critical user journeys
   - Run E2E tests to validate full system integration
   - E2E tests verify components work together from user perspective
   - Fix any integration issues discovered by E2E tests
   - All E2E tests MUST pass before feature is complete

6. **Final Integration & Validation**:
   - Run full test suite (unit + integration + E2E)
   - Verify no regressions
   - Review test coverage report
   - Validate against acceptance criteria

### Test Execution Strategy

**Run tests at appropriate scopes to balance fast feedback with comprehensive validation:**

- **During Active Development (RED/GREEN phases)**: Fast feedback loops
  - Run ONLY the specific test being written/modified
  - Verify test fails (RED) or passes (GREEN) immediately
  - Do NOT run full test suite after every test write
  - Goal: Immediate feedback on current work without waiting for full suite
  
- **At Phase Checkpoints**: Feature-level validation
  - End of RED phase: Run all integration + unit tests for current user story/feature
  - End of GREEN phase: Run all integration + unit tests for current user story/feature
  - End of REFACTOR phase: Run all tests for current user story/feature
  - End of ACCEPTANCE VALIDATION phase: Run all E2E tests for current user story
  - Goal: Verify phase completion without running unrelated tests
  
- **At Major Checkpoints**: Full suite validation
  - Before committing code
  - Before opening pull requests
  - During Final Integration & Validation phase
  - After merging feature branches
  - Goal: Comprehensive validation that nothing broke across the entire system

**Rationale**: Running the full test suite after every single test write wastes time
and creates unnecessary wait cycles. Fast feedback on specific tests during active
development maintains momentum. Checkpoint validation ensures quality gates are met
at appropriate milestones. Full suite validation catches integration issues before
code review and deployment.

**When Tests Fail at Checkpoints**:

When integration or unit tests fail during checkpoint validation:

1. **Assume the test is correct** - Tests were written first and reviewed, so trust them
2. **Fix the implementation first** - The implementation is what's being validated
3. **Only modify the test if**:
   - The test has a clear bug or incorrect assumption
   - Requirements changed after the test was written
   - The test is testing implementation details rather than behavior
4. **Document test changes** - If you must change a test, explain why in commit message

**Priority**: Implementation fixes > Test fixes. The test defines the contract; 
implementation must conform to it.

### Code Review Requirements

**Pull requests MUST include:**

- Link to tests written first (in RED phase)
- Evidence tests initially failed (commit history)
- All tests passing in GREEN phase
- Refactoring commits separate from feature commits
- Test coverage report showing integration test focus
- No production code commits before test commits

### Quality Gates

**Before merging, verify:**

- [ ] Red-Green-Refactor cycle documented in commits
- [ ] Integration tests cover primary behavior
- [ ] Pure functions have unit tests
- [ ] E2E tests for critical paths (if applicable)
- [ ] No mocking of internal services in integration tests
- [ ] External services use HTTP recording (VCR-style), not mocks
- [ ] Test quality checklist satisfied
- [ ] All tests passing
- [ ] Coverage targets met

## Testing Standards

### Test Organization

```
tests/
├── e2e/                    # End-to-end tests (10-20%)
│   ├── user_journeys/
│   └── critical_paths/
├── integration/            # Integration tests (60-70%)
│   ├── features/
│   ├── services/
│   └── api/
└── unit/                   # Unit tests (10-20%)
    └── pure_functions/
```

### Test Naming Conventions

**Test names MUST clearly describe what they test:**

- **Integration tests**: Describe the feature behavior and context
  - Example: `test_user_registration_with_email_verification`
  - Example: `test_order_processing_updates_inventory`
  
- **E2E tests**: Describe the complete user journey
  - Example: `test_complete_checkout_flow_with_payment`
  - Example: `test_user_signup_to_first_purchase`
  
- **Unit tests**: Describe the function and input scenario
  - Example: `test_calculate_discount_with_zero_percentage`
  - Example: `test_validate_email_rejects_invalid_format`

**Note**: Test organization (one test per file vs. multiple tests per file) is
implementation-specific and should follow language/framework conventions.

### Arrange-Act-Assert Pattern

**All tests MUST follow AAA structure:**

```python
def test_feature_behavior():
    # ARRANGE: Set up test data and preconditions
    user = create_test_user(email="test@example.com")
    
    # ACT: Execute the behavior being tested
    result = user_service.authenticate(user.email, "password")
    
    # ASSERT: Verify the expected outcome
    assert result.is_authenticated is True
    assert result.user.id == user.id
```

### Test Data Management

**Tests MUST be isolated and support parallel execution:**

- **Test Isolation**:
  - Each test MUST set up its own data in the Arrange phase
  - Tests MUST NOT depend on pre-seeded data or shared state
  - Tests MUST NOT affect other tests (no shared state between tests)
  - Tests MUST be runnable in any order (no implicit dependencies)
  
- **Parallel Execution Support**:
  - Test data strategy MUST support concurrent test execution
  - Use isolated resources per test:
    - Database: Separate transactions or test database instances
    - File system: Separate temporary directories per test
    - Network: Isolated ports or mock servers per test
  - Use test data builders or factories for object creation
  - Avoid manual object construction that leads to duplication
  
- **Resource Cleanup**:
  - Tests MUST clean up resources after completion
  - Database records, temporary files, network connections, etc.
  - Cleanup applies to all stateful resources (databases, files, network, etc.)
  - Failed tests should not leave orphaned resources

- **Migration and Seeding**:
  - Database migrations should be tested separately when possible
  - Seeding is for development environments only, NOT for tests
  - Tests create their own data (self-contained)
  - No test should assume specific data exists beforehand

**Rationale**: Test isolation enables fast, parallel execution and prevents flaky
tests caused by shared state. Self-contained tests are easier to understand,
debug, and maintain. Clean resource management prevents test pollution and
ensures consistent results across test runs.

## Recommended Workflow

**Command sequence for implementing features while following this constitution:**

### Recommended Workflow (Constitution Compliance)

For thorough constitution compliance and quality assurance:

```
1. /speckit.specify   - Define what to build (user stories, acceptance criteria)
2. /speckit.clarify   - Validate requirements are testable (quality gate)
3. /speckit.plan      - Create technical plan with TDD approach
4. /speckit.tasks     - Generate RED-GREEN-REFACTOR task breakdown
5. /speckit.analyze   - Verify TDD workflow and test distribution (quality gate)
6. /speckit.implement - Execute tasks following TDD workflow
7. /speckit.checklist - Final validation of constitution compliance (optional)
```

### Quality Gate Details

**`/speckit.clarify` (After specify)**:
- Validates requirements are testable and unambiguous
- Ensures acceptance criteria are clear enough for RED phase
- Identifies any areas needing more specification
- Catches requirement issues before planning begins

**`/speckit.analyze` (After tasks)**:
- Verifies TDD workflow is present (tests before implementation)
- Checks test distribution follows Testing Trophy paradigm
- Identifies gaps in test coverage or task ordering
- Ensures constitution compliance before implementation starts

**`/speckit.checklist` (After implement)** - Optional:
- Final validation that tests were written first
- Verifies all tests passing and properly isolated
- Confirms test-first commits in history
- Documents any exceptions taken during implementation

**Rationale**: The clarify and analyze commands act as quality gates to keep
developers honest about following TDD principles. These checkpoints catch issues
early when they are cheap to fix, rather than discovering problems after
implementation is complete. This workflow embeds constitution compliance into
the development process rather than treating it as an afterthought.

## Governance

### Constitution Authority

This constitution supersedes all other development practices. When conflicts
arise between this constitution and other guidelines, the constitution takes
precedence.

### Amendment Process

Constitution amendments require:

1. **Proposal**: Document proposed change with rationale
2. **Review**: Team review and discussion of implications
3. **Approval**: Consensus approval (or designated authority)
4. **Migration**: Update all dependent templates and documentation
5. **Version Increment**: Follow semantic versioning (MAJOR.MINOR.PATCH)

### Compliance Review

- All pull requests MUST verify constitution compliance
- Quality gates enforce TDD and testing trophy standards
- Exceptions MUST follow the Exception Process defined in principles
- Regular audits of test suite distribution (integration vs unit vs E2E)

### Exception Process

Deviations from constitutional principles are permitted when necessary, following this process:

**1. Document the Exception**:
- Which principle cannot be followed (e.g., Test-First Development, Testing Trophy)
- Specific reason (legacy code integration, urgent hotfix, prototype/spike, etc.)
- Scope (which feature/component/files affected)
- Time-box (how long exception will last)

**2. Get Appropriate Approval**:
- **Minor exceptions** (< 1 week, single feature): Code review acknowledgment required
- **Major exceptions** (> 1 week, core systems): Team lead or architect approval required
- **Systemic exceptions** (affects multiple teams/projects): Constitution amendment required

**3. Include Return Path**:
- Plan to return to compliance (e.g., "Refactor after release", "Rewrite in Q2")
- Acceptance criteria for when exception ends
- Who is responsible for compliance restoration

**4. Track & Review**:
- Add exception to PR description and commit messages
- Review active exceptions in retrospectives
- Automatically close exceptions when time-box expires

**Common Valid Exceptions**:
- Emergency production hotfixes (immediate fix, retrofit tests after)
- Exploratory spikes/prototypes (throwaway code, not production-bound)
- Legacy system integration (existing untestable code, document boundaries)
- Third-party library constraints (untestable framework code, isolate in adapters)

**Version**: 1.5.0 | **Ratified**: 2025-11-23 | **Last Amended**: 2025-11-23
