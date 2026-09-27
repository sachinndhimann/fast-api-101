# Exercise

Add password reset: `POST /auth/forgot-password` issues a short-lived single-use token (a `type:
"reset"` JWT, or a random server-side token); `POST /auth/reset-password` consumes it and updates the
hash. Make sure a reset token can't double as an access token.

## Interview-style scenario

A user's account was accessed from an unfamiliar country hours after they changed their password. Why
might a JWT-based system still let the old session through, and what would you add to prevent it?
