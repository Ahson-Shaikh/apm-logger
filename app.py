#!/usr/bin/env python3
# app.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from elasticapm import Client, instrument

SERVICE_NAME = os.getenv("SERVICE_NAME", "elk-test-api")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
APM_SERVER_URL = os.getenv("APM_SERVER_URL", "http://localhost:8200")

# Initialize APM client
apm_client = Client(
    service_name=SERVICE_NAME,
    environment=ENVIRONMENT,
    server_url=APM_SERVER_URL,
    # Add secret token if required by your APM server
    # secret_token=os.getenv("APM_SECRET_TOKEN", ""),
)

# Instrument the application for performance monitoring
instrument()

app = FastAPI(title="ELK APM Test API")

# --- Global exception hook so ANY unhandled error is logged + sent to APM ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # This will automatically send the error to Elastic APM
    apm_client.capture_exception()
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/health")
def health():
    # Log info message
    apm_client.logger.info("Health check")
    return {"status": "ok"}

@app.get("/boom")
def boom():
    # Raise a runtime error (unhandled -> goes through global handler above)
    raise RuntimeError("Boom! This is an intentional crash for APM.")

@app.get("/zero")
def zero():
    # Explicitly catch and log an exception
    try:
        1 / 0
    except Exception:
        # Capture the exception in APM
        apm_client.capture_exception()
        raise HTTPException(status_code=500, detail="Division by zero")

@app.get("/log-error")
def log_error(msg: str = "Simulated error from /log-error"):
    # Log an error message
    apm_client.logger.error(msg)
    return {"status": "logged", "message": msg}

@app.get("/payment/fail")
def payment_fail(order_id: str = "ORD-123", user_id: str = "u-abc"):
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
