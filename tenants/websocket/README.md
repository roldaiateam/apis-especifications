# Tenants WebSocket Contract

AsyncAPI contract for Tenants domain WebSocket events using Avro serialization.

## Overview

This contract defines the real-time WebSocket messages sent by the Tenants microservice to notify clients about tenant provisioning status changes. Messages are serialized using **Apache Avro** and delivered over **WebSocket Secure (WSS)**.

## Maven Artifact

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-websocket-stable</artifactId>
    <version>1.0.3-SNAPSHOT</version>
</dependency>
```

## Events

### TenantProvisioningStatusEvent

Sent when the provisioning status of a tenant changes.

**Channel:** `/ws/tenants/{tenantId}/provisioning-status`  
**Protocol:** `wss`  
**Content-Type:** `application/vnd.apache.avro+json`  
**Schema:** `tenants-avro/v1/tenant-provisioning-status-envelope.avsc`

#### Envelope Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `eventId` | string | Yes | Unique identifier for this event (UUID) |
| `eventType` | string | Yes | Always `"tenant.provisioning.status"` |
| `eventVersion` | string | Yes | Version of the event schema |
| `timestamp` | string | Yes | ISO 8601 timestamp when the event occurred |
| `correlationId` | string | Yes | Correlation ID for tracing requests across services |
| `payload` | TenantProvisioningStatusAvro | Yes | Provisioning status data |
| `metadata` | map<string, string> | No | Optional key-value metadata for extensibility |

#### Payload Fields (TenantProvisioningStatusAvro)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenantId` | string | Yes | Identifier of the tenant being provisioned |
| `status` | enum | Yes | Current lifecycle stage: `PENDING`, `VALIDATING`, `PROVISIONING`, `CONFIGURING`, `COMPLETED`, `FAILED` |
| `progress` | int | No | Completion percentage (0-100) |
| `step` | string | No | Technical step being executed |
| `details` | string | No | Human-readable explanation of the current status |
| `error` | ProvisioningErrorAvro | No | Error details if the provisioning failed |

#### Error Fields (ProvisioningErrorAvro)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Error code identifying the type of failure |
| `message` | string | Yes | Human-readable error message |
| `retryable` | boolean | Yes | Whether the failed operation can be retried |

#### Example Payload (JSON)

```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "eventType": "tenant.provisioning.status",
  "eventVersion": "1",
  "timestamp": "2026-02-07T10:30:00Z",
  "correlationId": "corr-abc-123",
  "payload": {
    "tenantId": "tenant-123",
    "status": "PROVISIONING",
    "progress": 45,
    "step": "creating-database",
    "details": "Creating tenant database schema",
    "error": null
  },
  "metadata": {
    "source": "provisioning-service"
  }
}
```

#### Example Error Payload (JSON)

```json
{
  "eventId": "660e9500-f39c-52e5-b827-557766551111",
  "eventType": "tenant.provisioning.status",
  "eventVersion": "1",
  "timestamp": "2026-02-07T10:35:00Z",
  "correlationId": "corr-abc-123",
  "payload": {
    "tenantId": "tenant-123",
    "status": "FAILED",
    "progress": 45,
    "step": "creating-database",
    "details": "Failed to create tenant database schema",
    "error": {
      "code": "DB_CREATION_FAILED",
      "message": "Could not create database: connection timeout",
      "retryable": true
    }
  },
  "metadata": null
}
```

## WebSocket Configuration

### Server

- **Host:** `api.midominio.com`
- **Protocol:** `wss`
- **Authentication:** Bearer JWT token

### Connection

Clients connect to the WebSocket endpoint providing the `tenantId` as a path parameter:

```
wss://api.midominio.com/ws/tenants/{tenantId}/provisioning-status
```

## Consuming Events

### 1. Add the Maven Dependency

Add this contract as a dependency to your microservice.

### 2. Access Avro Schema

The Avro schema is bundled in the JAR under `META-INF/asyncapi/`:

```java
InputStream schemaStream = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/tenants-avro/v1/tenant-provisioning-status-envelope.avsc");
```

### 3. Connect via WebSocket

Example with Spring WebSocket:

```java
WebSocketClient client = new StandardWebSocketClient();
WebSocketSession session = client.execute(
    new MyWebSocketHandler(),
    "wss://api.midominio.com/ws/tenants/tenant-123/provisioning-status"
).get();
```

### 4. Deserialize with Avro

Use Apache Avro library to deserialize:

```java
Schema schema = new Schema.Parser().parse(schemaStream);
DatumReader<GenericRecord> datumReader = new GenericDatumReader<>(schema);
Decoder decoder = DecoderFactory.get().jsonDecoder(schema, new ByteArrayInputStream(message));
GenericRecord record = datumReader.read(null, decoder);

GenericRecord payload = (GenericRecord) record.get("payload");
String tenantId = payload.get("tenantId").toString();
String status = payload.get("status").toString();
```

## Avro Schemas

| Schema | Description |
|--------|-------------|
| `tenants-avro/v1/tenant-provisioning-status-envelope.avsc` | Event envelope with metadata and payload |
| `tenants-avro/v1/imports/tenant-provisioning-status.avsc` | Provisioning status payload |
| `tenants-avro/v1/imports/provisioning-error.avsc` | Error details record |

## Versioning

- **Main branch:** Stable versions (e.g., `1.0.0`, `1.1.0`)
- **Develop branch:** Snapshot versions (e.g., `1.0.3-SNAPSHOT`)

Breaking changes will increment the major version and may require a new Avro schema version (e.g., `v2`).

## Resources

- AsyncAPI Specification: `asyncapi.yml`
- Avro Schemas: `tenants-avro/v1/`
- Metadata: `metadata.yml`

## Support

For questions or issues, contact the Roldaia Team at `roldaiateam@gmail.com`.