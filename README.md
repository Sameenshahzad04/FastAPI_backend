# FastAPI Learning Repository

A collection of FastAPI examples, tutorials, and sample projects built for learning and experimentation.

## What this repo contains

- `chat_App`
  - A sample FastAPI project directory included in the workspace.
  - Contains a modern FastAPI app structure with routers, database setup, static files, and templates.

- `Projects`
  - A set of day-by-day FastAPI examples covering common backend patterns and learning exercises.
  - Topics include:
    - JWT authentication
    - Alembic migrations
    - pagination
    - path, cookie, query, and request body handling
    - multi-tenant API design
    - payment integration
    - Redis usage
    - WebSockets and real-time flows
    - roles, subtasks, and organization model design
    - email notification workflows
    - search/query handling
    - WebRTC

- `doc_training`
  - Notes and training material related to the FastAPI examples in this workspace.

## Repo structure

- `chat_App/`
  - `project/` — FastAPI app source code and routing logic
  - `requirements.txt` — dependencies for the sample app
  - `.env` — environment configuration file
  - `alembic.ini` — migration settings for database schema changes

- `Projects/`
  - `Day_6_alembic/`
  - `Day_7_pagination/`
  - `Day_8_path_cookies/`
  - `Day_9_org_impl/`
  - `Day_10_Multi_tenant_api/`
  - `Day_11_search_query/`
  - `Day_12_super_admin_imp/`
  - `Day_13_Payment_integration/`
  - `Day_14_Payment_integration_2/`
  - `Day_15_roles2_task/`
  - `Day_16_roles2_subtasks/`
  - `Day_17_Email_notification/`
  - `Day_18_redis/`
  - `Day_19_redis_better_code/`
  - `Day_20_websocket/`
  - `Day_21_Websocket2_starting_concpet/`
  - `Day_22_webRTC/`

## Notes

- This repository is intended as a learning resource, not a production system.
- Each example is generally self-contained, with its own structure and dependencies.
- Use the folder names and code examples as references when building your own FastAPI applications.

## Recommended next steps

- Explore the folder structure under `Projects/` to find topic-focused examples.
- Inspect `chat_App/project/` for a sample FastAPI application layout.
- Run the sample apps locally with `uvicorn` to review API behavior and implementation details.
