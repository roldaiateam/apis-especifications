#!/usr/bin/env python3
"""
Generates API documentation dynamically for GitHub Pages deployment.

This script supports two modes:
1. Full mode: Regenerates the main index page by scanning existing docs/
2. Incremental mode: Adds/updates a specific API version

Features:
- Zero configuration for new APIs
- Dynamic version management with versions.json
- Version selector UI for each API
- Automatic cleanup of old stable versions (max 5)
- Complete

 dynamic discovery of APIs from docs/ structure
"""

import yaml
import json
import argparse
import shutil
import os
from pathlib import Path
from datetime import datetime

# Configuration
REPO_OWNER = "roldaiateam"
REPO_NAME = "apis-especifications"
MAX_STABLE_VERSIONS = 5


def get_version_type(version_string):
    """
    Detect version type from version string.

    Args:
        version_string: Version like "0.0.1", "0.0.1-SNAPSHOT", "0.0.1-unstable-20260214-abc123"

    Returns:
        str: "stable", "snapshot", or "unstable"
    """
    if '-SNAPSHOT' in version_string:
        return 'snapshot'
    elif '-unstable-' in version_string:
        return 'unstable'
    else:
        return 'stable'


def discover_apis_from_docs():
    """
    Scan docs/apis/ to discover existing APIs.
    Returns list of APIs with metadata from versions.json files.

    Returns:
        list: List of dicts with API metadata
    """
    apis = []
    apis_dir = Path('docs/apis')

    if not apis_dir.exists():
        return []

    for api_dir in sorted(apis_dir.iterdir()):
        if not api_dir.is_dir():
            continue

        versions_file = api_dir / 'versions.json'
        if not versions_file.exists():
            continue

        try:
            data = json.loads(versions_file.read_text())
            apis.append({
                'id': api_dir.name,
                'name': data.get('name', api_dir.name),
                'type': data.get('type', 'rest'),
                'latest_stable': data.get('latest', {}).get('stable'),
                'latest_snapshot': data.get('latest', {}).get('snapshot'),
                'version_count': len(data.get('versions', []))
            })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Warning: Could not parse versions.json for {api_dir.name}: {e}")
            continue

    return apis


def load_versions_metadata(api_id):
    """
    Load versions.json for a specific API.

    Args:
        api_id: API identifier (e.g., "tenants-rest")

    Returns:
        dict: Versions metadata or empty structure if not found
    """
    versions_file = Path(f'docs/apis/{api_id}/versions.json')

    if not versions_file.exists():
        return {
            'api': api_id,
            'name': api_id,
            'type': 'rest',
            'versions': [],
            'latest': {}
        }

    try:
        return json.loads(versions_file.read_text())
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: Could not parse versions.json for {api_id}: {e}")
        return {
            'api': api_id,
            'name': api_id,
            'type': 'rest',
            'versions': [],
            'latest': {}
        }


def update_versions_metadata(api_id, api_name, api_type, version, version_type, published_at, spec_file):
    """
    Update versions.json with a new version.

    Args:
        api_id: API identifier
        api_name: Human-readable API name
        api_type: "rest" or "event"
        version: Version string (e.g., "0.0.1", "0.0.1-SNAPSHOT")
        version_type: "stable", "snapshot", or "unstable"
        published_at: ISO timestamp
        spec_file: Name of the spec file (e.g., "openapi-rest.yml")
    """
    metadata = load_versions_metadata(api_id)

    # Update basic info
    metadata['name'] = api_name
    metadata['type'] = api_type

    # Remove existing version if updating
    metadata['versions'] = [v for v in metadata['versions'] if v['version'] != version]

    # Add new version
    metadata['versions'].append({
        'version': version,
        'type': version_type,
        'publishedAt': published_at,
        'spec': spec_file
    })

    # Sort versions by publishedAt (newest first)
    metadata['versions'].sort(key=lambda v: v['publishedAt'], reverse=True)

    # Update latest pointers
    if version_type == 'stable':
        metadata['latest']['stable'] = version
    elif version_type == 'snapshot':
        metadata['latest']['snapshot'] = version

    # If no latest stable but we have stable versions, set it
    if not metadata['latest'].get('stable'):
        stable_versions = [v for v in metadata['versions'] if v['type'] == 'stable']
        if stable_versions:
            metadata['latest']['stable'] = stable_versions[0]['version']

    # Save metadata
    versions_file = Path(f'docs/apis/{api_id}/versions.json')
    versions_file.write_text(json.dumps(metadata, indent=2))

    print(f"✅ Updated versions.json for {api_id}")


def cleanup_old_stable_versions(api_id, max_stable=MAX_STABLE_VERSIONS):
    """
    Remove old stable versions beyond the max limit.
    Keeps only the most recent stable versions.

    Args:
        api_id: API identifier
        max_stable: Maximum number of stable versions to keep
    """
    metadata = load_versions_metadata(api_id)

    stable_versions = [v for v in metadata['versions'] if v['type'] == 'stable']

    if len(stable_versions) <= max_stable:
        print(f"  ℹ️  {len(stable_versions)} stable version(s) - within limit")
        return

    # Sort by date (newest first)
    stable_versions.sort(key=lambda v: v['publishedAt'], reverse=True)

    # Versions to remove
    versions_to_remove = stable_versions[max_stable:]

    print(f"  🧹 Cleaning up {len(versions_to_remove)} old stable version(s)")

    for version_info in versions_to_remove:
        version = version_info['version']
        version_dir = Path(f'docs/apis/{api_id}/{version}')

        if version_dir.exists():
            shutil.rmtree(version_dir)
            print(f"    ✓ Removed {version}")

        # Remove from metadata
        metadata['versions'] = [v for v in metadata['versions'] if v['version'] != version]

    # Save updated metadata
    versions_file = Path(f'docs/apis/{api_id}/versions.json')
    versions_file.write_text(json.dumps(metadata, indent=2))

    print(f"✅ Cleanup complete for {api_id}")


def ensure_api_structure(api_id, api_name, api_type):
    """
    Create base structure for a new API if it doesn't exist.

    Args:
        api_id: API identifier
        api_name: Human-readable API name
        api_type: "rest" or "event"
    """
    api_dir = Path(f'docs/apis/{api_id}')

    if api_dir.exists():
        return

    api_dir.mkdir(parents=True)
    print(f"✨ New API detected: {api_name}")

    # Create initial versions.json
    versions_data = {
        'api': api_id,
        'name': api_name,
        'type': api_type,
        'versions': [],
        'latest': {}
    }

    (api_dir / 'versions.json').write_text(json.dumps(versions_data, indent=2))
    print(f"  ✓ Created versions.json")


def find_spec_file(definition_path, api_type):
    """
    Find the spec file in the given definition path.

    Args:
        definition_path: Path to the API definition (e.g., "tenants/rest")
        api_type: "rest" or "event"

    Returns:
        str: Spec filename or None
    """
    spec_path = Path(definition_path)

    if api_type == 'event':
        if (spec_path / 'asyncapi.yml').exists():
            return 'asyncapi.yml'
    else:  # rest
        patterns = ['openapi-rest.yml', 'openapi.yml', 'openapi-rest.yaml', 'openapi.yaml']
        for pattern in patterns:
            if (spec_path / pattern).exists():
                return pattern

    return None


def copy_api_version_files(source_path, api_id, version):
    """
    Copy API files to the versioned directory.

    Args:
        source_path: Source directory (e.g., "tenants/rest")
        api_id: API identifier (e.g., "tenants-rest")
        version: Version string (e.g., "0.0.1")
    """
    source = Path(source_path)
    target = Path(f'docs/apis/{api_id}/{version}')

    target.mkdir(parents=True, exist_ok=True)

    # Patterns to skip
    skip_patterns = {
        'target', '.classpath', '.project', '.settings', 'pom.xml',
        '.git', '__pycache__', '.DS_Store', 'README.md', 'metadata.yml'
    }

    copied_count = 0
    for file in source.rglob('*'):
        if not file.is_file():
            continue

        # Check if should skip
        should_skip = any(pattern in file.parts or file.name == pattern for pattern in skip_patterns)
        if should_skip:
            continue

        # Calculate relative path and destination
        relative_path = file.relative_to(source)
        dest_file = target / relative_path

        # Create parent directory
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(file, dest_file)
        copied_count += 1

    print(f"    ✓ Copied {copied_count} files to {target}")


def generate_version_selector_page(api_id, api_name, api_type, spec_file):
    """
    Generate the main API page with version selector.

    Args:
        api_id: API identifier
        api_name: Human-readable API name
        api_type: "rest" or "event"
        spec_file: Name of the spec file
    """
    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{api_name} - API Documentation</title>
    <link rel="stylesheet" type="text/css" href="../../swagger-ui/swagger-ui.css" />
    <link rel="icon" type="image/png" href="../../swagger-ui/favicon-32x32.png" sizes="32x32" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}

        *,
        *:before,
        *:after {{
            box-sizing: inherit;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        }}

        .topbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 0;
            color: white;
        }}

        .topbar-wrapper {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1460px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        .topbar .link {{
            color: white;
            text-decoration: none;
            font-size: 1.5em;
            font-weight: bold;
        }}

        .topbar .link:hover {{
            text-decoration: underline;
        }}

        .version-selector-container {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .version-selector-container label {{
            font-weight: 600;
            font-size: 0.9em;
        }}

        #version-selector {{
            padding: 8px 12px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-weight: 600;
            cursor: pointer;
            min-width: 300px;
        }}

        #version-selector option {{
            background: #667eea;
            color: white;
        }}

        .version-badge {{
            padding: 6px 14px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.85em;
            white-space: nowrap;
        }}

        .version-badge.stable {{
            background: #28a745;
            color: white;
        }}

        .version-badge.snapshot {{
            background: #ffc107;
            color: #333;
        }}

        .version-badge.unstable {{
            background: #dc3545;
            color: white;
        }}

        .back-link {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s ease;
        }}

        .back-link:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}

        .loading {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 1.2em;
        }}

        .error {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            margin: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="topbar-wrapper">
            <a href="../../" class="link">{api_name}</a>
            <div style="display: flex; align-items: center; gap: 15px;">
                <div class="version-selector-container">
                    <label for="version-selector">Version:</label>
                    <select id="version-selector">
                        <option value="">Loading versions...</option>
                    </select>
                    <span class="version-badge stable" id="version-badge">LOADING</span>
                </div>
                <a href="../../" class="back-link">← Back to Catalog</a>
            </div>
        </div>
    </div>

    <div id="swagger-ui" class="loading">Loading API documentation...</div>

    <script src="../../swagger-ui/swagger-ui-bundle.js" charset="UTF-8"></script>
    <script src="../../swagger-ui/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
    <script>
        let swaggerUI = null;
        let versionsData = null;

        // Load versions.json
        fetch('./versions.json')
            .then(r => {{
                if (!r.ok) throw new Error('Failed to load versions');
                return r.json();
            }})
            .then(data => {{
                versionsData = data;
                populateVersionSelector(data.versions);

                // Determine initial version (prefer snapshot, then latest stable)
                const initialVersion = data.latest.snapshot || data.latest.stable || data.versions[0]?.version;

                if (initialVersion) {{
                    loadVersion(initialVersion);
                }} else {{
                    showError('No versions available');
                }}
            }})
            .catch(error => {{
                console.error('Error loading versions:', error);
                showError('Failed to load API versions. Please try again later.');
            }});

        function populateVersionSelector(versions) {{
            const select = document.getElementById('version-selector');

            if (!versions || versions.length === 0) {{
                select.innerHTML = '<option value="">No versions available</option>';
                return;
            }}

            select.innerHTML = versions.map(v => {{
                const date = new Date(v.publishedAt).toLocaleDateString();
                const badge = v.type.charAt(0).toUpperCase() + v.type.slice(1);
                return `<option value="${{v.version}}" data-type="${{v.type}}">
                    v${{v.version}} (${{badge}}) - ${{date}}
                </option>`;
            }}).join('');
        }}

        function loadVersion(version) {{
            const versionData = versionsData.versions.find(v => v.version === version);

            if (!versionData) {{
                showError(`Version ${{version}} not found`);
                return;
            }}

            const specUrl = `./${{version}}/${{versionData.spec}}`;

            // Update selector
            document.getElementById('version-selector').value = version;
            updateBadge(versionData.type);

            // Load or update Swagger UI
            if (swaggerUI) {{
                swaggerUI.specActions.updateUrl(specUrl);
                swaggerUI.specActions.download(specUrl);
            }} else {{
                document.getElementById('swagger-ui').innerHTML = '';
                swaggerUI = SwaggerUIBundle({{
                    url: specUrl,
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    defaultModelsExpandDepth: 1,
                    defaultModelExpandDepth: 1,
                    docExpansion: "list",
                    filter: true,
                    showRequestHeaders: true,
                    tryItOutEnabled: true,
                    validatorUrl: null
                }});
            }}
        }}

        function updateBadge(type) {{
            const badge = document.getElementById('version-badge');
            badge.className = `version-badge ${{type}}`;
            badge.textContent = type.toUpperCase();
        }}

        function showError(message) {{
            document.getElementById('swagger-ui').innerHTML = `
                <div class="error">
                    <strong>Error:</strong> ${{message}}
                </div>
            `;
        }}

        document.getElementById('version-selector').addEventListener('change', (e) => {{
            if (e.target.value) {{
                loadVersion(e.target.value);
            }}
        }});
    </script>
</body>
</html>
'''

    index_file = Path(f'docs/apis/{api_id}/index.html')
    index_file.write_text(page_html)
    print(f"    ✓ Generated version selector page")


def generate_index_page():
    """
    Generate the main docs/index.html by scanning docs/apis/ directory.
    Completely dynamic - discovers APIs from existing structure.
    """
    apis = discover_apis_from_docs()

    api_rows = ''
    for api in sorted(apis, key=lambda x: x['name']):
        type_label = 'AsyncAPI' if api['type'] == 'event' else 'OpenAPI 3.0'
        type_badge_class = 'asyncapi' if api['type'] == 'event' else 'openapi'

        # Build version info
        version_info = []
        if api.get('latest_stable'):
            version_info.append(f"Stable: v{api['latest_stable']}")
        if api.get('latest_snapshot'):
            version_info.append(f"Snapshot: v{api['latest_snapshot']}")

        version_text = ' | '.join(version_info) if version_info else 'No versions'

        api_rows += f'''
                    <tr>
                        <td class="api-cell">{api['name']}</td>
                        <td><span class="badge {type_badge_class}">{type_label}</span></td>
                        <td class="version-info">{version_text}</td>
                        <td>
                            <a href="./apis/{api['id']}/" class="btn">View Documentation</a>
                        </td>
                    </tr>'''

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Contracts Catalog - ProactiveDevs</title>
    <link rel="icon" type="image/png" href="./swagger-ui/favicon-32x32.png">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .intro {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}

        .intro h2 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .intro p {{
            color: #555;
            margin-bottom: 10px;
        }}

        .intro a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}

        .intro a:hover {{
            text-decoration: underline;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 1em;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge.openapi {{
            background: #e7f3ff;
            color: #0066cc;
        }}

        .badge.asyncapi {{
            background: #fff4e5;
            color: #e65100;
        }}

        .btn {{
            display: inline-block;
            padding: 8px 16px;
            margin: 2px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        .api-cell {{
            font-weight: 600;
            color: #333;
        }}

        .version-info {{
            font-size: 0.9em;
            color: #666;
        }}

        footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}

        footer a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            color: #856404;
        }}

        .note strong {{
            color: #856404;
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            header p {{
                font-size: 1em;
            }}

            .content {{
                padding: 20px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px 8px;
            }}

            .btn {{
                display: block;
                margin: 5px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>API Contracts Catalog</h1>
            <p>ProactiveDevs Microservices Ecosystem</p>
        </header>

        <div class="content">
            <div class="intro">
                <h2>Welcome to the API Contracts Repository</h2>
                <p>
                    This catalog provides interactive documentation for all API specifications in the ProactiveDevs ecosystem.
                    Each API contract is published as a versioned Maven artifact that can be consumed by microservices.
                </p>
                <p>
                    <strong>Repository:</strong> <a href="https://github.com/{REPO_OWNER}/{REPO_NAME}" target="_blank">github.com/{REPO_OWNER}/{REPO_NAME}</a>
                </p>
                <p>
                    <strong>Deployment:</strong> This site is automatically deployed to GitHub Pages when new API versions are published.
                </p>
            </div>

            <h2 style="margin-bottom: 20px; color: #333;">Available APIs</h2>

            {'<p style="color: #666; padding: 20px; text-align: center;">No APIs published yet. Add your first API to get started!</p>' if not apis else f'''
            <table>
                <thead>
                    <tr>
                        <th>API Name</th>
                        <th>Type</th>
                        <th>Latest Versions</th>
                        <th>Documentation</th>
                    </tr>
                </thead>
                <tbody>{api_rows}
                </tbody>
            </table>
            '''}

            <div class="note">
                <strong>💡 Tip:</strong> Each API page includes a version selector to browse all published versions (stable, snapshot, and unstable).
                Click "View Documentation" to explore the interactive Swagger UI.
            </div>

            <h2 style="margin: 30px 0 20px; color: #333;">Using API Contracts in Your Microservice</h2>

            <div class="intro">
                <h3 style="margin-bottom: 10px;">Maven Dependency</h3>
                <p>Add the GitHub Packages repository and the contract dependency to your <code>pom.xml</code>:</p>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; margin-top: 10px; border: 1px solid #e9ecef;"><code>&lt;repositories&gt;
    &lt;repository&gt;
        &lt;id&gt;github&lt;/id&gt;
        &lt;url&gt;https://maven.pkg.github.com/{REPO_OWNER}/{REPO_NAME}&lt;/url&gt;
        &lt;snapshots&gt;
            &lt;enabled&gt;true&lt;/enabled&gt;
        &lt;/snapshots&gt;
    &lt;/repository&gt;
&lt;/repositories&gt;

&lt;dependency&gt;
    &lt;groupId&gt;com.proactivedevs.contracts&lt;/groupId&gt;
    &lt;artifactId&gt;{{api-name}}-stable&lt;/artifactId&gt;
    &lt;version&gt;{{version}}&lt;/version&gt;
&lt;/dependency&gt;</code></pre>
                <p style="margin-top: 15px;">
                    For more information, visit the
                    <a href="https://github.com/{REPO_OWNER}/{REPO_NAME}#readme" target="_blank">repository documentation</a>.
                </p>
            </div>
        </div>

        <footer>
            <p>
                Copyright &copy; 2026 ProactiveDevs |
                <a href="https://github.com/{REPO_OWNER}/{REPO_NAME}" target="_blank">View on GitHub</a>
            </p>
        </footer>
    </div>
</body>
</html>
'''

    index_file = Path('docs/index.html')
    index_file.write_text(index_html)

    print(f"✅ Generated index.html with {len(apis)} API(s)")


def mode_full():
    """
    Full mode: Regenerate main index page by scanning existing docs/apis/
    """
    print("🚀 Running in FULL mode")
    print("=" * 60)

    generate_index_page()

    print("\n✅ Full regeneration complete")


def mode_incremental(args):
    """
    Incremental mode: Add/update a specific API version

    Args:
        args: Parsed command line arguments
    """
    print("🚀 Running in INCREMENTAL mode")
    print("=" * 60)

    api_id = args.api
    api_name = args.api_name
    api_type = args.api_type
    version = args.version
    version_type = args.type
    published_at = args.published_at or datetime.now(timezone.utc).isoformat() + 'Z'
    source_path = args.source_path

    print(f"API: {api_name} ({api_id})")
    print(f"Type: {api_type}")
    print(f"Version: {version} ({version_type})")
    print(f"Published: {published_at}")
    print(f"Source: {source_path}")
    print()

    # Ensure API structure exists
    ensure_api_structure(api_id, api_name, api_type)

    # Find spec file
    spec_file = find_spec_file(source_path, api_type)
    if not spec_file:
        print(f"❌ Error: No spec file found in {source_path}")
        return False

    print(f"📋 Spec file: {spec_file}")

    # Copy API files to versioned directory
    copy_api_version_files(source_path, api_id, version)

    # Update versions.json
    update_versions_metadata(api_id, api_name, api_type, version, version_type, published_at, spec_file)

    # Generate version selector page
    generate_version_selector_page(api_id, api_name, api_type, spec_file)

    # Cleanup old stable versions
    if version_type == 'stable':
        cleanup_old_stable_versions(api_id)

    # Regenerate index (discovers APIs dynamically)
    print("\n📄 Regenerating main index...")
    generate_index_page()

    print(f"\n✅ Incremental update complete for {api_id} v{version}")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate API documentation for GitHub Pages deployment'
    )

    parser.add_argument(
        '--mode',
        choices=['full', 'incremental'],
        default='full',
        help='Generation mode (default: full)'
    )

    # Incremental mode arguments
    parser.add_argument('--api', help='API identifier (e.g., tenants-rest)')
    parser.add_argument('--api-name', help='Human-readable API name')
    parser.add_argument('--api-type', choices=['rest', 'event'], help='API type')
    parser.add_argument('--version', help='Version string (e.g., 0.0.1, 0.0.1-SNAPSHOT)')
    parser.add_argument('--type', choices=['stable', 'snapshot', 'unstable'], help='Version type')
    parser.add_argument('--published-at', help='Publication timestamp (ISO format)')
    parser.add_argument('--source-path', help='Path to API definition (e.g., tenants/rest)')

    # Special flags
    parser.add_argument(
        '--regenerate-index',
        action='store_true',
        help='Regenerate only the main index page'
    )

    args = parser.parse_args()

    # Handle special flags
    if args.regenerate_index:
        print("🔄 Regenerating index only...")
        generate_index_page()
        return

    # Run appropriate mode
    if args.mode == 'incremental':
        # Validate required arguments
        required = ['api', 'api_name', 'api_type', 'version', 'type', 'source_path']
        missing = [arg for arg in required if not getattr(args, arg)]

        if missing:
            parser.error(f"Incremental mode requires: {', '.join(['--' + arg.replace('_', '-') for arg in missing])}")

        success = mode_incremental(args)
        if not success:
            exit(1)
    else:
        mode_full()


if __name__ == '__main__':
    main()
