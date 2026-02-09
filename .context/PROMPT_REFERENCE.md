# 🎯 QUICK PROMPT REFERENCE

Use these prompts during development for common situations.

## 📚 GETTING STARTED

```
[Use START_HERE.md - paste that entire file into Claude Code]
```

---

## ✅ CONTINUING DEVELOPMENT

### After Completing a Task
```
Task [X.X] is complete and tested. Please:
1. Review the implementation against the acceptance criteria in tasks.md
2. If it passes, commit with message: "Complete task X.X: [description]"
3. Then move to Task [X.X+1]
```

### Starting a New Phase
```
We've completed Phase [N]. Before starting Phase [N+1]:
1. Review all code against technical.md architecture
2. Run all tests and verify they pass
3. Check test coverage
4. Then give me a summary and start Phase [N+1], Task 1
```

---

## 🔍 DEBUGGING & CLARIFICATION

### When Tests Fail
```
The tests for [component] are failing. Please:
1. Show me the actual vs expected output
2. Check the implementation against the spec in technical.md
3. Identify the root cause
4. Fix and re-run tests
```

### When Spec is Unclear
```
The acceptance criteria for Task [X.X] is unclear on [specific point].
Please check:
1. The detailed spec in technical.md Section [Y]
2. Related context in specs.md
3. Then clarify what the expected behavior should be
```

### When Implementation Differs from Spec
```
Wait - I need to verify this against the spec.
Please check [component] against:
1. The architecture in technical.md
2. The requirements in specs.md
3. The acceptance criteria in tasks.md Task [X.X]

Does it match? If not, what needs to change?
```

---

## 🧪 TESTING

### Write Tests for Component
```
Please write comprehensive tests for [component]:
1. Happy path (normal usage)
2. Edge cases (empty inputs, large inputs, boundary conditions)
3. Error cases (invalid data, missing dependencies)

Use pytest and aim for >90% coverage.
```

### Run Full Test Suite
```
Please run the full test suite:
1. Run: pytest tests/ -v --cov=ateam
2. Show me the coverage report
3. Identify any gaps in test coverage
4. Any failures or warnings?
```

---

## 📝 CODE QUALITY

### Review Implementation
```
Please review [file/component] for:
1. Compliance with technical.md architecture
2. Python best practices (type hints, docstrings, error handling)
3. Code quality issues
4. Potential bugs or edge cases

Suggest improvements.
```

### Refactor Code
```
The [component] works but could be cleaner. Please refactor to:
1. Follow the patterns in technical.md
2. Improve readability
3. Reduce complexity
4. Add missing type hints/docstrings
```

---

## 🎨 FEATURES & ENHANCEMENTS

### Add Error Handling
```
Please add proper error handling to [component]:
1. Use the ErrorMessages catalog from utils/errors.py
2. Include actionable error messages
3. Handle edge cases gracefully
4. Add tests for error conditions
```

### Implement Optional Feature
```
I'd like to add [feature] to [component].
Before implementing:
1. Check if it conflicts with specs
2. Propose where it fits in the architecture
3. Suggest how to test it
4. Then implement if I approve
```

---

## 📦 PACKAGING & DEPLOYMENT

### Prepare for Distribution
```
We're ready to prepare for distribution. Please:
1. Update pyproject.toml with correct version and metadata
2. Ensure all dependencies are listed
3. Create setup.sh and setup.bat scripts
4. Test installation in a clean virtual environment
5. Generate a release checklist
```

### Create Documentation
```
Please generate [type] documentation:
1. For [component/feature]
2. Include usage examples
3. Cover common issues
4. Match the tone/style in README.md
```

---

## 🐛 COMMON ISSUES

### Import Errors
```
I'm getting import errors. Please:
1. Check pyproject.toml dependencies
2. Verify __init__.py files exist
3. Check for circular imports
4. Fix and test: python -c "import ateam"
```

### Tests Not Found
```
pytest can't find tests. Please verify:
1. Test files are named test_*.py
2. Test functions start with test_
3. tests/ directory has __init__.py
4. pytest is installed
```

### Type Errors
```
mypy is reporting type errors. Please:
1. Run: mypy ateam/
2. Fix all type issues
3. Ensure all functions have type hints
4. Re-run mypy until clean
```

---

## 💡 PRODUCTIVITY TIPS

### Batch Similar Tasks
```
Looking at tasks [X.1] through [X.4], they're similar.
Can you implement all of them together:
1. Following the same patterns
2. Using shared helper functions
3. With a unified test suite
```

### Generate Boilerplate
```
Please generate the boilerplate for:
1. [Component] class following technical.md structure
2. Include all required methods with docstrings
3. Add type hints
4. Include basic error handling
5. Don't implement logic yet - just structure

I'll review before you implement.
```

### Create Examples
```
Please create 3 example files demonstrating:
1. [Feature/concept]
2. With different complexity levels (simple, medium, advanced)
3. Each should be runnable
4. Include comments explaining key points
```

---

## 🎓 LEARNING & EXPLORATION

### Explain Design Decision
```
Why did we choose [technology/pattern] for [component]?
Please explain:
1. The reasoning from technical.md
2. Alternatives we considered
3. Trade-offs we accepted
4. When this might need to change
```

### Compare Approaches
```
Before implementing [feature], let's explore options:
1. List 2-3 different approaches
2. Pros/cons of each
3. Which fits our architecture best
4. Your recommendation

Then I'll choose which to implement.
```

---

## 📊 PROGRESS TRACKING

### Show Project Status
```
Please give me a project status update:
1. Which phase/tasks are complete
2. What's currently in progress
3. Test coverage percentage
4. Any blockers or issues
5. Estimated % complete
```

### Update Tasks Checklist
```
We've completed tasks [X.1] through [X.N].
Please update tasks.md:
1. Mark completed tasks with [x]
2. Note current task
3. Show what's remaining in this phase
```

---

## 🚀 QUICK WINS

These are the most common prompts you'll use:

**Starting development:**
→ Use START_HERE.md

**After each task:**
→ "Task X.X complete. Review, commit, move to X.X+1"

**When stuck:**
→ "Check technical.md section [Y] for how to implement [feature]"

**Before committing:**
→ "Run all tests and verify they pass"

**Code review:**
→ "Review [file] against specs for compliance and quality"

---

**Remember:** The specs are your source of truth. When in doubt, check:
1. tasks.md for WHAT to build
2. technical.md for HOW to build it  
3. specs.md for WHY we're building it

Good luck! 🚀
