# Netlify Deployment para Documentación de APIs

Este documento explica cómo se ha configurado Netlify para mostrar documentación interactiva Swagger UI de las especificaciones OpenAPI de forma **completamente dinámica**.

## 🎯 Arquitectura de la Solución

### Principios de Diseño

✅ **Sin duplicación:** Las especificaciones OpenAPI permanecen en sus ubicaciones originales
✅ **Generación automática:** Todo se genera dinámicamente desde `metadata.yml`
✅ **Siempre actualizado:** Swagger UI carga specs directamente desde GitHub
✅ **Zero maintenance:** Agregar una nueva API solo requiere actualizar `metadata.yml`
✅ **Multi-branch:** Stable apunta a `main`, snapshot apunta a `develop`

### Cómo Funciona

1. **Defines la API** en `metadata.yml`:
   ```yaml
   apis:
     - name: "Products API"
       api-spec-type: rest
       definition-path: products/rest
   ```

2. **El script genera automáticamente**:
   - Página de índice con la nueva API
   - Páginas de Swagger UI (stable y snapshot)
   - Enlaces correctos a las especificaciones en GitHub

3. **GitHub Actions despliega** todo a Netlify

## 📁 Estructura de Archivos

```
apis-especifications/
├── metadata.yml                        # ← Única fuente de verdad
├── scripts/
│   └── generate-docs.py               # ← Script generador dinámico
├── docs/                              # ← Generado automáticamente
│   ├── index.html                     # Catálogo de APIs
│   ├── swagger-ui/                    # Assets de Swagger UI v5.11.0
│   ├── stable/
│   │   └── {api-id}/
│   │       └── index.html             # Apunta a branch main
│   └── snapshot/
│       └── {api-id}/
│           └── index.html             # Apunta a branch develop
├── tenants/rest/
│   └── openapi-rest.yml               # ← Especificación original (NO se duplica)
└── .github/workflows/
    └── deploy-netlify.yml             # Workflow de CI/CD para Netlify
```

**Importante:** El directorio `docs/` es generado completamente por el script. NO edites archivos manualmente en `docs/`.

## 🚀 Añadir una Nueva API OpenAPI

### Paso 1: Crea la especificación

```bash
# Crear estructura
mkdir -p products/rest/v1/services

# Crear especificación OpenAPI
cat > products/rest/openapi-rest.yml << 'EOF'
openapi: 3.0.3
info:
  title: Products API
  version: 1.0.0
paths:
  /v1/products:
    $ref: './v1/services/products-list.yml'
EOF
```

### Paso 2: Registra en metadata.yml

```yaml
apis:
  - name: "Tenants REST API"
    api-spec-type: rest
    definition-path: tenants/rest

  - name: "Products API"        # ← Nueva API
    api-spec-type: rest
    definition-path: products/rest
```

### Paso 3: Genera la documentación

```bash
# Ejecutar el script generador
python3 scripts/generate-docs.py
```

Output esperado:
```
🚀 Generating GitHub Pages documentation...
📋 Found 2 OpenAPI contract(s)
  📝 Processing: Tenants REST API
    ✓ Found spec: openapi-rest.yml
    ✓ Generated stable page: docs/stable/tenants-rest/index.html
    ✓ Generated snapshot page: docs/snapshot/tenants-rest/index.html
  📝 Processing: Products API
    ✓ Found spec: openapi-rest.yml
    ✓ Generated stable page: docs/stable/products-rest/index.html
    ✓ Generated snapshot page: docs/snapshot/products-rest/index.html
  📝 Generating index.html...
    ✓ Generated: docs/index.html

✅ Documentation generated successfully!
```

### Paso 4: Commit y push

```bash
git add metadata.yml products/ docs/
git commit -m "feat: add Products API"
git push
```

**Eso es todo!** GitHub Actions regenerará automáticamente la documentación y la desplegará a Netlify.

## 🔄 Workflow Automático de GitHub Actions

**Archivo:** `.github/workflows/deploy-netlify.yml`

### Triggers

El workflow se ejecuta cuando:
- Se modifica `metadata.yml`
- Se modifica cualquier archivo `openapi*.yml`
- Se modifican archivos en `docs/`
- Se modifica el script `scripts/generate-docs.py`

### Proceso

1. **Checkout del repositorio**
2. **Setup de Python 3.x**
3. **Instala PyYAML**
4. **Ejecuta `scripts/generate-docs.py`**
   - Lee `metadata.yml`
   - Encuentra todas las APIs tipo `rest`
   - Genera páginas HTML dinámicamente
5. **Commit de cambios** (si hubo actualizaciones)
6. **Despliega a Netlify**

### Ejemplo de ejecución

```yaml
- name: Generate documentation
  run: |
    python scripts/generate-docs.py
```

El script detecta automáticamente:
- ✅ Nuevas APIs añadidas a `metadata.yml`
- ✅ APIs eliminadas
- ✅ Cambios en nombres de APIs
- ✅ Cambios en rutas de especificaciones

## 📝 Script Generador: `scripts/generate-docs.py`

### Características

- **Lectura de metadata.yml:** Obtiene la lista de todas las APIs
- **Búsqueda automática:** Encuentra el archivo OpenAPI en cada `definition-path`
- **Generación de URLs:** Crea URLs correctas a GitHub raw files
- **Generación de HTML:** Crea todas las páginas necesarias
- **Validación:** Advierte si no encuentra especificaciones

### Patrones de búsqueda de OpenAPI

El script busca archivos con estos patrones:
- `openapi*.yml`
- `openapi*.yaml`
- `api*.yml`
- `api*.yaml`

### Conversión de IDs

El `definition-path` se convierte en ID de API:
- `tenants/rest` → `tenants-rest`
- `products/rest` → `products-rest`
- `users/api` → `users-api`

## 🌐 URLs del Sitio Desplegado

Una vez desplegado en Netlify:

**Landing page:**
- Production (main): `https://<your-site>.netlify.app/`
- Preview (develop): `https://develop--<your-site>.netlify.app/`

**APIs individuales:**
- Production: `https://<your-site>.netlify.app/stable/tenants-rest/`
- Preview: `https://develop--<your-site>.netlify.app/snapshot/tenants-rest/`

La URL exacta dependerá del nombre de tu sitio en Netlify.

Cada página de Swagger UI apunta directamente a:
- **Stable:** `https://raw.githubusercontent.com/roldaiateam/apis-especifications/main/{path}/openapi-rest.yml`
- **Snapshot:** `https://raw.githubusercontent.com/roldaiateam/apis-especifications/develop/{path}/openapi-rest.yml`

## 🔧 Actualizar Especificaciones OpenAPI

Para actualizar una especificación existente:

1. **Edita el archivo** en su ubicación original:
   ```bash
   vim tenants/rest/openapi-rest.yml
   ```

2. **Commit y push** a `develop` o `main`:
   ```bash
   git add tenants/rest/openapi-rest.yml
   git commit -m "feat: add new endpoint to Tenants API"
   git push
   ```

3. **GitHub Actions NO se ejecuta** (porque solo cambió el spec, no metadata.yml)

4. **Swagger UI muestra los cambios inmediatamente** (con posible cache de 1-2 minutos)

**No necesitas regenerar nada en `docs/`** porque las páginas apuntan directamente al archivo en GitHub.

## 🧪 Pruebas Locales

### Regenerar documentación localmente

```bash
# Instalar dependencias (solo primera vez)
python3 -m pip install pyyaml --user

# Ejecutar script
python3 scripts/generate-docs.py
```

### Visualizar localmente

```bash
cd docs
python3 -m http.server 8000
```

Abre http://localhost:8000 en tu navegador.

**Nota:** Las URLs a GitHub raw funcionan incluso en local.

## ⚙️ Configuración de Netlify

### Configuración Inicial

1. **Crea un sitio en Netlify:**
   - Ve a https://app.netlify.com/
   - Click en "Add new site" → "Import an existing project"
   - Conecta con tu repositorio de GitHub
   - Netlify detectará automáticamente el `netlify.toml`

2. **Obtén el Site ID:**
   - Ve a Site settings → General → Site details
   - Copia el "Site ID"

3. **Configura los Secrets en GitHub:**
   - Ve a tu repositorio → Settings → Secrets and variables → Actions
   - Verifica que existe `NETLIFY_AUTH_TOKEN` (ya configurado)
   - Añade `NETLIFY_SITE_ID` con el Site ID copiado

### Despliegue Automático

El workflow desplegará automáticamente:
- **Push a `main`** → Producción en Netlify
- **Push a `develop`** → Deploy preview en Netlify
- **Pull Requests** → Deploy preview con comentario en el PR

## 🐛 Solución de Problemas

### Problema: Nueva API no aparece en el catálogo

**Causa:** Olvidaste registrarla en `metadata.yml` o el `api-spec-type` no es `rest`.

**Solución:**
```yaml
apis:
  - name: "Mi Nueva API"
    api-spec-type: rest  # ← Debe ser "rest"
    definition-path: mi-api/rest
```

### Problema: Script no encuentra el OpenAPI spec

**Causa:** El archivo no sigue los patrones de búsqueda.

**Solución:** Renombra tu archivo a uno de estos nombres:
- `openapi-rest.yml` ✅
- `openapi.yml` ✅
- `api.yml` ✅

### Problema: Swagger UI muestra error al cargar

**Causa:** La URL a GitHub raw es incorrecta.

**Solución:** Verifica que:
1. El archivo existe en la rama correcta (`main` o `develop`)
2. La ruta en `metadata.yml` es correcta
3. Abre la URL raw directamente en el navegador para verificar

### Problema: Los cambios no se reflejan inmediatamente

**Causa:** Cache de GitHub raw files.

**Solución:**
- Espera 1-2 minutos
- Haz hard refresh (Ctrl+F5 / Cmd+Shift+R)
- Verifica que el commit se hizo en la rama correcta

## 📦 Archivos del Sistema

**Archivos creados:**
- `scripts/generate-docs.py` - Script generador dinámico
- `.github/workflows/deploy-netlify.yml` - Workflow de CI/CD para Netlify
- `.github/workflows/deploy-github-pages.yml.disabled` - Workflow de GitHub Pages (deshabilitado)
- `netlify.toml` - Configuración de Netlify
- `docs/` - Directorio generado automáticamente (NO editar manualmente)
- `GITHUB_PAGES_SETUP.md` - Esta guía (ahora para Netlify)

**Archivos modificados:**
- `README.md` - Añadida sección de documentación interactiva

## 🎓 Conceptos Clave

### Single Source of Truth

`metadata.yml` es la única fuente de verdad para:
- Qué APIs existen
- Dónde están ubicadas
- Qué tipo de API son (rest vs event)

### Generación vs Mantenimiento Manual

❌ **Antes (manual):**
- Agregar API → Crear 3 archivos HTML manualmente
- Cambiar nombre → Actualizar múltiples archivos
- Eliminar API → Recordar borrar todos los archivos relacionados

✅ **Ahora (automático):**
- Agregar API → Actualizar `metadata.yml` y push
- Cambiar nombre → Actualizar `metadata.yml` y push
- Eliminar API → Quitar de `metadata.yml` y push

### URLs Dinámicas vs Archivos Estáticos

El directorio `docs/` NO contiene copias de las especificaciones OpenAPI.
Solo contiene **páginas HTML que apuntan** a las especificaciones originales en GitHub.

**Ventajas:**
- Sin duplicación de archivos
- Sin sincronización necesaria
- Siempre muestra la versión más reciente

## 📚 Recursos Adicionales

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [PyYAML Documentation](https://pyyaml.org/)
