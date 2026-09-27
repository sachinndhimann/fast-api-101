# Exercise

Add a test proving an empty `text` string is rejected (add a Pydantic `min_length=1` constraint if not
already enforced). Confirm this validation-error test needs no database or auth override to run.

## Interview-style scenario

A teammate asks: "why test against fake SQLite when we run real Postgres in production — couldn't tests
pass while the real thing is broken?" How do you respond, and where's the line on what SQLite-backed
tests should and shouldn't be trusted to catch?
