# Skill Registry — food-store

**Generated**: 2026-05-08
**Source**: SDD Init scan

---

## Available Skills

### User-Level Skills (`~/.config/opencode/skills/`)

| Skill | Description | Trigger |
|-------|-------------|---------|
| `openspec-apply-change` | Implements tasks from an OpenSpec change | When user wants to implement/continue tasks |
| `openspec-archive-change` | Archives a completed change | When finalizing a change after implementation |
| `openspec-explore` | Explore mode for investigating ideas | When thinking through a feature before/during a change |
| `openspec-propose` | Proposes a new change with all artifacts | When describing what to build |
| `sdd-apply` | Implements tasks from a change | Writing actual code following specs/design |
| `sdd-archive` | Syncs delta specs to main specs and archives | After implementation and verification |
| `sdd-design` | Creates technical design document | Writing/updating technical design |
| `sdd-explore` | Explores/investigates ideas before committing | Thinking through a feature/codebase investigation |
| `sdd-init` | Initializes SDD context in any project | When initializing SDD in a project |
| `sdd-onboard` | Guided end-to-end SDD walkthrough | Onboarding through full SDD cycle |
| `sdd-propose` | Creates a change proposal | Creating/updating a proposal |
| `sdd-spec` | Writes specifications with requirements | Writing/updating specs for a change |
| `sdd-tasks` | Breaks down a change into task checklist | Creating/updating task breakdown |
| `sdd-verify` | Validates implementation matches specs | Verifying completed/partial changes |
| `branch-pr` | PR creation workflow with issue-first enforcement | Creating PR, opening PR, preparing for review |
| `go-testing` | Go testing patterns for Bubbletea TUI | Writing Go tests, teatest, test coverage |
| `issue-creation` | Issue creation with issue-first enforcement | Creating GitHub issue, reporting bug, feature request |
| `judgment-day` | Parallel adversarial review protocol | User says "judgment day", "dual review", "juzgar" |
| `skill-creator` | Creates new AI agent skills | Creating skill, adding instructions, documenting patterns |
| `skill-registry` | Creates/updates skill registry | Updating skills, scanning conventions |

### Project-Level Skills (not found)

No project-level skills found in `.agent/skills/`, `.claude/skills/`, `.gemini/skills/`, `.cursor/skills/`, or `skills/`.

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
| Runner | pytest (backend/pytest.ini: `asyncio_mode=auto`, `testpaths=tests`) |
| Integration | httpx AsyncClient + SQLite in-memory |
| Coverage | Not installed (pytest-cov missing) |
| Linter | flake8 (backend), ESLint (frontend) |
| Type Checker | mypy (backend), tsc (frontend) |
| Formatter | black + isort (backend), prettier (frontend) |
| Strict TDD | Enabled (test runner available) |
