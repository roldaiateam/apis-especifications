# Generación de Versiones Unstable de APIs

Este documento explica cómo usar el sistema de generación de versiones **unstable** (preview) de contratos API desde Pull Requests.

## ¿Qué son las versiones unstable?

Las versiones unstable son versiones **temporales** de contratos API que se generan desde un PR antes de que sea mergeado. Estas versiones permiten:

- ✅ Probar cambios en la API antes del merge
- ✅ Integrar y validar cambios en microservicios consumidores
- ✅ Detectar problemas de integración tempranamente
- ✅ Iterar rápidamente sin afectar versiones estables

Las versiones unstable:
- 🔹 Se publican a GitHub Packages con un sufijo único por branch
- 🔹 Se eliminan automáticamente cuando el PR es mergeado
- 🔹 No afectan las versiones estables existentes

---

## Cómo Generar una Versión Unstable

### 1. Crear un PR con cambios en tu API

Primero, crea un branch con tus cambios en el contrato API y abre un Pull Request.

### 2. Ejecutar el comando `/generate-api`

En el PR, escribe un comentario con el siguiente formato:

```
/generate-api --name "Tenants REST API" --packaging mvn
```

**Parámetros:**

| Parámetro | Descripción | Valores | Requerido |
|-----------|-------------|---------|-----------|
| `--name` | Nombre de la API (debe coincidir con el campo `name` en `metadata.yml` raíz) | String entre comillas | ✅ Sí |
| `--packaging` | Sistema de empaquetado | `mvn` (único soportado actualmente) | ⚠️ Opcional (default: `mvn`) |

**Ejemplo de nombres válidos:**
- `"Tenants REST API"` → `tenants/rest`
- `"Tenants Events"` → `tenants/event`

### 3. Esperar la generación

El workflow se ejecutará automáticamente y:

1. ✅ Validará los parámetros
2. 🔍 Encontrará el módulo correspondiente
3. 📦 Extraerá la versión desde el spec file (`info.version`)
4. 🏗️ Construirá el artefacto con un nombre unstable
5. 🚀 Lo desplegará a GitHub Packages
6. 💬 Comentará en el PR con las instrucciones de uso

### 4. Usar la versión unstable

El workflow comentará en el PR con el snippet Maven para consumir la versión:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-rest-unstable</artifactId>
    <version>0.0.1-feature-RDIA-86c7n8ka4-SNAPSHOT</version>
</dependency>
```

**Formato de la versión unstable:**
```
{api-version}-{branch-name}-SNAPSHOT
```

Ejemplo: Si la API tiene versión `0.0.1` y el branch es `feature/RDIA-86c7n8ka4`, la versión unstable será:
```
0.0.1-feature-RDIA-86c7n8ka4-SNAPSHOT
```

---

## Diferencias entre Stable y Unstable

| Aspecto | Stable | Unstable |
|---------|--------|----------|
| **ArtifactId** | `tenants-rest-stable` | `tenants-rest-unstable` |
| **Versión** | `1.0.0` o `1.0.0-SNAPSHOT` | `1.0.0-feature-xyz-SNAPSHOT` |
| **Publicación** | Automática en push a `main`/`develop` | Manual via comando en PR |
| **Ciclo de vida** | Permanente | Temporal (se elimina al mergear) |
| **Uso** | Producción y desarrollo | Testing e integración pre-merge |

---

## Cleanup Automático

Cuando el PR es **mergeado** (no solo cerrado), el workflow `cleanup-unstable-packages.yml` se ejecuta automáticamente:

1. 🔍 Identifica todas las versiones unstable asociadas al branch del PR
2. 🗑️ Elimina cada versión de GitHub Packages usando la API
3. 💬 Comenta en el PR confirmando la limpieza

**Requisito:** El cleanup requiere un Personal Access Token (PAT) con permisos:
- `read:packages`
- `delete:packages`
- `repo`

Este token debe estar guardado como secret `PACKAGES_PAT` en el repositorio.

---

## Estructura de Nombres de Paquetes

Los paquetes unstable siguen esta estructura:

```
com.proactivedevs.contracts.<domain>-<type>-unstable
```

Ejemplos:
- REST API: `com.proactivedevs.contracts.tenants-rest-unstable`
- Event API: `com.proactivedevs.contracts.tenants-event-unstable`

El sufijo `-unstable` reemplaza al `-stable` para evitar conflictos.

---

## Workflows Involucrados

### `generate-unstable-api.yml`

**Trigger:** Comentario en PR que contiene `/generate-api`

**Pasos principales:**
1. Parsear argumentos del comando
2. Obtener detalles del PR (branch, SHA)
3. Buscar el módulo por nombre de API
4. Extraer versión del spec file
5. Computar versión unstable y artifactId
6. Modificar POM temporalmente (solo en CI)
7. Build + Deploy a GitHub Packages
8. Comentar resultado en el PR

**Permisos requeridos:**
- `contents: read`
- `packages: write`
- `pull-requests: write`

### `cleanup-unstable-packages.yml`

**Trigger:** PR cerrado (solo si merged)

**Pasos principales:**
1. Obtener branch name del PR
2. Leer todos los módulos desde `metadata.yml`
3. Para cada módulo, buscar versiones que matcheen el patrón del branch
4. Eliminar cada versión usando la API de GitHub Packages
5. Comentar resultado en el PR

**Permisos requeridos:**
- `contents: read`
- `pull-requests: write`

**Secret requerido:**
- `PACKAGES_PAT` (PAT con `read:packages`, `delete:packages`, `repo`)

---

## Troubleshooting

### Error: "No module found with name"

**Causa:** El nombre especificado en `--name` no coincide con ningún `name` en `metadata.yml` raíz.

**Solución:** Verifica los nombres disponibles en `metadata.yml`:

```yaml
apis:
  - name: "Tenants Events"        # ← Usa este nombre exacto
    api-spec-type: event
    definition-path: tenants/event
  - name: "Tenants REST API"      # ← O este
    api-spec-type: rest
    definition-path: tenants/rest
```

### Error: "Unsupported packaging"

**Causa:** El parámetro `--packaging` tiene un valor diferente de `mvn`.

**Solución:** Actualmente solo se soporta `mvn`. Usa:
```
/generate-api --name "Tenants REST API" --packaging mvn
```

### El cleanup no elimina paquetes

**Causa posible:**

1. El secret `PACKAGES_PAT` no está configurado o no tiene los permisos correctos
2. Las versiones unstable fueron publicadas desde otro branch

**Solución:**
1. Verifica que el PAT tenga permisos `read:packages`, `delete:packages`, `repo`
2. Las versiones solo se eliminan si el nombre del branch coincide

---

## Ejemplo Completo de Flujo

### 1. Crear branch y modificar API

```bash
git checkout -b feature/add-tenant-status
# Modifica tenants/rest/openapi-rest.yml
# Incrementa version de 0.0.1 a 0.1.0
git add .
git commit -m "Add tenant status field"
git push origin feature/add-tenant-status
```

### 2. Abrir PR en GitHub

Crea el PR desde `feature/add-tenant-status` hacia `develop`

### 3. Generar versión unstable

En el PR, comenta:
```
/generate-api --name "Tenants REST API" --packaging mvn
```

### 4. El workflow genera y comenta

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-rest-unstable</artifactId>
    <version>0.1.0-feature-add-tenant-status-SNAPSHOT</version>
</dependency>
```

### 5. Integrar en microservicio consumidor

En `mic-clients/api-rest/pom.xml`:

```xml
<dependencies>
    <!-- Temporalmente usa la versión unstable -->
    <dependency>
        <groupId>com.proactivedevs.contracts</groupId>
        <artifactId>tenants-rest-unstable</artifactId>
        <version>0.1.0-feature-add-tenant-status-SNAPSHOT</version>
    </dependency>
</dependencies>
```

O si usas el plugin `roldaia-codegen-maven-plugin`, Maven detectará automáticamente el contrato unstable si está en el classpath.

### 6. Probar cambios

```bash
cd mic-clients
mvn clean install
# Ejecuta tests, verifica que todo funciona
```

### 7. Mergear PR

Una vez aprobado, mergea el PR. El workflow de cleanup se ejecutará automáticamente y eliminará la versión `0.1.0-feature-add-tenant-status-SNAPSHOT`.

### 8. Actualizar a versión stable

Después del merge a `develop`, el workflow `publish-contracts.yml` publicará la versión stable:
```
0.1.0-SNAPSHOT (en develop)
0.1.0 (cuando se mergee a main)
```

Actualiza `mic-clients` para usar la versión stable:
```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-rest-stable</artifactId>
    <version>0.1.0-SNAPSHOT</version>
</dependency>
```

---

## Notas Adicionales

- 📌 Las versiones unstable **NO sobrescriben** las versiones stable (usan artifactId diferente)
- 📌 Puedes generar múltiples versiones unstable del mismo módulo desde diferentes branches
- 📌 La limpieza es **automática** al mergear, no requiere intervención manual
- 📌 Si el workflow falla, revisa los logs en la pestaña "Actions" de GitHub
- 📌 El source of truth para la versión es **siempre** el campo `info.version` del spec file

---

## Referencias

- [Workflows de publicación](./publish-contracts.yml)
- [Workflow de validación](./validate-contracts.yml)
- [GitHub Packages Maven](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-apache-maven-registry)
- [GitHub Actions issue_comment trigger](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#issue_comment)
