# TraceRoot

TraceRoot is an agentic AI incident investigation platform designed to investigate production incidents using evidence from logs, metrics, deployments, runbooks, and previous incidents.

## Problem

Production incident investigation often requires engineers to manually correlate information across multiple systems such as logs, monitoring platforms, deployment histories, and documentation.

TraceRoot aims to automate parts of this investigation while keeping conclusions grounded in collected evidence.

## Core Workflow

Incident
→ Triage
→ Investigation Planning
→ Evidence Collection
→ Hypothesis Generation
→ Hypothesis Verification
→ Root Cause Report

## Planned Architecture

- React + TypeScript frontend
- FastAPI backend
- LangGraph investigation workflow
- LLM tool calling and structured outputs
- PostgreSQL
- pgvector for incident/runbook retrieval
- Observability and tracing
- Automated evaluation
- Docker

## Engineering Principles

- Evidence-first AI reasoning
- Structured and validated data
- Explicit agent state
- Tool-based access to external information
- Separation of deterministic application logic and LLM reasoning
- Testable components
- Observable agent execution

## Current Status

### Day 1

Completed:

- Project architecture initialized
- FastAPI application created
- Health endpoint implemented
- Pydantic domain schemas created
- Incident model
- Evidence model
- Hypothesis model
- InvestigationState model
- Schema validation
- Automated tests

Current test suite:

`7 passed`

## Development

Backend:

```bash
cd backend
uvicorn app.main:app --reload