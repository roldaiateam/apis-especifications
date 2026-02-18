#!/bin/bash
set -euo pipefail

# generate-mvn.sh
# Master Maven generator script for API specifications
# Usage: generate-mvn.sh <module-path> <stability> [version-override] [--deploy]
#
# Arguments:
#   module-path: Path to the module (e.g., tenants/event, tenants/rest)
#   stability: stable | unstable
#   version-override: Optional version override (e.g., 1.0.3-feature-xyz-SNAPSHOT)
#   --deploy: Optional flag to deploy artifacts to Maven repository
#
# Examples:
#   ./generate-mvn.sh tenants/event stable
#   ./generate-mvn.sh tenants/rest unstable 1.0.3-SNAPSHOT
#   ./generate-mvn.sh tenants/event stable 1.0.3 --deploy

MODULE_PATH="$1"
STABILITY="$2"
VERSION_OVERRIDE="${3:-}"
DEPLOY_FLAG="${4:-}"

# Determine deployment flag
SHOULD_DEPLOY=false
if [ "$DEPLOY_FLAG" = "--deploy" ] || [ "$VERSION_OVERRIDE" = "--deploy" ]; then
    SHOULD_DEPLOY=true
    if [ "$VERSION_OVERRIDE" = "--deploy" ]; then
        VERSION_OVERRIDE=""
    fi
fi

echo "=========================================="
echo "Maven Generator"
echo "=========================================="
echo "Module path: $MODULE_PATH"
echo "Stability: $STABILITY"
echo "Version override: ${VERSION_OVERRIDE:-<none>}"
echo "Deploy: $SHOULD_DEPLOY"
echo "=========================================="

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Validate module path exists
if [ ! -d "$MODULE_PATH" ]; then
    echo "ERROR: Module path not found: $MODULE_PATH" >&2
    exit 1
fi

# Determine module type (event, rest, websocket)
MODULE_TYPE=""
if [ -f "$MODULE_PATH/asyncapi.yml" ]; then
    if grep -q "mqtt" "$MODULE_PATH/asyncapi.yml" || grep -q "ws" "$MODULE_PATH/asyncapi.yml"; then
        MODULE_TYPE="websocket"
    else
        MODULE_TYPE="event"
    fi
    SPEC_FILE="$MODULE_PATH/asyncapi.yml"
elif [ -f "$MODULE_PATH/openapi-rest.yml" ]; then
    MODULE_TYPE="rest"
    SPEC_FILE="$MODULE_PATH/openapi-rest.yml"
else
    echo "ERROR: No spec file found (asyncapi.yml or openapi-rest.yml) in $MODULE_PATH" >&2
    exit 1
fi

echo "Module type: $MODULE_TYPE"
echo "Spec file: $SPEC_FILE"

# Extract version from spec file
echo "Extracting version from spec file..."
API_VERSION=$(bash "$REPO_ROOT/scripts/generators/common/extract-version.sh" "$SPEC_FILE")
echo "API version: $API_VERSION"

# Determine Maven version
if [ -n "$VERSION_OVERRIDE" ]; then
    MAVEN_VERSION="$VERSION_OVERRIDE"
else
    MAVEN_VERSION="$API_VERSION"
    if [ "$STABILITY" != "stable" ]; then
        MAVEN_VERSION="${MAVEN_VERSION}-SNAPSHOT"
    fi
fi

echo "Maven version: $MAVEN_VERSION"

# Determine artifact ID based on module path and stability
MODULE_NAME=$(echo "$MODULE_PATH" | sed 's/\//\-/g')
if [ "$STABILITY" = "stable" ]; then
    ARTIFACT_ID="${MODULE_NAME}-stable"
else
    ARTIFACT_ID="${MODULE_NAME}-unstable"
fi

echo "Artifact ID: $ARTIFACT_ID"

# Load Maven configuration
MVN_CONFIG="$REPO_ROOT/.github/generators/mvn/config.yml"
if [ ! -f "$MVN_CONFIG" ]; then
    echo "ERROR: Maven config not found: $MVN_CONFIG" >&2
    exit 1
fi

# Create temporary build directory
BUILD_DIR="/tmp/apis-build-$$/$ARTIFACT_ID"
mkdir -p "$BUILD_DIR"
echo "Build directory: $BUILD_DIR"

# Prepare context for template rendering
CONTEXT_FILE="$BUILD_DIR/context.yml"
echo "Creating template context..."

# Extract package name from metadata.yml if exists
PACKAGE_NAME="com.proactivedevs.contracts"
METADATA_FILE="$MODULE_PATH/metadata.yml"
if [ -f "$METADATA_FILE" ]; then
    # Try to extract package name from metadata
    PACKAGE_FROM_METADATA=$(grep -A 5 "generators:" "$METADATA_FILE" | grep "package_name:" | sed 's/.*package_name:[[:space:]]*//' | tr -d '"' | tr -d "'" || echo "")
    if [ -n "$PACKAGE_FROM_METADATA" ]; then
        PACKAGE_NAME="$PACKAGE_FROM_METADATA"
    fi
fi

echo "Package name: $PACKAGE_NAME"

# Create context YAML for template rendering
# First, create module-specific context
cat > "$CONTEXT_FILE.partial" <<EOF
module_path: $MODULE_PATH
module_type: $MODULE_TYPE
module_name: $MODULE_NAME
artifact_id: $ARTIFACT_ID
group_id: com.proactivedevs.contracts
version: $MAVEN_VERSION
api_version: $API_VERSION
stability: $STABILITY
package_name: $PACKAGE_NAME
spec_file: $SPEC_FILE
repo_root: $REPO_ROOT
EOF

# Merge with Maven config using yq
echo "Merging Maven configuration..."
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
    "$MVN_CONFIG" \
    "$CONTEXT_FILE.partial" > "$CONTEXT_FILE"

# Cleanup partial file
rm -f "$CONTEXT_FILE.partial"

echo "Context file created: $CONTEXT_FILE"

# Select appropriate POM template based on module type
if [ "$MODULE_TYPE" = "event" ] || [ "$MODULE_TYPE" = "websocket" ]; then
    POM_TEMPLATE="$REPO_ROOT/.github/generators/mvn/pom.event.xml.j2"
elif [ "$MODULE_TYPE" = "rest" ]; then
    POM_TEMPLATE="$REPO_ROOT/.github/generators/mvn/pom.rest.xml.j2"
else
    echo "ERROR: Unknown module type: $MODULE_TYPE" >&2
    exit 1
fi

if [ ! -f "$POM_TEMPLATE" ]; then
    echo "ERROR: POM template not found: $POM_TEMPLATE" >&2
    exit 1
fi

echo "POM template: $POM_TEMPLATE"

# Render POM template
echo "Rendering POM template..."
python3 "$REPO_ROOT/scripts/generators/common/render-template.py" \
    "$POM_TEMPLATE" \
    "$CONTEXT_FILE" \
    "$BUILD_DIR/pom.xml"

# Copy source files to build directory
echo "Copying source files..."
cp -r "$MODULE_PATH"/* "$BUILD_DIR/"

# Generate code based on module type
if [ "$MODULE_TYPE" = "event" ] || [ "$MODULE_TYPE" = "websocket" ]; then
    echo "Generating Avro code..."
    OUTPUT_DIR="$BUILD_DIR/target/generated-sources/avro"
    mkdir -p "$OUTPUT_DIR"

    bash "$REPO_ROOT/scripts/generators/common/generate-avro.sh" \
        "$MODULE_PATH" \
        "$OUTPUT_DIR"

elif [ "$MODULE_TYPE" = "rest" ]; then
    echo "Generating OpenAPI code..."
    OUTPUT_DIR="$BUILD_DIR/target/generated-sources/openapi"
    mkdir -p "$OUTPUT_DIR"

    bash "$REPO_ROOT/scripts/generators/common/generate-openapi.sh" \
        "$MODULE_PATH" \
        "$OUTPUT_DIR" \
        "$PACKAGE_NAME"
fi

# Create source directories for Maven
echo "Creating Maven source directories..."
mkdir -p "$BUILD_DIR/src/main/java"
mkdir -p "$BUILD_DIR/src/main/resources"

# Copy generated sources to src/main/java
if [ -d "$OUTPUT_DIR" ]; then
    echo "Copying generated sources to Maven structure..."
    find "$OUTPUT_DIR" -name "*.java" -type f -exec cp --parents {} "$BUILD_DIR/src/main/java/" \; 2>/dev/null || \
    find "$OUTPUT_DIR" -name "*.java" -type f | while read -r file; do
        rel_path=$(echo "$file" | sed "s|$OUTPUT_DIR/||")
        target_file="$BUILD_DIR/src/main/java/$rel_path"
        mkdir -p "$(dirname "$target_file")"
        cp "$file" "$target_file"
    done
fi

# Copy spec files and resources to src/main/resources
echo "Copying resources..."
if [ "$MODULE_TYPE" = "event" ] || [ "$MODULE_TYPE" = "websocket" ]; then
    RESOURCES_DIR="$BUILD_DIR/src/main/resources/META-INF/asyncapi"
    mkdir -p "$RESOURCES_DIR"
    cp "$MODULE_PATH/asyncapi.yml" "$RESOURCES_DIR/" || true
    cp "$MODULE_PATH/metadata.yml" "$RESOURCES_DIR/" || true

    # Copy Avro schemas
    if [ -d "$MODULE_PATH/tenants-avro" ]; then
        cp -r "$MODULE_PATH/tenants-avro" "$RESOURCES_DIR/" || true
    fi

elif [ "$MODULE_TYPE" = "rest" ]; then
    RESOURCES_DIR="$BUILD_DIR/src/main/resources/META-INF/openapi"
    mkdir -p "$RESOURCES_DIR"
    cp "$MODULE_PATH/openapi-rest.yml" "$RESOURCES_DIR/" || true
    cp "$MODULE_PATH/metadata.yml" "$RESOURCES_DIR/" || true

    # Copy any v1 directories
    if [ -d "$MODULE_PATH/v1" ]; then
        cp -r "$MODULE_PATH/v1" "$RESOURCES_DIR/" || true
    fi
fi

# Build with Maven
echo "=========================================="
echo "Building with Maven..."
echo "=========================================="
cd "$BUILD_DIR"

# Run Maven verify (compile + test)
echo "Running: mvn clean verify"
mvn clean verify

# Deploy if requested
if [ "$SHOULD_DEPLOY" = true ]; then
    echo "=========================================="
    echo "Deploying to Maven repository..."
    echo "=========================================="
    echo "Running: mvn deploy -DskipTests"
    mvn deploy -DskipTests
    echo "Deployment completed successfully"
fi

# Show build results
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo "Artifact ID: $ARTIFACT_ID"
echo "Version: $MAVEN_VERSION"
echo "Build directory: $BUILD_DIR"
echo ""

if [ -d "$BUILD_DIR/target" ]; then
    echo "Generated artifacts:"
    ls -lh "$BUILD_DIR/target"/*.jar 2>/dev/null || echo "No JAR files found"
fi

echo ""
echo "To inspect the build:"
echo "  cd $BUILD_DIR"
echo ""
echo "To clean up:"
echo "  rm -rf /tmp/apis-build-$$"
