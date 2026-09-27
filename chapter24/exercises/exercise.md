# Exercise

Add a third vulnerability pair: an endpoint taking a `redirect_url` query param that redirects the user
there (open redirect). Fix it by validating against an allowlist of your own domain(s).

## Interview-style scenario

Your ORM-based code is safe from classic SQL injection. A new "sort by" query param builds an `ORDER BY
{column_name}` clause dynamically since the ORM doesn't parameterize column names cleanly. What's the
risk, and how do you fix it without losing dynamic sorting?
