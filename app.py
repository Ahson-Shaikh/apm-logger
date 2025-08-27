#!/usr/bin/env python3
# app.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from apm_error_logger import get_logger  # imports the logger with APM handler

SERVICE_NAME = os.getenv("SERVICE_NAME", "elk-test-api")
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

log = get_logger("elk-test-api")
app = FastAPI(title="ELK APM Test API")

# --- Global exception hook so ANY unhandled error is logged + sent to APM ---
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # This prints to console AND ships to Elastic APM as an error
    log.exception("Unhandled exception", extra={
        "route": str(request.url),
        "method": request.method,
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
    })
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/health")
def health():
    log.info("Health check")
    return {"status": "ok"}

@app.get("/boom")
def boom():
    # Raise a runtime error (unhandled -> goes through global handler above)
    raise RuntimeError("Boom! This is an intentional crash for APM.")

@app.get("/zero")
def zero():
    # Explicitly catch and log an exception (logger.exception captures traceback)
    try:
        1 / 0
    except Exception:
        log.exception("Divide-by-zero in /zero", extra={"route": "/zero"})
        raise HTTPException(status_code=500, detail="Division by zero")

@app.get("/log-error")
def log_error(msg: str = "Simulated error from /log-error"):
    # Log an error WITHOUT throwing (still goes to APM because level=ERROR)
    log.error(msg, extra={"route": "/log-error"})
    return {"status": "logged", "message": msg}

@app.get("/payment/fail")
def payment_fail(order_id: str = "ORD-123", user_id: str = "u-abc"):
    # Structured fields using logger.extra
    log.error("Payment authorization failed",
              extra={"route": "/payment/fail", "order_id": order_id, "user_id": user_id, "reason": "card_declined"})
    return {"status": "logged", "order_id": order_id}
