Project Name: Backend Operations Platform

Description:
I am building a production-grade backend platform that provides three core capabilities used by real SaaS systems:

Reliable background job processing (with retries and failure handling)

Usage-based billing using a wallet + ledger model

Admin visibility into jobs, failures, and usage through APIs and a dashboard

The platform will expose APIs for submitting jobs, tracking their execution, enforcing rate limits, recording usage costs, and maintaining accurate ledger entries.

The system is intentionally not a CRUD app. It focuses on correctness under failure, idempotency, retry logic, and observability.

Tech stack: FastAPI (Python), PostgreSQL, Redis, background workers (Celery/RQ), React for dashboard.

Goal: Learn and demonstrate real backend system fundamentals like async processing, fault tolerance, billing accuracy, and system design.