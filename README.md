# APM Logger - FastAPI with Elastic APM Integration

A FastAPI application with integrated Elastic APM agent for comprehensive error logging, performance monitoring, transaction capture, and distributed tracing.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export APM_SERVER_URL="http://your-apm-server:8200"
export SERVICE_NAME="elk-test-api"
export ENVIRONMENT="dev"
export APM_DEBUG="true"  # Optional: for troubleshooting
```

### 3. Run the Application
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 4. Test Endpoints
```bash
./test_endpoints.sh
```

## 📋 What's Included

✅ **Error Tracking**: Automatic capture of exceptions and errors  
✅ **Transaction Capture**: All HTTP requests captured as APM transactions  
✅ **Performance Monitoring**: Request duration, status codes, and metrics  
✅ **Structured Logging**: Custom context fields (order_id, user_id, reason)  
✅ **Global Error Handling**: Catches all unhandled exceptions automatically  
✅ **Environment Configuration**: Easy setup for different environments  
✅ **System Metrics**: CPU, memory, and process monitoring  
✅ **Debug Mode**: Troubleshooting support for APM issues  

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APM_SERVER_URL` | APM server endpoint | `http://localhost:8200` | Yes |
| `SERVICE_NAME` | Service identifier in APM | `elk-test-api` | Yes |
| `ENVIRONMENT` | Environment tag | `dev` | Yes |
| `APM_SECRET_TOKEN` | Authentication token | - | No |
| `APM_DEBUG` | Enable debug mode | `false` | No |

### APM Client Configuration

The application uses a comprehensive APM configuration:

```python
apm_client = Client(
    service_name=SERVICE_NAME,
    environment=ENVIRONMENT,
    server_url=APM_SERVER_URL,
    transaction_max_spans=100,
    transaction_sample_rate=1.0,  # Capture 100% of transactions
    span_min_duration=0.0,        # Capture all spans
    collect_local_variables="errors",
    capture_span_stack_traces=True,
    capture_headers=True,
    capture_body="errors",
    instrument=True,
    debug=APM_DEBUG
)
```

## 🌐 API Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/health` | GET | Health check endpoint | 200 OK |
| `/boom` | GET | Triggers unhandled exception | 500 Error |
| `/zero` | GET | Handled exception with APM capture | 500 Error |
| `/log-error` | GET | Logs error without throwing | 200 OK |
| `/payment/fail` | GET | Structured error logging | 200 OK |

## 📊 Testing the APM Integration

### Manual Testing
```bash
# Health check (should return 200)
curl -s http://localhost:8000/health

# Unhandled exception -> APM error (and 500)
curl -s http://localhost:8000/boom

# Handled exception with APM capture -> APM error (and 500)
curl -s http://localhost:8000/zero

# Plain error log (no exception) -> APM error (200 response)
curl -s "http://localhost:8000/log-error?msg=Something%20broke%20but%20we%20caught%20it"

# Structured error with extra attributes
curl -s "http://localhost:8000/payment/fail?order_id=ORD-999&user_id=u-42"
```

### Automated Testing
```bash
# Run the test script
./test_endpoints.sh
```

## 🔍 Transaction Capture Solution

### Problem Solved
The original APM agent version (6.24.0) doesn't have automatic ASGI/FastAPI transaction capture, which is why transactions weren't appearing in Kibana.

### Solution Implemented
1. **Custom Middleware**: `apm_transaction_middleware` captures every HTTP request
2. **Transaction Naming**: Automatically names transactions as `METHOD /path`
3. **Transaction Results**: Sets success/failure based on HTTP status codes
4. **Duration Tracking**: Measures and logs request processing time
5. **Manual Spans**: Creates explicit spans for each endpoint using `capture_span`

### Result
You should now see transactions in Kibana for every endpoint call with:
- Request method and path
- Response status code
- Processing duration
- Success/failure status

## 📁 Project Structure

```
apm-logger/
├── app.py                 # Main FastAPI application with APM integration
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── setup_env.sh          # Environment setup script
├── test_endpoints.sh     # Endpoint testing script
├── elasticapm.yml        # APM configuration file
└── venv/                 # Python virtual environment
```

## 🛠️ Setup Scripts

### Environment Setup
```bash
# Run the setup script
./setup_env.sh

# This will:
# - Install all dependencies
# - Set environment variables
# - Provide usage instructions
```

### Testing
```bash
# Test all endpoints
./test_endpoints.sh

# This will test:
# - Health endpoint
# - Error logging
# - Exception handling
# - Transaction capture
```

## 🔧 Troubleshooting

### Transactions Not Appearing in Kibana

1. **Enable Debug Mode**
   ```bash
   export APM_DEBUG="true"
   ```

2. **Check APM Server**
   - Ensure your APM server is running
   - Verify the `APM_SERVER_URL` is correct
   - Check network connectivity

3. **Verify Configuration**
   - Confirm `SERVICE_NAME` and `ENVIRONMENT` are set
   - Check that the APM server can reach your application

4. **Check Application Logs**
   - Look for APM-related error messages
   - Verify the custom middleware is working

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection timeout | APM server not running or unreachable |
| No transactions in Kibana | Check debug mode and middleware configuration |
| Errors not captured | Verify exception handler is working |
| Performance issues | Check transaction sampling settings |

## 🚀 Next Steps

1. **Configure APM Server**: Set up Elastic APM server or use cloud APM service
2. **Custom Metrics**: Add business-specific metrics using `apm_client.metrics`
3. **User Context**: Set user information with `apm_client.set_user_context`
4. **Custom Spans**: Create custom performance spans for business logic
5. **Alerting**: Configure APM alerts for error thresholds
6. **Distributed Tracing**: Set up tracing across multiple services

## 📚 Additional Resources

- [Elastic APM Python Agent Documentation](https://www.elastic.co/guide/en/apm/agent/python/current/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Elastic APM Server Setup](https://www.elastic.co/guide/en/apm/server/current/)

## 🎯 Benefits

- **Production Ready**: Official Elastic APM agent with enterprise support
- **Performance Monitoring**: Automatic request tracing and performance metrics
- **Transaction Capture**: All HTTP requests properly tracked
- **Better Integration**: Seamless integration with Elastic Stack
- **Advanced Features**: Distributed tracing, custom metrics, user context
- **Maintenance**: Actively maintained with regular updates and security patches

---

Your application is now ready for production APM monitoring with full transaction capture! 🚀

For support or questions, check the troubleshooting section above or refer to the Elastic APM documentation.