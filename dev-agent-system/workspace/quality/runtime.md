# Quality Crew - Runtime Context

## Current Status
- **Crew**: Quality
- **Agents**: Unit Tester Agent, Linter Agent, Code Reviewer Agent
- **Runtime Focus**: Testing and code quality assurance

## Runtime Memory
- **System Memory**: `../../memory/crew_memory/` and `../../memory/global_kb/`
- **Workspace**: `../` (shared runtime communication)
- **Output**: `../../output/reports/` (quality reports output)

## Current Tasks
<!-- Active tasks for quality crew will be populated here -->

## Agent Status
- **Unit Tester Agent**: Standby
- **Linter Agent**: Standby
- **Code Reviewer Agent**: Standby

## Runtime Files
- This folder contains temporary runtime files for quality crew
- Files are created and managed during agent execution
- Context is maintained for coordination between quality agents

## Communication
- **Task Queue**: `../todo.md`
- **Progress**: `../progress.md`
- **System Context**: `../activeContext.md`
- **Tech Context**: `../techContext.md`