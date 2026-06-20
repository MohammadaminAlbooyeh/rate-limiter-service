# API Reference

## Rate Limiting

- `POST /api/v1/check` - Check if request is allowed
- `POST /api/v1/reset/{identity}` - Reset rate limit

## Rules

- `GET /api/v1/rules` - List all rules
- `POST /api/v1/rules` - Create rule
- `PUT /api/v1/rules/{id}` - Update rule
- `DELETE /api/v1/rules/{id}` - Delete rule

## Whitelist/Blacklist

- `POST /api/v1/whitelist` - Add to whitelist
- `POST /api/v1/blacklist` - Add to blacklist
- `DELETE /api/v1/whitelist/{id}` - Remove from whitelist
- `DELETE /api/v1/blacklist/{id}` - Remove from blacklist

## Analytics

- `GET /api/v1/analytics/usage` - Usage statistics
- `GET /api/v1/analytics/blocked` - Blocked requests
- `GET /api/v1/analytics/top` - Top consumers

## Health

- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
