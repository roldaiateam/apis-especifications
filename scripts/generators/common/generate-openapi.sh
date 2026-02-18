#!/bin/bash
set -euo pipefail

# generate-openapi.sh
# Generates Java classes from OpenAPI spec files using Docker
# Usage: generate-openapi.sh <module-path> <output-dir> <package-name>

MODULE_PATH="$1"
OUTPUT_DIR="$2"
PACKAGE_NAME="${3:-com.proactivedevs.contracts}"

OPENAPI_SPEC="${MODULE_PATH}/openapi-rest.yml"

echo "======================================"
echo "OpenAPI Code Generation"
echo "======================================"
echo "Module path: $MODULE_PATH"
echo "OpenAPI spec: $OPENAPI_SPEC"
echo "Output dir: $OUTPUT_DIR"
echo "Package name: $PACKAGE_NAME"

# Check if OpenAPI spec exists
if [ ! -f "$OPENAPI_SPEC" ]; then
    echo "ERROR: OpenAPI spec not found: $OPENAPI_SPEC" >&2
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Get absolute paths for Docker volume mounting
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ABS_MODULE_PATH="$REPO_ROOT/$MODULE_PATH"
ABS_OUTPUT_DIR="$(realpath "$OUTPUT_DIR")"

echo "Running OpenAPI code generation via Docker..."
echo "Docker image: openapitools/openapi-generator-cli:v7.2.0"
echo "DEBUG: REPO_ROOT=$REPO_ROOT"
echo "DEBUG: ABS_MODULE_PATH=$ABS_MODULE_PATH"
echo "DEBUG: ABS_OUTPUT_DIR=$ABS_OUTPUT_DIR"
echo "DEBUG: Checking if spec file exists at: $ABS_MODULE_PATH/openapi-rest.yml"
ls -la "$ABS_MODULE_PATH/openapi-rest.yml" || echo "ERROR: Spec file not found!"

# Generate Java classes from OpenAPI spec
docker run --rm \
  -v "$ABS_MODULE_PATH:/input" \
  -v "$ABS_OUTPUT_DIR:/output" \
  openapitools/openapi-generator-cli:v7.2.0 generate \
  -i /input/openapi-rest.yml \
  -g spring \
  -o /output \
  --model-package "${PACKAGE_NAME}.model" \
  --api-package "${PACKAGE_NAME}.api" \
  --additional-properties=useSpringBoot3=true,useTags=true,interfaceOnly=true \
  --global-property models,modelDocs=false

echo "OpenAPI code generation completed successfully"
echo "Generated files in: $OUTPUT_DIR"

# Fix file permissions (Docker runs as root, need to chown to current user)
echo "Fixing file permissions..."
sudo chown -R $(id -u):$(id -g) "$OUTPUT_DIR" || true

find "$OUTPUT_DIR" -type f -name "*.java" | head -10 || true
