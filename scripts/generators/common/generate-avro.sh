#!/bin/bash
set -euo pipefail

# generate-avro.sh
# Generates Java classes from Avro schema files using Docker
# Usage: generate-avro.sh <module-path> <output-dir>

MODULE_PATH="$1"
OUTPUT_DIR="$2"

AVRO_SCHEMA_DIR="${MODULE_PATH}/tenants-avro/v1"

echo "======================================"
echo "Avro Code Generation"
echo "======================================"
echo "Module path: $MODULE_PATH"
echo "Avro schema dir: $AVRO_SCHEMA_DIR"
echo "Output dir: $OUTPUT_DIR"

# Check if Avro schema directory exists
if [ ! -d "$AVRO_SCHEMA_DIR" ]; then
    echo "ERROR: Avro schema directory not found: $AVRO_SCHEMA_DIR" >&2
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Get absolute paths for Docker volume mounting
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
ABS_MODULE_PATH="$REPO_ROOT/$MODULE_PATH"
ABS_OUTPUT_DIR="$(realpath "$OUTPUT_DIR")"

echo "Running Avro code generation via Docker..."
echo "Docker image: apache/avro-tools:1.11.3"
echo "DEBUG: REPO_ROOT=$REPO_ROOT"
echo "DEBUG: ABS_MODULE_PATH=$ABS_MODULE_PATH"
echo "DEBUG: ABS_OUTPUT_DIR=$ABS_OUTPUT_DIR"
echo "DEBUG: Checking if Avro schema dir exists at: $ABS_MODULE_PATH/tenants-avro/v1"
ls -la "$ABS_MODULE_PATH/tenants-avro/v1" || echo "ERROR: Avro schema dir not found!"

# Generate Java classes from Avro schemas
docker run --rm \
  -v "$ABS_MODULE_PATH:/input" \
  -v "$ABS_OUTPUT_DIR:/output" \
  apache/avro-tools:1.11.3 \
  compile schema /input/tenants-avro/v1 /output

echo "Avro code generation completed successfully"
echo "Generated files in: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR" || true
