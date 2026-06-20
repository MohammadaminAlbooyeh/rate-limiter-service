# Architecture

## Overview

The rate limiter service uses a middleware-based architecture. Each request flows through identity extraction, rule matching, algorithm execution, and decision.

## Components

- **Middleware**: Intercepts HTTP requests
- **Algorithm Layer**: Pluggable rate limiting algorithms
- **Storage Layer**: Redis or in-memory backends
- **Rule Engine**: Matches requests to rate limit rules
- **API Layer**: REST endpoints for management
- **Frontend**: React dashboard

## Data Flow

Request → Identity Extraction → Rule Matching → Algorithm Check → Allow/Block
