---
name: api-schema-components
description: Generate domain schema components (Request, Response, Summary, Id types) under v1/components/<resource>/components.yml following the repository's naming and structure conventions.
---

# Skill: Domain Schema Components

## Purpose

This skill generates the **domain-specific schemas** for a REST API — the request bodies, response bodies, summary/list entities, and reusable ID types. These live in a dedicated components file per domain concept, separate from error schemas.

## When to Use

- After creating the error components (Skill 2) and before creating endpoint service files (Skill 4)
- When adding a new sub-resource to an existing API (e.g., `barcode/components.yml` under Products)
- When refactoring schemas for an existing API

## File Location

```
<resource>/rest/v1/components/<domain>/components.yml
```

Where `<domain>` is the logical grouping:
- Primary resource: `<resource>/components.yml` (e.g., `products/components.yml`)
- Sub-resources: `<sub-resource>/components.yml` (e.g., `barcode/components.yml`, `units/components.yml`)

### Examples from the repo

```
products/rest/v1/components/
├── products/components.yml     # CreateProductRequest, CreateProductResponse
├── barcode/components.yml      # GetProductBarcodeTypesResponse, BarcodeTypeId
├── units/components.yml        # GetProductUnitsResponse, UnitOfMeasure, UnitOfMeasureId
└── errors/components.yml       # ApiErrorResponse (handled by api-error-components skill)
```

## Naming Conventions

### Schema names — PascalCase, descriptive

| Pattern | Format | Example |
|---------|--------|---------|
| Create request | `Create<Resource>Request` | `CreateProductRequest`, `CreateTenantRequest` |
| Create response | `Create<Resource>Response` | `CreateProductResponse`, `CreateCategoryResponse` |
| Get single response | `Get<Resource>Response` | `Get<Resource>Response` |
| Get list response | `Get<Resources>Response` | `GetCategoriesResponse`, `GetProductBarcodeTypesResponse` |
| Update request | `Update<Resource>Request` | `Update<Resource>Request` |
| Summary entity | `<Resource>Summary` | `CategorySummary` |
| Full entity | `<Resource>` or `<Resource>Detail` | `UnitOfMeasure` |
| ID type | `<Resource>Id` | `CategoryId`, `BarcodeTypeId`, `UnitOfMeasureId` |
| Nested input | `Create<Resource><Child>Input` | `CreateProductBarcodeInput`, `CreateProductImageInput` |

### Property names — camelCase

All properties use camelCase. Examples from repo:
- `firstName`, `lastName`, `companyName`, `companyTin`
- `trackedByBatch`, `trackedBySerial`, `trackedByExpiry`
- `sellPrice`, `sellPriceCurrencyId`
- `barcodeTypeId`, `unitOfMeasureId`, `categoryId`
- `isMain`, `isDefault`, `sortOrder`
- `parentId`, `parentCategoryId`

### ID field patterns

The repo uses two ID types:

| Type | Format | When to use |
|------|--------|-------------|
| `integer` + `format: int64` | `42` | Auto-increment database IDs (products, categories, units) |
| `string` + `format: uuid` | `"550e8400-..."` | Distributed/external IDs (tenants) |

Always create a **reusable ID schema** for the primary resource:

```yaml
<Resource>Id:
  type: integer
  format: int64
  description: Unique identifier for the <resource>
  example: 42
```

---

## Schema Structure Patterns

### Pattern 1: Create Request — flat object with validations

```yaml
Create<Resource>Request:
  type: object
  description: >
    Request payload for creating a new <resource>.
    The tenant is automatically resolved from the JWT token.
    Business rules:
    - <List business validation rules here>
  required:
    - <field1>
    - <field2>
  properties:
    <field1>:
      type: string
      description: <Description>
      minLength: <min>
      maxLength: <max>
      pattern: "<regex>"
      example: "<example>"
    <field2>:
      type: integer
      format: int64
      description: <Description>
      example: <number>
```

**Validation annotations** used in the repo:
- `minLength` / `maxLength` — on all strings
- `pattern` — regex for structured strings (SKU, phone, password, company name)
- `minimum` — on numeric fields (e.g., `sellPrice` has `minimum: 0.01`)
- `format` — `email`, `uri`, `uuid`, `int32`, `int64`, `double`
- `nullable: true` — only on truly optional fields that can be null (like `details` in errors)

### Pattern 2: Create Response — minimal, just the ID

```yaml
Create<Resource>Response:
  type: object
  properties:
    <resource>Id:
      type: integer
      format: int64
      description: Unique identifier for the created <resource>.
      example: 42
```

Some responses include additional fields (e.g., `CreateTenantResponse` includes `token`). Add them only when the business logic requires returning more than the ID.

### Pattern 3: List/Get Response — wrapper object with array

```yaml
Get<Resources>Response:
  type: object
  properties:
    <resources>:
      type: array
      description: List of <resources> available for the tenant
      items:
        $ref: '#/components/schemas/<Resource>Summary'
```

> **Important**: Never return a raw array as the root response. Always wrap it in an object with a named array property.

### Pattern 4: Summary entity — lightweight representation for lists

```yaml
<Resource>Summary:
  type: object
  description: Summary information about a <resource>, used for listing without detailed information
  properties:
    id:
      $ref: '#/components/schemas/<Resource>Id'
    name:
      type: string
      description: Name of the <resource>
      example: "<Example>"
```

### Pattern 5: Reusable ID type

```yaml
<Resource>Id:
  type: integer
  format: int64
  description: Unique identifier for the <resource>
  example: 42
```

### Pattern 6: Nested input objects (for arrays in create requests)

When a create request contains an array of child objects:

```yaml
Create<Resource><Child>Input:
  type: object
  description: <Child> to be associated with a <resource> at creation time.
  required:
    - <field1>
    - <field2>
  properties:
    <field1>:
      type: string
      description: <Description>
      minLength: 1
      maxLength: 50
      example: "<example>"
    <field2>:
      type: boolean
      description: <Description>
      example: true
```

### Pattern 7: Cross-referencing schemas from other component files

When a schema needs to reference an ID type from a sibling component file:

```yaml
barcodeTypeId:
  $ref: '../barcode/components.yml#/components/schemas/BarcodeTypeId'
```

The relative path goes from the current component file to the sibling domain folder.

---

## Complete Template: Primary Resource Components

```yaml
components:
  schemas:
    Create<Resource>Request:
      type: object
      description: >
        Request payload for creating a new <resource>.
        The tenant is automatically resolved from the JWT token.
      required:
        - name
      properties:
        name:
          type: string
          description: Name of the <resource>
          minLength: 1
          maxLength: 255
          example: "<Example Name>"
        description:
          type: string
          description: Optional description
          maxLength: 500
          example: "<Example description>"

    Create<Resource>Response:
      type: object
      properties:
        <resource>Id:
          type: integer
          format: int64
          description: Unique identifier for the created <resource>.
          example: 42

    Get<Resources>Response:
      type: object
      properties:
        <resources>:
          type: array
          description: List of <resources> available for the tenant
          items:
            $ref: '#/components/schemas/<Resource>Summary'

    <Resource>Summary:
      type: object
      description: Summary information about a <resource>
      properties:
        id:
          $ref: '#/components/schemas/<Resource>Id'
        name:
          type: string
          description: Name of the <resource>
          example: "<Example>"

    <Resource>Id:
      type: integer
      format: int64
      description: Unique identifier for the <resource>
      example: 42
```

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Use snake_case for properties | Use camelCase: `firstName`, not `first_name` |
| Use snake_case for schema names | Use PascalCase: `CreateProductRequest`, not `create_product_request` |
| Return a raw array as root response | Wrap in object: `{ "items": [...] }` |
| Omit `example` on properties | Every property should have an `example` |
| Omit `description` on properties | Every property needs a `description` |
| Omit validation constraints on strings | Always add `minLength`, `maxLength`; add `pattern` for structured data |
| Define the same ID type in multiple files | Create a reusable `<Resource>Id` schema and `$ref` it |
| Put error schemas in this file | Errors go in `errors/components.yml` (separate skill) |
| Use `allOf` for simple extension | Only use `allOf` when genuinely extending a base schema |
