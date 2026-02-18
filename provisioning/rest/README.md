# Provisioning REST API Contract

## Overview

This contract defines the **Provisioning REST API** specification using OpenAPI 3.0.3.
It is published as a Maven artifact and consumed by services that need to follow tenant provisioning progress.

## Structure

```text
provisioning/rest/
├── openapi-rest.yml                    # Main OpenAPI spec (version source of truth)
├── metadata.yml                        # Contract metadata (api-spec-type: rest)
├── README.md                           # This file
├── pom.xml                             # Maven build configuration
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml          # Standard error responses
    │   └── provisioning/
    │       └── components.yml          # Provisioning schemas and parameters
    └── services/
        └── provisioning/
            ├── tenants-events.yml      # GET /v1/tenants/{tenantId}/events
            └── tenants-status.yml      # GET /v1/tenants/{tenantId}/status
```

## Version Management

The version in `openapi-rest.yml` under `info.version` is the source of truth for this contract.
Current version: **0.0.1**

## API Endpoints

### GET /v1/tenants/{tenantId}/events
Creates a Server-Sent Events (SSE) stream with real-time provisioning updates.

Response content type: `text/event-stream`

### GET /v1/tenants/{tenantId}/status
Returns the current provisioning status as polling fallback when SSE is unavailable.

Response schema: `TenantProvisioningStatus`

### Common Error Responses
`400`, `401`, `403`, `409`, `500`

## Maven Artifact

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>provisioning-rest-stable</artifactId>
    <version>X.Y.Z</version>
</dependency>
```

## Generated Model Package

`com.proactivedevs.contracts.provisioning.rest.v1.model`

## Maintainer

**Andrés Reinaldo Cid**
andresrc345@gmail.com
