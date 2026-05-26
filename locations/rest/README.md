# Locations REST API

OpenAPI contract for locations management endpoints.

## Overview

This contract defines the **Locations REST API** specification using OpenAPI 3.0.3.
It is published as a Maven artifact to GitHub Packages and can be consumed by microservices
that need to interact with locations operations.

---

## Structure

```
locations/rest/
├── openapi-rest.yml           # Main OpenAPI spec (VERSION SOURCE OF TRUTH)
├── metadata.yml               # Contract metadata (api-spec-type: rest)
├── README.md                  # This file
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml # Standard error responses
    │   ├── location-types/
    │   │   └── components.yml # Location type schemas
    │   └── locations/
    │       └── components.yml # Location request/response schemas
    └── services/
        ├── location-types/
        │   └── location-types-get-all.yml  # GET /v1/locations/location-types
        └── locations/
            ├── locations-create.yml        # POST /v1/locations
            └── locations-search.yml        # POST /v1/locations/search
```

---

## Version Management

The **version in `openapi-rest.yml` → `info.version` is the SINGLE SOURCE OF TRUTH**.
The CI/CD workflow automatically reads this version and synchronizes the Maven POM before building and publishing.

Current version: **0.0.4**

---

## API Endpoints

### GET /v1/locations/location-types
Retrieves a list of all location types.

**Response (200):** `LocationTypeListResponse`
- List of LocationType entities (id: int32, name: string)

**Error Responses:** 401, 403, 500

### POST /v1/locations
Creates a new location for the current tenant. Requires `store_admin` role.

**Request:** `CreateLocationRequest`
- `name` (string, required, 1-200): Location name. Must be unique per tenant.
- `locationTypeId` (int32, required): FK to location_types. MVP: STORE(1), STORE_WAREHOUSE(2).
- `latitude` (double, required, -90 to 90): Geographic latitude in decimal degrees (WGS84).
- `longitude` (double, required, -180 to 180): Geographic longitude in decimal degrees (WGS84).
- `address` (string, optional, max 500): Physical address.
- `description` (string, optional, max 1000): Optional description.

**Response (201):** `CreateLocationResponse`
- `id` (int32): Unique identifier of the created location.

**Error Responses:** 400 (LOCATION_VALIDATION, LOCATION_TYPE_NOT_ALLOWED_IN_MVP), 401, 403, 404 (LOCATION_TYPE_NOT_FOUND), 409 (LOCATION_NAME_DUPLICATED), 500

### POST /v1/locations/search
Searches locations for the current tenant with optional filters and pagination. Requires `store_admin` role.

**Request:** `SearchLocationsRequest`
- `filters` (object, optional):
  - `keyword` (string): Case-insensitive partial match on name and address.
  - `locationTypeId` (int32): Filter by location type.
  - `active` (boolean): Filter by active status.
- `page` (int32, default 0): Zero-based page index.
- `size` (int32, default 20, 1-100): Items per page.
- `sort` (array): Sort criteria with `field` (name, locationType) and `direction` (ASC, DESC).

**Response (200):** `SearchLocationsResponse`
- `page`, `size`, `totalPages`, `totalItems`: Pagination metadata.
- `items`: Array of `LocationSummary` with id, name, locationType, address, active, latitude, longitude.

**Error Responses:** 400, 401, 403, 500

---

## Maven Artifact

This contract is published to GitHub Packages as:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>locations-rest-stable</artifactId>
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
