# Maven Generator

This directory contains the Maven generator configuration and templates for converting API specifications (AsyncAPI and OpenAPI) into Maven artifacts (JARs).

## Overview

The Maven generator is part of the multi-generator architecture that decouples the repository from build-specific configuration. Instead of committing `pom.xml` files to git, we use Jinja2 templates that are rendered during CI/CD workflows.

## Files

### `config.yml`
Central configuration file containing:
- Maven plugin versions
- Dependency versions
- Artifact naming strategies
- Version strategies per branch
- Distribution management settings
- Module-specific defaults (event, websocket, rest)

### `pom.event.xml.j2`
Jinja2 template for generating `pom.xml` files for event/websocket modules (AsyncAPI + Avro).

**Features:**
- Avro code generation from `.avsc` schemas
- Includes `avro-maven-plugin` for compiling Avro schemas to Java classes
- Packages spec files in `META-INF/asyncapi`
- Configurable Avro generation options (string type, decimal support, setters, etc.)

### `pom.rest.xml.j2`
Jinja2 template for generating `pom.xml` files for REST modules (OpenAPI).

**Features:**
- OpenAPI code generation from `.yml` specifications
- Includes `openapi-generator-maven-plugin` with Spring generator
- Packages spec files in `META-INF/openapi`
- Generates only models (not APIs or supporting files)
- Configured for Spring Boot 3, Jakarta EE, and Lombok

## Template Variables

Templates expect the following context variables:

### Required Variables
- `maven` - Complete maven configuration from `config.yml`
- `artifact_id` - Generated artifact ID (e.g., `tenants-event-stable`)
- `version` - Maven version (e.g., `1.0.3` or `1.0.3-SNAPSHOT`)
- `module_name` - Human-readable module name
- `module_defaults` - Module-specific configuration from `config.yml`
- `distribution` - Distribution management configuration
- `package_name` - Java package name (for REST modules, e.g., `com.proactivedevs.contracts.tenants.rest.v1`)

### Example Context (Event Module)
```yaml
maven:
  group_id: com.proactivedevs.contracts
  java_version: 21
  encoding: UTF-8
  plugins:
    maven_resources: 3.3.1
    avro_maven_plugin: 1.11.3
    build_helper_maven_plugin: 3.5.0
  dependencies:
    avro: 1.11.3

artifact_id: tenants-event-stable
version: 1.0.3-SNAPSHOT
module_name: Tenants Event Contract
module_defaults:
  event:
    packaging: jar
    description: AsyncAPI contract for Events (RabbitMQ + Avro)
    # ... additional configuration

distribution:
  repository:
    id: github
    name: GitHub Packages
    url: https://maven.pkg.github.com/roldaiateam/apis-especifications
```

### Example Context (REST Module)
```yaml
maven:
  group_id: com.proactivedevs.contracts
  java_version: 21
  plugins:
    openapi_generator_maven_plugin: 7.2.0
  dependencies:
    swagger_annotations: 2.2.20
    jakarta_validation_api: 3.0.2
    lombok: 1.18.30

artifact_id: tenants-rest-stable
version: 0.0.1-SNAPSHOT
module_name: Tenants REST Contract
package_name: com.proactivedevs.contracts.tenants.rest.v1
module_defaults:
  rest:
    packaging: jar
    openapi:
      generator_name: spring
      # ... additional configuration
```

## Usage

### Manual Template Rendering (for testing)

```bash
# Render event module POM
python3 scripts/generators/common/render-template.py \
  .github/generators/mvn/pom.event.xml.j2 \
  /tmp/context.yml \
  /tmp/pom.xml

# Render REST module POM
python3 scripts/generators/common/render-template.py \
  .github/generators/mvn/pom.rest.xml.j2 \
  /tmp/context-rest.yml \
  /tmp/pom-rest.xml
```

### Automated Generation (CI/CD)

The generator script `scripts/generators/generate-mvn.sh` handles:
1. Reading module metadata and spec files
2. Extracting API version from spec
3. Determining Maven version based on branch
4. Rendering the appropriate POM template
5. Running Maven build and deploy

```bash
# Generate stable artifact from main branch
bash scripts/generators/generate-mvn.sh tenants/event stable

# Generate snapshot artifact from develop branch
bash scripts/generators/generate-mvn.sh tenants/rest unstable 1.0.3-SNAPSHOT
```

## Generated Artifacts

### Event/WebSocket Modules
**Artifact ID:** `{module_name}-{stability}` (e.g., `tenants-event-stable`)

**Contents:**
- Compiled Avro-generated Java classes
- `META-INF/asyncapi/asyncapi.yml` - AsyncAPI specification
- `META-INF/asyncapi/metadata.yml` - Module metadata
- `META-INF/asyncapi/tenants-avro/**/*.avsc` - Avro schemas

**Dependencies:**
- `org.apache.avro:avro:1.11.3`

### REST Modules
**Artifact ID:** `{module_name}-{stability}` (e.g., `tenants-rest-stable`)

**Contents:**
- OpenAPI-generated model classes (Spring Boot 3 + Lombok)
- `META-INF/openapi/openapi-rest.yml` - OpenAPI specification
- `META-INF/openapi/metadata.yml` - Module metadata
- `META-INF/openapi/v1/**/*.yml` - Additional OpenAPI fragments

**Dependencies:**
- `io.swagger.core.v3:swagger-annotations:2.2.20`
- `jakarta.validation:jakarta.validation-api:3.0.2`
- `org.projectlombok:lombok:1.18.30` (provided)
- `org.openapitools:jackson-databind-nullable:0.2.6`
- `jakarta.annotation:jakarta.annotation-api:2.1.1`

## Version Strategy

Maven versions are determined by the branch and stability flag:

| Branch Type | Stability | Version Pattern |
|-------------|-----------|-----------------|
| `main` | stable | `{api_version}` (e.g., `1.0.3`) |
| `develop` | stable | `{api_version}-SNAPSHOT` (e.g., `1.0.3-SNAPSHOT`) |
| `feature/*` | unstable | `{api_version}-{branch_name}-SNAPSHOT` (e.g., `1.0.3-feature-xyz-SNAPSHOT`) |

The `api_version` is always extracted from the spec file's `info.version` field.

## Backward Compatibility

The generated JARs are **100% identical** to those produced by the previous system where `pom.xml` files were checked into git. This ensures zero impact on consumers.

**Unchanged:**
- Maven coordinates (groupId:artifactId:version)
- JAR structure and contents
- Java package names
- Dependency versions
- Spec file locations in JAR

**Consumer projects require no changes:**
```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event-stable</artifactId>
    <version>1.0.3</version>
</dependency>
```

## Configuration Updates

### Adding New Dependencies

To add dependencies to all modules of a type:

1. Update `config.yml`:
```yaml
maven:
  dependencies:
    new_library: 2.0.0
```

2. Update the corresponding template (`pom.event.xml.j2` or `pom.rest.xml.j2`):
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>new-library</artifactId>
    <version>{{ maven.dependencies.new_library }}</version>
</dependency>
```

### Changing Plugin Versions

Update plugin versions in `config.yml`:
```yaml
maven:
  plugins:
    avro_maven_plugin: 1.12.0  # Updated version
```

Templates automatically use the new version on next build.

### Modifying Code Generation Options

For Avro (event modules), update in `config.yml`:
```yaml
module_defaults:
  event:
    avro:
      string_type: CharSequence  # Changed from String
      create_setters: false      # Changed from true
```

For OpenAPI (REST modules), update in `config.yml`:
```yaml
module_defaults:
  rest:
    openapi:
      config_options:
        useSpringBoot3: true
        useLombok: true
        # Add new options here
```

## Troubleshooting

### Template Rendering Errors

If template rendering fails, check:
1. YAML context file is valid
2. All required variables are present
3. Jinja2 syntax is correct in template

**Debug by rendering manually:**
```bash
python3 scripts/generators/common/render-template.py \
  .github/generators/mvn/pom.event.xml.j2 \
  /tmp/debug-context.yml \
  /tmp/debug-pom.xml

# Inspect the rendered output
cat /tmp/debug-pom.xml
```

### Maven Build Failures

If Maven build fails:
1. Verify the rendered POM is valid XML
2. Check that all plugin versions exist in Maven Central
3. Ensure dependency versions are compatible
4. Verify the spec file paths are correct

**Test locally:**
```bash
# Render and validate POM
xmllint --noout /tmp/pom.xml

# Run Maven build
cd /tmp/build-directory
mvn clean verify -X  # -X for debug output
```

### Missing Generated Sources

If generated sources are missing:
1. Check Avro/OpenAPI source directories exist
2. Verify schema files are valid
3. Check plugin execution order in POM
4. Ensure build-helper-maven-plugin adds sources

## Related Documentation

- [Generator Architecture](../../README.md)
- [Generator Registry](../registry.yml)
- [Module Metadata](../../../tenants/event/metadata.yml)
- [Jinja2 Template Syntax](https://jinja.palletsprojects.com/)
