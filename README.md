# API Specifications

Repository for API contracts (AsyncAPI & OpenAPI) published as Maven artifacts.

## Overview

This repository manages API contracts for all microservices in the ProactiveDevs ecosystem. Each contract is published as a versioned Maven dependency that can be consumed by microservices.

## Structure

```
apis-especifications/
├── metadata.yml              # Global API catalog
├── tenants/
│   └── event/               # Tenants AsyncAPI contract (events)
│       ├── asyncapi.yml     # AsyncAPI 3.0 specification
│       ├── tenants-avro/    # Avro schemas
│       └── metadata.yml     # Contract metadata
└── [future APIs]
```

## Interactive API Documentation

Browse and test our OpenAPI contracts interactively using Swagger UI:

**Netlify Site:** The site will be deployed automatically via GitHub Actions to Netlify.

### Available REST APIs

| API | Stable (main) | Snapshot (develop) |
|-----|---------------|-------------------|
| Tenants REST API | Available at `/stable/tenants-rest/` | Available at `/snapshot/tenants-rest/` |

**Note:** AsyncAPI specifications (event-driven APIs) are not displayed via Swagger UI. Use [AsyncAPI Studio](https://studio.asyncapi.com/) or download the specs from this repository.

**Setup:** See [NETLIFY_SETUP.md](./NETLIFY_SETUP.md) for deployment configuration.

## Maven Artifacts

All contracts are published to GitHub Packages under:

**GroupId:** `com.proactivedevs.contracts`

### Available Contracts

| Contract | ArtifactId | Type | Version |
|----------|-----------|------|---------|
| Tenants Events | `tenants-event` | AsyncAPI | 1.0.0 |
| Tenants REST | `tenants-rest-stable` | OpenAPI | 0.0.1 |

## Versioning Strategy

This repository uses a dual-branch versioning strategy:

### Main Branch (Stable)
- Contains production-ready contracts
- Version format: `X.Y.Z` (e.g., `1.0.0`)
- Published as stable releases to GitHub Packages
- Automatically tagged with `vX.Y.Z` on every merge

### Develop Branch (Snapshot)
- Contains contracts under development
- Version format: `X.Y.Z-SNAPSHOT` (e.g., `1.0.0-SNAPSHOT`)
- Published as snapshot releases
- Updated continuously as development progresses

## Using Contracts in Your Microservice

### 1. Add GitHub Packages Repository

In your `pom.xml` or `settings.xml`:

```xml
<repositories>
    <repository>
        <id>github</id>
        <url>https://maven.pkg.github.com/ThalioStock/apis-especifications</url>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

### 2. Add Contract Dependency

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event</artifactId>
    <version>1.0.0</version>
</dependency>
```

For development/testing with SNAPSHOT versions:
```xml
<version>1.0.0-SNAPSHOT</version>
```

### 3. Access Contract Resources

AsyncAPI and Avro schemas are bundled in the JAR under `META-INF/asyncapi/`:

```java
// Load AsyncAPI spec
InputStream asyncapiStream = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/asyncapi.yml");

// Load Avro schema
InputStream avroStream = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/tenants-avro/v1/tenant-created-envelope.avsc");
```

## CI/CD Pipeline

The repository uses GitHub Actions to automatically publish contracts:

### On Push to Main
1. Removes `-SNAPSHOT` from version
2. Builds and verifies the contracts
3. Deploys to GitHub Packages as a stable release
4. Creates a Git tag (`vX.Y.Z`)

### On Push to Develop
1. Keeps `-SNAPSHOT` version
2. Builds and verifies the contracts
3. Deploys to GitHub Packages as a snapshot release

## Development Workflow

### Adding a New API Contract

1. Create a new directory under the appropriate domain (e.g., `products/event/`)
2. Add the contract files:
   - `asyncapi.yml` or `openapi.yml`
   - Schemas (Avro, JSON Schema, etc.)
   - `metadata.yml`
   - `README.md`
   - `pom.xml`
3. Register the contract in root `metadata.yml`
4. Add the module to root `pom.xml`
5. Commit to `develop` branch
6. Test the SNAPSHOT version in consuming microservices
7. Merge to `main` when ready for production

### Updating an Existing Contract

#### Non-breaking Changes (Patch/Minor)
1. Update the contract in `develop` branch
2. Increment version appropriately (e.g., `1.0.0` → `1.1.0` or `1.0.1`)
3. Test with SNAPSHOT in consuming services
4. Merge to `main` when validated

#### Breaking Changes (Major)
1. Increment major version (e.g., `1.0.0` → `2.0.0`)
2. Consider creating a new schema version directory (e.g., `v2/`)
3. Document migration path in README
4. Coordinate with consuming teams before release

## Contract Guidelines

### AsyncAPI Contracts
- Use AsyncAPI 3.0.0
- Define all channels, operations, and messages
- Include RabbitMQ bindings (exchange type, routing keys)
- Use Avro for message serialization
- Document all fields with descriptions

### Avro Schemas
- Version schemas in separate directories (`v1/`, `v2/`)
- Use meaningful namespaces: `com.proactivedevs.contracts.<domain>.v<X>`
- Include documentation in `doc` fields
- Plan for forward/backward compatibility

### Metadata
- Update `metadata.yml` with contract details
- Include messaging configuration (exchange, routing keys)
- Document event types and purposes

## Support

For questions or issues:
- Create an issue in this repository
- Contact: `team@proactivedevs.com`

## License

Copyright © 2026 ProactiveDevs
