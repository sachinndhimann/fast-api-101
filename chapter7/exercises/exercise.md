# Exercise

Add `PATCH /profiles/{email}`: users edit their own bio; managers edit any teammate's; admins edit
anyone's. Compose this from dependencies rather than one large `if` chain.

## Interview-style scenario

`GET /invoices/{id}` checks role >= accountant but not company ownership. A support employee at Company
A requests an ID from Company B and sees its data. What class of bug is this, and where should the fix
live — route, service, or query?
