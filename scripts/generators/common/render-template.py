#!/usr/bin/env python3
"""
Renders Jinja2 templates with YAML context.

Usage:
    render-template.py <template-file> <context-yaml> <output-file>

Example:
    python3 render-template.py pom.xml.j2 context.yml output/pom.xml
"""

import sys
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_template(template_path, context_path, output_path):
    """
    Renders a Jinja2 template with context from a YAML file.

    Args:
        template_path: Path to the Jinja2 template file
        context_path: Path to the YAML file containing template context
        output_path: Path where the rendered output will be written
    """
    # Load context from YAML
    with open(context_path, 'r') as f:
        context = yaml.safe_load(f)

    # Setup Jinja2 environment
    template_dir = Path(template_path).parent
    template_name = Path(template_path).name

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['xml', 'html']),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )

    # Custom filters
    env.filters['replace_slash'] = lambda s: s.replace('/', '-')
    env.filters['replace_dash'] = lambda s: s.replace('-', '_')

    # Render template
    template = env.get_template(template_name)
    rendered = template.render(**context)

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, 'w') as f:
        f.write(rendered)

    print(f"✅ Rendered {template_path} → {output_path}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: render-template.py <template> <context-yaml> <output>")
        print()
        print("Example:")
        print("  python3 render-template.py pom.xml.j2 context.yml output/pom.xml")
        sys.exit(1)

    try:
        render_template(sys.argv[1], sys.argv[2], sys.argv[3])
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        sys.exit(1)
