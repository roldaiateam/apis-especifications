---
name: api-sse-endpoint
description: Generate SSE (Server-Sent Events) streaming endpoints with text/event-stream content type, polling fallback, event schemas, and reconnection support.
---

# Skill: SSE (Server-Sent Events) Endpoint

## Purpose

This skill generates **SSE streaming endpoints** using `text/event-stream` content type. It covers the full SSE pattern: streaming GET endpoint, polling fallback endpoint, event schemas, reconnection via `Last-Event-ID`, and gap-free sync via timestamp parameters.

The Provisioning API in this repo already has a status-check endpoint (`GET /v1/tenants/status`) that returns provisioning state. This skill extends that concept into a full SSE streaming pattern.

## When to Use

- Real-time updates to the frontend (provisioning progress, order status, inventory changes)
- Long-running operations where the client needs progress feedback
- Event-driven UIs that need push notifications without WebSocket complexity

## File Locations

```
<resource>/rest/v1/
├── services/<resource>/
│   ├── <resource>-events.yml          ← SSE streaming endpoint
│   └── <resource>-status.yml          ← polling fallback endpoint
└── components/<resource>/
    └── components.yml                 ← event schemas added here
```

Root spec additions:

```yaml
paths:
  /v1/<resource>/events:
    $ref: './v1/services/<resource>/<resource>-events.yml'
  /v1/<resource>/status:
    $ref: './v1/services/<resource>/<resource>-status.yml'
```

---

## SSE Endpoint Pattern

SSE endpoints use `GET` with `text/event-stream` content type. The connection remains open and the server pushes events as they occur.

### Key design decisions

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| HTTP method | GET | SSE standard; EventSource API requires GET |
| Content type | `text/event-stream` | SSE specification requirement |
| Reconnection | `Last-Event-ID` header | Built into browser EventSource API |
| Gap recovery | `since` query parameter | Allows clients to replay missed events |
| Subscription filter | Query parameters | Filter which events to receive |

---

## Event Schema

Define a typed event schema for the domain:

```yaml
<Resource>StatusEvent:
  type: object
  description: >
    A single event in the <resource> event stream.
    Sent as the `data` field of an SSE message.
  required:
    - eventId
    - eventType
    - timestamp
  properties:
    eventId:
      type: string
      description: Unique identifier for this event. Used as SSE `id` field for reconnection.
      example: "evt-00042"
    eventType:
      type: string
      description: Type of the event.
      enum:
        - <RESOURCE>.CREATED
        - <RESOURCE>.UPDATED
        - <RESOURCE>.DELETED
        - <RESOURCE>.STATUS_CHANGED
      example: "<RESOURCE>.STATUS_CHANGED"
    timestamp:
      type: string
      format: date-time
      description: ISO 8601 timestamp of when the event occurred.
      example: "2026-02-18T10:12:05Z"
    data:
      type: object
      description: Event-specific payload. Structure depends on eventType.
      additionalProperties: true
```

### Event stream format (SSE wire format)

The actual wire format for SSE events is:

```
id: evt-00042
event: provisioning.update
data: {"status":"IN_PROGRESS","progress":40,"currentStep":"INVENTORY_SCHEMA_CREATED","timestamp":"2026-02-18T10:12:05Z"}

id: evt-00043
event: provisioning.complete
data: {"status":"COMPLETED","progress":100,"completedAt":"2026-02-18T10:12:10Z","timestamp":"2026-02-18T10:12:10Z"}

```

> Each event block is separated by a blank line. The `id` field enables automatic reconnection.

---

## Complete Template: SSE Streaming Service File (`<resource>-events.yml`)

```yaml
get:
  tags:
    - <Resource>
  summary: Subscribe to <resource> events (SSE)
  description: >
    Opens a Server-Sent Events stream for real-time <resource> updates.
    The connection remains open and the server pushes events as they occur.

    **Reconnection**: If the connection drops, the client should reconnect
    with the `Last-Event-ID` header set to the last received event ID.
    The server will replay any missed events.

    **Gap recovery**: Use the `since` query parameter to receive all events
    after a specific timestamp, useful for initial sync or catching up.

    **Heartbeat**: The server sends a comment line (`:heartbeat`) every 30 seconds
    to keep the connection alive through proxies and load balancers.
  operationId: subscribeTo<Resource>Events
  parameters:
    - name: since
      in: query
      required: false
      description: >
        ISO 8601 timestamp. Only events occurring after this timestamp will be sent.
        Used for initial sync or gap recovery after reconnection.
      schema:
        type: string
        format: date-time
      example: "2026-02-18T10:00:00Z"
    - name: Last-Event-ID
      in: header
      required: false
      description: >
        ID of the last received event. Set automatically by the browser EventSource API
        on reconnection. The server replays all events after this ID.
      schema:
        type: string
      example: "evt-00042"
  responses:
    '200':
      description: Event stream established
      content:
        text/event-stream:
          schema:
            type: string
            description: >
              SSE event stream. Each event has the format:
              id: <eventId>
              event: <eventType>
              data: <JSON payload>
          example: |
            id: evt-00042
            event: <resource>.status_changed
            data: {"status":"IN_PROGRESS","progress":40,"timestamp":"2026-02-18T10:12:05Z"}

            id: evt-00043
            event: <resource>.status_changed
            data: {"status":"COMPLETED","progress":100,"timestamp":"2026-02-18T10:12:10Z"}
    '400':
      $ref: '../../components/errors/components.yml#/components/responses/BadRequest'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Complete Template: Polling Fallback Service File (`<resource>-status.yml`)

For clients that cannot use SSE (mobile apps, batch jobs), provide a polling endpoint:

```yaml
get:
  tags:
    - <Resource>
  summary: Get current <resource> status
  description: >
    Returns the current state of the <resource> as a snapshot.
    Use this as a polling fallback when SSE is not available.
    Includes a `timestamp` field for gap-free sync with the event stream.
  operationId: get<Resource>Status
  parameters:
    - name: <resource>Id
      in: path
      required: true
      description: Unique identifier of the <resource> to check status for.
      schema:
        $ref: '../../components/<resource>/components.yml#/components/schemas/<Resource>Id'
  responses:
    '200':
      description: Current status retrieved successfully
      content:
        application/json:
          schema:
            $ref: '../../components/<resource>/components.yml#/components/schemas/<Resource>StatusSnapshot'
    '401':
      $ref: '../../components/errors/components.yml#/components/responses/Unauthorized'
    '403':
      $ref: '../../components/errors/components.yml#/components/responses/Forbidden'
    '404':
      $ref: '../../components/errors/components.yml#/components/responses/NotFound'
    '500':
      $ref: '../../components/errors/components.yml#/components/responses/InternalServerError'
```

## Snapshot Schema (for polling endpoint)

```yaml
<Resource>StatusSnapshot:
  type: object
  description: >
    Current state snapshot of the <resource>.
    The `timestamp` field allows clients to transition from polling to SSE
    by passing it as the `since` parameter when subscribing to events.
  required:
    - status
    - timestamp
  properties:
    status:
      type: string
      description: Current status of the <resource>.
      enum:
        - PENDING
        - IN_PROGRESS
        - COMPLETED
        - FAILED
      example: "IN_PROGRESS"
    progress:
      type: integer
      format: int32
      description: Progress percentage (0-100).
      minimum: 0
      maximum: 100
      example: 40
    currentStep:
      type: string
      description: Human-readable description of the current processing step.
      example: "INVENTORY_SCHEMA_CREATED"
    startedAt:
      type: string
      format: date-time
      description: When the process started.
      example: "2026-02-18T10:12:03Z"
    completedAt:
      type: string
      format: date-time
      nullable: true
      description: When the process completed. Null if not yet completed.
      example: null
    errorMessage:
      type: string
      nullable: true
      description: Error details if status is FAILED.
      example: null
    timestamp:
      type: string
      format: date-time
      description: >
        Server timestamp of this snapshot. Use as the `since` parameter
        when transitioning to SSE to ensure no events are missed.
      example: "2026-02-18T10:12:05Z"
```

---

## Heartbeat and Timeout Guidance

### Heartbeat

The server should send a comment line every 30 seconds to prevent connection timeout:

```
:heartbeat

```

This is a single line starting with `:` followed by a blank line. It is ignored by SSE clients but keeps the TCP connection alive through proxies.

### Timeout considerations

| Component | Recommended timeout | Notes |
|-----------|-------------------|-------|
| Server-side connection | 5 minutes max | Close and let client reconnect |
| Proxy/load balancer | > 30 seconds | Must be longer than heartbeat interval |
| Client reconnection delay | 3 seconds default | Browser EventSource handles this automatically |

---

## Security Considerations for Long-lived Connections

- **JWT expiration**: Long-lived SSE connections may outlive the JWT token. The server should validate the token periodically and close the connection with a specific event if expired:
  ```
  event: auth.expired
  data: {"message":"Token expired, please reconnect with a fresh token"}
  ```
- **Rate limiting**: Limit the number of concurrent SSE connections per tenant
- **Resource cleanup**: Always close server-side resources when the client disconnects

---

## Anti-patterns

| Do NOT | Do instead |
|--------|------------|
| Use POST for SSE endpoints | Use GET (required by EventSource API) |
| Return `application/json` for SSE | Use `text/event-stream` |
| Skip the `id` field in events | Always include `id` for reconnection support |
| Send events without heartbeat | Send `:heartbeat` comment every 30 seconds |
| Ignore `Last-Event-ID` header | Replay missed events on reconnection |
| Keep connections open forever | Set max connection lifetime (5 min) and let clients reconnect |
| Put SSE schemas in the error components file | SSE event schemas go in the domain components file |
| Use SSE for large data transfers | SSE is for small event payloads; use REST for bulk data |
| Forget to provide a polling fallback | Always create a status endpoint for non-SSE clients |
