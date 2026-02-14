# Documentation Generator Script

## generate-docs.py

Script Python que genera automáticamente la documentación Swagger UI para todas las APIs OpenAPI definidas en `metadata.yml`.

### Uso

```bash
python3 scripts/generate-docs.py
```

### Requisitos

```bash
pip install pyyaml
```

### Funcionamiento

1. Lee `metadata.yml` del directorio raíz
2. Filtra todas las APIs con `api-spec-type: rest`
3. Para cada API:
   - Busca el archivo OpenAPI (patrones: `openapi*.yml`, `openapi*.yaml`, `api*.yml`, `api*.yaml`)
   - Genera URLs a GitHub raw para branches `main` y `develop`
   - Crea páginas Swagger UI en `docs/stable/{api-id}/` y `docs/snapshot/{api-id}/`
4. Genera `docs/index.html` con el catálogo completo de APIs

### Output

```
docs/
├── index.html                    # Catálogo de APIs
├── swagger-ui/                   # Assets (no se regeneran)
├── stable/
│   └── {api-id}/
│       └── index.html           # Apunta a main branch
└── snapshot/
    └── {api-id}/
        └── index.html           # Apunta a develop branch
```

### Integración CI/CD

Este script se ejecuta automáticamente en GitHub Actions via `.github/workflows/deploy-netlify.yml`:

```yaml
- name: Generate documentation
  run: |
    python scripts/generate-docs.py
```

### Configuración

Variables en el script:
- `REPO_OWNER`: Owner del repositorio en GitHub
- `REPO_NAME`: Nombre del repositorio
- `STABLE_BRANCH`: Rama para versiones stable (default: `main`)
- `SNAPSHOT_BRANCH`: Rama para versiones snapshot (default: `develop`)
