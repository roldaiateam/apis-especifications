---
name: api-endpoint-service
description: Generate individual endpoint service files (v1/services/<resource>/*.yml) for CRUD operations following the repository's operationId, response code, and $ref conventions.
---

# Skill: Endpoint Service Files

## Purpose

This skill generates the **individual service YAML files** that define each endpoint's HTTP methods, request/response schemas, and error mappings. Each service file represents one URL path and can contain one or multiple HTTP methods.

## When to Use

- After creating error components (Skill 2) and domain schema components (Skill 3)
- When adding a new endpoint to an existing API
- When you need to understand the file naming or operationId conventions

## File Location

```
<resource>/rest/v1/services/<domain>/<domain>-<action>.yml
```

### File naming convention

The service file name maps from the URL path:

| URL Path | Service File | Contains |
|----------|-------------|----------|
| `/v1/<resource>` | `<resource>-create.yml` | POST (create) and optionally GET (list) |
| `/v1/<resource>/{<resource>Id}` | `<resource>-by-id.yml` | GET, PUT, PATCH, DELETE for single resource |
| `/v1/<resource>/search` | `<resource>-search.yml` | POST search (see api-search-endpoint skill) |
| `/v1/<resource>/<sub-resource>` | `<sub-resource>.yml` or `<sub-resource>-<action>.yml` | Operations on sub-resources |

### Examples from the repo

| File | Methods | operationId(s) |
|------|---------|----------------|
| `products/products-create.yml` | POST | `createProduct` |
| `barcode/barcode-types.yml` | GET | `getProductBarcodeTypes` |
| `units/units.yml` | GET | `getAllProductUnits` |
| `categories/categories-create.yml` | POST, GET | `createCategory`, `getCategories` |
| `tenants/tenants-create.yml` | POST | `createTenant` |
| `auth/auth-login.yml` | POST | `login` |
| `provisioning/tenants-status.yml` | GET | `getTenantProvisioningStatus` |

## operationId Naming Rules

Format: **`verbNoun[Qualifier]`** in camelCase.

| Intent | Verb | Example |
|--------|------|---------|
| Create a resource | `create` | `createProduct`, `createCategory`, `createTenant` |
| Get a single resource by ID | `get` | `get<Resource>ById` |
| Get all / list resources | `getAll` or `get` | `getAllProductUnits`, `getCategories` |
| Get a specific sub-resource list | `get<Parent><SubResource>` | `getProductBarcodeTypes` |
| Update a resource | `update` | `update<Resource>` |
| Delete a resource | `delete` | `delete<Resource>` |
| Search with filters | `search` | `search<Resources>` |
| Authentication action | domain verb | `login` |
| Status check | `get...Status` | `getTenantProvisioningStatus` |

### Rules
- **Must be unique** across the entire API spec (not just per file)
- **No hyphens**, no spaces, no version tokens
- **camelCase** always
- The verb reflects the HTTP method's intent, not the HTTP method itself

## Response Code Patterns per HTTP Method

### POST (create)

```yaml
post:
  responses:
    '201':
      description: <Resource> created successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Create<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '409':
      $ref: '../../components/errors/components.yml#/components/responses/Conflict'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

### GET (single resource)

```yaml
get:
  responses:
    '200':
      description: <Resource> retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Get<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

### GET (list / collection)

```yaml
get:
  responses:
    '200':
      description: List of <resources> retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Get<Resources>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

> **Note**: List endpoints return `200` with an empty array when no results found — never `204`.

### PUT (full update)

```yaml
put:
  responses:
    '200':
      description: <Resource> updated successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Update<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '409':
      $ref: '../../components/errors/components.yml#/components/responses/Conflict'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

### DELETE

```yaml
delete:
  responses:
    '204':
      description: <Resource> deleted successfully
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

---

## Complete Template: POST Create Endpoint

```yaml
post:
  tags:
    - <Resource>
  summary: Create a new <resource>
  description: >
    Creates a new <resource> in the system.
    The tenant is automatically resolved from the JWT token (claim: tenant_name).
    Requires role: store_admin.
  operationId: create<Resource>
  requestBody:
    description: Data for creating a new <resource>
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/<resource>/components.yml#/components/schemas/Create<Resource>Request'
        examples:
          standard:
            summary: Standard <resource> creation
            value:
              name: "<Example Name>"
              # ... other required fields
          minimal:
            summary: Minimal <resource> without optional fields
            value:
              name: "<Example Name>"
  responses:
    '201':
      description: <Resource> created successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Create<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '409':
      $ref: '../../components/errors/components.yml#/components/responses/Conflict'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Complete Template: GET List Endpoint

```yaml
get:
  tags:
    - <Resource>
  summary: Get all <resources>
  description: >
    Retrieves a list of all <resources> available in the system
    for the tenant resolved from the JWT token.
  operationId: get<Resources>
  responses:
    '200':
      description: List of <resources> retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Get<Resources>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Complete Template: Multi-method File (POST + GET on same path)

When a single URL path supports multiple methods (e.g., `POST /v1/categories` and `GET /v1/categories`), they go in the **same service file**:

```yaml
post:
  tags:
    - <Resource>
  summary: Create a new <resource>
  description: Creates a new <resource> in the system. The tenant is automatically resolved from the JWT token.
  operationId: create<Resource>
  requestBody:
    description: Data for creating a new <resource>
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/<resource>/components.yml#/components/schemas/Create<Resource>Request'
  responses:
    '201':
      description: <Resource> created successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Create<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '409':
      $ref: '../../components/errors/components.yml#/components/responses/Conflict'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
get:
  tags:
    - <Resource>
  summary: Get all <resources>
  description: Retrieves a list of all <resources> available in the system for the tenant.
  operationId: get<Resources>
  responses:
    '200':
      description: List of <resources> retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Get<Resources>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Complete Template: GET by ID + PUT + DELETE (single resource path)

For paths like `/v1/<resource>/{<resource>Id}`:

```yaml
get:
  tags:
    - <Resource>
  summary: Get a <resource> by ID
  description: Retrieves the details of a specific <resource> by its unique identifier.
  operationId: get<Resource>ById
  parameters:
    - name: <resource>Id
      in: path
      required: true
      description: Unique identifier of the <resource>
      schema:
        $ref: '../../components/<resource>/components.yml#/components/schemas/<Resource>Id'
  responses:
    '200':
      description: <Resource> retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Get<Resource>Response'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
put:
  tags:
    - <Resource>
  summary: Update a <resource>
  description: Updates an existing <resource> identified by its unique identifier.
  operationId: update<Resource>
  parameters:
    - name: <resource>Id
      in: path
      required: true
      description: Unique identifier of the <resource>
      schema:
        $ref: '../../components/<resource>/components.yml#/components/schemas/<Resource>Id'
  requestBody:
    description: Updated data for the <resource>
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/<resource>/components.yml#/components/schemas/Update<Resource>Request'
  responses:
    '200':
      description: <Resource> updated successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Update<Resource>Response'
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '409':
      $ref: '../../components/errors/components.yml#/components/responses/Conflict'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
delete:
  tags:
    - <Resource>
  summary: Delete a <resource>
  description: Deletes a <resource> identified by its unique identifier.
  operationId: delete<Resource>
  parameters:
    - name: <resource>Id
      in: path
      required: true
      description: Unique identifier of the <resource>
      schema:
        $ref: '../../components/<resource>/components.yml#/components/schemas/<Resource>Id'
  responses:
    '204':
      description: <Resource> deleted successfully
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## $ref Path Convention

All `$ref` paths from service files follow this pattern:

```
../../components/<domain>/components.yml#/components/schemas/<SchemaName>
../../components/errors/components.yml#/components/responses/<ResponseName>
```

The `../../` navigates from `v1/services/<domain>/` up to `v1/`, then into `components/`.

## Registering the Service File in openapi-rest.yml

After creating the service file, add the path entry to the root spec:

```yaml
paths:
  /v1/<resource>:
    $ref: './v1/services/<resource>/<resource>-create.yml'
  /v1/<resource>/{<resource>Id}:
    $ref: './v1/services/<resource>/<resource>-by-id.yml'
```

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Use hyphens in `operationId` | Use camelCase: `createProduct`, not `create-product` |
| Include HTTP method in operationId | `createProduct`, not `postProduct` |
| Include version in operationId | `createProduct`, not `createProductV1` |
| Use `204` for list endpoints with no results | Return `200` with an empty array |
| Use `409` on GET endpoints | 409 is for state-changing methods only |
| Define parameters inline when a reusable ID type exists | Use `$ref` to the ID schema |
| Put multiple unrelated paths in one service file | One file per URL path |
| Forget to add `tags` to each method | Always include the resource tag |
| Quote `200` differently from `'200'` | Always use single-quoted strings: `'200'`, `'400'`, etc. |
