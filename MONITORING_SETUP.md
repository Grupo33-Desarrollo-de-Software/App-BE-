# API Monitoring and Diagnostics System - Setup Guide

## Overview

A comprehensive API monitoring and diagnostics system has been implemented for your Django/Angular application. This system provides real-time monitoring, error tracking, and performance metrics.

## Features Implemented

### Backend (Django)

1. **APIMonitor Model** - Stores detailed API request/response data
2. **APIMonitoringMiddleware** - Captures all API requests automatically
3. **Admin-Only Dashboard Endpoints** - Secure API endpoints for monitoring data
4. **Comprehensive Logging** - Detailed error tracking with stack traces

### Frontend (Angular)

1. **Monitoring Dashboard Component** - Visual dashboard for API metrics
2. **Real-time Metrics Display** - Charts and statistics
3. **Error Details View** - Detailed error information with stack traces

## Setup Instructions

### 1. Database Migration

Run the following commands to create the necessary database tables:

```bash
cd Notify
python manage.py makemigrations logger
python manage.py migrate
```

### 2. Verify Middleware Configuration

The middleware has been added to `Notify/settings.py`. Verify it's in the MIDDLEWARE list:

```python
MIDDLEWARE = [
    "logger.middleware.APIMonitoringMiddleware",  # Comprehensive API monitoring
    "logger.middleware.logResponsetimeMiddleware",  # Legacy logging
    # ... other middleware
]
```

### 3. Admin Access

The monitoring dashboard requires admin privileges. Ensure your user has `is_staff=True` and `is_superuser=True`:

```python
# In Django shell or admin
user = Usuario.objects.get(username='your_admin_username')
user.is_staff = True
user.is_superuser = True
user.save()
```

### 4. API Endpoints

The following endpoints are available (admin-only):

- `GET /api/v1/logger/monitoring/dashboard?hours=24` - Main dashboard metrics
- `GET /api/v1/logger/monitoring/details/<request_id>` - Detailed request information
- `GET /api/v1/logger/monitoring/errors?hours=24&status_code=500&endpoint=/api/...` - Filtered error list

### 5. Frontend Access

Navigate to: `http://localhost:4200/admin/monitoreo`

**Note:** You must be logged in with an admin account and have the auth token in localStorage.

## How to Login and Store Token

### Option 1: Using Browser Console

1. Open your Angular app: `http://localhost:4200`
2. Open Developer Tools (F12) → Console tab
3. Run this script:

```javascript
fetch('http://127.0.0.1:8000/api-user-login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',  // Your admin username
    password: 'your_password'  // Your admin password
  })
})
.then(response => response.json())
.then(data => {
  localStorage.setItem('auth_token', data.token);
  localStorage.setItem('user_id', data.id.toString());
  localStorage.setItem('username', data.username);
  console.log('✅ Login successful! Token stored.');
  console.log('Navigate to: http://localhost:4200/admin/monitoreo');
})
.catch(error => console.error('Login failed:', error));
```

### Option 2: Register a New User

1. Navigate to: `http://localhost:4200/register`
2. Fill out the registration form
3. The token will be automatically stored in localStorage
4. Make the user an admin via Django admin or shell
5. Access the monitoring dashboard

## Dashboard Metrics

The dashboard displays:

1. **Total Request Count** - Number of API requests in the selected time range
2. **Average Response Time** - Mean response time across all requests
3. **Error Count & Rate** - Total errors and percentage of requests that failed
4. **Error Breakdown** - Errors grouped by HTTP status code
5. **Top Endpoints** - Most frequently accessed endpoints with performance data
6. **Recent Errors** - Latest errors with full details including stack traces
7. **Requests Per Hour** - Time series data for request volume

## Data Captured

For each API request, the system captures:

- **Request ID** (UUID) - Unique identifier for tracing
- **Timestamp** - When the request occurred
- **HTTP Method** - GET, POST, PUT, DELETE, etc.
- **Endpoint** - Full request path
- **Status Code** - HTTP response status
- **Response Time** - Time taken to process the request (milliseconds)
- **User** - Authenticated user (if applicable)
- **IP Address** - Client IP address
- **User Agent** - Browser/client information
- **Error Message** - Error details (if error occurred)
- **Stack Trace** - Full exception stack trace (if error occurred)
- **Request Body** - Request payload (limited to 10KB for POST/PUT/PATCH)

## Security

- All monitoring endpoints require admin privileges (`IsAdminUser` permission)
- Request bodies are limited to prevent storing sensitive data
- Only API endpoints (`/api/*`) are monitored (admin, static files excluded)

## Performance Considerations

- Database indexes are created on frequently queried fields
- Request body storage is limited to 10KB
- Error messages and stack traces are truncated to prevent excessive storage
- Recent errors are limited to 100 results

## Troubleshooting

### Dashboard shows "Access denied"
- Ensure your user has `is_staff=True` and `is_superuser=True`
- Verify you're sending the authentication token in the request headers
- Check that the token is stored in localStorage: `localStorage.getItem('auth_token')`

### No data showing
- Check that the middleware is active in settings.py
- Verify API requests are being made (the system only monitors `/api/*` endpoints)
- Check the database for APIMonitor records

### High database growth
- Consider implementing data retention policies
- The system stores all API requests - for high-traffic applications, consider archiving old data

## Next Steps

1. Run migrations: `python manage.py migrate`
2. Test the middleware by making some API requests
3. Log in and store your auth token
4. Access the dashboard at `/admin/monitoreo`
5. Monitor your API health in real-time!

## Additional Notes

- The system automatically starts monitoring once the middleware is active
- All API responses include an `X-Request-ID` header for tracing
- Error details are automatically captured when exceptions occur
- The dashboard supports time range filtering (1h, 6h, 12h, 24h, 48h, 72h)

