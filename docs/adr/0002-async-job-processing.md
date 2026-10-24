# ADR-0002: Asynchronous job processing

- **Status:** Accepted when the DIP-6 pull request is merged (team approval)
- **Date:** 2026-10-23

## Context
Analysis of a video takes much longer than a normal HTTP request. See [05](../05-technology-comparison.md) D5.

## Decision
REST API enqueues jobs in Redis; a separate worker (RQ) executes them; progress is pushed to the browser by Server-Sent Events.

## Consequences
+ Requests stay fast; failures are isolated in the worker; jobs can be cancelled.
− Adds Redis to the deployment; mitigate with `docker compose`.
− For an early prototype FastAPI BackgroundTasks may be used and replaced later behind the same job interface.
- Browsers cannot call gRPC directly and need a translating proxy (gRPC-Web with Envoy); SSE over plain HTTP avoids that.
- Package licences: `rq` 2.12.0 BSD-2-Clause, `redis` client 8.1.0 MIT.
