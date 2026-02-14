#!/usr/bin/env python3
"""
Generates GitHub Pages documentation dynamically based on metadata.yml
This script:
1. Reads metadata.yml to find all OpenAPI contracts
2. Generates index.html with all available APIs
3. Generates Swagger UI pages for each API (stable and snapshot versions)
"""

import yaml
import os
from pathlib import Path

# Configuration
REPO_OWNER = "roldaiateam"
REPO_NAME = "apis-especifications"
STABLE_BRANCH = "main"
SNAPSHOT_BRANCH = "develop"

def load_metadata():
    """Load and parse metadata.yml"""
    with open('metadata.yml', 'r') as f:
        return yaml.safe_load(f)

def find_openapi_file(definition_path):
    """Find the OpenAPI spec file in the given path"""
    spec_path = Path(definition_path)

    # Look for common OpenAPI file patterns
    patterns = ['openapi*.yml', 'openapi*.yaml', 'api*.yml', 'api*.yaml']

    for pattern in patterns:
        files = list(spec_path.glob(pattern))
        if files:
            return files[0].name

    return None

def get_api_identifier(definition_path):
    """Convert definition path to API identifier (e.g., tenants/rest -> tenants-rest)"""
    return definition_path.replace('/', '-')

def generate_swagger_page(api_name, spec_url, version_type, definition_path, spec_file, branch):
    """Generate Swagger UI HTML page"""

    is_stable = version_type == 'stable'
    topbar_color = '#667eea' if is_stable else '#ffc107'
    topbar_text_color = 'white' if is_stable else '#333'
    badge_bg = '#28a745' if is_stable else '#ff9800'
    badge_text = 'STABLE' if is_stable else 'SNAPSHOT'
    back_link_bg = 'rgba(255, 255, 255, 0.2)' if is_stable else 'rgba(0, 0, 0, 0.1)'
    back_link_hover = 'rgba(255, 255, 255, 0.3)' if is_stable else 'rgba(0, 0, 0, 0.2)'

    warning_banner = ''
    if not is_stable:
        warning_banner = '''
    <div class="warning-banner">
        ⚠️ This is a SNAPSHOT version from the develop branch - not intended for production use
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{api_name} - {badge_text.title()} Version</title>
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
        }}

        .topbar {{
            background-color: {topbar_color};
            padding: 10px 0;
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
            color: {topbar_text_color};
            text-decoration: none;
            font-size: 1.5em;
            font-weight: bold;
        }}

        .topbar .link:hover {{
            text-decoration: underline;
        }}

        .version-badge {{
            background: {badge_bg};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            display: inline-block;
        }}

        .back-link {{
            background: {back_link_bg};
            color: {topbar_text_color};
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s ease;
        }}

        .back-link:hover {{
            background: {back_link_hover};
        }}

        .warning-banner {{
            background: #fff3cd;
            border-left: 4px solid #ff9800;
            padding: 15px;
            margin: 0;
            color: #856404;
            text-align: center;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="topbar-wrapper">
            <a href="../../" class="link">API Contracts Catalog</a>
            <div>
                <span class="version-badge">{badge_text}</span>
                <a href="../../" class="back-link">← Back to Catalog</a>
            </div>
        </div>
    </div>
{warning_banner}
    <div id="swagger-ui"></div>

    <script src="../../swagger-ui/swagger-ui-bundle.js" charset="UTF-8"></script>
    <script src="../../swagger-ui/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
    <script>
        window.onload = function() {{
            // Use Netlify Function proxy to load specs from GitHub
            const branch = "{branch}";
            const specPath = "{definition_path}/{spec_file}";
            const specUrl = `/.netlify/functions/github-spec-proxy?branch=${{branch}}&path=${{specPath}}`;

            const ui = SwaggerUIBundle({{
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
                validatorUrl: null, // Disable validator to avoid CORS issues with $ref
                requestInterceptor: (req) => {{
                    // Intercept requests for $ref files and route them through the proxy
                    if (req.url.endsWith('.yml') || req.url.endsWith('.yaml')) {{
                        // Check if it's a relative path (not already proxied)
                        if (!req.url.includes('github-spec-proxy')) {{
                            // Extract the relative path from the URL
                            const url = new URL(req.url, window.location.origin);
                            const pathname = url.pathname;

                            // If it's a relative reference (starts with ./ or just a path)
                            if (pathname.includes('/v1/')) {{
                                // Extract the part after the last occurrence of the base path
                                const match = pathname.match(/\\/(v1\\/.*\\.ya?ml)$/);
                                if (match) {{
                                    const relativePath = match[1];
                                    // Route through proxy with correct branch and path
                                    req.url = `/.netlify/functions/github-spec-proxy/${{relativePath}}`;
                                }}
                            }}
                        }}
                    }}
                    return req;
                }}
            }});

            window.ui = ui;
        }};
    </script>
</body>
</html>
'''

def generate_index_page(openapi_apis):
    """Generate the main index.html page"""

    api_rows = ''
    for api in openapi_apis:
        api_id = get_api_identifier(api['definition-path'])
        api_name = api['name']

        api_rows += f'''
                    <tr>
                        <td class="api-cell">{api_name}</td>
                        <td><span class="badge openapi">OpenAPI 3.0</span></td>
                        <td>
                            <a href="./stable/{api_id}/" class="btn">View Swagger</a>
                        </td>
                        <td>
                            <a href="./snapshot/{api_id}/" class="btn snapshot">View Swagger</a>
                        </td>
                    </tr>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProactiveDevs API Contracts</title>
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
            background: #e7f3ff;
            color: #0066cc;
        }}

        .badge.openapi {{
            background: #e7f3ff;
            color: #0066cc;
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

        .btn.snapshot {{
            background: #ffc107;
            color: #333;
        }}

        .btn.snapshot:hover {{
            background: #ffb300;
        }}

        .api-cell {{
            font-weight: 600;
            color: #333;
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
                    This catalog provides interactive documentation for all OpenAPI specifications in the ProactiveDevs ecosystem.
                    Each API contract is published as a versioned Maven artifact that can be consumed by microservices.
                </p>
                <p>
                    <strong>Repository:</strong> <a href="https://github.com/{REPO_OWNER}/{REPO_NAME}" target="_blank">github.com/{REPO_OWNER}/{REPO_NAME}</a>
                </p>
                <p>
                    <strong>Deployment:</strong> This site is automatically deployed to Netlify via GitHub Actions.
                </p>
            </div>

            <h2 style="margin-bottom: 20px; color: #333;">Available REST APIs</h2>

            <table>
                <thead>
                    <tr>
                        <th>API Name</th>
                        <th>Type</th>
                        <th>Stable (main)</th>
                        <th>Snapshot (develop)</th>
                    </tr>
                </thead>
                <tbody>{api_rows}
                </tbody>
            </table>

            <div class="note">
                <strong>Note:</strong> AsyncAPI specifications (event-driven APIs) are not displayed via Swagger UI.
                To view AsyncAPI contracts, please use <a href="https://studio.asyncapi.com/" target="_blank">AsyncAPI Studio</a>
                or download the specifications directly from the repository.
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
    &lt;artifactId&gt;tenants-rest-stable&lt;/artifactId&gt;
    &lt;version&gt;0.0.1&lt;/version&gt;
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

def main():
    """Main function to generate all documentation"""
    print("🚀 Generating GitHub Pages documentation...")

    # Load metadata
    metadata = load_metadata()
    apis = metadata.get('apis', [])

    # Filter OpenAPI contracts
    openapi_apis = [api for api in apis if api.get('api-spec-type') == 'rest']

    print(f"📋 Found {len(openapi_apis)} OpenAPI contract(s)")

    # Create docs directory structure
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    # Generate pages for each OpenAPI contract
    for api in openapi_apis:
        api_name = api['name']
        definition_path = api['definition-path']
        api_id = get_api_identifier(definition_path)

        print(f"  📝 Processing: {api_name}")

        # Find OpenAPI spec file
        spec_file = find_openapi_file(definition_path)
        if not spec_file:
            print(f"    ⚠️  Warning: No OpenAPI spec found in {definition_path}")
            continue

        print(f"    ✓ Found spec: {spec_file}")

        # Generate URLs for stable and snapshot
        stable_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{STABLE_BRANCH}/{definition_path}/{spec_file}"
        snapshot_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{SNAPSHOT_BRANCH}/{definition_path}/{spec_file}"

        # Create directories
        stable_dir = docs_dir / 'stable' / api_id
        snapshot_dir = docs_dir / 'snapshot' / api_id
        stable_dir.mkdir(parents=True, exist_ok=True)
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Generate Swagger UI pages
        stable_page = generate_swagger_page(api_name, stable_url, 'stable', definition_path, spec_file, branch='main')
        snapshot_page = generate_swagger_page(api_name, snapshot_url, 'snapshot', definition_path, spec_file, branch='develop')

        # Write pages (specs are loaded via Netlify proxy, no need to copy)
        (stable_dir / 'index.html').write_text(stable_page)
        (snapshot_dir / 'index.html').write_text(snapshot_page)

        print(f"    ✓ Generated stable page: docs/stable/{api_id}/index.html (proxy: main/{definition_path}/{spec_file})")
        print(f"    ✓ Generated snapshot page: docs/snapshot/{api_id}/index.html (proxy: develop/{definition_path}/{spec_file})")

    # Generate index page
    print("  📝 Generating index.html...")
    index_html = generate_index_page(openapi_apis)
    (docs_dir / 'index.html').write_text(index_html)
    print("    ✓ Generated: docs/index.html")

    print(f"\n✅ Documentation generated successfully!")
    print(f"   {len(openapi_apis)} OpenAPI contract(s) processed")
    print(f"\n💡 To preview locally:")
    print(f"   cd docs && python3 -m http.server 8000")
    print(f"   open http://localhost:8000")

if __name__ == '__main__':
    main()
