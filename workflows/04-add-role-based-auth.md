# Workflow: Add role-based authorization on top of existing auth

## Problem
You have working authentication (workflow 03) but every logged-in user can currently do everything —
you need to restrict certain actions to certain roles.

## Investigation
List every route again, this time by required role: public, any-authenticated-user, specific-role-only,
or resource-owner-only (chapter 7's ownership dimension, distinct from role).

## Implementation
Add a `role` field to your user model. Build `require_role(*roles)` as a dependency factory (chapter 7).
Apply it per-route: `Depends(require_role(Role.admin))`. For ownership checks, compare the resource's
owner field against `current_user` inside the route or service, not just a role check.

## Testing
For every protected resource, test three cases explicitly: owner/correct-role succeeds, wrong role gets
403, unauthenticated gets 401. See chapter 7's `test_authz.py` for the pattern.

## Validation
Specifically test the IDOR case: can user A access/modify user B's resource by guessing/changing an ID
in the URL? This should be a 403 or 404, never a 200.

## Production considerations
Log authorization failures (403s) distinctly from 401s — a spike in 403s on a specific resource can
indicate someone probing for IDOR vulnerabilities, worth alerting on in a security-conscious system.
