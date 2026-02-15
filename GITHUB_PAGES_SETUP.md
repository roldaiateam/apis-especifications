# GitHub Pages Documentation System

Complete guide to the automated API documentation system powered by GitHub Pages.

## Overview

This repository uses **GitHub Pages with GitHub Actions** to provide interactive documentation for all published API contracts. The system is fully automated and dynamic - when you publish a new API or version, the documentation updates automatically.

**Live Site:** https://roldaiateam.github.io/apis-especifications/

## Key Features

### 1. **Automatic Version Management**

Every time you publish a new version of an API to GitHub Packages, the documentation is automatically updated:

- **Stable versions** (from `main`): Published with semantic versioning (e.g., `1.0.1`)
- **Snapshot versions** (from `develop`): Published with `-SNAPSHOT` suffix (e.g., `1.0.1-SNAPSHOT`)
- **Unstable versions** (from PRs): Published with timestamp and commit hash (e.g., `1.0.1-unstable-20260215-abc123`)

### 2. **Interactive Version Selector**

Each API has a dynamic version selector in the UI that allows you to:

- View any published version of the API
- Compare different versions side-by-side
- See when each version was published
- Identify version types with color-coded badges

### 3. **PR Preview System**

When you create a Pull Request that modifies API specifications:

- A preview of the documentation is automatically generated
- A comment is posted on the PR with the preview URL
- The preview updates automatically when you push new commits
- The preview is cleaned up automatically when the PR is closed/merged

**Preview URL format:** `https://roldaiateam.github.io/apis-especifications/pr-{number}/`

### 4. **Zero Configuration for New APIs**

Adding a new API requires NO manual documentation configuration:

1. Add entry to `metadata.yml`
2. Create folder structure (e.g., `products/rest/openapi-rest.yml`)
3. Publish the API to GitHub Packages

Everything else is automatic:
- Documentation structure is created
- Version selector is generated
- API appears in the main catalog
- PR previews work immediately

## Architecture

### Workflows

The documentation system consists of three GitHub Actions workflows:

#### 1. `deploy-github-pages.yml`

**Trigger:** Automatically runs when `publish-contracts.yml` completes successfully

**What it does:**
1. Downloads artifact from `publish-contracts.yml` containing published version info
2. For each published API:
   - Detects version type (stable/snapshot/unstable)
   - Detects API type (REST/Event)
   - Generates documentation incrementally using `scripts/generate-docs.py`
   - Updates `versions.json` for that API
   - Copies OpenAPI specs and components
3. Regenerates the main index page (catalog)
4. Deploys everything to GitHub Pages

**Key feature:** Only processes APIs that were actually published, making it efficient.

#### 2. `pr-preview.yml`

**Trigger:** Pull Request opened/updated that modifies API specifications

**What it does:**
1. Detects which APIs were modified in the PR
2. Generates preview documentation (no versioning, just current state)
3. Deploys to `gh-pages-preview` branch under `/pr-{number}/`
4. Posts/updates comment on PR with preview URL

**Paths that trigger preview:**
- `metadata.yml`
- `**/openapi*.yml`
- `**/asyncapi.yml`
- `scripts/generate-docs.py`

#### 3. `cleanup-pr-previews.yml`

**Trigger:** Pull Request closed

**What it does:**
1. Removes the preview directory for that PR from `gh-pages-preview` branch
2. Updates the preview index page
3. Keeps the preview branch clean

### Documentation Structure

```
docs/
├── index.html                          # Main catalog page (auto-generated)
├── apis/
│   └── {api-id}/                       # e.g., tenants-rest, products-event
│       ├── index.html                  # Version selector page
│       ├── versions.json               # Metadata of all published versions
│       └── {version}/                  # e.g., 1.0.1, 1.0.1-SNAPSHOT
│           ├── index.html              # Swagger UI viewer
│           ├── openapi-rest.yml        # Main OpenAPI spec
│           └── v1/                     # Referenced components ($ref files)
│               └── ...
└── swagger-ui/                         # Shared Swagger UI assets (optional)
```

### Version Metadata (`versions.json`)

Each API has a `versions.json` file that tracks all published versions:

```json
{
  "api": "tenants-rest",
  "name": "Tenants REST API",
  "type": "rest",
  "versions": [
    {
      "version": "1.0.1",
      "type": "stable",
      "publishedAt": "2026-02-14T21:00:00Z",
      "spec": "openapi-rest.yml"
    },
    {
      "version": "1.0.1-SNAPSHOT",
      "type": "snapshot",
      "publishedAt": "2026-02-15T09:30:00Z",
      "spec": "openapi-rest.yml"
    },
    {
      "version": "1.0.2-unstable-20260215-abc123",
      "type": "unstable",
      "publishedAt": "2026-02-15T14:22:00Z",
      "spec": "openapi-rest.yml"
    }
  ],
  "latest": {
    "stable": "1.0.1",
    "snapshot": "1.0.1-SNAPSHOT",
    "unstable": "1.0.2-unstable-20260215-abc123"
  }
}
```

### Version Lifecycle

#### Stable Versions (from `main`)

- **Retention:** Last 5 versions are kept, older ones are automatically removed
- **Purpose:** Production-ready API versions
- **Badge:** Green badge labeled "STABLE"

#### Snapshot Versions (from `develop`)

- **Retention:** Only 1 version (always replaced on new publish)
- **Purpose:** Development/testing version
- **Badge:** Yellow/amber badge labeled "SNAPSHOT"

#### Unstable Versions (from PRs)

- **Retention:** Removed after 7 days (handled by existing cleanup workflow)
- **Purpose:** Temporary testing in PRs
- **Badge:** Red badge labeled "UNSTABLE"

## Setup Requirements

### Repository Configuration

1. **Repository must be PUBLIC**
   - GitHub Pages with GitHub Actions requires a public repository
   - Go to: Settings > Danger Zone > Change repository visibility > Public

2. **GitHub Pages Configuration**
   - Go to: Settings > Pages
   - Source: **GitHub Actions** (NOT "Deploy from a branch")
   - This allows workflows to deploy directly

3. **Permissions**
   - The `GITHUB_TOKEN` already has sufficient permissions
   - Workflows have `contents: write` and `pages: write` permissions

### No Additional Secrets Required

The system uses the built-in `GITHUB_TOKEN` - no additional secrets or configuration needed.

## Documentation Generation Script

The core of the system is `scripts/generate-docs.py` with two operating modes:

### Mode 1: Incremental (Used by CI/CD)

Adds or updates a specific version of a specific API:

```bash
python scripts/generate-docs.py --mode incremental \
  --api "tenants-rest" \
  --api-name "Tenants REST API" \
  --api-type "rest" \
  --version "1.0.1" \
  --type "stable" \
  --published-at "2026-02-15T10:00:00Z" \
  --source-path "tenants/rest"
```

**What it does:**
1. Creates API structure if it's a new API
2. Loads existing `versions.json` or creates new one
3. Adds/updates the version entry
4. Copies OpenAPI spec and all `v*/` component directories
5. Generates version selector page
6. Cleans up old stable versions (keeps max 5)
7. Regenerates main index page

### Mode 2: Full (Used for maintenance)

Regenerates the main index page by scanning the existing structure:

```bash
python scripts/generate-docs.py
```

**What it does:**
1. Scans `docs/apis/` to discover all APIs
2. Reads `versions.json` for each API
3. Regenerates `docs/index.html` with complete catalog
4. Does NOT modify individual API versions

## Version Selector UI

Each API documentation page includes an interactive version selector:

```html
<select id="version-selector">
  <option value="1.0.1" data-type="stable">v1.0.1 (Stable) - 2026-02-14</option>
  <option value="1.0.1-SNAPSHOT" data-type="snapshot">v1.0.1-SNAPSHOT (Snapshot) - 2026-02-15</option>
</select>
```

**Features:**
- Dynamically populated from `versions.json`
- Color-coded badges (green=stable, yellow=snapshot, red=unstable)
- Shows publication date for each version
- Loads OpenAPI spec dynamically when version changes
- Preserves Swagger UI state during version switching

## PR Preview Workflow

### How It Works

1. **Developer creates PR** that modifies `tenants/rest/openapi-rest.yml`

2. **GitHub Actions detects change** and runs `pr-preview.yml`:
   - Parses git diff to find changed API modules
   - Generates preview documentation (simplified, no versioning)
   - Deploys to `gh-pages-preview` branch under `/pr-123/`

3. **Bot comments on PR:**
   ```markdown
   ## 📄 API Documentation Preview

   Your API changes are ready for preview:

   🔗 **[View All API Previews](https://roldaiateam.github.io/apis-especifications/pr-123/)**

   ---
   ⚠️ This is a preview build. Changes are not published to GitHub Packages yet.
   ```

4. **Developer reviews preview** at the URL

5. **PR is merged/closed** → `cleanup-pr-previews.yml` automatically removes `/pr-123/`

### Preview Features

- **Live updates:** Push new commits → preview updates automatically
- **No version history:** Previews show only the current PR state
- **Warning banner:** Yellow banner at top indicates it's a preview
- **Isolated deployment:** Uses separate `gh-pages-preview` branch
- **Automatic cleanup:** No manual intervention needed

## Testing the System

### Test 1: Publish a New Version

1. Modify `tenants/rest/openapi-rest.yml` and increment version to `0.0.3`
2. Commit and push to `develop`
3. Verify:
   - `publish-contracts.yml` runs and publishes to GitHub Packages
   - `deploy-github-pages.yml` triggers automatically after
   - https://roldaiateam.github.io/apis-especifications/ updates
   - Version selector includes `0.0.3-SNAPSHOT`
   - Swagger UI loads the new spec correctly

### Test 2: Create a PR Preview

1. Create feature branch with API change
2. Open PR to `develop`
3. Verify:
   - `pr-preview.yml` workflow runs
   - Bot posts comment with preview URL
   - Preview URL works and shows changes
   - Push new commit → preview updates
   - Close PR → preview is cleaned up

### Test 3: Add a Completely New API

1. Add entry to `metadata.yml`:
   ```yaml
   - name: "Products REST API"
     api-spec-type: rest
     definition-path: products/rest
   ```

2. Create `products/rest/openapi-rest.yml` with version `1.0.0`

3. Create `products/rest/pom.xml`

4. Push to `main`

5. Verify:
   - `publish-contracts.yml` detects and publishes `products-rest-stable:1.0.0`
   - `deploy-github-pages.yml` automatically creates `docs/apis/products-rest/`
   - `versions.json` is created for products-rest
   - Main catalog updates with "Products REST API"
   - https://roldaiateam.github.io/apis-especifications/apis/products-rest/ works
   - Version selector shows v1.0.0

**ZERO manual configuration required!**

## Maintenance

### Manual Index Regeneration

If the main index page gets out of sync:

```bash
python scripts/generate-docs.py
```

This scans `docs/apis/` and regenerates the catalog.

### Manual Version Cleanup

To manually clean up old versions:

```bash
python scripts/generate-docs.py --mode incremental \
  --api "tenants-rest" \
  --version "1.0.1" \
  --type "stable" \
  --published-at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --source-path "tenants/rest"
```

The script automatically removes versions beyond the 5 most recent stable versions.

### Checking Version History

View all versions for an API:

```bash
cat docs/apis/tenants-rest/versions.json | python -m json.tool
```

### Debugging Workflows

View workflow runs:
- Go to: Actions tab in GitHub
- Select workflow: "Deploy to GitHub Pages" or "PR Documentation Preview"
- View logs for detailed execution information

## Troubleshooting

### Issue: Documentation Not Updating

**Check:**
1. Did `publish-contracts.yml` complete successfully?
2. Did it actually publish a new version to GitHub Packages?
3. Check `deploy-github-pages.yml` logs for errors
4. Verify repository is public and GitHub Pages is configured

### Issue: Version Not Appearing in Selector

**Check:**
1. Open `docs/apis/{api-id}/versions.json` - is the version listed?
2. Hard refresh browser (Ctrl+Shift+R) to bypass cache
3. Check if version was cleaned up (if it's an old stable version beyond the 5 most recent)

### Issue: PR Preview Not Generated

**Check:**
1. Did the PR actually modify API spec files?
2. Check `pr-preview.yml` workflow logs
3. Verify paths match the trigger patterns (openapi*.yml, asyncapi.yml)
4. Check PR comments - bot may have posted an error

### Issue: 404 on GitHub Pages

**Check:**
1. Repository is public
2. GitHub Pages source is set to "GitHub Actions"
3. `deploy-github-pages.yml` has run at least once
4. Check Actions tab for deployment status

### Issue: Swagger UI Not Loading Spec

**Check:**
1. Browser console for CORS or network errors
2. Verify OpenAPI spec is valid YAML
3. Check that all `$ref` files are copied to the version directory
4. Inspect Network tab - is the spec file actually being fetched?

## Advantages Over Netlify

### Why We Migrated

1. **No Request Limits**: GitHub Pages has generous limits for public repos
2. **Free for Public Repos**: No cost concerns
3. **Integrated with GitHub Actions**: Seamless CI/CD integration
4. **Version History**: Built-in support for multiple versions
5. **PR Previews**: Native support with GitHub Actions
6. **No External Dependencies**: Everything in one place

### What We Gained

- **Automatic version management** with cleanup policies
- **Dynamic version selector** in the UI
- **PR previews** with automatic comments
- **Completely dynamic system** - new APIs need zero configuration
- **Better performance** - GitHub's CDN is fast
- **Simplified workflow** - fewer moving parts

## Future Enhancements

Possible improvements to consider:

1. **Search Functionality**: Add search across all API versions
2. **Diff Viewer**: Compare two versions side-by-side
3. **AsyncAPI Support**: Add AsyncAPI UI for event-driven specs
4. **Download Specs**: Button to download raw OpenAPI/AsyncAPI files
5. **API Changelog**: Auto-generate changelog from version differences
6. **Metrics Dashboard**: Track API usage, popular versions, etc.

## Support

For issues or questions:
- Create an issue in this repository
- Check workflow logs in the Actions tab
- Review this documentation
- Contact: team@proactivedevs.com

---

**Documentation System Version:** 1.0
**Last Updated:** 2026-02-15
