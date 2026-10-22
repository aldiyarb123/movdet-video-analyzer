# ADR-0002: Asynchronous job processing

- **Status:** Proposed
- **Date:** 2026-10-23

## Context
Analysis of a video takes much longer than a normal HTTP request. See [05](../05-technology-comparison.md) D5.

## Decision
REST API enqueues jobs in Redis; a separate worker (RQ) executes them; progress is pushed to the browser by Server-Sent Events.

## Consequences
+ Requests stay fast; failures are isolated in the worker; jobs can be cancelled.
− Adds Redis to the deployment; mitigate with `docker compose`.
− For an early prototype FastAPI BackgroundTasks may be used and replaced later behind the same job interface.
