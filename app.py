#!/usr/bin/env python3
# app.py
import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from elasticapm import Client, instrument, capture_span, set_transaction_name, set_transaction_result

SERVICE_NAME = os.getenv("SERVICE_NAME", "elk-test-api")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
APM_SERVER_URL = os.getenv("APM_SERVER_URL", "http://localhost:8200")

# Initialize APM client with comprehensive configuration for transaction tracking
apm_client = Client(
    service_name=SERVICE_NAME,
    environment=ENVIRONMENT,
    server_url=APM_SERVER_URL,
    # Add secret token if required by your APM server
    # secret_token=os.getenv("APM_SECRET_TOKEN", ""),
    
    # Transaction and span configuration
    transaction_max_spans=100,
    transaction_sample_rate=1.0,  # Capture 100% of transactions
    span_min_duration=0.0,        # Capture all spans regardless of duration
    
    # Performance monitoring
    collect_local_variables="errors",
    capture_span_stack_traces=True,
    
    # HTTP request tracking
    capture_headers=True,
    capture_body="errors",
    
    # Instrumentation settings
    instrument=True,
    
    # Logging configuration
    log_level="info",
    
    # Metrics collection
    metrics_interval="30s",
    
    # Central configuration
    central_config=False,  # Disable to use local config
    
    # Debug mode for troubleshooting
    debug=os.getenv("APM_DEBUG", "false").lower() == "true",
)

# Instrument the application for performance monitoring
# This is crucial for capturing transactions and spans
instrument()

app = FastAPI(title="ELK APM Test API")

# Custom middleware to capture all HTTP requests as APM transactions
@app.middleware("http")
async def apm_transaction_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Set transaction name based on the endpoint
    transaction_name = f"{request.method} {request.url.path}"
    set_transaction_name(transaction_name)
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Set transaction result based on status code
        if response.status_code < 400:
            set_transaction_result("success")
        else:
            set_transaction_result("failure")
        
        # Log the transaction duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        apm_client.logger.info(f"Request processed", extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration, 2)
        })
        
        return response
        
    except Exception as exc:
        # Set transaction result for errors
        set_transaction_result("failure")
        
        # Capture the exception
        apm_client.capture_exception()
        
        # Re-raise the exception
        raise exc

# --- Global exception hook so ANY unhandled error is logged + sent to APM ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # This will automatically send the error to Elastic APM
    apm_client.capture_exception()
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/health")
def health():
    # Create a transaction for this endpoint
    with capture_span("health_check", span_type="app"):
        # Log info message
        apm_client.logger.info("Health check")
        return {"status": "ok"}

@app.get("/boom")
def boom():
    # Create a transaction for this endpoint
    with capture_span("boom_endpoint", span_type="app"):
        # Raise a runtime error (unhandled -> goes through global handler above)
        raise RuntimeError("Boom! This is an intentional crash for APM.")

@app.get("/zero")
def zero():
    # Create a transaction for this endpoint
    with capture_span("zero_endpoint", span_type="app"):
        # Explicitly catch and log an exception
        try:
            1 / 0
        except Exception:
            # Capture the exception in APM
            apm_client.capture_exception()
            raise HTTPException(status_code=500, detail="Division by zero")

@app.get("/log-error")
def log_error(msg: str = "Simulated error from /log-error"):
    # Create a transaction for this endpoint
    with capture_span("log_error_endpoint", span_type="app"):
        # Log an error message
        apm_client.logger.error(msg)
        return {"status": "logged", "message": msg}

@app.get("/payment/fail")
def payment_fail(order_id: str = "ORD-123", user_id: str = "u-abc"):
    # Create a transaction for this endpoint
    with capture_span("payment_fail_endpoint", span_type="app"):
        # Log error with custom context
        apm_client.logger.error(
            "Payment authorization failed",
            extra={
                "order_id": order_id,
                "user_id": user_id,
                "reason": "card_declined"
            }
        )
        return {"status": "logged", "order_id": order_id}
