# ThreadIQ Backend Architecture

## Overview

ThreadIQ is an AI platform for fashion catalog intelligence. It is designed to ingest product data, enrich it with AI-generated descriptions and metadata, and support semantic search and downstream automation for fashion catalog workflows.

The backend currently provides a lightweight FastAPI foundation that supports versioned API routes, a service layer for business logic, repository abstractions for persistence, and SQLAlchemy models for database interaction. This structure is intentionally modular so the platform can grow toward more advanced AI orchestration and data-processing capabilities.

---

## Current Architecture

The current backend follows a layered architecture that separates API concerns from business logic and persistence.

FastAPI

↓

Router

↓

Service

↓

Repository

↓

SQLAlchemy

↓

PostgreSQL

### Components

- FastAPI
  - Provides the API surface for the application.
  - Handles request/response lifecycle and dependency injection.

- Router
  - Responsible for HTTP concerns only.
  - Maps incoming requests to service methods and returns serialized responses.

- Service Layer
  - Contains business rules and use-case orchestration.
  - Keeps application logic independent from HTTP and persistence details.

- Repository Layer
  - Encapsulates data access logic.
  - Abstracts storage behavior so the service layer does not depend on concrete data access implementations.

- SQLAlchemy
  - Provides ORM mapping, model definitions, and database interaction.
  - Supports maintainable persistence for the current application model layer.

- PostgreSQL
  - Serves as the relational persistence layer for production-style deployments.
  - Provides reliability, transactions, and integration readiness for future domain growth.

---

## Why Repository Pattern

The repository pattern is used to separate persistence logic from application behavior.

### Benefits

- Keeps database access isolated from business logic.
- Makes the service layer easier to test with mocks or alternative implementations.
- Reduces coupling to a specific storage engine.
- Allows the application to evolve from an in-memory demo to a real database-backed service without changing business logic.

In production systems, this pattern is valuable because persistence concerns often change over time. A repository boundary gives teams flexibility to swap implementations, add caching, or introduce a different database strategy without forcing broad architectural changes.

---

## Why Service Layer

The service layer exists to hold business rules and application use cases.

### Benefits

- Keeps routers thin and focused on HTTP concerns.
- Centralizes logic that would otherwise be duplicated across endpoints.
- Makes business behavior easier to test independently of the web framework.
- Preserves a clear separation between transport concerns and domain behavior.

Production systems rely on this separation because it makes the application easier to evolve. Business rules change more often than transport mechanisms, and keeping them in a dedicated layer reduces churn in the API layer.

---

## Why Dependency Injection

Dependency injection is used to construct and provide collaborators such as repositories and services in a consistent way.

### Benefits

- Improves testability by making dependencies replaceable.
- Reduces tight coupling between layers.
- Simplifies future integration of different implementations.
- Enables cleaner composition of the application runtime.

In production systems, dependency injection is critical because it makes the codebase easier to reason about, easier to test, and safer to evolve as features grow.

---

## Why API Versioning

The backend uses versioned API routes to preserve compatibility as the platform evolves.

### Benefits

- Allows the introduction of breaking changes without disrupting existing clients.
- Makes contract evolution explicit and manageable.
- Enables staged rollout of new API capabilities.

Production systems use versioning to protect integrations and simplify backward compatibility planning. As ThreadIQ grows, versioning will be important for maintaining stable interfaces for downstream clients and partner systems.

---

## Why UUID

UUIDs are used for identifiers to support distributed and future-scale data operations.

### Benefits

- Avoid collisions across systems and environments.
- Support distributed ingestion and multi-service workflows.
- Make entity identity safer in asynchronous and replicated environments.
- Reduce coupling to database-specific autoincrement behavior.

Production systems prefer UUIDs in distributed applications because they are more robust than integer identifiers when data is generated in multiple places or across service boundaries.

---

## Why Docker

Docker is used to provide a consistent deployment and development environment.

### Benefits

- Standardizes local development and production runtime behavior.
- Simplifies dependency management and onboarding.
- Makes service deployment more portable across environments.
- Helps ensure that the backend runs consistently with the expected runtime configuration.

Production systems rely on containerization to reduce environment drift and make deployments repeatable and reliable.

---

## Why Alembic

Alembic is used to manage database schema evolution over time.

### Benefits

- Tracks schema changes in a controlled and versioned way.
- Makes migrations reproducible across environments.
- Reduces risk when changing tables, indexes, and constraints.
- Supports long-term maintainability of the persistence layer.

Production systems use migration tools such as Alembic because schema changes are a critical part of application evolution and must be managed safely.

---

## Future Architecture

The current architecture is a foundation for a more advanced AI-driven catalog platform. Over time, the backend will expand to include background jobs, orchestrated AI agents, and intelligent retrieval services.

### Planned Components

- Jobs
  - Background workers for ingestion, enrichment, indexing, and processing tasks.
  - Will handle asynchronous work that should not block the API layer.

- Agent Orchestrator
  - Coordinates multi-step AI workflows across specialized agents.
  - Will manage sequencing, retries, dependency resolution, and results aggregation.

- Vision Agent
  - Processes product images and extracts visual features, attributes, and classification signals.
  - Will provide structured outputs for product enrichment and catalog intelligence.

- Validation Engine
  - Enforces business rules and data quality checks.
  - Will validate AI-generated outputs before they are persisted or used downstream.

- Description Agent
  - Generates enriched product descriptions and metadata from available content.
  - Will integrate with catalog pipelines and improve product discoverability.

- Embedding Service
  - Converts product data into vector representations for semantic comparison and retrieval.
  - Will support similarity search and intelligent ranking.

- Semantic Search
  - Provides retrieval over product content using embeddings and metadata.
  - Will enable more natural, intent-based search experiences for catalog data.

### Future Integration Model

The long-term architecture will evolve from the current layered API service into a hybrid design combining:

- synchronous API routes for user-facing operations,
- asynchronous background jobs for heavy processing,
- orchestrated AI workflows for enrichment and validation,
- vector-based retrieval for semantic search.

In this future model, the existing service and repository boundaries will remain valuable. Routers will continue to handle transport concerns, services will orchestrate business behavior, repositories will manage persistence, and new domain services will be introduced for AI workflows and search-related operations.

---

## Architectural Direction

ThreadIQ’s backend architecture is intended to remain modular, testable, and scalable. The current implementation establishes the base layers needed for future growth while keeping the codebase understandable and maintainable.

As the system grows, the architecture will continue to emphasize:

- clear separation of concerns,
- dependency inversion,
- robust persistence boundaries,
- asynchronous processing for heavy workloads,
- and extensible AI orchestration pipelines.
