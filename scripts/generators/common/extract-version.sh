#!/bin/bash
set -euo pipefail

# extract-version.sh
# Extracts version from AsyncAPI or OpenAPI spec files
# Usage: extract-version.sh <spec-file-path>

SPEC_FILE="$1"

if [ ! -f "$SPEC_FILE" ]; then
    echo "ERROR: Spec file not found: $SPEC_FILE" >&2
    exit 1
fi

echo "Extracting version from: $SPEC_FILE" >&2

# Extract version from spec file (works for both asyncapi.yml and openapi-rest.yml)
VERSION=$(grep -A 10 '^info:' "$SPEC_FILE" | grep 'version:' | sed 's/.*version:[[:space:]]*//' | tr -d '"' | tr -d "'")

if [ -z "$VERSION" ]; then
    echo "ERROR: Could not extract version from $SPEC_FILE" >&2
    exit 1
fi

echo "Extracted version: $VERSION" >&2
echo "$VERSION"
