# Workflow: Extract a module from a modular monolith into its own service

## Problem
One module (e.g. Payments, chapter 17) needs to scale, deploy, or be owned independently of the rest of
the monolith, and you've decided (chapter 19) the trade-off is worth it for this specific module.

## Investigation
Confirm the module's boundary is actually clean: does anything else `import` directly from this module's
internals rather than calling its public function/API surface? Does it share database tables with other
modules in ways that would break if it had its own database?

## Implementation
1. Stand up the new service with the module's code, its own database (migrate its tables out).
2. Replace the in-process function call from other modules with an HTTP client call to the new service
   (chapter 18's pattern), including a timeout and basic error handling for "service unavailable."
3. Keep the monolith's old code path behind a feature flag briefly, so you can roll back to the
   in-process call if the new service has problems.

## Testing
Test the new service in isolation (its own test suite, chapter 23's patterns). Test the calling
module's new HTTP-based integration, including the failure case (new service down → appropriate error,
not a hang — chapter 21's resilience patterns).

## Validation
Run both the old and new code paths in parallel against production-like traffic (shadow testing) if
feasible, comparing outputs, before fully cutting over.

## Production considerations
Add observability (chapter 22) for the new service from day one — you're introducing a new failure mode
(network calls where function calls used to be) and need to see it clearly, not discover it via a
customer-reported incident.
