---
name: api-openapi-spec
description: Generate the root OpenAPI 3.0.3 specification file (openapi-rest.yml), per-API metadata.yml, README.md, and register the new API in the global metadata.yml registry.
---

# Skill: Root OpenAPI Spec + Metadata + README + Registration

## Purpose

This skill handles the creation of the **four foundational files** every new REST API needs in this repository:

1. `openapi-rest.yml` — the root OpenAPI 3.0.3 specification
2. `metadata.yml` — per-API metadata (name, version, codegen config, generators)
3. `README.md` — human-readable documentation of the API
4. Registration entry in the **global** `metadata.yml` at the repository root

Without all four, the CI/CD pipeline (publish-contracts, generate-docs, Maven codegen) will not pick up the new API.

## When to Use

- You are creating a **brand new** REST API in this repository
- You need to scaffold the directory tree before adding schemas and endpoints
- You need to register an existing API that was not yet added to the global registry

## File Locations

Given a new API called `<resource>` (kebab-case, plural), the files go here:

```
<resource>/
└── rest/
    ├── openapi-rest.yml        ← this skill
    ├── metadata.yml            ← this skill
    ├── README.md               ← this skill
    └── v1/
        ├── services/
        │   └── <resource>/     ← created by api-endpoint-service skill
        └── components/
            ├── <resource>/     ← created by api-schema-components skill
            └── errors/         ← created by api-error-components skill
```

And the global registry:

```
metadata.yml                    ← add entry here
```

## Decision: Backend API vs Platform API

This repo has two tiers of APIs. Choose the correct one before generating:

| Criterion | Backend / Domain API | Platform / Infrastructure API |
|-----------|---------------------|-------------------------------|
| **Purpose** | Tenant-scoped business resources (products, categories, orders) | Cross-cutting platform concerns (auth, provisioning) |
| **Base path context** | `/mic-inventory` | `/micclients` |
| **URL base path** | `/api/<resource>` | Varies (e.g., `/v1/auth/login`, `/v1/tenants/status`) |
| **Localhost port** | `8090` | `8080` |
| **Examples in repo** | Products, Categories | Auth, Provisioning, Tenants |

Most new APIs will be **Backend / Domain** APIs.

## Server URL Pattern

All APIs use exactly 4 server environments. The context path depends on the tier:

**Backend / Domain APIs** (port 8090, context `/mic-inventory`):
```yaml
servers:
  - url: http://localhost:8090/mic-inventory
    description: Localhost
  - url: https://proactivedevs-template-des/mic-inventory
    description: DES
  - url: https://proactivedevs-template-pre/mic-inventory
    description: PRE
  - url: https://proactivedevs-template-prod/mic-inventory
    description: PRO
```

**Platform / Infrastructure APIs** (port 8080, context `/micclients`):
```yaml
servers:
  - url: http://localhost:8080/micclients
    description: Localhost
  - url: https://proactivedevs-template-des/micclients
    description: DES
  - url: https://proactivedevs-template-pre/micclients
    description: PRE
  - url: https://proactivedevs-template-prod/micclients
    description: PRO
```

## Security Schemes

All APIs in the repo use the same security block. Always include both `basicAuth` and `bearerAuth`:

```yaml
security:
  - basicAuth: []
  - bearerAuth: []

components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

> **Note**: The Auth API only defines `bearerAuth` (no `basicAuth`). Unless you have a specific reason, include both for new APIs.

## Conventions

### Tag naming
- One tag per API, matching the resource name in **PascalCase** singular or plural as appropriate
- Format: `name: <Resource>` + `description: Operations about <Resource> management`
- Examples from repo: `Products`, `Categories`, `Tenants`, `Auth`, `Provisioning`

### info.title
- Format: `<Resource> API` (e.g., `Products API`, `Categories API`)
- Do NOT include "REST" in the title

### info.version
- Semantic versioning starting at `0.0.1` for new APIs
- This is the **single source of truth** for the API version — CI/CD reads it from here

### Path $ref pattern
- Each path entry points to a service file via `$ref`
- Format: `$ref: './v1/services/<resource>/<resource>-<action>.yml'`
- Example: `$ref: './v1/services/products/products-create.yml'`

---

## Template: `openapi-rest.yml`

```yaml
openapi: 3.0.3

info:
  title: <Resource> API
  description: <One-line description of what this API provides>
  contact:
    name: Proactive Devs team
    email: proactivedevs@gmail.com
    url: 'http://proactivedevs.com'
  version: 0.0.1

servers:
  - url: http://localhost:8090/mic-inventory
    description: Localhost
  - url: https://proactivedevs-template-des/mic-inventory
    description: DES
  - url: https://proactivedevs-template-pre/mic-inventory
    description: PRE
  - url: https://proactivedevs-template-prod/mic-inventory
    description: PRO

tags:
  - name: <Resource>
    description: Operations about <Resource> management

security:
  - basicAuth: []
  - bearerAuth: []

paths:
  /v1/<resource>:
    $ref: './v1/services/<resource>/<resource>-create.yml'
  # Add more paths as needed:
  # /v1/<resource>/{<resource>Id}:
  #   $ref: './v1/services/<resource>/<resource>-by-id.yml'
  # /v1/<resource>/search:
  #   $ref: './v1/services/<resource>/<resource>-search.yml'

components:
  securitySchemes:
    basicAuth:
      type: http
      scheme: basic
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Template: `metadata.yml`

```yaml
---
api-spec-type: rest

api:
  name: <Resource> REST API
  version: 0.0.1
  description: >
    <Multi-line description of the API's purpose and scope.>
  maintainer:
    name: Andres Reinaldo Cid
    email: andresrc345@gmail.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
  basePath: /api/<resource>
  contact:
    name: Roldaia Team
    email: roldaiateam@gmail.com
  documentation:
    url: ./README.md

openapi:
  spec-version: 3.0.3
  spec-file: openapi-rest.yml
  format: openapi

codegen:
  package-prefix: com.proactivedevs.contracts.<resource>.rest.v1
  model-package: com.proactivedevs.contracts.<resource>.rest.v1.model

generators:
  mvn:
    enabled: true
    package_name: com.proactivedevs.contracts.<resource>.rest.v1
    artifact_id_override: null
  npm:
    enabled: false
    package_name: "@proactivedevs/contracts-<resource>-rest"
  go:
    enabled: false
  python:
    enabled: false
```

### metadata.yml field reference

| Field | Required | Description |
|-------|----------|-------------|
| `api-spec-type` | Yes | Always `rest` for REST APIs |
| `api.name` | Yes | Human-readable name, format: `<Resource> REST API` |
| `api.version` | Yes | Must match `info.version` in `openapi-rest.yml` |
| `api.basePath` | Yes | The logical base path (e.g., `/api/products`) |
| `codegen.package-prefix` | Yes | Java package: `com.proactivedevs.contracts.<resource>.rest.v1` |
| `generators.mvn.enabled` | Yes | Always `true` — Maven is the only active generator |

---

## Template: `README.md`

```markdown
# <Resource> REST API

OpenAPI contract for <resource> management endpoints.

## Overview

This contract defines the **<Resource> REST API** specification using OpenAPI 3.0.3.
It is published as a Maven artifact to GitHub Packages and can be consumed by microservices
that need to interact with <resource> operations.

---

## Structure

```
<resource>/rest/
├── openapi-rest.yml           # Main OpenAPI spec (VERSION SOURCE OF TRUTH)
├── metadata.yml               # Contract metadata (api-spec-type: rest)
├── README.md                  # This file
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml # Standard error responses
    │   └── <resource>/
    │       └── components.yml # Request/Response schemas
    └── services/
        └── <resource>/
            └── <resource>-create.yml  # POST /v1/<resource> endpoint
```

---

## Version Management

The **version in `openapi-rest.yml` → `info.version` is the SINGLE SOURCE OF TRUTH**.
The CI/CD workflow automatically reads this version and synchronizes the Maven POM before building and publishing.

Current version: **0.0.1**

---

## API Endpoints

### POST /v1/<resource>
Creates a new <resource> in the system.

**Request Body:** `Create<Resource>Request`
- <list required and optional fields>

**Response (201):** `Create<Resource>Response`
- <resourceId> (integer/uuid)

**Error Responses:** 400, 401, 403, 409, 500

---

## Maven Artifact

This contract is published to GitHub Packages as:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId><resource>-rest-stable</artifactId>
    <version>X.Y.Z</version>
</dependency>
```

The JAR includes:
- Original OpenAPI spec files in `META-INF/openapi/`
- Pre-generated Java DTO models (Request/Response classes)

---

## Maintainer

**Andres Reinaldo Cid**
andresrc345@gmail.com
```

---

## Global Registry: Adding the New API

Every new API **must** be registered in the root `metadata.yml` file. Without this entry, the CI/CD pipeline will not discover or publish the API.

### Current registry format

```yaml
---
pipeline:
  version: 3

apis:
  - name: "Tenants Events"
    api-spec-type: event
    definition-path: tenants/event
  - name: "Tenants REST API"
    api-spec-type: rest
    definition-path: tenants/rest
  # ... existing entries ...
```

### Entry to add for a new REST API

Append this block to the `apis` list:

```yaml
  - name: "<Resource> REST API"
    api-spec-type: rest
    definition-path: <resource>/rest
```

### Registration checklist

- [ ] `name` matches `api.name` in the per-API `metadata.yml`
- [ ] `api-spec-type` is `rest`
- [ ] `definition-path` points to the directory containing `openapi-rest.yml` (relative from repo root, no leading slash)
- [ ] Entry is added at the **end** of the `apis` list

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Include "REST" in `info.title` | Use `<Resource> API` |
| Start version at `1.0.0` for new APIs | Start at `0.0.1` |
| Use different server URLs than the repo standard | Copy the exact 4-environment block |
| Forget to register in global `metadata.yml` | Always add the registry entry |
| Put security schemes inline per operation | Define them globally in `components.securitySchemes` |
| Create the `v1/` subdirectories in this skill | Those are created by the other skills (error, schema, endpoint) |
