# Generate OpenAPI Skills & Agent for an APIFirst Repository

## What this prompt does

Analyzes an APIFirst contract-only repository and generates a complete set of modular skills + one orchestrating agent for creating new OpenAPI 3.0.3 specifications that match the existing patterns exactly. Includes SSE (Server-Sent Events) endpoint generation support.

## How to use

Run this prompt, then answer the questions about your repository. The agent will:
1. Analyze the repository structure, naming conventions, and patterns
2. Query Inditex API guidelines via Geppetto MCP tools
3. Generate 7 skills + 1 agent under `.claude/`

---

## Instructions for the AI

You are tasked with creating a reusable set of **skills** and one **agent** for generating OpenAPI 3.0.3 API specifications in an Inditex APIFirst repository. Follow these steps rigorously.

### Phase 1: Repository Analysis (DO NOT SKIP)

Before writing any file, fully analyze the repository to extract patterns. You must discover:

1. **Repository type**: Confirm it is contract-only (no application code, only OpenAPI specs + infra)
2. **API inventory**: List all existing APIs with their versions, endpoint counts, and maturity
3. **Directory structure**: Map the exact file tree per API (`openapi-rest.yml`, `metadata.yml`, `README.md`, `services/`, `components/`)
4. **Two-tier architecture**: Identify if there are backend microservices and BFF APIs, their base paths
5. **Naming conventions**: Extract patterns for operationId, schema names, path segments, parameters, enums
6. **Error schema**: Determine the exact error response structure (check if it uses RFC9457 or a custom pattern like `errorCode`/`errorMessage`)
7. **Pagination pattern**: Identify if the repo uses SlicedSchema, PagedSchema, cursor-based, or other
8. **Search pattern**: Check if searches use POST with body or GET with query params
9. **BFF patterns**: Look for batch operations, discriminators, oneOf unions
10. **Server environments**: Extract the exact server URLs (Localhost, DES, PRE, PRO)
11. **Security schemes**: Identify auth patterns (Basic, Bearer, OAuth2, API Key)
12. **Registration**: Find the global API registry file (`apis/metadata.yml`) and its format. Every new API must be registered here.
13. **Per-API metadata and docs**: Each API must have a `metadata.yml` (name, version, contact, visibility) and a `README.md` (summary, about, configuration, endpoints, examples, team info) inside its `rest/` directory.
13. **Inditex White Paper rules**: Use the `geppetto_api_search` tool to query Inditex API design guidelines and note any divergences from the repo's actual patterns

**Key files to read:**
- `apis/metadata.yml` (or equivalent registry)
- Any `openapi-rest.yml` (root spec of the most mature API)
- Any `metadata.yml` inside an API directory
- Any `README.md` inside an API directory
- Service files under `v1/services/` (one per endpoint pattern: create, get, update, delete, search)
- Component files under `v1/components/<resource>/components.yml` (domain schemas)
- Component files under `v1/components/error/components.yml` (error schemas)
- BFF API specs if they exist

### Phase 2: Decisions (ASK THE USER)

Before generating, ask the user to confirm the following. **Use the `question` built-in tool** to present these decisions as interactive selection prompts (with predefined options the user can pick from) instead of plain text questions. This provides a better UX with clickable options.

1. **Output directory**: `.claude/` or `.opencode/` or other?
2. **Language**: English or Spanish for skill/agent content?
3. **Error schema**: Keep current repo pattern or migrate to RFC9457?
4. **Content ratio**: How much reasoning/guidance vs raw code templates? (Recommend ~60/40)

### Phase 3: Generate Skills (7 files)

Create these 6 skill files, each with YAML frontmatter (`name`, `description`) and markdown body. Each skill must be:
- **Self-contained**: No dependency on other skills for understanding
- **Repository-specific**: All examples extracted from the actual repo, not generic
- **Actionable**: Include complete YAML templates with `<placeholder>` markers

#### Skill 1: `skills/api-openapi-spec/SKILL.md`
- Purpose: Generate `openapi-rest.yml` + `metadata.yml` + `README.md`
- Content: Backend vs BFF decision criteria, server URLs, security schemes, tag conventions
- Template: Complete root spec with placeholders
- Include: `metadata.yml` template with name, version, status, contact, visibility fields
- Include: `README.md` template with sections: Summary, About, Configuration, Documentation (endpoint list), Example (HTTP request), Main Goal, Specifics, Usage, Team
- Include: Registration instructions for the global `apis/metadata.yml` — every new API must add an entry with `name`, `api-spec-type: rest`, and `definition-path`

#### Skill 2: `skills/api-error-components/SKILL.md`
- Purpose: Generate `v1/components/error/components.yml`
- Content: The exact error schema from the repo (copy as-is for every new API)
- Template: Complete error components file
- Include: Reference table of which HTTP codes apply to which verbs

#### Skill 3: `skills/api-schema-components/SKILL.md`
- Purpose: Generate `v1/components/<resource>/components.yml`
- Content: Naming conventions (PascalCase schemas, camelCase properties), allOf inheritance, validation constraints
- Templates: ID types, Summary entities, Full entities (allOf extension), Request/Response schemas, Parameters
- Include: Anti-patterns to avoid

#### Skill 4: `skills/api-endpoint-service/SKILL.md`
- Purpose: Generate individual `v1/services/*.yml` files
- Content: operationId naming rules, response code patterns per HTTP method, $ref conventions
- Templates: POST create, GET single, PUT update, DELETE, multi-method files
- Include: File naming convention (URL path → file name mapping)

#### Skill 5: `skills/api-search-endpoint/SKILL.md`
- Purpose: Generate POST search endpoints with pagination
- Content: SearchSchema + SlicedSchema + Filters pattern
- Templates: Complete search request/response schemas, service file
- Include: Real request/response JSON examples

#### Skill 6: `skills/api-bff-layer/SKILL.md`
- Purpose: Generate BFF API specs
- Content: Mirror pattern (1:1), batch operations with discriminator/oneOf, BFF-specific endpoints
- Templates: BFF root spec, batch operation schemas (request + response with success/failure split)
- Include: Steps to create a new BFF API

#### Skill 7: `skills/api-sse-endpoint/SKILL.md`
- Purpose: Generate SSE (Server-Sent Events) streaming endpoints with `text/event-stream` content type
- Content: SSE endpoint pattern (GET with `text/event-stream`), polling fallback pattern, event schema modeling, reconnection/replay via `since` parameter and `Last-Event-ID` header
- Templates: SSE GET endpoint service file, polling GET fallback service file, event schema (`<Resource>StatusEvent`), snapshot response with `timestamp` for gap-free sync, SSE-specific parameters (`since`, subscription filter)
- Include: Heartbeat/timeout guidance, `Last-Event-ID` reconnection, security considerations for long-lived connections, performance/scalability rules, anti-patterns table
- Reference: Based on `bff-rooms` API patterns (`rooms-events.yml`, `rooms-status.yml`, `RoomStatusEvent` schema)

### Phase 4: Generate Agent (1 file)

Create `agents/api-generator.md` with YAML frontmatter (`description`, `mode: primary`, `tools` — include `question` in the tools list) and markdown body:

- **Repository context**: Full inventory of existing APIs
- **Workflow**: Step-by-step sequence:
  1. Requirements gathering (resource name, tier, endpoints, entities, special patterns)
  2. Interactive refinement — Present a design summary and ask targeted questions to refine naming, schema design, endpoint matrix, error codes, and BFF scope. Do NOT proceed until the user approves the design.
  3. Plan approval — Ask the user their preferred level of detail ("detallado" or "fast") as an interactive question, then present the execution plan accordingly:
     - **Detallado**: For each file, show full path, contents summary (schemas with properties, endpoints with verb+path+operationId, $ref dependencies), and execution order
     - **Fast**: Numbered list of files with one-line description each
     Ask: "¿Te parece bien este plan? ¿Quieres cambiar algo antes de empezar?". Do NOT generate files until approved.
  4. Generate root spec + metadata + README → errors → schemas → endpoints → search → BFF → register in apis/metadata.yml
- **Conventions reference**: Complete naming rules, response code mappings, validation requirements
- **Quality checklist**: Verification items before delivery
- **Skill references**: List available skills and when to load each one
- **Interactive questions**: The agent MUST use the `question` tool for all user-facing decisions (requirements gathering, design approval, plan detail level, confirmation to proceed). Present options as selectable choices whenever possible instead of asking in plain text.
- **Inditex White Paper key rules**: Top 10 rules that must always be applied

### Phase 5: Verify

After generating all files:
1. Count total lines across all 8 files
2. Verify no skill has logic overlap with another
3. Confirm all examples are from the actual repo (not generic)
4. List all created files with their line counts

### Output Quality Rules

- **No generic content**: Every template must use real values from the analyzed repo (server URLs, team contacts, base paths, etc.)
- **Placeholder format**: Use `<Resource>` (PascalCase), `<resource>` (kebab-case), `<description>` — clearly marked
- **Every skill must include**: Purpose, When to Use, File Location, Templates, Conventions, Inditex White Paper Alignment
- **Agent must include**: Repository Context, Workflow, Conventions, Quality Checklist, Available Skills
