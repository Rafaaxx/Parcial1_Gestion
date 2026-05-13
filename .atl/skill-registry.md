# Skill Registry — food-store

**Generated**: 2026-05-12
**Source**: SDD Init scan

---

## Available Skills

### User-Level Skills

#### `~/.config/opencode/skills/`

| Skill | Description | Trigger |
|-------|-------------|---------|
| `branch-pr` | PR creation workflow with issue-first enforcement | Creating PR, opening PR, preparing for review |
| `find-skills` | Helps users discover and install agent skills | "how do I do X", "find a skill for X" |
| `go-testing` | Go testing patterns for Bubbletea TUI | Writing Go tests, teatest, test coverage |
| `issue-creation` | Issue creation with issue-first enforcement | Creating GitHub issue, reporting bug, feature request |
| `judgment-day` | Parallel adversarial review protocol | User says "judgment day", "dual review", "juzgar" |
| `sdd-apply` | Implements tasks from a change, writing actual code | Implementing one or more tasks from a change |
| `sdd-archive` | Syncs delta specs to main specs and archives | Archiving a change after implementation and verification |
| `sdd-design` | Creates technical design document with architecture decisions | Writing/updating technical design for a change |
| `sdd-explore` | Explores and investigates ideas before committing | Thinking through a feature, investigating codebase |
| `sdd-init` | Initializes SDD context in any project | User wants to initialize SDD in a project |
| `sdd-onboard` | Guided end-to-end SDD workflow walkthrough | Onboarding through full SDD cycle |
| `sdd-propose` | Creates a change proposal with intent, scope, approach | Creating/updating a proposal for a change |
| `sdd-spec` | Writes specifications with requirements and scenarios | Writing/updating specs for a change |
| `sdd-tasks` | Breaks down a change into implementation task checklist | Creating/updating task breakdown for a change |
| `sdd-verify` | Validates implementation matches specs, design, and tasks | Verifying completed/partial changes |
| `skill-creator` | Creates new AI agent skills | Creating skill, adding instructions, documenting patterns |
| `skill-registry` | Creates/updates skill registry for the current project | Updating skills, scanning conventions |

#### `~/.agents/skills/`

| Skill | Description | Trigger |
|-------|-------------|---------|
| `architecture-patterns` | Implement proven backend architecture patterns | Designing clean architecture, refactoring monolith, implementing hexagonal/onion patterns, debugging dependency cycles |

#### `~/.cursor/skills/` and `~/.opencode/skills/`

| Skill | Description | Trigger |
|-------|-------------|---------|
| `openspec-apply-change` | Implements tasks from an OpenSpec change | When user wants to implement/continue tasks |
| `openspec-archive-change` | Archives a completed change | When finalizing a change after implementation |
| `openspec-explore` | Explore mode for investigating ideas | When thinking through a feature before/during a change |
| `openspec-propose` | Proposes a new change with all artifacts | When describing what to build |

> Note: openspec-* skills in `.cursor/skills/` and `.opencode/skills/` are duplicates of those in `~/.config/opencode/skills/`. Only `.config/opencode/skills/` versions are loaded as available skills.

### Project-Level Skills

**Not found** — no project-level skills in `.agent/skills/`, `.claude/skills/`, `.gemini/skills/`, `.cursor/skills/`, or `skills/`.

---

## Project Conventions

### Index File: `agents.md`

Located at project root. Contains:

1. **Role Definition**: Food Store Project Architect & Senior Developer
2. **Truth Source**: Read `docs/Integrador.txt`, `docs/Historias_de_usuario.txt`, `docs/Descripcion.txt` before changes
3. **Skill Router** (task-to-skill mapping):

| Task Type | Skill to Use |
|-----------|-------------|
| Diseño General o Infraestructura | `architecture-patterns` |
| Modelos de DB o Migraciones | `sqlalchemy-alembic-expert-best-practices-code-review` |
| Creación de Endpoints / Rutas | `fastapi-templates` |
| Lógica de Negocio en Python | `python-expert-best-practices-code-review` |
| Validación de API / Swagger | `openapi-specification-v2` |
| Búsqueda de nuevas capacidades | `find-skills` |

4. **MCP Tools Protocol**:
   - MCP Postgres → Access to local PostgreSQL server
   - Database: `food_store_db`
   - Pre-validation: Check table/data types match `Integrador.txt`
   - Engram & Context7 for persistent memory

### Documentation Files

| File | Purpose |
|------|---------|
| `docs/Integrador.txt` | Technical specification (v5.0, ERD, architecture, patterns) |
| `docs/Descripcion.txt` | Project overview, actors, tech stack |
| `docs/Historias_de_usuario.txt` | US-000 through US-076 with acceptance criteria |
| `docs/SKILLS.md` | Installed skills documentation |
| `docs/CHANGES.md` | Change log |

### README.md Conventions
- Conventional commits: `feat(module): desc`, `fix(module): desc`, `refactor(module): desc`, `test(module): desc`, `docs(module): desc`
- Stack: FastAPI · SQLModel · PostgreSQL · Alembic · React · TypeScript · Vite · TanStack · Zustand · Tailwind

---

## Testing Configuration

| Aspect | Value |
|--------|-------|
| Runner (backend) | pytest (pytest.ini: `asyncio_mode=auto`, `testpaths=backend/tests`) |
| Runner (frontend) | vitest (vitest.config.ts: happy-dom, globals) |
| Integration (backend) | httpx AsyncClient + ASGITransport + SQLite in-memory |
| Integration (frontend) | @testing-library/react + @testing-library/user-event + jest-dom |
| PostgreSQL tests | @pytest.mark.postgres with pg fixtures |
| Coverage | Not installed (pytest-cov missing, vitest --coverage not configured) |
| Linter | flake8 (backend), ESLint 9 (frontend) |
| Type Checker | mypy (backend), tsc (frontend via npm run build) |
| Formatter | black + isort (backend), prettier (frontend) |
| Pre-commit | husky + lint-staged |
| Strict TDD | Enabled (test runner available) |

---

## Compact Rules

When applying changes, follow these rules:

1. **Proposal**: Include rollback plan; identify affected modules; reference user stories
2. **Specs**: Use Given/When/Then scenarios; RFC 2119 keywords (MUST, SHALL, SHOULD, MAY); document FSM transitions
3. **Design**: Include sequence diagrams for complex flows; document ADRs; respect unidirectional imports (Router → Service → UoW → Repository → Model); maintain FSD structure
4. **Tasks**: Group by phase (infrastructure, implementation, testing); hierarchical numbering; keep small enough for one session
5. **Apply**: Follow existing code patterns; load relevant skills; pre-validate DB changes against Integrador.txt; run pytest for backend
6. **Verify**: Run tests; compare every spec scenario; validate FSM state transitions
7. **Archive**: Warn before destructive deltas; update main specs after verification

### Frontend-Specific
- Path aliases: `@/` → `src/`, `@shared/` → `src/shared/`, `@features/` → `src/features/`, `@entities/` → `src/entities/`, `@pages/` → `src/pages/`, `@app/` → `src/app/`, `@config/` → `src/config/`
- Zustand stores for client state (cart, auth, UI); TanStack Query for server state
- Feature-Sliced Design: Pages consume Features, Features consume Shared/Entities
