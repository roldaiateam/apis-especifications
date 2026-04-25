---
name: api-bff-layer
description: Generate BFF (Backend-for-Frontend) API specifications including mirror endpoints, batch operations with discriminator/oneOf, and BFF-specific aggregation patterns.
---

# Skill: BFF API Layer

## Purpose

This skill introduces a **BFF (Backend-for-Frontend) pattern** that does not yet exist in the repository. It defines how to create presentation-layer APIs that aggregate, transform, or batch calls to the existing backend domain APIs.

The BFF layer sits between the frontend client and the backend microservices, providing optimized endpoints tailored to specific UI needs.

## When to Use

- A frontend needs data from multiple backend APIs in a single call
- You need batch operations (create/update/delete multiple resources at once)
- The frontend requires a different response shape than the backend provides
- You want to shield the frontend from backend API changes

## Architecture Position

```
Frontend (SPA/Mobile)
    │
    ▼
BFF API  (/bff/<resource>)     ← this skill
    │
    ▼
Backend APIs (/api/<resource>)  ← existing domain APIs
```

## Directory Structure

BFF APIs follow the same structure as backend APIs but live in their own directory:

```
bff-<resource>/
└── rest/
    ├── openapi-rest.yml
    ├── metadata.yml
    ├── README.md
    └── v1/
        ├── services/
        │   └── <resource>/
        │       ├── <resource>-batch.yml
        │       └── <resource>-aggregate.yml
        └── components/
            ├── <resource>/
            │   └── components.yml
            └── errors/
                └── components.yml
```

## BFF-specific Conventions

### Naming

| Aspect | Backend API | BFF API |
|--------|-------------|---------|
| Directory | `<resource>/` | `bff-<resource>/` |
| Title | `<Resource> API` | `<Resource> BFF API` |
| Tag | `<Resource>` | `<Resource>` (same — the BFF serves the same domain) |
| Base path | `/api/<resource>` | `/bff/<resource>` |
| operationId | `createProduct` | `batchCreateProducts` or `getProductDashboard` |

### Server URLs

BFF APIs use their own context path:

```yaml
servers:
  - url: http://localhost:8091/mic-bff
    description: Localhost
  - url: https://proactivedevs-template-des/mic-bff
    description: DES
  - url: https://proactivedevs-template-pre/mic-bff
    description: PRE
  - url: https://proactivedevs-template-prod/mic-bff
    description: PRO
```

> Port `8091` and context `/mic-bff` differentiate BFF from backend (`8090`/`mic-inventory`).

---

## Pattern 1: Mirror Endpoints (1:1 Proxy)

The simplest BFF pattern — the BFF exposes the same endpoint shape as the backend but may add/remove fields or apply transformations.

```yaml
# BFF mirrors backend POST /v1/products but adds frontend-specific fields
post:
  tags:
    - Products
  summary: Create a product (BFF)
  description: >
    Creates a product via the backend Products API.
    Adds frontend-specific validation and field mapping.
  operationId: createProductBff
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/products/components.yml#/components/schemas/CreateProductBffRequest'
  responses:
    '201':
      description: Product created successfully
      content:
        application/json:
          schema:
            $ref: '../../components/products/components.yml#/components/schemas/CreateProductBffResponse'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Pattern 2: Batch Operations with Discriminator

Batch endpoints allow the frontend to send multiple operations in a single request. Use `oneOf` with a `discriminator` to support different action types:

### Batch Request Schema

```yaml
Batch<Resource>Request:
  type: object
  description: Batch request containing multiple <resource> operations.
  required:
    - operations
  properties:
    operations:
      type: array
      description: List of operations to execute. Maximum 50 per request.
      minItems: 1
      maxItems: 50
      items:
        $ref: '#/components/schemas/<Resource>BatchOperation'

<Resource>BatchOperation:
  type: object
  description: A single operation within a batch request.
  required:
    - action
  discriminator:
    propertyName: action
    mapping:
      CREATE: '#/components/schemas/<Resource>BatchCreate'
      UPDATE: '#/components/schemas/<Resource>BatchUpdate'
      DELETE: '#/components/schemas/<Resource>BatchDelete'
  oneOf:
    - $ref: '#/components/schemas/<Resource>BatchCreate'
    - $ref: '#/components/schemas/<Resource>BatchUpdate'
    - $ref: '#/components/schemas/<Resource>BatchDelete'

<Resource>BatchCreate:
  type: object
  required:
    - action
    - data
  properties:
    action:
      type: string
      enum: [CREATE]
    correlationId:
      type: string
      description: Client-provided ID to correlate request items with response items.
      example: "op-001"
    data:
      $ref: '#/components/schemas/Create<Resource>Request'

<Resource>BatchUpdate:
  type: object
  required:
    - action
    - <resource>Id
    - data
  properties:
    action:
      type: string
      enum: [UPDATE]
    correlationId:
      type: string
      example: "op-002"
    <resource>Id:
      $ref: '#/components/schemas/<Resource>Id'
    data:
      $ref: '#/components/schemas/Update<Resource>Request'

<Resource>BatchDelete:
  type: object
  required:
    - action
    - <resource>Id
  properties:
    action:
      type: string
      enum: [DELETE]
    correlationId:
      type: string
      example: "op-003"
    <resource>Id:
      $ref: '#/components/schemas/<Resource>Id'
```

### Batch Response Schema (success/failure split)

```yaml
Batch<Resource>Response:
  type: object
  description: >
    Results of the batch operation. Each operation is reported individually
    as either a success or a failure. The batch itself always returns 200
    even if individual operations fail.
  properties:
    results:
      type: array
      items:
        $ref: '#/components/schemas/<Resource>BatchResult'
    summary:
      $ref: '#/components/schemas/BatchSummary'

<Resource>BatchResult:
  type: object
  properties:
    correlationId:
      type: string
      description: Client-provided correlation ID from the request.
      example: "op-001"
    status:
      type: string
      enum: [SUCCESS, FAILURE]
      description: Whether this individual operation succeeded or failed.
    <resource>Id:
      $ref: '#/components/schemas/<Resource>Id'
    error:
      $ref: '../errors/components.yml#/components/schemas/ApiErrorResponse'

BatchSummary:
  type: object
  description: Aggregate summary of batch results.
  properties:
    total:
      type: integer
      format: int32
      description: Total number of operations in the batch.
      example: 5
    succeeded:
      type: integer
      format: int32
      description: Number of operations that succeeded.
      example: 4
    failed:
      type: integer
      format: int32
      description: Number of operations that failed.
      example: 1
```

### Batch Service File

```yaml
post:
  tags:
    - Products
  summary: Execute batch product operations
  description: >
    Processes multiple product operations (CREATE, UPDATE, DELETE) in a single request.
    Each operation is executed independently — a failure in one does not rollback others.
    Maximum 50 operations per batch.
  operationId: batchProducts
  requestBody:
    description: Batch of product operations
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/products/components.yml#/components/schemas/BatchProductsRequest'
  responses:
    '200':
      description: Batch processed (individual results may include failures)
      content:
        application/json:
          schema:
            $ref: '../../components/products/components.yml#/components/schemas/BatchProductsResponse'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Pattern 3: Aggregation Endpoint

BFF endpoints that combine data from multiple backend APIs:

```yaml
get:
  tags:
    - Products
  summary: Get product dashboard data
  description: >
    Retrieves an aggregated view of product data for the dashboard,
    combining product counts, category summary, and recent activity
    from multiple backend services.
  operationId: getProductDashboard
  responses:
    '200':
      description: Dashboard data retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/products/components.yml#/components/schemas/ProductDashboardResponse'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

---

## Steps to Create a New BFF API

1. Create directory: `bff-<resource>/rest/`
2. Generate `openapi-rest.yml` using the BFF server URLs (port 8091, context `/mic-bff`)
3. Generate `metadata.yml` with `basePath: /bff/<resource>` and codegen package `com.proactivedevs.contracts.bff.<resource>.rest.v1`
4. Generate `README.md`
5. Copy error components from any existing API (identical file)
6. Create domain schemas in `v1/components/<resource>/components.yml`
7. Create service files in `v1/services/<resource>/`
8. Register in global `metadata.yml`:
   ```yaml
   - name: "<Resource> BFF REST API"
     api-spec-type: rest
     definition-path: bff-<resource>/rest
   ```

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Put BFF endpoints in the backend API spec | Create a separate `bff-<resource>/` directory |
| Use the same port/context as backend | BFF uses `8091`/`mic-bff` |
| Return `207 Multi-Status` for batches | Return `200` with per-item `status` field |
| Allow unlimited batch size | Cap at `maxItems: 50` |
| Roll back entire batch on single failure | Process each operation independently |
| Name BFF operationIds identically to backend | Suffix with `Bff` or use `batch`/`dashboard` prefixes |
| Duplicate backend schemas in BFF | Reference or create BFF-specific schemas; do NOT copy-paste backend schemas |
