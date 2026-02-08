# Tenants Events Contract

AsyncAPI contract for Tenants domain events published to RabbitMQ.

## Overview

This contract defines the events emitted by the Tenants microservice when tenant-related actions occur. Events are published using **Apache Avro** serialization to a **RabbitMQ Topic Exchange** for maximum flexibility and extensibility.

## Maven Artifact

```xml
<dependency>
    <groupId>com.proactivedevs.contracts</groupId>
    <artifactId>tenants-event-stable</artifactId>
    <version>1.0.0</version>
</dependency>
```

For SNAPSHOT versions (from `develop` branch):
```xml
<version>1.0.0-SNAPSHOT</version>
```

## Events

### TenantCreated

Emitted when a new tenant is successfully created.

**Exchange:** `tenants.events` (Topic Exchange)  
**Routing Key:** `tenant.created`  
**Content-Type:** `application/vnd.apache.avro+json`  
**Schema:** `tenants-avro/v1/tenant-created-envelope.avsc`

#### Payload Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `eventId` | string | Yes | Unique identifier for this event (UUID) |
| `eventType` | string | Yes | Always `"tenant.created"` |
| `timestamp` | string | Yes | ISO 8601 timestamp when the event occurred |
| `tenantId` | string | Yes | Unique identifier for the tenant |
| `tenantName` | string | Yes | Name of the tenant/organization |
| `userName` | string | Yes | Name of the user who created the tenant |
| `metadata` | map<string, string> | No | Optional key-value metadata for extensibility |

#### Example Payload (JSON)

```json
{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "eventType": "tenant.created",
  "timestamp": "2026-02-07T10:30:00Z",
  "tenantId": "tenant-123",
  "tenantName": "Acme Corporation",
  "userName": "John Doe",
  "metadata": {
    "source": "web-portal",
    "region": "us-east-1"
  }
}
```

## RabbitMQ Configuration

### Exchange

- **Name:** `tenants.events`
- **Type:** `topic`
- **Durable:** `true`
- **Auto-delete:** `false`

### Server (Development)

- **Host:** `localhost:5672`
- **Protocol:** `amqp`
- **Virtual Host:** `/`
- **Credentials:** `guest/guest`

## Consuming Events

### 1. Add the Maven Dependency

Add this contract as a dependency to your microservice.

### 2. Access Avro Schema

The Avro schema is bundled in the JAR under `META-INF/asyncapi/`:

```java
InputStream schemaStream = getClass()
    .getClassLoader()
    .getResourceAsStream("META-INF/asyncapi/tenants-avro/v1/tenant-created-envelope.avsc");
```

### 3. Configure RabbitMQ Listener

Example with Spring AMQP:

```java
@RabbitListener(bindings = @QueueBinding(
    value = @Queue(value = "my-service-tenants-queue", durable = "true"),
    exchange = @Exchange(value = "tenants.events", type = ExchangeTypes.TOPIC, durable = "true"),
    key = "tenant.created"
))
public void handleTenantCreated(byte[] message) {
    // Deserialize Avro message
    TenantCreatedEvent event = deserializeAvro(message);
    // Process event
}
```

### 4. Deserialize with Avro

Use Apache Avro library to deserialize:

```java
Schema schema = new Schema.Parser().parse(schemaStream);
DatumReader<GenericRecord> datumReader = new GenericDatumReader<>(schema);
Decoder decoder = DecoderFactory.get().jsonDecoder(schema, new ByteArrayInputStream(message));
GenericRecord record = datumReader.read(null, decoder);

String tenantId = record.get("tenantId").toString();
String tenantName = record.get("tenantName").toString();
```

## Future Events

This contract will be extended with additional events:

- `tenant.updated` - Emitted when tenant details are modified
- `tenant.deleted` - Emitted when a tenant is deleted
- `tenant.suspended` - Emitted when a tenant is suspended

## Versioning

- **Main branch:** Stable versions (e.g., `1.0.0`, `1.1.0`)
- **Develop branch:** Snapshot versions (e.g., `1.0.0-SNAPSHOT`)

Breaking changes will increment the major version and may require a new Avro schema version (e.g., `v2`).

## Resources

- AsyncAPI Specification: `asyncapi.yml`
- Avro Schemas: `tenants-avro/v1/`
- Metadata: `metadata.yml`

## Support

For questions or issues, contact the ProactiveDevs team at `team@proactivedevs.com`.
