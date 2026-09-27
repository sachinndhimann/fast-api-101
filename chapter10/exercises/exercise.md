# Exercise

Add a stricter limiter tier on `POST /auth/login` (ties to chapter 6), keyed by the *submitted
username* rather than IP, so rotating IPs doesn't let an attacker dodge the limit against one account.

## Interview-style scenario

Your rate limiter is per-IP, 100/minute. After a mobile carrier's IP pool gets flagged, legitimate users
behind that IP get blocked despite making far fewer requests each. What's happening, and what are two
fixes that don't just raise the limit?
