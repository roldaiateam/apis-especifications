# Generator Scripts

This directory contains the code generation scripts for transforming API specifications into language-specific artifacts.

## Architecture

The generator system is designed to be **generator-agnostic**, supporting multiple target languages and build systems:

- **Maven (Java)**: Current implementation
- **npm (TypeScript/JavaScript)**: Future
- **Go**: Future
- **Python**: Future

## Directory Structure

```
scripts/generators/
├── generate-mvn.sh              # Maven generator (Java)
├── common/                      # Shared utilities
│   ├── extract-version.sh       # Extract version from spec files
│   ├── render-template.py       # Jinja2 template renderer
│   ├── generate-avro.sh         # Avro → Java code generation (Docker)
│   └── generate-openapi.sh      # OpenAPI → Java code generation (Docker)
└── README.md                    # This file
```

## Maven Generator

### Usage

```bash
./scripts/generators/generate-mvn.sh <module-path> <stability> [version-override] [--deploy]
```

**Arguments:**
- `module-path`: Path to the API module (e.g., `tenants/event`, `tenants/rest`)
- `stability`: `stable` or `unstable`
- `version-override`: (Optional) Override version from spec file
- `--deploy`: (Optional) Deploy artifacts to Maven repository after build

**Examples:**

```bash
# Generate stable version from main branch
./scripts/generators/generate-mvn.sh tenants/event stable

# Generate unstable snapshot version
./scripts/generators/generate-mvn.sh tenants/rest unstable

# Generate with custom version
./scripts/generators/generate-mvn.sh tenants/event stable 1.0.3

# Generate and deploy
./scripts/generators/generate-mvn.sh tenants/event stable 1.0.3 --deploy

# Generate feature branch snapshot
./scripts/generators/generate-mvn.sh tenants/event unstable 1.0.3-feature-auth-SNAPSHOT --deploy
```

### How It Works

1. **Version Extraction**: Reads `info.version` from `asyncapi.yml` or `openapi-rest.yml`
2. **Version Strategy**:
   - `stable`: Uses version as-is (e.g., `1.0.3`)
   - `unstable`: Appends `-SNAPSHOT` (e.g., `1.0.3-SNAPSHOT`)
   - Override: Uses provided version exactly
3. **Code Generation**:
   - **Avro**: Uses `apache/avro-tools:1.11.3` Docker image
   - **OpenAPI**: Uses `openapitools/openapi-generator-cli:v7.2.0` Docker image
4. **Template Rendering**: Generates `pom.xml` from Jinja2 templates
5. **Maven Build**: Runs `mvn clean verify` to compile and test
6. **Deployment**: (Optional) Runs `mvn deploy` to publish to GitHub Packages

### Build Artifacts

Generated artifacts are placed in `/tmp/apis-build-<pid>/<artifact-id>/`:

```
/tmp/apis-build-12345/tenants-event-stable/
├── pom.xml                              # Generated from template
├── src/
│   └── main/
│       ├── java/                        # Generated Java classes
│       │   └── com/proactivedevs/contracts/...
│       └── resources/
│           └── META-INF/
│               └── asyncapi/            # Spec files
│                   ├── asyncapi.yml
│                   ├── metadata.yml
│                   └── tenants-avro/
└── target/
    ├── tenants-event-stable-1.0.3.jar   # Built artifact
    └── generated-sources/
        └── avro/                        # Generated code
```

### JAR Contents

The generated JAR includes:

- **Compiled Java classes**: Generated from Avro/OpenAPI specs
- **Spec files**: Located in `META-INF/asyncapi/` or `META-INF/openapi/`
- **Schemas**: Avro schemas or OpenAPI definitions
- **Metadata**: Module metadata from `metadata.yml`

### Artifact Naming

- **Stable**: `{module-name}-stable` (e.g., `tenants-event-stable`)
- **Unstable**: `{module-name}-unstable` (e.g., `tenants-event-unstable`)

### Maven Coordinates

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event-stable</artifactId>
    <version>1.0.3</version>
</dependency>
```

## Common Utilities

### extract-version.sh

Extracts the version from AsyncAPI or OpenAPI spec files.

```bash
./scripts/generators/common/extract-version.sh tenants/event/asyncapi.yml
# Output: 1.0.3
```

### render-template.py

Renders Jinja2 templates with YAML context.

```bash
python3 ./scripts/generators/common/render-template.py \
    .github/generators/mvn/pom.event.xml.j2 \
    context.yml \
    output/pom.xml
```

**Context YAML Example:**

```yaml
module_path: tenants/event
module_type: event
artifact_id: tenants-event-stable
group_id: com.proactivedevs.contracts
version: 1.0.3
package_name: com.proactivedevs.contracts.tenants.v1
```

### generate-avro.sh

Generates Java classes from Avro schema files using Docker.

```bash
./scripts/generators/common/generate-avro.sh \
    tenants/event \
    /tmp/output
```

**Requirements:**
- Docker must be running
- Avro schemas in `{module}/tenants-avro/v1/*.avsc`

### generate-openapi.sh

Generates Java classes from OpenAPI specifications using Docker.

```bash
./scripts/generators/common/generate-openapi.sh \
    tenants/rest \
    /tmp/output \
    com.proactivedevs.contracts.tenants.v1
```

**Requirements:**
- Docker must be running
- OpenAPI spec at `{module}/openapi-rest.yml`

## Error Handling

All scripts use `set -euo pipefail` for strict error handling:

- **`-e`**: Exit immediately if a command fails
- **`-u`**: Treat unset variables as errors
- **`-o pipefail`**: Fail if any command in a pipeline fails

## Dependencies

### System Requirements

- **Bash**: 4.0+
- **Python**: 3.8+
- **Docker**: 20.10+
- **Maven**: 3.9+
- **Java**: 21

### Python Dependencies

- `jinja2`: Template rendering
- `pyyaml`: YAML parsing

Install with:

```bash
pip install jinja2 pyyaml
```

## CI/CD Integration

These scripts are designed to run in GitHub Actions workflows:

### publish-contracts.yml

Publishes stable versions from `main` branch:

```yaml
- name: Generate Maven artifacts
  run: |
    ./scripts/generators/generate-mvn.sh \
      "${{ matrix.module }}" \
      stable \
      "${{ steps.version.outputs.version }}" \
      --deploy
```

### generate-unstable-api.yml

Generates unstable versions from feature branches:

```yaml
- name: Generate unstable artifacts
  run: |
    ./scripts/generators/generate-mvn.sh \
      "${{ matrix.module }}" \
      unstable \
      "${{ steps.version.outputs.version }}-SNAPSHOT" \
      --deploy
```

## Debugging

### Verbose Output

All scripts include helpful echo statements showing:

- Input parameters
- Detected module type
- Extracted versions
- Build directory paths
- Generated files

### Build Inspection

Build artifacts remain in `/tmp/apis-build-<pid>/` for inspection:

```bash
# Find your build directory
ls -la /tmp/apis-build-*/

# Inspect the generated POM
cat /tmp/apis-build-12345/tenants-event-stable/pom.xml

# View generated Java classes
find /tmp/apis-build-12345/tenants-event-stable/src/main/java -name "*.java"

# Examine JAR contents
unzip -l /tmp/apis-build-12345/tenants-event-stable/target/*.jar
```

### Cleanup

Remove build artifacts:

```bash
# Clean specific build
rm -rf /tmp/apis-build-12345

# Clean all builds
rm -rf /tmp/apis-build-*
```

## Extending to Other Generators

To add a new generator (e.g., npm, Go, Python):

1. Create configuration: `.github/generators/{generator}/config.yml`
2. Create templates: `.github/generators/{generator}/*.j2`
3. Create generator script: `scripts/generators/generate-{generator}.sh`
4. Update registry: `.github/generators/registry.yml`
5. Enable in module metadata: `{module}/metadata.yml`

**Example: npm Generator**

```bash
#!/bin/bash
# scripts/generators/generate-npm.sh
MODULE_PATH=$1
STABILITY=$2

# Extract version
VERSION=$(./scripts/generators/common/extract-version.sh "$MODULE_PATH/asyncapi.yml")

# Render package.json
python3 ./scripts/generators/common/render-template.py \
    .github/generators/npm/package.json.j2 \
    context.yml \
    /tmp/build/package.json

# Generate TypeScript code
# ... npm-specific generation logic ...

# Build and publish
cd /tmp/build
npm install
npm run build
npm publish
```

## Troubleshooting

### Docker Errors

If Docker commands fail:

```bash
# Check Docker is running
docker ps

# Pull required images
docker pull apache/avro-tools:1.11.3
docker pull openapitools/openapi-generator-cli:v7.2.0
```

### Permission Errors

Make scripts executable:

```bash
chmod +x scripts/generators/generate-mvn.sh
chmod +x scripts/generators/common/*.sh
chmod +x scripts/generators/common/*.py
```

### Template Rendering Errors

Check Python dependencies:

```bash
python3 -c "import jinja2, yaml; print('OK')"
```

### Maven Build Failures

Check Java and Maven versions:

```bash
java -version    # Should be 21
mvn -version     # Should be 3.9+
```

## Version Strategy

| Branch   | Input Version | Output Version              |
|----------|---------------|-----------------------------|
| main     | 1.0.3         | 1.0.3 (stable)              |
| develop  | 1.0.3         | 1.0.3-SNAPSHOT (unstable)   |
| feature  | 1.0.3         | 1.0.3-feature-xyz-SNAPSHOT  |

## Support

For issues or questions:

1. Check script output for error messages
2. Inspect `/tmp/apis-build-*/` for generated files
3. Review templates in `.github/generators/mvn/`
4. Check module `metadata.yml` configuration
