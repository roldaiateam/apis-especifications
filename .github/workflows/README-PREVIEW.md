# API Preview Workflows

Este repositorio incluye workflows de GitHub Actions para generar previews temporales de las APIs en Pull Requests.

## 📋 Workflows Disponibles

### 1. **PR Preview on Demand** (`pr-preview-on-demand.yml`)

Genera previews de APIs bajo demanda mediante comandos en comentarios de PR.

**Trigger:** Comentarios en PRs que comienzan con `/generate-preview-api`

**Comandos disponibles:**

```bash
# Generar preview de todas las APIs modificadas en la PR
/generate-preview-api

# Generar preview de una API específica (debe coincidir con el nombre en metadata.yml)
/generate-preview-api --name "Tenants REST API"
/generate-preview-api --name "Tenants Events"
```

**Funcionamiento:**
1. Detecta el comando en el comentario
2. Identifica las APIs a previsualizar (todas las modificadas o una específica)
3. Genera documentación estática con Swagger UI (REST) o AsyncAPI (Events)
4. Despliega a la rama `gh-pages-preview`
5. Comenta en la PR con el enlace a la preview

**URL de acceso:**
```
https://<owner>.github.io/<repo>/pr-<numero>/
```

### 2. **Cleanup PR Previews** (`cleanup-pr-previews.yml`)

Limpia automáticamente las páginas de preview cuando se cierra una PR.

**Trigger:** Cuando se cierra una PR (merged o closed)

**Funcionamiento:**
1. Checkout de la rama `gh-pages-preview`
2. Elimina el directorio `pr-<numero>` correspondiente
3. Regenera el índice con las PRs restantes
4. Hace commit y push de los cambios

## 🚀 Configuración Inicial

### Paso 1: Habilitar GitHub Pages

1. Ve a **Settings** → **Pages**
2. En **Source**, selecciona **Deploy from a branch**
3. Selecciona la rama `gh-pages-preview` (se creará automáticamente en el primer preview)
4. Selecciona la carpeta `/` (root)
5. Guarda los cambios

### Paso 2: Permisos del Workflow

Asegúrate de que GitHub Actions tenga permisos de escritura:

1. Ve a **Settings** → **Actions** → **General**
2. En **Workflow permissions**, selecciona **Read and write permissions**
3. Marca **Allow GitHub Actions to create and approve pull requests**
4. Guarda los cambios

## 📝 Uso Práctico

### Ejemplo 1: Preview de todas las APIs modificadas

```markdown
Comentario en PR:
/generate-preview-api

Respuesta del bot:
✅ Preview generado
🔗 https://roldaiateam.github.io/apis-especifications/pr-123/
```

### Ejemplo 2: Preview de una API específica

```markdown
Comentario en PR:
/generate-preview-api --name "Tenants REST API"

Respuesta del bot:
✅ Preview generado para: Tenants REST API
🔗 https://roldaiateam.github.io/apis-especifications/pr-123/
```

### Ejemplo 3: Error - API no encontrada

```markdown
Comentario en PR:
/generate-preview-api --name "API Inexistente"

Respuesta del bot:
❌ Error: API 'API Inexistente' not found in metadata.yml
```

## 🏗️ Estructura de Archivos

```
gh-pages-preview/
├── index.html                    # Índice de todas las PRs con preview
├── pr-123/
│   ├── index.html               # Índice de APIs de esta PR
│   └── apis/
│       ├── tenants-rest/
│       │   ├── index.html       # Viewer Swagger UI
│       │   ├── openapi-rest.yml
│       │   └── v1/              # Referencias externas
│       └── tenants-event/
│           ├── index.html       # Viewer AsyncAPI
│           ├── asyncapi.yml
│           └── v1/
└── pr-124/
    └── ...
```

## 🔍 Detección de APIs

### Automática (modo `all_changed`)
El workflow detecta automáticamente las APIs modificadas comparando con la rama base:

- Archivos `openapi*.yml` modificados → API REST detectada
- Archivos `asyncapi.yml` modificados → API Event detectada
- Archivo `metadata.yml` modificado → Todas las APIs

### Manual (modo `single`)
Cuando se especifica `--name`, el workflow busca en `metadata.yml`:

```yaml
apis:
  - name: "Tenants REST API"       # ← Este nombre debe coincidir
    api-spec-type: rest
    definition-path: tenants/rest
```

## 🎨 Viewers

### REST APIs → Swagger UI
- Librería: `swagger-ui-dist@5.10.5`
- Características: Explorador interactivo, pruebas de endpoints

### Event APIs → AsyncAPI Web Component
- Librería: `@asyncapi/web-component`
- Características: Visualización de canales, mensajes y schemas

## 🧹 Limpieza Automática

Al cerrar/mergear una PR:
1. Se ejecuta `cleanup-pr-previews.yml`
2. Se elimina `pr-<numero>` de `gh-pages-preview`
3. Se regenera el índice sin esa PR
4. Los enlaces quedan rotos (404) ✅

## ⚠️ Consideraciones

### Seguridad
- Los previews son **públicos** en GitHub Pages
- No incluir secrets ni información sensible en las specs

### Limitaciones
- GitHub Pages tiene un límite de **1 GB** por repositorio
- Workflows tienen timeout de **6 horas**
- Máximo **1000 requests/hora** a GitHub API

### Performance
- Cada preview es independiente (no comparte assets)
- Los viewers se cargan desde CDN (no consumen storage del repo)

## 🐛 Troubleshooting

### El workflow no se ejecuta
- ✅ Verifica que el comentario empiece exactamente con `/generate-preview-api`
- ✅ Verifica que sea en una **PR abierta**, no en un issue

### La página 404
- ✅ Verifica que GitHub Pages esté habilitado en Settings
- ✅ Espera 1-2 minutos después del despliegue (propagación)
- ✅ Verifica que la rama `gh-pages-preview` exista

### El viewer no carga
- ✅ Verifica que los archivos `.yml` estén en la carpeta correcta
- ✅ Revisa la consola del navegador (F12) para errores
- ✅ Verifica que las referencias `$ref` sean relativas correctas

### API no detectada
- ✅ Verifica que el nombre en `--name` coincida exactamente con `metadata.yml`
- ✅ Verifica que los cambios estén en archivos `openapi*.yml` o `asyncapi.yml`
- ✅ Verifica que la ruta en `definition-path` sea correcta

## 📚 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [AsyncAPI](https://www.asyncapi.com/)
