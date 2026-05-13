# Self-Defending GPT: System Architecture

This document outlines the complete system architecture for Self-Defending GPT, an AI-powered security gateway for Large Language Model (LLM) applications.

## 1. Guiding Principles

- **Security First**: Every request and response is untrusted and must be sanitized.
- **Defense in Depth**: Multiple layers of security controls (prevent, detect, respond).
- **Real-time Analysis**: Sub-second latency for security pipelines to avoid impacting user experience.
- **Zero Trust**: Trust is not static; it's continuously calculated based on behavior.
- **High-Fidelity Audits**: Every decision made by the gateway is logged for forensics.

## 2. System Overview

The system is a proxy that sits between users and LLMs. It inspects traffic, applies security policies, and provides a real-time dashboard for Security Operations Center (SOC) analysts.

- **Frontend**: A Next.js application for the SOC dashboard and administrative controls.
- **Backend**: A FastAPI application serving the core security pipeline and API.
- **Database**: MongoDB Atlas for storing all operational and analytical data.
- **LLM Integration**: NVIDIA Nemotron API for advanced threat analysis and content moderation.
- **Deployment**: Vercel for the frontend, Render for the backend.

![System Flow](https://i.imgur.com/example.png) <!-- Placeholder for a diagram -->

---

## 3. Backend Architecture (FastAPI)

The backend is a modular FastAPI application responsible for all core logic.

### Modules:

- **`api`**: Defines all public-facing API endpoints, handles request/response validation (Pydantic).
- **`security`**: The core security pipeline.
    - **`analyzer`**: Contains modules for analyzing and sanitizing prompts and LLM responses.
    - **`decision`**: The policy engine that decides whether to `ALLOW`, `BLOCK`, or `TRANSFORM` a request/response.
    - **`redaction`**: Services for redacting PII and other sensitive data.
- **`trust`**: Manages the trust scoring engine.
    - Calculates, updates, and decays trust scores for users and sessions.
- **`llm`**: A dedicated client for interacting with the NVIDIA Nemotron API.
    - Manages API keys, handles retries, and formats requests for security analysis.
- **`memory`**: Manages conversation history and context securely.
- **`analytics`**: Ingests events from the pipeline and aggregates them for the SOC dashboard.
- **`core`**: Shared components like database connections, logging configuration, and application settings.

---

## 4. Frontend Architecture (Next.js)

The frontend is a dashboard and management UI for SOC analysts and administrators.

### Pages:

- **`/dashboard`**: The main SOC dashboard showing real-time threat activity, KPIs, and system status.
- **`/threats`**: A detailed, filterable log of all detected security incidents.
- **`/trust`**: Visualization of user and session trust scores over time.
- **`/policies`**: An interface for viewing, creating, and managing security policies.
- **`/audit`**: An immutable log viewer for all significant system and user actions.
- **`/admin`**: Workspace for managing users, roles, and API keys.

---

## 5. Database Collections (MongoDB Atlas)

- **`users`**: User profiles, roles, and authentication metadata.
- **`sessions`**: Records of user sessions, including client fingerprints and risk state.
- **`messages`**: Stores all prompts and LLM responses, along with their security analysis metadata.
- **`policies`**: Security rule definitions, version history, and activation status.
- **`incidents`**: A log of all detected threats, including classification, severity, and associated message/session.
- **`trust_scores`**: Time-series data of trust scores for each user/session.
- **`audit_logs`**: Immutable, append-only log for critical actions (e.g., policy changes, user role updates).
- **`analytics_aggregates`**: Pre-computed data to power the dashboard visualizations (e.g., hourly threat counts).

---

## 6. Security Pipeline Flow

This is the core of the "Self-Defending" capability.

1.  **Input Normalization**: The raw prompt is cleaned (e.g., strip control characters, normalize Unicode).
2.  **Heuristic Analysis**: Fast checks for known attack patterns (e.g., SQLi, XSS, prompt injection signatures).
3.  **AI-Powered Analysis**: If heuristics are inconclusive, the prompt is sent to a fine-tuned NVIDIA Nemotron model for deeper threat analysis (e.g., detecting novel jailbreak attempts, social engineering).
4.  **Policy Decision**: The `decision` engine evaluates findings against active policies. The outcome is one of:
    - `ALLOW`: The prompt is safe.
    - `BLOCK`: The prompt is malicious and is blocked. An incident is logged.
    - `TRANSFORM`: The prompt is modified (e.g., PII redacted) before being sent to the LLM.
5.  **LLM Interaction**: The (potentially transformed) prompt is sent to the application's primary LLM.
6.  **Output Analysis**: The LLM's response is analyzed for toxicity, data leakage, and policy violations.
7.  **Final Decision**: The response is either sent to the user, filtered, or blocked.
8.  **Logging & Scoring**: All data and decisions from the pipeline are logged, and the user's trust score is updated.

---

## 7. Trust Score Flow

The trust score is a real-time metric representing the system's confidence in a user or session.

1.  **Initialization**: A new session starts with a baseline trust score (e.g., 90/100).
2.  **On Event**: Every prompt/response pair is an event.
    - **Negative Signals**: Malicious prompts, policy violations, or toxic outputs decrease the score. The magnitude of the decrease depends on the severity of the finding.
    - **Positive Signals**: A consistent stream of safe interactions causes the score to gradually recover towards the baseline.
3.  **Thresholds**:
    - **High Trust (e.g., > 80)**: Normal operation.
    - **Medium Trust (e.g., 40-80)**: Stricter security policies are applied; prompts may face more scrutiny.
    - **Low Trust (e.g., < 40)**: Rate limiting is applied. Only very safe prompts are allowed.
    - **Zero Trust (e.g., < 10)**: The session is temporarily blocked. An alert is sent to the SOC.

---

## 8. SOC Dashboard Flow

The dashboard provides at-a-glance visibility into the system's security posture.

1.  **Data Ingestion**: The FastAPI backend's `analytics` module receives events from the security pipeline.
2.  **Aggregation**: A background worker (or MongoDB Atlas Trigger) runs periodically to process raw events from `incidents` and `messages` into `analytics_aggregates`.
3.  **API Layer**: The FastAPI backend exposes dedicated, read-only endpoints (e.g., `/api/analytics/overview`).
4.  **Frontend Visualization**: The Next.js dashboard pages fetch data from the analytics endpoints and render it using charting libraries (e.g., Recharts). The dashboard uses Server-Side Rendering (SSR) or Incremental Static Regeneration (ISR) to stay fresh.

---

## 9. Deployment Architecture

- **Frontend (Next.js)**:
    - **Host**: Vercel.
    - **Process**: `git push` to the `main` branch triggers an automatic build and deployment.
    - **Features**: Global CDN, Edge Functions for middleware, automatic SSL.
- **Backend (FastAPI)**:
    - **Host**: Render.
    - **Process**: Deployed as a Docker container. A `render.yaml` file in the repo defines the service. `git push` triggers a new Docker build and a zero-downtime deployment.
    - **Features**: Autoscaling based on CPU/memory, managed PostgreSQL/Redis, private networking to connect to other Render services.
- **Database (MongoDB Atlas)**:
    - **Configuration**: Deployed as a serverless or provisioned cluster.
    - **Security**: Network access is restricted to the Render backend's outbound IP addresses and Vercel's function IPs. VPC peering is used for a more secure connection if available on the plan.
- **CI/CD**:
    - **Provider**: GitHub Actions.
    - **Workflow**: On every push, run linters, and unit tests. On merge to `main`, trigger deployments to Vercel and Render.
