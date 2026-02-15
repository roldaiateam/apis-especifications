# API Specifications

Repository for API contracts (AsyncAPI & OpenAPI) published as Maven artifacts.

## Overview

This repository manages API contracts for all microservices in the ProactiveDevs ecosystem. Each contract is published as a versioned Maven dependency that can be consumed by microservices.

**Key Features:**
- Pre-compiled Avro classes included in artifacts (no plugin needed in consumers)
- AsyncAPI version is the single source of truth
- Automated version validation on Pull Requests
- Automatic POM synchronization from AsyncAPI specs
- PR comments with Maven dependencies after successful publication

## Structure

```
apis-especifications/
├── .github/
│   └── workflows/
│       ├── validate-contracts.yml    # PR version validation
│       └── publish-contracts.yml     # Contract publication
├── metadata.yml                      # Global API catalog
├── tenants/
│   └── event/                       # Tenants AsyncAPI contract (events)
│       ├── asyncapi.yml             # AsyncAPI 3.0 specification (SOURCE OF TRUTH for version)
│       ├── tenants-avro/            # Avro schemas with import pattern
│       │   └── v1/
│       │       ├── imports/
│       │       │   └── tenant-created.avsc
│       │       └── tenant-created-envelope.avsc
│       ├── metadata.yml             # Contract metadata
│       └── pom.xml                  # Maven module config (with Avro generation)
└── [future APIs]
```

## Interactive API Documentation

Browse and test our API contracts interactively with version history and PR previews.

**GitHub Pages:** https://roldaiateam.github.io/apis-especifications/

### Features

- **Version History**: Browse all published versions of each API (stable, snapshot, unstable)
- **Version Selector**: Switch between different versions dynamically in the UI
- **PR Previews**: Automatic preview documentation for Pull Requests with live URL
- **Automatic Updates**: Documentation deploys automatically when new versions are published to GitHub Packages

### Available APIs

The documentation catalog is automatically generated and includes all published APIs with their version history. Visit the GitHub Pages site to explore:

- REST APIs with interactive Swagger UI
- Version comparison and selection
- Complete OpenAPI specifications

**Note:** AsyncAPI specifications (event-driven APIs) are bundled in the Maven artifacts but not displayed in the web documentation. Use [AsyncAPI Studio](https://studio.asyncapi.com/) or access them from the JAR metadata.

**Setup:** See [GITHUB_PAGES_SETUP.md](./GITHUB_PAGES_SETUP.md) for deployment architecture and configuration.

## Maven Artifacts

All contracts are published to GitHub Packages under:

**GroupId:** `com.proactivedevs.contracts`

### Available Contracts

| Contract | ArtifactId | Type | Version |
|----------|-----------|------|---------|
| Tenants Events | `tenants-event` | AsyncAPI | 1.0.0 |
| Tenants REST | `tenants-rest-stable` | OpenAPI | 0.0.1 |

## Versioning Strategy

### Single Source of Truth: `asyncapi.yml`

The **`info.version`** field in each contract's `asyncapi.yml` is the **authoritative version**. The Maven POM version is automatically synchronized from this value during CI/CD.

**Example:**
```yaml
asyncapi: 3.0.0
info:
  title: Tenants Events API
  version: 1.0.1  # ← This is the source of truth
```

### Dual-Branch Workflow

#### Main Branch (Stable)
- Contains production-ready contracts
- Version format: `X.Y.Z` (e.g., `1.0.1`)
- Published as stable releases to GitHub Packages
- Maven artifact: `tenants-event-1.0.1.jar`
- Automatically tagged with `vX.Y.Z` on merge

#### Develop Branch (Snapshot)
- Contains contracts under development
- Same version in `asyncapi.yml` as main (e.g., `1.0.1`)
- Published with `-SNAPSHOT` suffix automatically
- Maven artifact: `tenants-event-1.0.1-SNAPSHOT.jar`
- Updated continuously as development progresses

### Version Validation Rules

When you open a Pull Request, the `validate-contracts.yml` workflow automatically validates that your API version follows these rules:

| PR Type | Rule | Example |
|---------|------|---------|
| **Feature → Develop** | API version must be **greater than** the latest stable version published on main | If main has `1.0.0`, your PR must have at least `1.0.1` |
| **Develop → Main** | API version must be **greater than** the latest stable version (cannot match existing stable) | If main has `1.0.0`, develop must have `1.0.1` or higher |

**Note:** You only need to change the version in `asyncapi.yml`. The POM is updated automatically.

## Using Contracts in Your Microservice

### 1. Configure GitHub Packages Authentication

Add to your `~/.m2/settings.xml`:

```xml
<servers>
    <server>
        <id>github</id>
        <username>YOUR_GITHUB_USERNAME</username>
        <password>YOUR_GITHUB_TOKEN</password>
    </server>
</servers>
```

### 2. Add GitHub Packages Repository

In your `pom.xml`:

```xml
<repositories>
    <repository>
        <id>github</id>
        <url>https://maven.pkg.github.com/roldaiateam/apis-especifications</url>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

### 3. Add Contract Dependency

For stable releases (from main):
```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event</artifactId>
    <version>1.0.1</version>
</dependency>
```

For development/testing (from develop):
```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event</artifactId>
    <version>1.0.1-SNAPSHOT</version>
</dependency>
```

**Note:** The dependency will be automatically posted as a comment in your PR after successful publication.

### 4. Use Pre-compiled Avro Classes

The artifact includes pre-generated Avro Java classes. **No Avro plugin needed in your project!**

```java
import com.proactivedevs.contracts.tenants.v1.TenantCreated;
import com.proactivedevs.contracts.tenants.v1.TenantCreatedEvent;

// Use the generated classes directly
TenantCreated tenant = TenantCreated.newBuilder()
    .setTenantId("123")
    .setTenantName("Acme Corp")
    .setUserName("john.doe")
    .build();

TenantCreatedEvent event = TenantCreatedEvent.newBuilder()
    .setEventId(UUID.randomUUID().toString())
    .setEventType("tenant.created")
    .setTimestamp(Instant.now().toString())
    .setPayload(tenant)
    .build();
```

### 5. Access Contract Metadata

AsyncAPI and Avro schemas are bundled in the JAR under `META-INF/asyncapi/`:

```java
// Load AsyncAPI spec
InputStream asyncapiStream = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/asyncapi.yml");

// Load Avro schema
InputStream avroSchema = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/tenants-avro/v1/tenant-created-envelope.avsc");
```

## CI/CD Pipeline

### Workflow 1: Validate Contracts (`validate-contracts.yml`)

**Trigger:** Pull Request to `main` or `develop`

**Purpose:** Ensures API versions follow increment rules before merging.

**Process:**
1. Detects which contract modules have changes in the PR
2. Extracts API version from each module's `asyncapi.yml` (`info.version`)
3. Queries GitHub Packages API for published versions
4. Validates version based on target branch rules (see Version Validation Rules above)
5. Fails the PR check if validation fails with clear error messages

**Example PR Check Output:**
```
✅ tenants/event: Version 1.0.1 is valid (greater than latest stable 1.0.0)
```

### Workflow 2: Publish Contracts (`publish-contracts.yml`)

**Trigger:** Push to `main` or `develop` (after PR merge)

**Purpose:** Builds and publishes contract artifacts to GitHub Packages.

**Process:**

1. **Detect Changes:** Only processes modules with actual changes
2. **Validate Versions:** Re-validates as safety net (same logic as PR validation)
3. **Sync POM Version:** Reads `asyncapi.yml` → `info.version` and updates Maven POM
   - On `main`: Uses version as-is (e.g., `1.0.1`)
   - On `develop`: Appends `-SNAPSHOT` (e.g., `1.0.1-SNAPSHOT`)
4. **Build & Test:** Runs `mvn clean verify`
   - Generates Avro classes from schemas
   - Packages classes + schemas into JAR
5. **Deploy:** Publishes to GitHub Packages
6. **Comment on PR:** Posts dependency information as PR comment
7. **Tag Release:** Creates Git tag `vX.Y.Z` (main only)

**Example PR Comment:**
```markdown
## 📦 Contracts Published Successfully

**Release version:** `1.0.1` (stable)

### Maven Dependencies

Add the following dependencies to your `pom.xml`:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event</artifactId>
    <version>1.0.1</version>
</dependency>
```

---

**📚 Package location:** [GitHub Packages](https://github.com/roldaiateam/apis-especifications/packages)
```

## Development Workflow

### Adding a New API Contract

1. **Create directory structure:**
   ```bash
   mkdir -p <domain>/<type>/
   # Example: products/event/
   ```

2. **Add contract files:**
   - `asyncapi.yml` (or `openapi.yml`) - **Set initial version here**
   - Avro schemas in `<domain>-avro/v1/`
   - `metadata.yml`
   - `README.md`
   - `pom.xml` (include Avro maven plugin + build-helper plugin)

3. **Register the contract:**
   - Add module to root `pom.xml`
   - Update root `metadata.yml`

4. **Commit and test:**
   ```bash
   git checkout develop
   git add .
   git commit -m "feat: Add products event contract"
   git push
   ```

5. **Validate with SNAPSHOT:** Test the published snapshot in consuming microservices

6. **Release to production:**
   - Create PR: `develop` → `main`
   - Workflow validates version
   - Merge PR → Stable version published + tagged

### Updating an Existing Contract

#### Step 1: Update the Version (Source of Truth)

**Only change the version in `asyncapi.yml`:**

```yaml
asyncapi: 3.0.0
info:
  title: Tenants Events API
  version: 1.0.2  # ← Increment this (was 1.0.1)
```

**Do NOT touch the POM version** - it will be automatically synchronized during publication.

#### Step 2: Make Your Changes

- Update message schemas
- Add/modify channels or operations
- Update documentation

#### Step 3: Create Feature Branch and PR

```bash
git checkout develop
git pull
git checkout -b feature/update-tenant-event
# Make your changes
git add .
git commit -m "feat: Add tenant updated event"
git push -u origin feature/update-tenant-event
```

Create PR: `feature/update-tenant-event` → `develop`

The validation workflow will:
- ✅ Check that `1.0.2 > 1.0.1` (latest stable)
- ✅ Pass the PR check

#### Step 4: Merge and Test Snapshot

After merging to `develop`:
- Artifact published: `tenants-event-1.0.2-SNAPSHOT.jar`
- PR comment shows Maven dependency
- Test in your microservices with snapshot version

#### Step 5: Release to Production

Create PR: `develop` → `main`

After merge:
- Artifact published: `tenants-event-1.0.2.jar`
- Git tag created: `v1.0.2`
- PR comment shows Maven dependency

### Version Increment Guidelines

| Change Type | Version Increment | Example |
|------------|------------------|---------|
| Bug fix in schema/docs | Patch | `1.0.1` → `1.0.2` |
| New optional field | Minor | `1.0.2` → `1.1.0` |
| New message type (non-breaking) | Minor | `1.1.0` → `1.2.0` |
| Breaking change | Major | `1.2.0` → `2.0.0` |

#### Breaking Changes (Major Version)

1. Increment major version (e.g., `1.0.0` → `2.0.0`)
2. Consider creating new schema version directory (e.g., `v2/`)
3. Update namespace in Avro schemas: `com.proactivedevs.contracts.tenants.v2`
4. Document migration path in contract README
5. Coordinate with consuming teams before release
6. Keep old version available during transition period

## Contract Guidelines

### AsyncAPI Contracts

- **Use AsyncAPI 3.0.0**
- **Version field is mandatory** - this drives Maven versioning
- Define all channels, operations, and messages clearly
- Include RabbitMQ bindings (exchange type, routing keys, durability)
- Reference Avro schemas using `$ref` to `.avsc` files
- Document all fields with descriptions
- Include examples where helpful

### Avro Schemas

- **Version schemas in directories:** `v1/`, `v2/`, etc.
- **Use import pattern for reusable types:**
  ```
  tenants-avro/v1/
  ├── imports/
  │   └── tenant-created.avsc  ← Reusable record
  └── tenant-created-envelope.avsc  ← References by name
  ```
- **Namespaces:** `com.proactivedevs.contracts.<domain>.v<X>`
- **Field documentation:** Always include `doc` fields
- **Compatibility:** Plan for forward/backward compatibility
- **Logical types:** Use Avro logical types (timestamp-millis, decimal, etc.)

### POM Configuration for New Contracts

Each contract module needs:

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.avro</groupId>
        <artifactId>avro</artifactId>
        <version>1.11.3</version>
    </dependency>
</dependencies>

<build>
    <resources>
        <!-- Bundle AsyncAPI and schemas -->
        <resource>
            <directory>${project.basedir}</directory>
            <includes>
                <include>asyncapi.yml</include>
                <include>metadata.yml</include>
                <include>*-avro/**/*.avsc</include>
            </includes>
            <targetPath>META-INF/asyncapi</targetPath>
        </resource>
    </resources>

    <plugins>
        <!-- Generate Avro classes -->
        <plugin>
            <groupId>org.apache.avro</groupId>
            <artifactId>avro-maven-plugin</artifactId>
            <version>1.11.3</version>
            <executions>
                <execution>
                    <phase>generate-sources</phase>
                    <goals>
                        <goal>schema</goal>
                    </goals>
                    <configuration>
                        <sourceDirectory>${project.basedir}/*-avro/v1</sourceDirectory>
                        <imports>
                            <import>${project.basedir}/*-avro/v1/imports/*.avsc</import>
                        </imports>
                        <excludes>
                            <exclude>**/imports/**</exclude>
                        </excludes>
                        <outputDirectory>${project.build.directory}/generated-sources/avro</outputDirectory>
                    </configuration>
                </execution>
            </executions>
        </plugin>

        <!-- Add generated sources to classpath -->
        <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>build-helper-maven-plugin</artifactId>
            <version>3.5.0</version>
            <executions>
                <execution>
                    <phase>generate-sources</phase>
                    <goals>
                        <goal>add-source</goal>
                    </goals>
                    <configuration>
                        <sources>
                            <source>${project.build.directory}/generated-sources/avro</source>
                        </sources>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### Metadata Files

Update `metadata.yml` with:
- Contract name and description
- API version (informational - synced from asyncapi.yml)
- Messaging configuration (exchanges, routing keys, queues)
- Event types and their purposes
- Changelog of major changes

## Troubleshooting

### PR Validation Fails

**Error:** "Version 1.0.0 must be > 1.0.0 (latest stable)"

**Solution:** Increment the version in `asyncapi.yml`:
```yaml
info:
  version: 1.0.1  # Was 1.0.0
```

### Cannot Download Artifact from GitHub Packages

**Problem:** 401 Unauthorized

**Solution:** Configure GitHub token in `~/.m2/settings.xml`:
```xml
<server>
    <id>github</id>
    <username>YOUR_GITHUB_USERNAME</username>
    <password>ghp_xxxxxxxxxxxx</password>
</server>
```

Token needs `read:packages` scope.

### Avro Classes Not Found in Consumer

**Problem:** `ClassNotFoundException: com.proactivedevs.contracts.tenants.v1.TenantCreated`

**Possible causes:**
1. **Dependency not added** - Check your `pom.xml`
2. **Wrong version** - Ensure version exists in GitHub Packages
3. **IDE cache** - Run `mvn clean compile` or reimport Maven project
4. **Repository not configured** - Add GitHub Packages repository to `pom.xml`

### POM Version Out of Sync

**Problem:** POM shows `1.0.0-SNAPSHOT` but asyncapi.yml has `1.0.1`

**Solution:** This is expected! The POM will be automatically synchronized during CI/CD. Just commit the `asyncapi.yml` change. When the workflow runs, it will:
1. Read version `1.0.1` from `asyncapi.yml`
2. Update POM to `1.0.1-SNAPSHOT` (on develop) or `1.0.1` (on main)
3. Build and publish with correct version

**Do NOT manually update POM versions** - let the automation handle it.

## Support

For questions or issues:
- Create an issue in this repository
- Contact: `team@proactivedevs.com`

## License

Copyright © 2026 ProactiveDevs
