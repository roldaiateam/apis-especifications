# Categories REST API Contract

## Overview

This contract defines the **Categories REST API** specification using OpenAPI 3.0.3.  
It is published as a Maven artifact to GitHub Packages and can be consumed by microservices that need to interact with category operations.

The tenant is automatically resolved from the JWT token (XEO claim) — no tenant parameter is required in any endpoint.

---

## Structure

The contract follows the established pattern for REST API specifications in this repository:

```
categories/rest/
├── openapi-rest.yml           # Main OpenAPI spec (VERSION SOURCE OF TRUTH)
├── metadata.yml               # Contract metadata (api-spec-type: rest)
├── README.md                  # This file
└── v1/
    ├── components/
    │   ├── errors/
    │   │   └── components.yml # Standard error responses
    │   └── categories/
    │       └── components.yml # Request/Response schemas
    └── services/
        └── categories/
            └── categories-create.yml # POST /v1/categories endpoint
```

---

## Version Management

The **version in `openapi-rest.yml` → `info.version` is the SINGLE SOURCE OF TRUTH**.  
The CI/CD workflow automatically reads this version and synchronizes the Maven POM before building and publishing.

Current version: **0.0.1**

---

## API Endpoints

### POST /v1/categories
Creates a new category in the system. The tenant is resolved automatically from the JWT.

**Request Body:** `CreateCategoryRequest`
- name (string, required, minLength: 2, maxLength: 100)
- description (string, optional, maxLength: 500)
- parentCategoryId (integer/long, optional) — parent category for hierarchical classification

**Response (201):** `CreateCategoryResponse`
- categoryId (integer/long) — identifier of the created category

**Error Responses:** 400, 401, 403, 409, 500

---

## Maven Artifact

This contract is published to GitHub Packages as:

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>categories-rest-stable</artifactId>
    <version>X.Y.Z</version> <!-- Version from openapi-rest.yml -->
</dependency>
```

The JAR includes:
- Original OpenAPI spec files in `META-INF/openapi/`
- Pre-generated Java DTO models (Request/Response classes)

---

## Consuming This Contract

The contract artifact provides **pre-compiled DTOs** and the **OpenAPI spec file**.  
Consumers can use the DTOs directly and generate the API layer locally (controller interface or REST client).

### Option 1: Server Implementation (Controller Interface)

If you're **implementing the API** (e.g., in `mic-clients`):

1. Add the contract dependency:
```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>categories-rest-stable</artifactId>
    <version>0.0.1-SNAPSHOT</version>
</dependency>
```

2. Configure `openapi-generator-maven-plugin` to generate **only the API interface**:
```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>7.2.0</version>
    <executions>
        <execution>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <inputSpec>classpath:/META-INF/openapi/openapi-rest.yml</inputSpec>
                <generatorName>spring</generatorName>
                <apiPackage>your.package.api</apiPackage>
                <modelPackage>com.proactivedevs.contracts.categories.rest.v1.model</modelPackage>
                <generateApis>true</generateApis>
                <generateModels>true</generateModels> <!-- or false to use pre-compiled -->
                <generateSupportingFiles>false</generateSupportingFiles>
                <configOptions>
                    <interfaceOnly>true</interfaceOnly>
                    <useSpringBoot3>true</useSpringBoot3>
                    <useTags>true</useTags>
                    <skipDefaultInterface>true</skipDefaultInterface>
                    <useJakartaEe>true</useJakartaEe>
                </configOptions>
            </configuration>
        </execution>
    </executions>
</plugin>
```

3. Implement the generated interface in your controller:
```java
@RestController
public class CategoriesController implements CategoriesApi {
    // Use DTOs from com.proactivedevs.contracts.categories.rest.v1.model.*
    // Tenant is resolved automatically from the JWT (XEO claim) — do not add it as a parameter
}
```

### Option 2: Client Implementation (REST Client)

If you're **consuming the API** from another service:

1. Add the contract dependency (same as above)

2. Configure `openapi-generator-maven-plugin` to generate a **REST client**:
```xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>7.2.0</version>
    <executions>
        <execution>
            <goals>
                <goal>generate</goal>
            </goals>
            <configuration>
                <inputSpec>classpath:/META-INF/openapi/openapi-rest.yml</inputSpec>
                <generatorName>java</generatorName>
                <library>restclient</library> <!-- Spring 6 RestClient -->
                <apiPackage>your.package.client.api</apiPackage>
                <modelPackage>com.proactivedevs.contracts.categories.rest.v1.model</modelPackage>
                <generateApis>true</generateApis>
                <generateModels>true</generateModels> <!-- or false to use pre-compiled -->
                <generateSupportingFiles>true</generateSupportingFiles>
                <configOptions>
                    <useJakartaEe>true</useJakartaEe>
                </configOptions>
            </configuration>
        </execution>
    </executions>
</plugin>
```

3. Use the generated client:
```java
@Service
public class CategoriesClientAdapter {
    private final CategoriesApi categoriesClient;

    // Use DTOs from com.proactivedevs.contracts.categories.rest.v1.model.*
}
```

### Notes

- **`generateModels=true`**: Generates DTOs locally (use this if you prefer local generation)
- **`generateModels=false`**: Uses pre-compiled DTOs from the contract artifact (lighter build)
- **Model package must match**: `com.proactivedevs.contracts.categories.rest.v1.model`
- The spec file is available at: `classpath:/META-INF/openapi/openapi-rest.yml`
- **Tenant resolution**: The tenant is extracted from the JWT token automatically via XEO — never pass it as a request parameter

---

## Maintainer

**Andrés Reinaldo Cid**  
andresrc345@gmail.com
