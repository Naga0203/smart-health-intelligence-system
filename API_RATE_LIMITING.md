# API Rate Limiting Documentation

## Overview

The AI Health Intelligence System implements comprehensive rate limiting to prevent abuse and ensure fair usage of the computationally expensive health analysis API.

## Rate Limiting Strategy

### Multi-Layer Protection

The system uses multiple layers of rate limiting:

1. **Burst Protection** - Prevents rapid-fire requests
2. **Hourly Limits** - Controls sustained usage
3. **Daily Limits** - Prevents excessive long-term usage
4. **IP-Based Limits** - Additional protection regardless of authentication

## Rate Limits by Endpoint

### `/api/health/analyze` (Authenticated)

**Primary health analysis endpoint with Firebase authentication**

| Throttle Type | Limit | Purpose |
|--------------|-------|---------|
| Burst | 10 requests/minute | Prevent rapid-fire abuse |
| Hourly | 100 requests/hour | Control sustained usage |
| Daily | 200 requests/day | Prevent excessive usage |
| IP-Based | 200 requests/hour | Additional IP protection |

### `/api/assess` (Anonymous)

**Health assessment endpoint without authentication**

| Throttle Type | Limit | Purpose |
|--------------|-------|---------|
| Anonymous | 5 requests/hour | Strict limit for unauthenticated users |
| IP-Based | 200 requests/hour | Additional IP protection |

## Throttle Classes

### HealthAnalysisRateThrottle
- **Scope**: `health_analysis`
- **Default Rate**: 100 requests/hour
- **Applied To**: Authenticated users
- **Purpose**: Control sustained usage of health analysis

### HealthAnalysisBurstRateThrottle
- **Scope**: `health_analysis_burst`
- **Default Rate**: 10 requests/minute
- **Applied To**: All health analysis requests
- **Purpose**: Prevent rapid-fire request abuse

### AnonymousHealthAnalysisThrottle
- **Scope**: `anon_health_analysis`
- **Default Rate**: 5 requests/hour
- **Applied To**: Unauthenticated users
- **Purpose**: Stricter limits for anonymous access

### IPBasedRateThrottle
- **Scope**: `ip_based`
- **Default Rate**: 200 requests/hour
- **Applied To**: All requests by IP address
- **Purpose**: Prevent distributed abuse attempts

### DailyRateThrottle
- **Scope**: `daily_health_analysis`
- **Default Rate**: 200 requests/day
- **Applied To**: Authenticated users
- **Purpose**: Prevent excessive long-term usage

### AdaptiveRateThrottle
- **Scope**: `adaptive`
- **Default Rate**: 100 requests/hour
- **Applied To**: Can be applied to any endpoint
- **Purpose**: Future enhancement for dynamic rate adjustment

## Error Response Format

When rate limit is exceeded, the API returns:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests",
  "details": "Rate limit exceeded. Please try again in 60 seconds.",
  "wait_seconds": 60,
  "status_code": 429
}
```

**HTTP Status Code**: `429 Too Many Requests`

## Rate Limit Headers

The API includes standard rate limit headers in responses:

- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining in current window
- `X-RateLimit-Reset` - Time when the rate limit resets (Unix timestamp)

## Monitoring and Logging

### Rate Limit Violations

All rate limit violations are logged with:
- User ID (if authenticated)
- IP address
- Throttle class that triggered
- Wait time until reset
- Timestamp

### Log Format

```
WARNING: Rate limit exceeded - User: firebase_uid, IP: 192.168.1.1, 
         Throttle: HealthAnalysisBurstRateThrottle, Wait: 60s
```

### Violation Tracking

Rate limit violations are cached for 24 hours to identify potential abuse patterns:
- Cache key: `rate_limit_violations:{user_id}:{ip_address}`
- Timeout: 86400 seconds (24 hours)

## Configuration

### Settings Location

Rate limits are configured in `health_ai_backend/settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'health_analysis': '100/hour',
        'health_analysis_burst': '10/min',
        'anon_health_analysis': '5/hour',
        'ip_based': '200/hour',
        'daily_health_analysis': '200/day',
        'adaptive': '100/hour',
    }
}
```

### Cache Configuration

Rate limiting uses Django's cache framework:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'health-ai-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    }
}
```

## Customization

### Adjusting Rate Limits

To adjust rate limits, modify the `DEFAULT_THROTTLE_RATES` in settings.py:

```python
'health_analysis': '200/hour',  # Increase to 200/hour
'health_analysis_burst': '20/min',  # Increase to 20/min
```

### Adding Custom Throttles

1. Create a new throttle class in `api/throttling.py`:

```python
class CustomRateThrottle(SimpleRateThrottle):
    scope = 'custom_scope'
    
    def get_cache_key(self, request, view):
        # Custom cache key logic
        pass
```

2. Add the scope to settings:

```python
'custom_scope': '50/hour',
```

3. Apply to view:

```python
class MyView(APIView):
    throttle_classes = [CustomRateThrottle]
```

## Best Practices

### For API Consumers

1. **Implement Exponential Backoff**: When receiving 429 errors, wait progressively longer between retries
2. **Cache Responses**: Cache assessment results to reduce API calls
3. **Batch Requests**: Group multiple assessments when possible
4. **Monitor Usage**: Track your API usage to stay within limits

### For Administrators

1. **Monitor Logs**: Regularly review rate limit violation logs
2. **Adjust Limits**: Tune rate limits based on usage patterns
3. **Use Redis**: For production, use Redis cache instead of LocMemCache
4. **Set Alerts**: Configure alerts for excessive rate limit violations

## Production Recommendations

### Redis Cache

For production deployments, use Redis for better performance and distributed caching:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Load Balancer Configuration

When using load balancers, ensure:
- Rate limiting is applied per-user, not per-server
- Shared cache (Redis) is used across all servers
- IP addresses are correctly forwarded (X-Forwarded-For header)

## Testing Rate Limits

### Manual Testing

```bash
# Test burst rate limiting
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/health/analyze \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"symptoms": ["fever"], "age": 30, "gender": "male"}'
  echo "Request $i"
done
```

### Automated Testing

Run the test suite:

```bash
python api/test_throttling_unit.py
```

## Troubleshooting

### Rate Limit Not Working

1. Check cache is configured correctly
2. Verify throttle classes are imported in views
3. Ensure `throttle_classes` is set on the view
4. Check Django REST Framework settings

### False Positives

If legitimate users are being rate limited:
1. Review rate limit thresholds
2. Check for shared IP addresses (NAT, proxies)
3. Consider implementing user tiers with different limits
4. Review cache key generation logic

## Security Considerations

1. **DDoS Protection**: Rate limiting provides basic DDoS protection
2. **Credential Stuffing**: Limits prevent rapid credential testing
3. **Resource Exhaustion**: Prevents single users from monopolizing resources
4. **Cost Control**: Limits API costs from external services (Gemini AI)

## Future Enhancements

1. **User Tiers**: Different rate limits for different subscription levels
2. **Dynamic Adjustment**: Adjust rates based on system load
3. **Quota Management**: Monthly/yearly quotas in addition to time-based limits
4. **Rate Limit Dashboard**: Web interface for monitoring and management
5. **Whitelist/Blacklist**: IP-based access control lists

## References

- Django REST Framework Throttling: https://www.django-rest-framework.org/api-guide/throttling/
- HTTP 429 Status Code: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429
- Rate Limiting Best Practices: https://cloud.google.com/architecture/rate-limiting-strategies-techniques
