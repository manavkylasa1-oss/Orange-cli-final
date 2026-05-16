# Orange-cli-final
This repository contains the Assignment 4 implementation of the portfolio management API built on Flask and Flask-SQLAlchemy.

The project now follows a production-style request flow where each HTTP request acts as a transactional boundary. Database changes are made in the service layer, flushed as needed, and committed only at the route layer after successful completion. Failures are handled through centralized Flask error handlers so that invalid requests and runtime errors return consistent API responses and do not leave partial writes behind.

The application includes:
- Pydantic validation for request bodies with structured `422` error responses
- a dedicated trade service with `POST /trades/buy` and `POST /trades/sell`
- live Alpha Vantage integration for security lookup and pricing
- Flask-Caching to reduce repeated external API calls
- AWS Cognito OIDC authentication for protected routes
- portfolio-level authorization with owner, viewer, and manager roles
- repaired and expanded pytest coverage for validation, auth, authz, trading, and caching behavior

Testing was updated to use a Flask app context with in-memory SQLite and mocked external API calls. The final local test run passes with:

- 48 tests passing
- 82% coverage from `pytest --cov=app tests/`

This branch contains the completed Assignment 4 submission work and is intended to be merged into `main` through a pull request.
