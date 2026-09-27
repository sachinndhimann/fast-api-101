# Workflow: Design a REST API for a new resource

## Problem
You're adding a new resource (e.g. "Invoices") and need to decide its URL structure, methods, and status
codes before writing any code, so the API is consistent with the rest of your system (chapter 2).

## Investigation
List the operations you actually need: list, read one, create, update (full or partial?), delete,
any custom actions (e.g. "send invoice", "mark paid")? Custom actions are often better modeled as
sub-resources (`POST /invoices/{id}/send`) than as verbs in the main path.

## Implementation
```
GET    /invoices              list, with pagination + filtering
GET    /invoices/{id}         read one
POST   /invoices              create
PATCH  /invoices/{id}         partial update
DELETE /invoices/{id}         remove
POST   /invoices/{id}/send    custom action, modeled as a sub-resource
```
Define Pydantic schemas: separate `InvoiceCreate`, `InvoiceUpdate` (all fields optional), and
`InvoiceOut` (chapter 1) — resist the urge to reuse one model for all three.

## Testing
Write the OpenAPI-facing tests first (status codes, required fields) before the implementation, if your
team practices anything TDD-adjacent — the design should survive contact with a test written purely from
the API contract, before real logic exists.

## Validation
Check against chapter 2's checklist: nouns not verbs in the URL, correct status codes per method,
pagination on the list endpoint, a consistent error envelope (chapter 9) for all failure cases.

## Production considerations
Decide your versioning approach (chapter 2) for this resource now, even if you don't need it yet —
retrofitting `/v1/` prefixes after external clients exist is a breaking, coordinated change.
