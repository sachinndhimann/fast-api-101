# Exercise

Add a `/ready` check for a message-queue connection (a third `DependencyStatus` flag). Write a test
proving a queue outage alone (DB and cache healthy) flips readiness to `False` while liveness stays
unaffected.

## Interview-style scenario

A service's liveness AND readiness probes both point at the same DB-checking endpoint. During a 10-minute
DB blip, what happens to its running Kubernetes instances, and how is that worse than correctly
separated endpoints?
