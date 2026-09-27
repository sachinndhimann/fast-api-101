# Chapter 24 — Security

## Concept

A tour of the most common API vulnerabilities, each shown as a working exploit against intentionally
insecure code, then fixed — because a vulnerability described only in prose is easy to underestimate.

## Why it exists

Security bugs are unusual in that they're often invisible until actively exploited — a SQL injection
bug can sit in production for years with zero visible symptoms until someone finds it. Seeing an actual
exploit succeed against real (if intentionally bad) code is what makes "always use parameterized
queries" feel like a rule with teeth, not a suggestion.

## SQL injection — demonstrated as a real exploit

`app/vulnerable.py`'s `vulnerable_get_user_by_name` builds SQL via an f-string. `app/tests/test_security.py`
proves the vulnerability with an actual attack:

```python
payload = "nonexistent' OR '1'='1"
rows = vulnerable_get_user_by_name(db, payload)
assert len(rows) == 2   # BOTH users returned, despite querying for a name matching neither
```

The payload turns `WHERE name = '...'` into `WHERE name = 'nonexistent' OR '1'='1'` — always true,
returning every row. `app/fixed.py`'s parameterized version (`conn.execute(query, (name,))`) sends the
payload as **data**, never as SQL syntax, and the same test against it correctly returns zero rows.

```bash
cd chapter24
PYTHONPATH=. pytest app/tests -v
```

## Password security

Chapter 6 already does this correctly (bcrypt hashing). Here, `app/vulnerable.py`'s
`vulnerable_password_check` compares stored **plaintext** directly — the vulnerability isn't in the
comparison logic itself, it's that a plaintext password exists in storage at all. One database leak
means every password is immediately usable with no cracking required. `app/fixed.py` hashes with bcrypt,
so a leaked hash requires (expensive, slow-by-design) brute-forcing to recover the original.

## CORS misconfiguration

```python
VULNERABLE_CORS_CONFIG = {"allow_origins": ["*"], "allow_credentials": True}   # see chapter 8
FIXED_CORS_CONFIG = {"allow_origins": ["https://app.example.com"], "allow_credentials": True}
```

`"*"` with credentials allowed is exactly the misconfiguration chapter 8 flags — browsers actually
reject this combination per spec in well-behaved clients, but relying on browser enforcement alone,
rather than being explicit, is fragile and has historically had inconsistent enforcement across
browsers/proxies.

## Other vulnerability classes to know

- **JWT vulnerabilities**: accepting `alg: none` (an unsigned token) if your JWT library isn't
  configured to reject it explicitly; using a weak/guessable signing secret (chapter 6).
- **Secrets in code/version control**: this course's own `chapter6/app/security.py` has a hardcoded
  `SECRET_KEY` marked clearly as dev-only — in real code, secrets come from environment variables or a
  secrets manager, never a committed file.
- **CSRF**: relevant specifically when using cookie-based auth (chapter 6's cookie-vs-localStorage
  discussion) — a browser auto-sends cookies, so state-changing endpoints need CSRF tokens or
  `SameSite` cookie attributes.
- **SSRF (Server-Side Request Forgery)**: if your API fetches a URL provided by user input (e.g. "import
  from this URL" features), an attacker can point it at internal-only services (`http://169.254.169.254`
  cloud metadata endpoints, internal admin panels) that aren't meant to be internet-reachable — validate
  and restrict destination URLs.
- **Rate limiting** (chapter 10) as a security control, not just a performance one — it's your primary
  defense against credential-stuffing and brute-force attacks on auth endpoints.
- **Input validation** (chapter 1's Pydantic models) as a security boundary, not just a UX nicety —
  strict types and length limits reject a large class of malformed/malicious input before it reaches
  business logic at all.
- **Security headers**: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`,
  `Content-Security-Policy` — cheap to add via middleware (chapter 8), meaningfully reduce several attack
  classes.
- **Dependency vulnerabilities**: run `pip-audit` or similar in CI — a vulnerability in a transitive
  dependency is exploitable regardless of how careful your own code is.
- **API abuse**: scraping, credential stuffing, automated account creation — rate limiting (chapter 10)
  plus CAPTCHA/behavioral signals for the highest-risk endpoints.

## Common mistakes

- Believing "we use an ORM, so we're safe from SQL injection" — true only if you never drop to raw SQL
  with string formatting for a "quick" query, which happens under time pressure more often than teams
  admit.
- Rolling your own crypto/hashing instead of using a maintained library (`passlib`, standard JWT
  libraries) — cryptographic code has failure modes that are easy to get subtly, dangerously wrong.
- Treating security as a final "hardening pass" before launch instead of a property enforced continuously
  — most of this chapter's fixes are cheaper to build in from the start than to retrofit later.

## Production considerations

- Automate what you can: dependency scanning in CI, static analysis for common injection patterns,
  secret-scanning pre-commit hooks to catch accidentally committed credentials.
- Assume breach for defense-in-depth: hashed passwords, parameterized queries, and rate limiting are each
  independently valuable — a system with all three survives a single point of failure in a way a system
  relying on just one control doesn't.

## Exercise

Add a third vulnerability pair to this file: an endpoint that takes a `redirect_url` query parameter and
redirects the user there (open redirect vulnerability), then fix it by validating the URL against an
allowlist of your own domain(s).

## Interview-style scenario

> "Your team's ORM-based code is safe from classic SQL injection. A new feature adds a 'sort by' query
> parameter that's used to build an `ORDER BY {column_name}` clause dynamically, since the ORM doesn't
> cleanly support parameterizing column names. What's the risk here, and how would you fix it without
> giving up the dynamic sorting feature?"
