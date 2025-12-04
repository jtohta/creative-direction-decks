# Project: Creative Direction Decks

TypeForm-style Streamlit questionnaire for creative direction intake.

## Git Workflow Rules

**CRITICAL: NEVER push directly to main**
- ALWAYS create a feature branch for ANY changes
- ALWAYS push to the feature branch, never to main
- Let the user create PRs and merge
- Branch naming: `feature-name` or `fix-issue-description`

## Commands
- **Run app**: `streamlit run app.py`
- **Run all tests**: `pytest`
- **Run single test**: `pytest tests/path/to/test_file.py::test_function_name -v`
- **Run by marker**: `pytest -m unit` | `pytest -m integration` | `pytest -m e2e`
- **Lint**: `ruff check .`

## Architecture
- **src/**: Application code (models/, services/, config/, utils/)
- **tests/**: Test files mirroring src structure (unit/, integration/, e2e/)
- **app.py**: Streamlit entry point

## Code Style
- Python 3.13+, Streamlit 1.39+, boto3 for R2 storage, yagmail/smtplib for email
- Use type hints; follow PEP 8; prefer dataclasses for models
- Use pytest-vcr for external HTTP calls (record/replay pattern, no mocks)
- Test naming: `test_<feature>_<scenario>` (e.g., `test_validate_email_rejects_invalid_format`)

---

# AI Agent Development Guidelines

**Purpose**: Framework-agnostic guidelines for AI agents working on software projects.  
**Last Updated**: 2025-12-01

## Core Principles

### 1. Test-Driven Development (TDD) - MANDATORY

**Red-Green-Refactor cycle MUST be strictly enforced:**

- **RED**: Write failing tests before any implementation code
  - Tests must be written and reviewed before implementation begins
  - Tests must fail initially, proving they test something real
  - No implementation code without corresponding failing tests

- **GREEN**: Write minimal code to make tests pass
  - Implement only what's needed to satisfy the test
  - Focus on making it work, not making it perfect
  - All tests must pass before proceeding to refactor

- **REFACTOR**: Improve code quality while maintaining passing tests
  - Clean up implementation without changing behavior
  - Tests must remain green throughout refactoring
  - No new functionality during refactor phase

**Exception Process**: When TDD cannot be followed, document:
- **What**: Which principle cannot be followed
- **Why**: Specific reason (legacy integration, spike/prototype, time-critical hotfix, etc.)
- **When**: Time-box for how long exception applies
- **Return Path**: Plan to return to TDD compliance

### 2. Testing Trophy Paradigm - MANDATORY

**Test distribution MUST follow the Testing Trophy model:**

```
        /\
       /  \  E2E (Few - 10-20%)
      /    \
     /------\
    / Integration \ (Most - 60-70%)
   /--------------\
  /     Unit      \ (Least - 10-20%, Pure Functions Only)
 /________________\
```

- **Integration Tests (60-70%)**: Primary testing focus - DRIVE implementation
  - Test multiple components working together
  - Test real data flows and business logic
  - Test service interactions and state management
  - Test API endpoints with real dependencies
  - **Written FIRST** in RED phase to drive implementation design

- **End-to-End Tests (10-20%)**: Acceptance validation - VALIDATE integration
  - Test complete user workflows from UI to database
  - Test deployment configurations and environment setup
  - Focus on happy path and critical error scenarios
  - **Written AFTER implementation** to validate full system integration

- **Unit Tests (10-20%)**: Pure functions only - DRIVE pure function implementation
  - ONLY write unit tests for pure functions (deterministic, no side effects)
  - NO unit tests for classes, services, or stateful components
  - Examples: data transformers, calculators, validators, formatters
  - **Written FIRST** in RED phase to drive pure function design

### 3. Integration-First Testing

**Integration tests are the foundation of test coverage:**

- Integration tests must cover:
  - New feature implementations
  - Changes to existing contracts or interfaces
  - Inter-service communication
  - Database operations and data persistence
  - Authentication and authorization flows
  - Error handling and edge cases

- Integration tests must use real implementations:
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

### 4. Pure Functions & Unit Testing

**Unit tests are reserved for pure functions:**

A function qualifies for unit testing if it is:
- **Deterministic**: Same input always produces same output
- **No side effects**: Doesn't modify external state
- **No I/O**: Doesn't read/write files, databases, or networks
- **Stateless**: Doesn't depend on or modify mutable state

Examples:
- ✓ `formatDate(timestamp) → string`
- ✓ `calculateDiscount(price, percentage) → number`
- ✓ `validateEmail(email) → boolean`
- ✗ `UserService.createUser()` - has side effects
- ✗ `FileRepository.save()` - performs I/O
- ✗ `AuthMiddleware.verify()` - depends on state

**If you're tempted to mock dependencies for a unit test, write an integration test instead.**

### 5. Test Quality Standards

**Test quality checklist:**
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Tests are atomic (one behavior per test)
- [ ] Test names clearly describe what they test
- [ ] Tests verify meaningful scenarios, not just code coverage
- [ ] Tests fail when they should (verify by breaking implementation)
- [ ] Tests are independent (can run in any order)

**Meaningful test scenarios:**
- Real-world use cases
- Edge cases and boundary conditions
- Error conditions and failure modes
- Security vulnerabilities
- Different input types/sizes/formats
- Integration points between components

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

**When Tests Fail at Checkpoints:**
1. **Assume the test is correct** - Tests were written first and reviewed, so trust them
2. **Fix the implementation first** - The implementation is what's being validated
3. **Only modify the test if**:
   - The test has a clear bug or incorrect assumption
   - Requirements changed after the test was written
   - The test is testing implementation details rather than behavior
4. **Document test changes** - If you must change a test, explain why in commit message

**Priority**: Implementation fixes > Test fixes. The test defines the contract; implementation must conform to it.

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

## Code Quality Principles

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
- [ ] Coverage targets met (meaningful tests, not arbitrary percentages)

## General Development Guidelines

### Code Style

- Follow language-specific conventions and style guides
- Use consistent naming conventions across the codebase
- Prefer guard clauses over nested if statements
- Write self-documenting code with clear variable and function names
- Keep functions small and focused on a single responsibility

### Documentation

- Write clear commit messages that explain what and why
- Document complex algorithms and business logic
- Keep README files up to date with setup and usage instructions
- Document API contracts and interfaces
- Include examples in documentation when helpful

### Error Handling

- Provide user-friendly error messages
- Log errors with sufficient context for debugging
- Handle edge cases gracefully
- Fail fast with clear error messages rather than silent failures
- Use appropriate error types/exceptions for different failure modes

### Security

- Never commit secrets, API keys, or credentials
- Use environment variables or secure secret management
- Validate and sanitize all user inputs
- Follow security best practices for authentication and authorization
- Keep dependencies up to date to address security vulnerabilities

## Quick Reference

**8 Key Rules for Quick Lookup:**

1. **Write Tests First** - Follow Red-Green-Refactor cycle (MANDATORY)
2. **Testing Trophy** - Focus on integration tests (most), some E2E tests, unit tests only for pure functions
3. **Test Execution Strategy** - Run specific tests during development, full suite at checkpoints
4. **Exception Process** - Use when TDD cannot be followed (document what/why/when/return path)
5. **Test Isolation** - Tests must be isolated with their own data, no shared state, clean up resources
6. **Test Contract** - Tests define the contract, implementation must conform (fix implementation first when tests fail)
7. **E2E Timing** - E2E tests written AFTER implementation to validate integration
8. **External Services** - Use HTTP recording (VCR-style) for external services, not mocks

## Notes

- These guidelines are framework-agnostic and can be adapted to any technology stack
- The principles prioritize test quality and meaningful coverage over arbitrary metrics
- Focus on user value and business needs, not implementation details
- When in doubt, prefer integration tests over unit tests with mocks
- Tests should verify real scenarios that could cause production failures

