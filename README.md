# APM Logger

A FastAPI application with integrated Elastic APM error logging and monitoring.

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn requests
```

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# APM Configuration
export APM_SERVER_URL="http://<apm-host>:8200"   # e.g., http://localhost:8200
export SERVICE_NAME="elk-test-api"
export ENVIRONMENT="dev"
```

Or set them directly in your shell:

```bash
export APM_SERVER_URL="http://localhost:8200"
export SERVICE_NAME="elk-test-api"
export ENVIRONMENT="dev"
```

### 3. Run the Application

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Testing the APM Logger

Use these curl commands to test different error scenarios:

### Healthy (no error)
```bash
curl -s http://localhost:8000/health
```

### Unhandled exception -> APM error (and 500)
```bash
curl -s http://localhost:8000/boom
```

### Handled exception with logger.exception -> APM error (and 500)
```bash
curl -s http://localhost:8000/zero
```

### Plain error log (no exception) -> APM error (200 response)
```bash
curl -s "http://localhost:8000/log-error?msg=Something%20broke%20but%20we%20caught%20it"
```

### Structured error with extra attributes (order_id, user_id, reason)
```bash
curl -s "http://localhost:8000/payment/fail?order_id=ORD-999&user_id=u-42"
```

## API Endpoints

- `/health` - Health check endpoint
- `/boom` - Triggers an unhandled exception for testing APM error capture
- `/zero` - Demonstrates handled exceptions with structured logging
- `/log-error` - Logs errors without throwing exceptions
- `/payment/fail` - Shows structured error logging with custom attributes

## Features

- Global exception handler that captures all unhandled errors
- Structured logging with extra context fields
- Integration with Elastic APM for error monitoring
- Environment-based configuration
- Service name and environment tagging for all logs
