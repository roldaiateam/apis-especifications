---
name: api-error-components
description: Generate the standardized error schema and reusable error responses file (v1/components/errors/components.yml) for a new REST API.
---

# Skill: Error Components

## Purpose

This skill generates the **error schema and reusable response definitions** that every REST API in this repository must include. The error structure is standardized across all APIs — every new API gets an identical copy of the base error schema, with API-specific error examples added as needed.

## When to Use

- Creating a new REST API (this is always the **first component file** to generate)
- Adding new error response types to an existing API
- Verifying that an API's error components match the repository standard

## File Location

```
<resource>/rest/v1/components/errors/components.yml
```

> **Important**: The folder is named `errors/` (with 's'), not `error/`.

## Error Schema: `ApiErrorResponse`

This repository uses a **custom error schema** (not RFC9457). The schema is identical across all 5 existing APIs:

```yaml
ApiErrorResponse:
  type: object
  additionalProperties: false
  properties:
    errorCode:
      type: string
      description: Error code
      example: "VALIDATION_ERROR"
    errorMessage:
      type: string
      description: Error message
      example: "An error occurred"
      maxLength: 255
    details:
      type: object
      nullable: true
      additionalProperties: true
      description: >
        Optional structured metadata providing additional context about the error.
        Present only when the error carries extra information (e.g. a list of missing entity IDs).
```

### Field reference

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `errorCode` | string | Yes | Machine-readable error identifier, UPPER_SNAKE_CASE |
| `errorMessage` | string | Yes | Human-readable description, max 255 chars |
| `details` | object | No | Additional context (e.g., `{ "ids": [10, 42] }`) |

### errorCode naming convention

- Format: `UPPER_SNAKE_CASE`
- Pattern: `<DOMAIN>_<SPECIFIC_ERROR>` or standalone like `VALIDATION_ERROR`
- Examples from repo:
  - `VALIDATION_ERROR` — generic validation failure
  - `UNAUTHORIZED` — missing/invalid JWT
  - `FORBIDDEN` — insufficient role
  - `CATEGORY_NOT_FOUND` — domain-specific 404
  - `PRODUCT_SKU_ALREADY_EXISTS` — domain-specific 409
  - `BARCODE_ALREADY_EXISTS` — domain-specific 409
  - `BATCH_AND_SERIAL_EXCLUSIVE` — business rule violation (400)

## Reusable Responses

The file defines **named responses** that are referenced via `$ref` from service files. These are the standard set:

| Response Name | HTTP Code | When to Use |
|---------------|-----------|-------------|
| `BadRequest` | 400 | Syntax errors, invalid fields, business rule violations |
| `Unauthorized` | 401 | Missing or invalid JWT token |
| `Forbidden` | 403 | User role insufficient for the operation |
| `NotFound` | 404 | Entity not found for the current tenant |
| `Conflict` | 409 | Uniqueness constraint violated (POST, PUT, PATCH, DELETE only) |
| `InternalServerError` | 500 | Unexpected server error |
| `ServiceUnavailable` | 503 | Service temporarily unavailable |
| `GatewayTimeout` | 504 | Timeout from upstream service |
| `Default` | default | Catch-all for unexpected errors |

### Which responses apply to which HTTP methods

| Response | POST | GET | PUT | PATCH | DELETE |
|----------|------|-----|-----|-------|--------|
| BadRequest (400) | Yes | Yes | Yes | Yes | Yes |
| Unauthorized (401) | Yes | Yes | Yes | Yes | Yes |
| Forbidden (403) | Yes | Yes | Yes | Yes | Yes |
| NotFound (404) | Optional | Yes | Yes | Yes | Yes |
| Conflict (409) | Yes | No | Yes | Yes | Optional |
| InternalServerError (500) | Yes | Yes | Yes | Yes | Yes |

> **Rule**: `409 Conflict` must **never** be used on GET operations. It is valid for POST, PUT, PATCH, and recommended for DELETE when applicable.

---

## Complete Template

Copy this file as-is for every new API. Only modify the `examples` to match the new API's domain:

```yaml
components:
  schemas:
    ApiErrorResponse:
      type: object
      additionalProperties: false
      properties:
        errorCode:
          type: string
          description: Error code
          example: "VALIDATION_ERROR"
        errorMessage:
          type: string
          description: Error message
          example: "An error occurred"
          maxLength: 255
        details:
          type: object
          nullable: true
          additionalProperties: true
          description: >
            Optional structured metadata providing additional context about the error.
            Present only when the error carries extra information (e.g. a list of missing entity IDs).

  responses:
    BadRequest:
      description: Request contains incorrect syntax, invalid fields, or violated logical validation rules
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
          examples:
            validationError:
              summary: Validation rule violation
              value:
                errorCode: VALIDATION_ERROR
                errorMessage: <Describe a domain-specific validation failure>
    Unauthorized:
      description: JWT is missing or invalid
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
          examples:
            unauthorized:
              value:
                errorCode: UNAUTHORIZED
                errorMessage: Missing or invalid token
    Forbidden:
      description: User role is insufficient to execute this endpoint
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
          examples:
            forbidden:
              value:
                errorCode: FORBIDDEN
                errorMessage: Insufficient role to execute operation
    NotFound:
      description: Referenced entity was not found for the current tenant
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
          examples:
            notFound:
              value:
                errorCode: <RESOURCE>_NOT_FOUND
                errorMessage: <Resource> does not exist for current tenant
    Conflict:
      description: Uniqueness or state conflict for tenant
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
          examples:
            conflict:
              value:
                errorCode: <RESOURCE>_ALREADY_EXISTS
                errorMessage: <Resource> already exists for tenant
    InternalServerError:
      description: Internal Server Error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
    ServiceUnavailable:
      description: Service Unavailable
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
    GatewayTimeout:
      description: Gateway Timeout - Use it to report a Timeout occurred on the server.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
    Default:
      description: Unexpected error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ApiErrorResponse'
```

## How Service Files Reference These Responses

From any service file under `v1/services/<resource>/`, errors are referenced like this:

```yaml
responses:
  '400':
    $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
  '401':
    $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
  '403':
    $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
  '500':
    $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

### Inline vs $ref error responses

Some endpoints define **inline** error responses instead of using `$ref` — this is done when the endpoint needs **custom examples** specific to that operation. See the Products API `products-create.yml` for an example where `400` is defined inline with multiple domain-specific examples while `401`, `403`, `409`, `500` use `$ref`.

**Rule of thumb**:
- Use `$ref` for standard errors (401, 403, 500)
- Use inline definitions when you need operation-specific `examples` (usually 400, 404, 409)

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Name the folder `error/` (singular) | Always use `errors/` (plural) |
| Use RFC9457 fields (`type`, `title`, `status`, `detail`) | Use `errorCode`, `errorMessage`, `details` |
| Use `additionalProperties: true` on `ApiErrorResponse` root | Use `additionalProperties: false` at root; `details` is the flexible field |
| Omit `maxLength: 255` on `errorMessage` | Always include it |
| Use `409 Conflict` on GET endpoints | 409 is only for POST, PUT, PATCH, DELETE |
| Invent new response names not in the standard set | Use only the 8 named responses above |
