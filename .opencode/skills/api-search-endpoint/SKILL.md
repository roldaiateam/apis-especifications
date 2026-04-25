---
name: api-search-endpoint
description: Generate POST search endpoints with pagination (limit/offset) including search request schemas, paginated response schemas, filter objects, and the service file.
---

# Skill: Search Endpoint with Pagination

## Purpose

This skill introduces a **search pattern** that does not yet exist in the repository. It defines how to create `POST /v1/<resource>/search` endpoints with request body filters and paginated responses using **limit/offset** pagination.

The pattern is designed to be fully consistent with the existing repository conventions (same error refs, same $ref style, same operationId naming, same directory structure).

## When to Use

- Adding search/filter capability to an existing or new API
- When GET query parameters would be too complex (many filters, nested criteria)
- When you need paginated results for large collections

## Why POST for Search?

- GET with many query params becomes unwieldy and hits URL length limits
- POST body allows structured, nested filter objects
- The operationId convention uses `search<Resources>` to distinguish from `get<Resources>` (which returns all without pagination)

## File Locations

The search pattern adds files in two locations:

```
<resource>/rest/v1/
├── services/<resource>/
│   └── <resource>-search.yml              ← service file (this skill)
└── components/<resource>/
    └── components.yml                     ← add search schemas here (this skill)
```

And a new path in the root spec:

```yaml
paths:
  /v1/<resource>/search:
    $ref: './v1/services/<resource>/<resource>-search.yml'
```

## Pagination Pattern: Limit/Offset

This repo adopts **limit/offset** pagination for search endpoints:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | integer (int32) | 20 | Maximum items to return (1-100) |
| `offset` | integer (int32) | 0 | Number of items to skip |

### Why limit/offset

- Simplest pattern, good fit for the repo's current maturity (early versions, small datasets)
- Framework-friendly (Spring Data, JPA pagination)
- Easy for clients to implement "page N" by computing `offset = (page - 1) * limit`

---

## Search Request Schema

```yaml
Search<Resources>Request:
  type: object
  description: >
    Search criteria and pagination parameters for querying <resources>.
    All filter fields are optional. When omitted, no filter is applied for that field.
    Results are paginated using limit/offset.
  properties:
    filters:
      $ref: '#/components/schemas/<Resource>SearchFilters'
    limit:
      type: integer
      format: int32
      description: Maximum number of items to return. Must be between 1 and 100.
      minimum: 1
      maximum: 100
      default: 20
      example: 20
    offset:
      type: integer
      format: int32
      description: Number of items to skip before starting to return results.
      minimum: 0
      default: 0
      example: 0
    sortBy:
      type: string
      description: Field name to sort results by.
      enum:
        - name
        - createdAt
        - updatedAt
      default: createdAt
      example: "name"
    sortDirection:
      type: string
      description: Sort direction.
      enum:
        - asc
        - desc
      default: asc
      example: "asc"
```

## Filter Schema

```yaml
<Resource>SearchFilters:
  type: object
  description: >
    Optional filter criteria for searching <resources>.
    All fields are optional — omit a field to skip that filter.
  properties:
    name:
      type: string
      description: Partial match on <resource> name (case-insensitive)
      maxLength: 255
      example: "Leche"
    categoryId:
      type: integer
      format: int64
      description: Filter by category identifier
      example: 10
    createdFrom:
      type: string
      format: date-time
      description: Filter <resources> created on or after this timestamp (ISO 8601)
      example: "2026-01-01T00:00:00Z"
    createdTo:
      type: string
      format: date-time
      description: Filter <resources> created on or before this timestamp (ISO 8601)
      example: "2026-12-31T23:59:59Z"
```

> **Customize the filter fields** to match the domain. The above are examples — replace with fields relevant to your resource.

## Paginated Response Schema

```yaml
Search<Resources>Response:
  type: object
  description: Paginated search results for <resources>.
  properties:
    data:
      type: array
      description: List of <resources> matching the search criteria for the current page.
      items:
        $ref: '#/components/schemas/<Resource>Summary'
    pagination:
      $ref: '#/components/schemas/PaginationMetadata'

PaginationMetadata:
  type: object
  description: Pagination information for the current result set.
  properties:
    limit:
      type: integer
      format: int32
      description: Maximum number of items per page.
      example: 20
    offset:
      type: integer
      format: int32
      description: Number of items skipped.
      example: 0
    total:
      type: integer
      format: int64
      description: Total number of items matching the search criteria.
      example: 150
    hasMore:
      type: boolean
      description: Whether there are more results beyond the current page.
      example: true
```

---

## Complete Service File Template: `<resource>-search.yml`

```yaml
post:
  tags:
    - <Resource>
  summary: Search <resources> with filters
  description: >
    Searches <resources> using optional filter criteria with paginated results.
    The tenant is automatically resolved from the JWT token.
    All filter fields are optional. When no filters are provided, all <resources> for the tenant are returned.
  operationId: search<Resources>
  requestBody:
    description: Search criteria and pagination parameters
    required: true
    content:
      application/json:
        schema:
          $ref: '../../components/<resource>/components.yml#/components/schemas/Search<Resources>Request'
        examples:
          withFilters:
            summary: Search with name filter and pagination
            value:
              filters:
                name: "Leche"
              limit: 10
              offset: 0
              sortBy: "name"
              sortDirection: "asc"
          noFilters:
            summary: Get first page of all <resources>
            value:
              limit: 20
              offset: 0
          emptyBody:
            summary: Default search (empty body)
            value: {}
  responses:
    '200':
      description: Search results retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/Search<Resources>Response'
          examples:
            withResults:
              summary: Page with results
              value:
                data:
                  - id: 1
                    name: "Leche Entera 1L"
                  - id: 2
                    name: "Leche Desnatada 1L"
                pagination:
                  limit: 10
                  offset: 0
                  total: 25
                  hasMore: true
            emptyResults:
              summary: No matching results
              value:
                data: []
                pagination:
                  limit: 20
                  offset: 0
                  total: 0
                  hasMore: false
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Registering in openapi-rest.yml

Add the search path to the root spec:

```yaml
paths:
  /v1/<resource>:
    $ref: './v1/services/<resource>/<resource>-create.yml'
  /v1/<resource>/search:
    $ref: './v1/services/<resource>/<resource>-search.yml'
```

> **Note**: The search path is `/v1/<resource>/search`, not `/v1/<resource>` with a query param. This is a dedicated POST endpoint.

---

## Full JSON Request/Response Examples

### Request

```json
POST /v1/products/search
Content-Type: application/json
Authorization: Bearer eyJhbGciOi...

{
  "filters": {
    "name": "Leche",
    "categoryId": 10
  },
  "limit": 10,
  "offset": 20,
  "sortBy": "name",
  "sortDirection": "asc"
}
```

### Response (200 OK)

```json
{
  "data": [
    {
      "id": 21,
      "name": "Leche Entera 1L"
    },
    {
      "id": 22,
      "name": "Leche Semidesnatada 1L"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 20,
    "total": 45,
    "hasMore": true
  }
}
```

### Response (200 OK — no results)

```json
{
  "data": [],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total": 0,
    "hasMore": false
  }
}
```

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Use GET with many query params for complex searches | Use POST with body |
| Return `204` for empty search results | Return `200` with `data: []` and `total: 0` |
| Return raw array as root response | Wrap in `{ "data": [...], "pagination": {...} }` |
| Use `409 Conflict` on search endpoints | Search is read-only; only 400, 401, 403, 500 |
| Name the operationId `postSearch<Resources>` | Use `search<Resources>` |
| Put pagination fields at root level mixed with data | Separate `data` and `pagination` at root |
| Allow `limit` > 100 | Cap at 100 to prevent abuse |
| Omit `total` from pagination | Always include it for client-side page calculation |
