# Suppliers REST API

OpenAPI contract for supplier management endpoints.

## Overview

This contract defines the **Suppliers REST API** specification using OpenAPI 3.0.3.
It is published as a Maven artifact to GitHub Packages and can be consumed by microservices
that need to interact with supplier operations.

---

## Structure

```
suppliers/rest/
├── openapi-rest.yml           # Main OpenAPI spec (VERSION SOURCE OF TRUTH)
├── metadata.yml               # Contract metadata (api-spec-type: rest)
├── README.md                  # This file
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml # Standard error responses
    │   └── suppliers/
    │       └── components.yml # Request/Response schemas
    └── services/
        └── suppliers/
            └── suppliers-create.yml  # POST /v1/suppliers endpoint
```

---

## Version Management

The **version in `openapi-rest.yml` → `info.version` is the SINGLE SOURCE OF TRUTH**.
The CI/CD workflow automatically reads this version and synchronizes the Maven POM before building and publishing.

Current version: **0.0.1**

---

## API Endpoints

### POST /v1/suppliers
Creates a new supplier in the system.

**Request Body:** `CreateSupplierRequest`
- `name` (string, required) — min 1, max 200, unique per tenant
- `contactName` (string, optional) — max 200
- `phone` (string, optional) — max 50
- `email` (string, optional) — RFC 5322 format
- `address` (string, optional) — max 500
- `taxId` (string, optional) — max 50, unique per tenant if provided
- `notes` (string, optional) — max 1000

**Response (201):** `CreateSupplierResponse`
- `supplierId` (integer, int64)

**Error Responses:** 400, 401, 403, 409, 500

---

## Maven Artifact

This contract is published to GitHub Packages as:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>suppliers-rest-stable</artifactId>
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
