#!/usr/bin/env python3
import logging, os, sys, json, socket
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

APM_SERVER_URL = os.getenv("APM_SERVER_URL", "http://localhost:8200").rstrip("/")
SERVICE_NAME   = os.getenv("SERVICE_NAME", "my-python-service")
ENVIRONMENT    = os.getenv("ENVIRONMENT", "prod")
SERVICE_VERSION= os.getenv("SERVICE_VERSION", "")
HOSTNAME       = socket.gethostname()

def _session():
    s = requests.Session()
    s.mount("http://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.3,
                                                     status_forcelist=(429,500,502,503,504),
                                                     allowed_methods=frozenset(["POST"]))))
    s.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.3,
                                                      status_forcelist=(429,500,502,503,504),
                                                      allowed_methods=frozenset(["POST"]))))
    return s

def _metadata_line():
    md = {
        "metadata": {
            "service": {
                "name": SERVICE_NAME,
                "environment": ENVIRONMENT,
                **({"version": SERVICE_VERSION} if SERVICE_VERSION else {})
            },
            "system": {
                "hostname": HOSTNAME,
                "detected_hostname": HOSTNAME
            }
        }
    }
    return json.dumps(md, separators=(",", ":"))

class ElasticAPMErrorHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.s = _session()
        self.endpoint = f"{APM_SERVER_URL}/intake/v2/events"
        # No auth headers at all (your APM server is open)
        self.headers = {
            "Content-Type": "application/x-ndjson",
            "User-Agent": "python-elastic-apm-error-logger/1.0",
        }

    def emit(self, rec: logging.LogRecord):
        if rec.levelno < logging.ERROR:
            return
        try:
            exc_text = None
            if rec.exc_info:
                exc_text = logging.Formatter().formatException(rec.exc_info)

            err = {
                "error": {
                    "log": {
                        "level": rec.levelname,
                        "logger_name": rec.name,
                        "message": rec.getMessage(),
                    },
                    # microseconds since epoch per APM intake
                    "timestamp": int(rec.created * 1_000_000),
                    "culprit": f"{rec.module}:{rec.funcName}",
                    "context": {
                        "service": {"name": SERVICE_NAME, "environment": ENVIRONMENT},
                        "labels": {
                            "host": HOSTNAME,
                            "pid": rec.process,
                            "thread": rec.threadName,
                            "file": rec.pathname,
                            "line": rec.lineno,
                        },
                    },
                }
            }
            if exc_text:
                err["error"]["exception"] = [{
                    "message": rec.getMessage(),
                    "stacktrace": [{
                        "abs_path": rec.pathname,
                        "function": rec.funcName,
                        "lineno": rec.lineno
                    }]
                }]

            body = _metadata_line() + "\n" + json.dumps(err, separators=(",", ":")) + "\n"
            resp = self.s.post(self.endpoint, data=body, headers=self.headers, timeout=5)
            if resp.status_code >= 300:
                print(f"[ElasticAPMErrorHandler] {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"[ElasticAPMErrorHandler] send failed: {e}", file=sys.stderr)

def get_logger(name="app") -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    # Console (shows the error immediately)
    c = logging.StreamHandler(sys.stdout)
    c.setLevel(logging.INFO)
    c.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    log.addHandler(c)

    # APM forwarder (ERROR+ only)
    log.addHandler(ElasticAPMErrorHandler())
    return log

# --- Demo ---
if __name__ == "__main__":
    logger = get_logger("demo")
    logger.info("Service starting…")
    try:
        1 / 0
    except Exception:
        # prints to console AND ships to Elastic APM
        logger.exception("Unhandled exception during request", extra={"route": "/compute", "user_id": "abc123"})
    logger.info("Continuing after error…")
