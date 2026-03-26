# Products REST API

OpenAPI contract for product management endpoints.

## Endpoints

- `POST /v1/products`: Create a new product for the current tenant.
- `GET /v1/products/barcode-types`: Retrieve available barcode type names.

## Notes

- Tenant is resolved from JWT claim `tenant_name`.
- `store_admin` role is required for product creation.
- Product `name` and `sku` are unique per tenant.
