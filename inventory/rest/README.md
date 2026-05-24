# Inventory REST API

OpenAPI contract for inventory management endpoints.

## Overview

This contract defines the **Inventory REST API** specification using OpenAPI 3.0.3.
It is published as a Maven artifact to GitHub Packages and can be consumed by microservices
that need to interact with inventory operations.

---

## Structure

```
inventory/rest/
├── openapi-rest.yml           # Main OpenAPI spec (VERSION SOURCE OF TRUTH)
├── metadata.yml               # Contract metadata (api-spec-type: rest)
├── README.md                  # This file
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml # Standard error responses
    │   └── movement-types/
    │       └── components.yml # Request/Response schemas
    └── services/
        └── movement-types/
            └── movement-types-get-all.yml  # GET /v1/inventory/movement-types endpoint
```

---

## Version Management

The **version in `openapi-rest.yml` → `info.version` is the SINGLE SOURCE OF TRUTH**.
The CI/CD workflow automatically reads this version and synchronizes the Maven POM before building and publishing.

Current version: **0.0.1**

---

## API Endpoints

### GET /v1/inventory/movement-types
Retrieves a list of all movement types.

**Response (200):** `MovementTypeListResponse`
- List of MovementType entities (id: int32, name: string)

**Error Responses:** 401, 403, 500

---

## Maven Artifact

This contract is published to GitHub Packages as:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>inventory-rest-stable</artifactId>
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
