# Project: Backend Operations Platform

This project is a high-reliability infrastructure layer designed to handle the "heavy lifting" of a SaaS application. Instead of focusing on simple data entry, it prioritizes **distributed system integrity**, **idempotency**, and **financial accuracy**.

---

## ## Core Capabilities

### 1. Reliable Background Job Processing
The system moves time-consuming or unreliable tasks out of the request-response cycle to ensure high availability.
* **Retry Policies:** Implementation of exponential backoff for transient failures.
* **Dead Letter Queues (DLQ):** Failed jobs are archived for manual inspection after reaching maximum retries.
* **Idempotency:** Unique keys ensure that if a job is triggered twice, the side effect only occurs once.

### 2. Usage-Based Billing (Wallet + Ledger)
A robust financial model that ensures no transaction is lost or double-counted.
* **The Ledger:** An append-only table recording every single transaction (debits/credits). This is the immutable "source of truth."
* **The Wallet:** Represents the current balance, derived from ledger entries or cached for performance.
* **Atomic Transactions:** Utilizing database-level ACID properties to ensure that "deducting credits" and "executing a job" are treated as a single unit of work.



### 3. Admin & Observability Dashboard
A centralized management view for operators to monitor the health of the system.
* **Job Metrics:** Tracking success/failure rates and processing latency.
* **Usage Logs:** Real-time visibility into which users or API keys are consuming resources.
* **Manual Intervention:** Interfaces to re-run failed jobs or adjust ledger balances.

---

## ## Technical Architecture

The platform uses a "Producer-Consumer" pattern backed by a persistent database and a high-speed message broker.

| Component | Technology | Responsibility |
| :--- | :--- | :--- |
| **API Layer** | **FastAPI** | Handles job submission, rate limiting, and dashboard queries. |
| **Message Broker** | **Redis** | Acts as the high-speed transport/queue for pending jobs. |
| **Task Queue** | **Celery / RQ** | Manages distributed worker processes and retry logic. |
| **Primary Database** | **PostgreSQL** | Stores the Ledger, Job States, and User Wallets. |
| **Frontend** | **React** | Visualizes system health, job status, and usage graphs. |



---

## ## Engineering Focus Areas

* **Fault Tolerance:** How the system recovers if a worker crashes mid-task (using ACKs to ensure the job is returned to the queue).
* **Concurrency Control:** Using PostgreSQL row-level locking to prevent "double-spending" when multiple jobs finish simultaneously.
* **Observability:** Implementing structured logging and health checks to detect bottlenecks before they impact users.

---

## ## Learning Objectives
1.  **Distributed Logic:** Solving the "at-least-once" vs "exactly-once" delivery challenge.
2.  **State Management:** Moving beyond CRUD to manage complex state transitions (e.g., `Pending` → `Processing` → `Success/Failure`).
3.  **Financial Integrity:** Implementing the same design patterns used by major providers like Stripe or AWS for usage tracking.
